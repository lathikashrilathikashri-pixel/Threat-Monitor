"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: External Device Security Agent - Configuration
FILE: security-agent/config.py
===================================================================================
WHAT THIS FILE DOES:
    Configures the lightweight Python monitoring agent running on external devices:
    - SERVER_URL: Base URL of the deployed cloud backend (e.g. Render/Railway)
    - DEVICE_ID: Unique identifier for this laptop/workstation
    - DEVICE_TOKEN: Secret API key issued during device registration
    - HEARTBEAT_INTERVAL: Seconds between health telemetry pings
    - TELEMETRY_INTERVAL: Seconds between security event log collections

WHY IT IS REQUIRED:
    Decouples credentials and target server URLs from the monitoring code, allowing
    the agent to be easily moved between physical laptops, VMs, or cloud servers.

HOW IT CONNECTS TO OTHER MODULES:
    - Used by security-agent/api_client.py to dispatch HTTPS requests.
    - Used by security-agent/agent.py to drive the monitoring loop.
===================================================================================
"""

import os
import platform

# Target Server URL:
# Replace with your LIVE cloud URL during external deployment:
# e.g., "https://cyber-threat-soc-backend.onrender.com"
SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:5000").rstrip("/")

# Unique identifier for this monitored external device
# Defaults to the computer's hostname if not explicitly set
DEVICE_ID = os.environ.get("DEVICE_ID", f"LAPTOP-{platform.node().upper()[:12]}")

# Authentication token issued by the backend (matches Device.api_key)
DEVICE_TOKEN = os.environ.get("DEVICE_TOKEN", "sec_dev_token_alpha_9921")

# Telemetry cadence (in seconds)
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", 30))
TELEMETRY_INTERVAL = int(os.environ.get("TELEMETRY_INTERVAL", 45))

# Local log file
LOG_FILE = os.environ.get("LOG_FILE", "agent_telemetry.log")

# Suspicious process signatures to detect locally on the host
SUSPICIOUS_PROCESS_PATTERNS = [
    "mimikatz", "netcat", "nc.exe", "nmap", "wireshark",
    "keylogger", "hydra", "metasploit", "meterpreter"
]
