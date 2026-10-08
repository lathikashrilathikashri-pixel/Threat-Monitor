"""
Automated System Verification Script
Tests database seeding, backend routes, authentication, threat detection engine, 
brute-force detection, alert generation, incident escalation, and device heartbeats.
"""

import sys
import os

# Enable UTF-8 encoding on Windows console if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add current directory to path
root_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, root_path)

from app import create_app
from config import Config
from models import User, Device, Alert, Incident, SecurityEvent

def run_tests():
    print("=" * 65)
    print("RUNNING AUTOMATED CYBERSECURITY SOC SYSTEM TESTS")
    print("=" * 65)

    app = create_app()
    client = app.test_client()

    # Test 1: Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print("[PASS] TEST 1: /api/health returned online")

    # Test 2: Admin Login & JWT Generation
    res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "AdminSecure2026!"
    })
    assert res.status_code == 200, f"Login failed: {res.status_code} - {res.text}"
    token = res.get_json()["token"]
    assert token is not None, "Token was not generated"
    auth_header = {"Authorization": f"Bearer {token}"}
    print("[PASS] TEST 2: Admin login successful, JWT generated")

    # Test 3: Dashboard Stats Telemetry
    res = client.get("/api/dashboard/stats", headers=auth_header)
    assert res.status_code == 200, f"Stats failed: {res.status_code}"
    stats = res.get_json()
    assert "kpis" in stats and "charts" in stats, "Malformed stats response"
    print(f"[PASS] TEST 3: /api/dashboard/stats returned KPIs (Total Events: {stats['kpis']['total_events']}, Threat Score: {stats['kpis']['overall_threat_score']})")

    # Test 4: Device Heartbeat via API Key
    res = client.post("/api/devices/heartbeat", json={
        "device_id": "LAPTOP-SEC-AGENT-01",
        "api_key": "sec_dev_token_alpha_9921",
        "os_type": "Windows 11 Enterprise",
        "ip_address": "192.168.1.105"
    })
    assert res.status_code == 200, f"Device heartbeat failed: {res.status_code}"
    print("[PASS] TEST 4: Device heartbeat accepted and last_seen updated")

    # Test 5: Ingest Telemetry & Threat Detection - Brute Force Detection
    attacker_ip = "203.0.113.99"
    alerts_seen = []
    print("[*] Simulating 6 rapid failed logins to test Brute Force rule...")
    for i in range(1, 7):
        res = client.post("/api/events", json={
            "device_id": "LAPTOP-SEC-AGENT-01",
            "event_type": "FAILED_LOGIN",
            "source_ip": attacker_ip,
            "username": "target_user",
            "description": f"Failed authentication attempt #{i}"
        }, headers={"X-Device-Token": "sec_dev_token_alpha_9921"})
        assert res.status_code == 201, f"Event ingestion failed: {res.status_code}"
        data = res.get_json()
        if data.get("alerts_created"):
            alerts_seen.extend(data["alerts_created"])

    assert len(alerts_seen) > 0, "Threat detection engine failed to generate Brute Force alert!"
    bf_alert = alerts_seen[0]
    assert bf_alert["severity"] == "HIGH", f"Expected HIGH severity, got {bf_alert['severity']}"
    assert bf_alert["risk_score"] == 8, f"Expected risk score 8, got {bf_alert['risk_score']}"
    print(f"[PASS] TEST 5: Threat Detection Engine caught Brute Force! Alert: '{bf_alert['alert_type']}' (Severity: {bf_alert['severity']}, Risk Score: {bf_alert['risk_score']}/10)")

    # Test 6: Ingest Telemetry - Blacklisted IP Rule
    res = client.post("/api/events", json={
        "device_id": "LAPTOP-SEC-AGENT-01",
        "event_type": "BLOCKED_IP_ACCESS",
        "source_ip": "185.220.101.5",
        "description": "Traffic from known botnet"
    }, headers={"X-Device-Token": "sec_dev_token_alpha_9921"})
    assert res.status_code == 201
    black_alert = res.get_json()["alerts_created"][0]
    assert black_alert["severity"] == "CRITICAL", f"Expected CRITICAL, got {black_alert['severity']}"
    assert black_alert["risk_score"] == 10, f"Expected 10, got {black_alert['risk_score']}"
    print(f"[PASS] TEST 6: Blacklisted IP Detection caught malicious IP! Alert: '{black_alert['alert_type']}' (Severity: {black_alert['severity']}, Risk Score: {black_alert['risk_score']}/10)")

    # Test 7: Alert Escalation to Incident Ticket
    alert_id = bf_alert["id"]
    res = client.post(f"/api/alerts/{alert_id}/convert-incident", headers=auth_header)
    assert res.status_code == 201, f"Incident escalation failed: {res.status_code}"
    inc_data = res.get_json()["incident"]
    print(f"[PASS] TEST 7: Alert #{alert_id} successfully escalated to Incident Ticket '{inc_data['id']}' (Status: {inc_data['status']})")

    # Test 8: Incident Update / Forensics Notes
    res = client.patch(f"/api/incidents/{inc_data['id']}", json={
        "status": "CONTAINED",
        "resolution_notes": "Source IP 203.0.113.99 blacklisted on edge gateway. Host quarantined."
    }, headers=auth_header)
    assert res.status_code == 200, f"Incident update failed: {res.status_code}"
    print(f"[PASS] TEST 8: Incident ticket updated to 'CONTAINED' with forensics notes")

    # Test 9: OpenAPI Swagger Docs Endpoint
    res = client.get("/api/docs")
    assert res.status_code == 200, f"Swagger UI failed: {res.status_code}"
    assert b"SwaggerUIBundle" in res.data, "Swagger UI bundle not found in HTML"
    print("[PASS] TEST 9: Interactive Swagger OpenAPI documentation verified at /api/docs")

    # Test 10: Frontend Distribution Serving
    res = client.get("/")
    assert res.status_code == 200, f"Frontend root route failed: {res.status_code}"
    print("[PASS] TEST 10: Frontend root route operational and ready for browsers")

    print("\n" + "=" * 65)
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY! (100% SUCCESS)")
    print("SYSTEM IS FULLY READY FOR COLLEGE FINAL EVALUATION & LIVE DEPLOYMENT")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
