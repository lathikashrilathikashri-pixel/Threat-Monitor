"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Threat Detection & Correlation Engine
FILE: backend/detection_engine.py
===================================================================================
WHAT THIS FILE DOES:
    Implements rule-based, defensive cybersecurity detection algorithms that 
    analyze incoming security events and authentication attempts in real-time.
    
    Detection Rules:
    1. Brute Force Detection (>5 failed logins from same IP in 5 min window)
    2. Suspicious / Blacklisted IP Detection (matches blocked_ips table)
    3. Port Scan Detection (multiple distinct destination ports targeted in short window)
    4. Repeated Suspicious Events (device risk escalation)
    5. Abnormal Login Sequences (repeated failed logins followed by successful login)
    6. Suspicious Process / Tool Detection (detection of unauthorized offensive tools)
    
    Risk Scoring Algorithm:
    - Normalizes severity (LOW: 1-3, MEDIUM: 4-6, HIGH: 7-8, CRITICAL: 9-10)
    - Dynamically compounds risk if the IP or device has prior alerts.
    - NEVER blindly trusts client-reported severity; validates and recalculates.

WHY IT IS REQUIRED:
    Core component of a Security Operations Center (SOC). Ingested raw logs are 
    noisy; this engine correlates events, identifies genuine attack patterns, and
    generates prioritized actionable alerts.

HOW IT CONNECTS TO OTHER MODULES:
    - Called by backend/routes/event_routes.py upon receiving telemetry POST /api/events.
    - Called by backend/routes/auth_routes.py upon recording login attempts.
    - Writes new Alert records into the database via SQLAlchemy session.
===================================================================================
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from models import SecurityEvent, Alert, BlockedIP, LoginAttempt, Device
from config import Config

class ThreatDetectionEngine:
    """
    SOC Defensive Rule Engine & Multi-Factor Risk Scoring Calculator.
    """

    def __init__(self, db_session):
        self.session = db_session

    def process_event(self, event_data: dict, client_ip: str) -> tuple[str, int, list[Alert]]:
        """
        Main entrypoint when an external device or simulation sends an event.
        Returns:
            (verified_severity, calculated_risk_score, list_of_new_alerts)
        """
        alerts_generated = []
        source_ip = event_data.get("source_ip") or client_ip
        device_id = event_data.get("device_id")
        event_type = event_data.get("event_type", "GENERIC_EVENT").upper()
        destination_port = event_data.get("destination_port")
        process_name = event_data.get("process_name")
        description = event_data.get("description", "")

        # Base Risk Score calculation (1-10)
        base_score = 2
        initial_severity = "LOW"

        # ---------------------------------------------------------
        # RULE 1: Suspicious / Blocked IP Blacklist Check
        # ---------------------------------------------------------
        is_blocked = self._check_blocked_ip(source_ip)
        if is_blocked:
            base_score = 10
            initial_severity = "CRITICAL"
            alert = Alert(
                alert_type="Blacklisted IP Communication Detected",
                severity="CRITICAL",
                risk_score=10,
                source_ip=source_ip,
                device_id=device_id,
                description=f"Inbound/Outbound traffic detected from blacklisted IP address: {source_ip}. Event: {description}",
                status="NEW"
            )
            self.session.add(alert)
            alerts_generated.append(alert)

        # ---------------------------------------------------------
        # RULE 2: Suspicious Process / Tool Execution Check
        # ---------------------------------------------------------
        if process_name and self._is_suspicious_process(process_name):
            score = 8
            base_score = max(base_score, score)
            initial_severity = "HIGH"
            alert = Alert(
                alert_type="Suspicious Process Execution",
                severity="HIGH",
                risk_score=score,
                source_ip=source_ip,
                device_id=device_id,
                description=f"Unauthorized/Suspicious security tooling or binary detected running on endpoint {device_id}: {process_name}",
                status="NEW"
            )
            self.session.add(alert)
            alerts_generated.append(alert)

        # ---------------------------------------------------------
        # RULE 3: Port Scan Detection
        # ---------------------------------------------------------
        if event_type in ["PORT_SCAN", "PORT_SCAN_ATTEMPT"] or (destination_port and self._detect_port_scan(source_ip, device_id)):
            score = 8
            base_score = max(base_score, score)
            initial_severity = "HIGH"
            alert = Alert(
                alert_type="Potential Port Scan Attack",
                severity="HIGH",
                risk_score=score,
                source_ip=source_ip,
                device_id=device_id,
                description=f"Device {device_id} or host {source_ip} probed multiple ports within a brief time window.",
                status="NEW"
            )
            self.session.add(alert)
            alerts_generated.append(alert)

        # ---------------------------------------------------------
        # RULE 4: Failed Login / Brute Force Telemetry Check
        # ---------------------------------------------------------
        if event_type in ["FAILED_LOGIN", "AUTH_FAILURE"]:
            base_score = max(base_score, 4)
            initial_severity = "MEDIUM" if initial_severity == "LOW" else initial_severity
            
            # Check if this crosses the threshold for a Brute Force Alert
            bf_alert = self.check_brute_force(source_ip, device_id)
            if bf_alert:
                base_score = max(base_score, bf_alert.risk_score)
                initial_severity = bf_alert.severity
                alerts_generated.append(bf_alert)

        # ---------------------------------------------------------
        # RULE 5: Multi-Event Repetition & Device Risk Escalation
        # ---------------------------------------------------------
        escalation_score = self._calculate_repetition_escalation(source_ip, device_id)
        final_score = min(10, base_score + escalation_score)
        
        # Translate score to official SOC Severity level
        verified_severity = self._score_to_severity(final_score)

        return verified_severity, final_score, alerts_generated

    def check_brute_force(self, source_ip: str, device_id: str = None) -> Alert | None:
        """
        Rule: If the same IP produces > 5 failed logins within 5 minutes,
        trigger a HIGH severity 'Brute Force Attack Detected' alert.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=Config.BRUTE_FORCE_WINDOW_MINUTES)
        
        # Query failed login attempts from this IP within window
        failed_count = (
            self.session.query(func.count(LoginAttempt.id))
            .filter(
                LoginAttempt.ip_address == source_ip,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at >= cutoff_time
            )
            .scalar() or 0
        )

        # Also count raw FAILED_LOGIN security events if submitted via external agent
        event_failed_count = (
            self.session.query(func.count(SecurityEvent.id))
            .filter(
                SecurityEvent.source_ip == source_ip,
                SecurityEvent.event_type.in_(["FAILED_LOGIN", "AUTH_FAILURE"]),
                SecurityEvent.timestamp >= cutoff_time
            )
            .scalar() or 0
        )

        total_failures = failed_count + event_failed_count

        if total_failures >= Config.BRUTE_FORCE_MAX_FAILURES:
            # Check if we already created an active alert for this in the last 5 minutes to avoid spamming duplicates
            recent_alert = (
                self.session.query(Alert)
                .filter(
                    Alert.alert_type == "Brute Force Attack Detected",
                    Alert.source_ip == source_ip,
                    Alert.created_at >= cutoff_time
                )
                .first()
            )
            if not recent_alert:
                alert = Alert(
                    alert_type="Brute Force Attack Detected",
                    severity="HIGH",
                    risk_score=8,
                    source_ip=source_ip,
                    device_id=device_id or "NETWORK-GATEWAY",
                    description=f"Detected {total_failures} repeated failed authentication attempts from IP {source_ip} within {Config.BRUTE_FORCE_WINDOW_MINUTES} minutes.",
                    status="NEW"
                )
                self.session.add(alert)
                return alert
        return None

    def check_abnormal_login(self, username: str, source_ip: str) -> Alert | None:
        """
        Rule: Detect repeated failed logins followed immediately by a successful login.
        Indicates probable password guessing / brute force breakthrough.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        
        recent_failures = (
            self.session.query(func.count(LoginAttempt.id))
            .filter(
                LoginAttempt.ip_address == source_ip,
                LoginAttempt.username == username,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at >= cutoff_time
            )
            .scalar() or 0
        )

        if recent_failures >= 3:
            alert = Alert(
                alert_type="Abnormal Login Sequence / Credential Compromise",
                severity="HIGH",
                risk_score=7,
                source_ip=source_ip,
                device_id="AUTH-GATEWAY",
                description=f"Account '{username}' logged in successfully immediately following {recent_failures} failed login attempts from IP {source_ip}.",
                status="NEW"
            )
            self.session.add(alert)
            return alert
        return None

    def _check_blocked_ip(self, ip_address: str) -> bool:
        """Checks if the given IP address is in the active blacklisted table."""
        match = (
            self.session.query(BlockedIP)
            .filter(BlockedIP.ip_address == ip_address, BlockedIP.is_active == True)
            .first()
        )
        return match is not None

    def _is_suspicious_process(self, process_name: str) -> bool:
        """Matches process against known offensive security and hacking tools."""
        p_lower = process_name.lower().strip()
        for suspicious in Config.SUSPICIOUS_PROCESS_NAMES:
            if suspicious in p_lower:
                return True
        return False

    def _detect_port_scan(self, source_ip: str, device_id: str) -> bool:
        """
        Determines if more than Config.PORT_SCAN_PORT_THRESHOLD distinct ports 
        were hit from the same IP/Device within the time window.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=Config.PORT_SCAN_WINDOW_MINUTES)
        distinct_ports = (
            self.session.query(func.count(func.distinct(SecurityEvent.destination_port)))
            .filter(
                SecurityEvent.source_ip == source_ip,
                SecurityEvent.destination_port != None,
                SecurityEvent.timestamp >= cutoff
            )
            .scalar() or 0
        )
        return distinct_ports >= Config.PORT_SCAN_PORT_THRESHOLD

    def _calculate_repetition_escalation(self, source_ip: str, device_id: str) -> int:
        """
        Increases risk score if the device/IP has had unresolved alerts in past 24 hours.
        """
        yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
        active_alerts_count = (
            self.session.query(func.count(Alert.id))
            .filter(
                Alert.source_ip == source_ip,
                Alert.status.in_(["NEW", "INVESTIGATING"]),
                Alert.created_at >= yesterday
            )
            .scalar() or 0
        )
        if active_alerts_count >= 3:
            return 2
        elif active_alerts_count >= 1:
            return 1
        return 0

    @staticmethod
    def _score_to_severity(score: int) -> str:
        """Maps 1-10 numerical risk score to SOC severity categories."""
        if score >= 9:
            return "CRITICAL"
        elif score >= 7:
            return "HIGH"
        elif score >= 4:
            return "MEDIUM"
        return "LOW"
