"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Safe Academic Demonstration & Threat Event Simulator
FILE: security-agent/simulate_events.py
===================================================================================
WHAT THIS FILE DOES:
    Provides a safe, non-malicious event simulator designed specifically for 
    academic demonstrations and college viva evaluations:
    - Simulates Brute Force authentication attacks (triggers HIGH alert, Risk Score: 8)
    - Simulates Network Port Scan reconnaissance (triggers HIGH alert, Risk Score: 8)
    - Simulates Communication from Blacklisted Threat Actors (triggers CRITICAL alert, Score: 10)
    - Simulates Endpoint Tool Execution anomalies (triggers HIGH alert, Risk Score: 8)
    - Transmits safe JSON payloads over HTTPS to the deployed cloud backend.

WHY IT IS REQUIRED:
    Allows the student to demonstrate the full end-to-end detection pipeline live in front 
    of professors/examiners from an external laptop or mobile hotspot WITHOUT needing
    actual exploit payloads or dangerous attack tools.

HOW IT CONNECTS TO OTHER MODULES:
    - Targets the cloud backend URL set in security-agent/config.py (or via prompt/cli).
    - Verified by backend/detection_engine.py.
    - Instantly reflected on the React SOC Dashboard in real-time.
===================================================================================
"""

import os
import sys
import time
import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import SERVER_URL, DEVICE_ID, DEVICE_TOKEN

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def send_simulated_event(url, token, event_data):
    """Dispatches event to backend /api/events and formats response for the audience."""
    headers = {
        "Content-Type": "application/json",
        "X-Device-Token": token
    }
    try:
        response = requests.post(f"{url}/api/events", json=event_data, headers=headers, timeout=8)
        if response.status_code in [200, 201]:
            res_json = response.json()
            risk = res_json.get("calculated_risk_score", "N/A")
            alerts = res_json.get("alerts_created", [])
            print(f"  [OK] Event Accepted! Backend Calculated Risk Score: [{risk}/10]")
            if alerts:
                for a in alerts:
                    print(f"  [ALERT TRIGGERED] '{a.get('alert_type')}' | Severity: {a.get('severity')} | Risk Score: {a.get('risk_score')}")
            else:
                print("  [i] Event recorded as baseline security telemetry.")
            return res_json
        else:
            print(f"  [x] Backend returned HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"  [x] Connection failed to {url}: {e}")
    return None

def scenario_brute_force(server_url, token):
    """
    Simulates 6 rapid failed SSH/RDP login attempts from an external IP.
    The Threat Detection Engine should catch this at attempt #5 and fire a Brute Force Alert.
    """
    print_header("SCENARIO 1: BRUTE FORCE ATTACK SIMULATION (Rule 1)")
    attacker_ip = "203.0.113.88"
    target_user = "admin"
    print(f"[*] Attacker IP:       {attacker_ip}")
    print(f"[*] Target User:       {target_user}")
    print("[*] Threshold:         >5 failed attempts within 5 minutes triggers HIGH Alert")
    print("-" * 70)

    for i in range(1, 7):
        print(f"\n[Attempt {i}/6] Simulating failed login credential attempt...")
        payload = {
            "device_id": DEVICE_ID,
            "event_type": "FAILED_LOGIN",
            "source_ip": attacker_ip,
            "username": target_user,
            "description": f"Simulated invalid password attempt #{i} for user '{target_user}'"
        }
        send_simulated_event(server_url, token, payload)
        time.sleep(1)

    print("\n[OK] Brute Force scenario complete! Check SOC Dashboard for 'Brute Force Attack Detected'.")

def scenario_port_scan(server_url, token):
    """
    Simulates rapid SYN scans across multiple destination ports.
    The Threat Detection Engine should detect probe across >5 distinct ports.
    """
    print_header("SCENARIO 2: NETWORK PORT SCAN RECONNAISSANCE (Rule 3)")
    scanner_ip = "198.51.100.42"
    target_ports = [21, 22, 80, 443, 3389, 8080]
    print(f"[*] Scanner IP:       {scanner_ip}")
    print(f"[*] Target Ports:     {target_ports}")
    print("-" * 70)

    for port in target_ports:
        print(f"\n[*] Probing port {port}...")
        payload = {
            "device_id": DEVICE_ID,
            "event_type": "PORT_SCAN_ATTEMPT",
            "source_ip": scanner_ip,
            "destination_port": port,
            "description": f"Simulated TCP SYN probe targeting port {port}"
        }
        send_simulated_event(server_url, token, payload)
        time.sleep(1)

    print("\n[OK] Port scan scenario complete! Check SOC Dashboard for 'Potential Port Scan Attack'.")

def scenario_blacklisted_ip(server_url, token):
    """
    Simulates inbound traffic originating from a blacklisted Tor exit node / botnet IP.
    The Threat Detection Engine should immediately trigger a CRITICAL alert.
    """
    print_header("SCENARIO 3: BLACKLISTED / BLOCKED IP ACTIVITY (Rule 2)")
    blacklisted_ip = "185.220.101.5"  # Pre-seeded in blocked_ips table
    print(f"[*] Malicious IP:      {blacklisted_ip} (Listed in SOC Blacklist)")
    print("-" * 70)

    payload = {
        "device_id": DEVICE_ID,
        "event_type": "BLOCKED_IP_ACCESS",
        "source_ip": blacklisted_ip,
        "description": "Unauthorized inbound traffic attempt from blacklisted botnet IP"
    }
    send_simulated_event(server_url, token, payload)
    print("\n[OK] Blacklist scenario complete! Check SOC Dashboard for 'Blacklisted IP Communication Detected'.")

def scenario_suspicious_process(server_url, token):
    """
    Simulates detection of unauthorized offensive tool execution (e.g. mimikatz).
    """
    print_header("SCENARIO 4: SUSPICIOUS PROCESS / OFFENSIVE TOOL EXECUTION (Rule 6)")
    print("[*] Tool Name:         mimikatz.exe (Known credential extractor)")
    print("-" * 70)

    payload = {
        "device_id": DEVICE_ID,
        "event_type": "SUSPICIOUS_PROCESS",
        "source_ip": "192.168.1.105",
        "process_name": "mimikatz.exe",
        "description": "Unauthorized credential extraction binary detected running in user space."
    }
    send_simulated_event(server_url, token, payload)
    print("\n[OK] Process anomaly scenario complete! Check SOC Dashboard for 'Suspicious Process Execution'.")

def main():
    target_url = os.environ.get("SERVER_URL") or SERVER_URL
    token = os.environ.get("DEVICE_TOKEN") or DEVICE_TOKEN

    print("=" * 70)
    print("  SOC LIVE THREAT DETECTION & ACADEMIC DEMONSTRATION SIMULATOR")
    print(f"  Target Server: {target_url}")
    print(f"  Device Token:  {token}")
    print("=" * 70)

    # Check backend liveness
    try:
        health_resp = requests.get(f"{target_url}/api/health", timeout=5)
        if health_resp.status_code == 200:
            print("[OK] Connected successfully to SOC Backend API!\n")
        else:
            print(f"[!] Warning: Backend returned HTTP {health_resp.status_code}\n")
    except Exception as e:
        print(f"[!] Warning: Could not reach {target_url}/api/health: {e}\n")

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if "brute" in arg:
            scenario_brute_force(target_url, token)
            return
        elif "port" in arg:
            scenario_port_scan(target_url, token)
            return
        elif "black" in arg or "block" in arg:
            scenario_blacklisted_ip(target_url, token)
            return
        elif "process" in arg:
            scenario_suspicious_process(target_url, token)
            return
        elif "all" in arg:
            scenario_brute_force(target_url, token)
            time.sleep(2)
            scenario_port_scan(target_url, token)
            time.sleep(2)
            scenario_blacklisted_ip(target_url, token)
            time.sleep(2)
            scenario_suspicious_process(target_url, token)
            return

    # Interactive Menu
    print("Select a Safe Threat Simulation Scenario:")
    print("  1. Run Brute Force Attack Simulation (6 failed logins -> HIGH Alert)")
    print("  2. Run Port Scan Reconnaissance Simulation (6 ports probed -> HIGH Alert)")
    print("  3. Run Blacklisted IP Detection Simulation (Tor node traffic -> CRITICAL Alert)")
    print("  4. Run Suspicious Process Execution Simulation (mimikatz signature -> HIGH Alert)")
    print("  5. Run COMPLETE FULL SUITE (All 4 scenarios sequentially)")
    print("  0. Exit")

    choice = input("\nEnter choice [1-5]: ").strip()
    if choice == "1":
        scenario_brute_force(target_url, token)
    elif choice == "2":
        scenario_port_scan(target_url, token)
    elif choice == "3":
        scenario_blacklisted_ip(target_url, token)
    elif choice == "4":
        scenario_suspicious_process(target_url, token)
    elif choice == "5":
        scenario_brute_force(target_url, token)
        time.sleep(2)
        scenario_port_scan(target_url, token)
        time.sleep(2)
        scenario_blacklisted_ip(target_url, token)
        time.sleep(2)
        scenario_suspicious_process(target_url, token)
    else:
        print("[*] Exiting simulation.")

if __name__ == "__main__":
    main()
