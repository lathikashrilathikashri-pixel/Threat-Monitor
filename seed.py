"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Database Seeding & Demo Generator
FILE: backend/seed.py
===================================================================================
WHAT THIS FILE DOES:
    Populates the database with initial SOC demo data:
    1. Default User Accounts:
       - Admin: username='admin', password='AdminSecure2026!'
       - Analyst: username='analyst1', password='AnalystPass2026!'
       - User: username='auditor', password='AuditorPass2026!'
    2. Registered External Monitoring Endpoints (Laptops & VMs with API keys)
    3. Blacklisted IP entries (known malicious botnets/scanners)
    4. Starter Security Events, Alerts, and Incident tickets

WHY IT IS REQUIRED:
    Provides an out-of-the-box working SOC environment for college viva evaluation 
    and immediate demonstration without requiring manual data entry.

HOW IT CONNECTS TO OTHER MODULES:
    - Creates records via SQLAlchemy models in backend/models.py.
    - Can be executed directly or called on startup if database is empty.
===================================================================================
"""

from datetime import datetime, timezone, timedelta
try:
    from models import Base, User, Device, SecurityEvent, Alert, Incident, LoginAttempt, BlockedIP
except (ImportError, ModuleNotFoundError):
    from backend.models import Base, User, Device, SecurityEvent, Alert, Incident, LoginAttempt, BlockedIP

def seed_database(session):
    """Inserts initial demo datasets if tables are unseeded."""
    # Check if admin already exists
    if session.query(User).filter(User.username == "admin").first():
        print("[*] Database already populated with seed data.")
        return

    print("[+] Seeding default SOC users...")
    admin = User(username="admin", email="admin@soc-command.local", role="Admin")
    admin.set_password("AdminSecure2026!")

    analyst = User(username="analyst1", email="analyst1@soc-command.local", role="Security Analyst")
    analyst.set_password("AnalystPass2026!")

    auditor = User(username="auditor", email="auditor@soc-command.local", role="User")
    auditor.set_password("AuditorPass2026!")

    session.add_all([admin, analyst, auditor])
    session.flush()

    print("[+] Seeding registered external monitoring devices...")
    device1 = Device(
        id="LAPTOP-SEC-AGENT-01",
        device_name="External ThinkPad T14 (Student Device)",
        os_type="Windows 11 Enterprise",
        ip_address="192.168.1.105",
        api_key="sec_dev_token_alpha_9921",
        status="ONLINE",
        last_seen=datetime.now(timezone.utc)
    )

    device2 = Device(
        id="VM-KALI-DEFENSE-02",
        device_name="Linux Security Gateway VM",
        os_type="Ubuntu 24.04 LTS",
        ip_address="10.0.4.15",
        api_key="sec_dev_token_beta_3310",
        status="ONLINE",
        last_seen=datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    session.add_all([device1, device2])
    session.flush()

    print("[+] Seeding perimeter IP blacklist...")
    b1 = BlockedIP(
        ip_address="185.220.101.5",
        reason="Known Tor Exit Node / Malicious Brute Force Botnet",
        blocked_by="SOC Automated Defense",
        is_active=True
    )
    b2 = BlockedIP(
        ip_address="45.143.200.12",
        reason="Repeated Port Scanning & Web Vulnerability Probing",
        blocked_by="analyst1",
        is_active=True
    )
    session.add_all([b1, b2])
    session.flush()

    print("[+] Seeding sample security events...")
    now = datetime.now(timezone.utc)
    events = [
        SecurityEvent(
            device_id=device1.id,
            event_type="FAILED_LOGIN",
            source_ip="185.220.101.5",
            username="administrator",
            description="Repeated failed RDP authentication attempt",
            severity="HIGH",
            timestamp=now - timedelta(minutes=40)
        ),
        SecurityEvent(
            device_id=device1.id,
            event_type="PORT_SCAN_ATTEMPT",
            source_ip="45.143.200.12",
            destination_port=445,
            description="SYN packet probe detected across SMB and NetBIOS ports",
            severity="HIGH",
            timestamp=now - timedelta(minutes=30)
        ),
        SecurityEvent(
            device_id=device2.id,
            event_type="SUSPICIOUS_PROCESS",
            source_ip="10.0.4.15",
            process_name="mimikatz.exe",
            description="Credential extraction tool execution detected in memory",
            severity="HIGH",
            timestamp=now - timedelta(minutes=15)
        ),
        SecurityEvent(
            device_id=device1.id,
            event_type="SYSTEM_HEARTBEAT",
            source_ip="192.168.1.105",
            description="Normal endpoint health telemetry reported",
            severity="LOW",
            timestamp=now - timedelta(minutes=2)
        )
    ]
    session.add_all(events)
    session.flush()

    print("[+] Seeding active security alerts...")
    a1 = Alert(
        alert_type="Brute Force Attack Detected",
        severity="HIGH",
        risk_score=8,
        source_ip="185.220.101.5",
        device_id=device1.id,
        description="Over 6 failed authentication attempts detected within 3 minutes from blacklisted IP.",
        status="NEW",
        created_at=now - timedelta(minutes=39)
    )
    a2 = Alert(
        alert_type="Suspicious Process Execution",
        severity="HIGH",
        risk_score=8,
        source_ip="10.0.4.15",
        device_id=device2.id,
        description="Unauthorized execution of 'mimikatz.exe' detected on security node.",
        status="INVESTIGATING",
        created_at=now - timedelta(minutes=14)
    )
    session.add_all([a1, a2])
    session.flush()

    print("[+] Seeding sample incident response ticket...")
    inc = Incident(
        id="INC-2026-0042",
        title="Host Compromise Investigation on VM-KALI-DEFENSE-02",
        description="Execution of credential dumping binary mimikatz detected. Host isolated for forensic imaging.",
        severity="HIGH",
        source="Alert #2 (Suspicious Process Execution)",
        assigned_analyst="analyst1",
        status="INVESTIGATING",
        resolution_notes="Endpoint network interface quarantined. Memory dump captured for offline volatility analysis.",
        alert_id=a2.id,
        created_at=now - timedelta(minutes=12)
    )
    session.add(inc)

    print("[+] Seeding sample failed login attempts...")
    for i in range(4):
        session.add(LoginAttempt(
            ip_address="185.220.101.5",
            username="admin",
            success=False,
            attempted_at=now - timedelta(minutes=45 - i)
        ))

    session.commit()
    print("[+] SOC Database successfully initialized and seeded with demo telemetry!")
