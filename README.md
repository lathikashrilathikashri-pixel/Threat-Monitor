# Lightweight Python Security Monitoring Agent

An autonomous endpoint security monitoring agent designed to run on an external laptop, workstation, or virtual machine and transmit security telemetry securely to the cloud backend.

---

## 🌟 Key Features

1. **Host Telemetry Collection**: Monitors system memory, CPU utilization, local IP, and hostname.
2. **Network Socket Inspection**: Continuously monitors open ports and active connections.
3. **Process Anomaly Detection**: Scans running processes for unauthorized offensive tools (e.g., `mimikatz`, `netcat`, `nmap`).
4. **Heartbeat Liveness Reporting**: Sends periodic health checks every 30 seconds to maintain `ONLINE` status in the SOC Dashboard.
5. **Safe Event Simulator**: Built-in `simulate_events.py` for live college viva demonstrations without malicious exploits.
6. **Robust Network Resilience**: Automatic 3-stage exponential backoff retry on transient internet disconnects.

---

## 🚀 Setup Instructions

### 1. Requirements
- Python 3.9+
- Network connectivity to the deployed SOC backend (either local LAN or cloud URL)

### 2. Installation

```bash
# Navigate to the agent directory
cd security-agent

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

The agent reads configuration from environment variables or `config.py`.

Set your target server URL and device token before running:

### On Windows (PowerShell):
```powershell
$env:SERVER_URL = "https://your-soc-backend.onrender.com"
$env:DEVICE_ID = "STUDENT-LAPTOP-01"
$env:DEVICE_TOKEN = "sec_dev_token_alpha_9921"
```

### On Linux / macOS / Virtual Machine (Bash):
```bash
export SERVER_URL="https://your-soc-backend.onrender.com"
export DEVICE_ID="VM-UBUNTU-TEST"
export DEVICE_TOKEN="sec_dev_token_alpha_9921"
```

---

## 🏃 Running the Continuous Agent Daemon

To start continuous telemetry collection and heartbeat reporting:

```bash
python agent.py
```

Sample output:
```text
=================================================================
CYBERSECURITY ENDPOINT MONITORING AGENT INITIALIZING
Target Server URL: https://your-soc-backend.onrender.com
Device ID:         STUDENT-LAPTOP-01
OS Architecture:   Windows 10.0.26100 (AMD64)
=================================================================
[*] Performing initial endpoint handshake with cloud backend...
[✓] Handshake verified. Device registered in SOC asset database.
[*] Security monitoring loop active. Press Ctrl+C to terminate.
[+] Heartbeat sent successfully (CPU: 12.4%, RAM: 58.2%)
```

---

## 🎯 Running the Safe Viva Demonstration (`simulate_events.py`)

For your college final practical evaluation, run the event simulator from your second laptop or VM to trigger live alerts on the dashboard:

```bash
python simulate_events.py
```

### Demonstration Scenarios Available:
1. **Brute Force Attack**: Dispatches 6 failed logins from an attacker IP -> Backend calculates **Risk Score 8** -> triggers **HIGH** severity alert on dashboard.
2. **Port Scan Reconnaissance**: Probes 6 distinct ports -> Backend correlates scan -> triggers **HIGH** alert.
3. **Blacklisted IP Communication**: Sends traffic from a known botnet IP -> triggers immediate **CRITICAL** alert.
4. **Suspicious Process Execution**: Simulates detection of `mimikatz.exe` -> triggers **HIGH** alert.
5. **Full Suite**: Automatically executes all 4 scenarios with visual explanations.
