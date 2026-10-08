"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: External Device Security Agent - Telemetry Collector
FILE: security-agent/collector.py
===================================================================================
WHAT THIS FILE DOES:
    Collects safe, non-invasive system and network telemetry from the host machine:
    - Host Information: OS, architecture, hostname, memory, and CPU utilization
    - Network Connections: Open sockets, local ports, remote peer IPs
    - Process Inventory: Running processes and command line names
    - Failed Login / Security signals where accessible via OS event APIs

WHY IT IS REQUIRED:
    Provides the ground-truth operational data needed by the SOC backend to 
    detect unauthorized network connections, anomalous tools, and resource spikes.

HOW IT CONNECTS TO OTHER MODULES:
    - Uses 'psutil' and 'socket' standard libraries.
    - Feeds collected host metrics into security-agent/detector.py for analysis.
    - Transmitted by security-agent/api_client.py to the cloud backend.
===================================================================================
"""

import os
import platform
import socket
from datetime import datetime, timezone

try:
    import psutil
except ImportError:
    psutil = None

class SystemTelemetryCollector:
    """Collects safe security telemetry from Windows, Linux, and macOS endpoints."""

    def __init__(self, device_id: str):
        self.device_id = device_id

    def collect_system_summary(self) -> dict:
        """Collects basic OS, host, and hardware health metrics."""
        summary = {
            "device_id": self.device_id,
            "hostname": platform.node(),
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": f"{platform.system()} {platform.release()}",
            "architecture": platform.machine(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": self._get_local_ip()
        }

        if psutil:
            try:
                summary["cpu_percent"] = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                summary["ram_percent"] = mem.percent
                summary["ram_available_mb"] = round(mem.available / (1024 * 1024), 2)
            except Exception:
                pass

        return summary

    def collect_network_connections(self) -> list[dict]:
        """Collects active TCP/UDP connections for network anomaly analysis."""
        connections = []
        if not psutil:
            return connections

        try:
            # Safely query active inet connections
            for conn in psutil.net_connections(kind="inet"):
                if conn.status in ["ESTABLISHED", "LISTEN", "SYN_SENT"]:
                    r_ip = conn.raddr.ip if conn.raddr else None
                    r_port = conn.raddr.port if conn.raddr else None
                    l_port = conn.laddr.port if conn.laddr else None
                    
                    connections.append({
                        "fd": conn.fd,
                        "family": str(conn.family),
                        "type": str(conn.type),
                        "local_port": l_port,
                        "remote_ip": r_ip,
                        "remote_port": r_port,
                        "status": conn.status,
                        "pid": conn.pid
                    })
        except (psutil.AccessDenied, Exception):
            # Non-elevated accounts may not see all network sockets; gracefully skip
            pass

        return connections[:50]  # Limit payload size

    def collect_running_processes(self) -> list[dict]:
        """Lists currently executing processes to scan for unauthorized security tools."""
        processes = []
        if not psutil:
            return processes

        try:
            for proc in psutil.process_iter(["pid", "name", "username"]):
                try:
                    p_info = proc.info
                    processes.append({
                        "pid": p_info.get("pid"),
                        "name": p_info.get("name") or "unknown",
                        "username": p_info.get("username")
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        return processes

    def _get_local_ip(self) -> str:
        """Determines the preferred outbound IPv4 address."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Does not actually transmit packets; resolves routing interface
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip
