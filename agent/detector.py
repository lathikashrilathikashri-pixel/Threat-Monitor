"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: External Device Security Agent - Local Anomaly Detector
FILE: security-agent/detector.py
===================================================================================
WHAT THIS FILE DOES:
    Applies local host-level security heuristics to telemetry collected on the endpoint:
    - Scans running processes for unauthorized hacking tools or offensive binaries
    - Detects anomalous network connections (unusual outbound ports)
    - Formats suspicious findings into standardized security event payloads

WHY IT IS REQUIRED:
    Provides edge detection capability. Instead of flooding the cloud backend with 
    hundreds of normal system calls, the agent filters and flags noteworthy security
    events directly on the host machine.

HOW IT CONNECTS TO OTHER MODULES:
    - Analyzes telemetry from security-agent/collector.py.
    - Produces event dictionaries transmitted by security-agent/api_client.py.
    - Read patterns from security-agent/config.py.
===================================================================================
"""

from datetime import datetime, timezone
from config import SUSPICIOUS_PROCESS_PATTERNS

class LocalSecurityDetector:
    """Evaluates host state and generates security event notifications."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self._reported_processes = set()

    def evaluate_processes(self, processes: list[dict], host_ip: str) -> list[dict]:
        """
        Inspects running processes against blacklisted offensive tool names.
        Generates SUSPICIOUS_PROCESS events if matches are found.
        """
        events = []
        for proc in processes:
            proc_name = (proc.get("name") or "").lower()
            pid = proc.get("pid")

            for pattern in SUSPICIOUS_PROCESS_PATTERNS:
                if pattern in proc_name:
                    dedup_key = f"{pattern}-{pid}"
                    if dedup_key in self._reported_processes:
                        continue  # Avoid repeated alerts for the same PID instance

                    self._reported_processes.add(dedup_key)
                    events.append({
                        "device_id": self.device_id,
                        "event_type": "SUSPICIOUS_PROCESS",
                        "source_ip": host_ip,
                        "process_name": proc.get("name"),
                        "username": proc.get("username"),
                        "description": f"Potential security tool or suspicious binary '{proc.get('name')}' (PID: {pid}) detected on host.",
                        "severity": "HIGH",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "raw_data": proc
                    })
        return events

    def evaluate_connections(self, connections: list[dict], host_ip: str) -> list[dict]:
        """
        Inspects outbound connections for unusual target ports (e.g. 4444, 1337, 6667).
        """
        events = []
        suspicious_ports = [4444, 5555, 6667, 1337, 31337]

        for conn in connections:
            r_port = conn.get("remote_port")
            r_ip = conn.get("remote_ip")
            if r_port in suspicious_ports and r_ip:
                events.append({
                    "device_id": self.device_id,
                    "event_type": "SUSPICIOUS_CONNECTION",
                    "source_ip": host_ip,
                    "destination_port": r_port,
                    "description": f"Outbound connection detected to high-risk destination port {r_port} at remote IP {r_ip}.",
                    "severity": "MEDIUM",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "raw_data": conn
                })
        return events
