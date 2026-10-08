# ACADEMIC PROJECT REPORT

## PROJECT TITLE:
**Real-Time Cybersecurity Threat Monitoring and Incident Response System**

**Academic Level:** Level 5 / B.Sc Computer Science with Cyber Security (Year 2 Final Evaluation)  
**Academic Year:** 2025–2026  

---

## 1. ABSTRACT
Modern enterprise digital infrastructure faces an escalating volume of automated intrusion techniques, ranging from distributed brute force attacks against authentication gateways to stealth port scanning and unauthorized tooling execution on remote workstations. Traditional centralized intrusion detection systems (IDS) often operate retrospectively, suffering from log aggregation latency and high false-positive rates. 

This project designs and implements an end-to-end, multi-tier **Real-Time Cybersecurity Threat Monitoring and Incident Response System**. The platform is engineered for live cloud deployment and facilitates bidirectional security telemetry flow: a lightweight autonomous Python agent residing on an external host collects local socket, process, and authentication signals; securely transmits encrypted JSON payloads over HTTPS to a cloud-hosted Flask REST API; correlates events through a deterministic, rule-based **Threat Detection & Risk Scoring Engine**; persists audit records in a relational PostgreSQL database; and immediately visualizes prioritized threats on a reactive, SOC-grade web operations dashboard built with React.js. The architecture encompasses automated brute force mitigation, port scan reconnaissance detection, IP perimeter blacklisting, and an incident response ticketing lifecycle with Role-Based Access Control (RBAC).

---

## 2. PROBLEM STATEMENT
Educational institutions, small-to-medium enterprises (SMEs), and remote organizations face several operational cybersecurity challenges:
1. **Lack of Unified Telemetry:** Endpoint devices operate in silos without coordinated visibility into anomalous processes or repeated authentication failures.
2. **Alert Fatigue:** Raw security event streams produce overwhelming noise. Without multi-factor risk scoring, critical threats are lost within voluminous log dumps.
3. **Decoupled Incident Response:** Detection systems often lack native integration with remediation workflows, delaying analyst containment actions (quarantining hosts, updating perimeter blacklists).
4. **Localhost Limitations:** Academic projects are frequently confined to localhost loopback interfaces (`127.0.0.1`), failing to simulate genuine cross-network internet communication between external hosts and cloud endpoints.

---

## 3. PROJECT OBJECTIVES
1. **Develop an Autonomous Endpoint Security Agent:** Build a non-invasive Python monitoring agent capable of gathering process signatures, open network sockets, and health heartbeats from external laptops/virtual machines.
2. **Implement an Ingestion REST API:** Expose robust endpoints featuring JWT and Device API Token authentication, CORS governance, and security hardening headers.
3. **Construct a Rule-Based Threat Detection Engine:** Formulate mathematical correlation heuristics for:
   - High-frequency brute force detection (>5 failed authentications within 5 minutes).
   - Horizontal and vertical TCP port scan reconnaissance.
   - Perimeter blacklist matching (CRITICAL severity alert generation).
   - Abnormal authentication sequences (repeated failures followed by breakthrough).
   - Unauthorized offensive tool/process execution (e.g., Mimikatz, Netcat).
4. **Dynamic Risk Scoring:** Compute normalized severity scores (1–10 scale: Low, Medium, High, Critical) based on asset value, event repetition, and historical alerts.
5. **SOC-Grade Command Center:** Deliver an ergonomic dark-mode SOC dashboard providing real-time telemetry polling, time-series charts, alert triage, and incident response ticket management.
6. **Live Cloud Architecture:** Ensure 100% cloud portability across Render/Railway (Backend & PostgreSQL) and Vercel (Frontend) accessible from external networks.

---

## 4. SYSTEM ARCHITECTURE & DATA FLOW

### High-Level Architecture Diagram
```
+-------------------------------------------------------------+
|                 EXTERNAL MONITORED HOST                     |
|           (Physical Laptop / Virtual Machine)               |
|                                                             |
|   +-----------------------+     +-----------------------+   |
|   |  System Collector     |     |   Local Detector      |   |
|   |  (psutil / sockets)   | --> | (Signature Matching)  |   |
|   +-----------------------+     +-----------------------+   |
|                                             |               |
|                                 +-----------------------+   |
|                                 |   HTTPS API Client    |   |
|                                 | (Token Auth + Retry)  |   |
|                                 +-----------------------+   |
+---------------------------------------------|---------------+
                                              | HTTPS / JSON
                                              v [Internet / WAN]
+-------------------------------------------------------------+
|                   CLOUD BACKEND LAYER                       |
|           (Flask REST API / Gunicorn / Render)              |
|                                                             |
|   +-----------------------------------------------------+   |
|   | Security Gateway: JWT Auth, Rate Limiter, CORS      |   |
|   +-----------------------------------------------------+   |
|                             |                               |
|   +-----------------------------------------------------+   |
|   | Threat Detection Engine: 6 Defensive SOC Rules      |   |
|   | - Brute Force Correlator (Sliding Window)           |   |
|   | - Port Scan Analyzer (Distinct Port Counter)        |   |
|   | - Perimeter Blacklist Matcher                       |   |
|   | - Multi-Factor Risk Score Calculator (1-10)         |   |
|   +-----------------------------------------------------+   |
|              |                                |             |
+--------------|--------------------------------|-------------+
               |                                |
               v                                v
+-----------------------------+   +---------------------------+
|      DATABASE LAYER         |   |     FRONTEND SOC DASHBOARD|
|  (PostgreSQL Database)      |   |     (React.js / Vite)     |
|                             |   |                           |
| - users (RBAC, Salted Hash) |   | - Threat Exposure Gauge   |
| - devices (Heartbeats)      |   | - Live KPI Metric Cards   |
| - security_events (Logs)    |   | - Telemetry Event Stream  |
| - alerts (Triage Status)    |   | - Alert Triage Controls   |
| - incidents (Forensics)     |   | - Incident Response Board |
| - blocked_ips (Blacklist)   |   | - Device Fleet Status     |
+-----------------------------+   +---------------------------+
```

---

## 5. THREAT DETECTION & RISK SCORING ALGORITHMS

### 5.1 Rule 1: Sliding-Window Brute Force Detection
```python
def check_brute_force(source_ip, window_minutes=5, threshold=5):
    cutoff = current_timestamp - window_minutes
    failures = count(login_attempts WHERE ip == source_ip AND success == False AND time >= cutoff)
    if failures >= threshold:
        generate_alert(
            alert_type="Brute Force Attack Detected",
            severity="HIGH",
            risk_score=8
        )
```

### 5.2 Rule 2: Perimeter Blacklist Enforcement
```python
def check_blocked_ip(source_ip):
    if exists(blocked_ips WHERE ip == source_ip AND is_active == True):
        generate_alert(
            alert_type="Blacklisted IP Communication Detected",
            severity="CRITICAL",
            risk_score=10
        )
```

### 5.3 Rule 3: Network Port Scan Reconnaissance
```python
def check_port_scan(source_ip, window_minutes=3, port_threshold=5):
    cutoff = current_timestamp - window_minutes
    distinct_ports = count(distinct(destination_port) WHERE source_ip == source_ip AND time >= cutoff)
    if distinct_ports >= port_threshold:
        generate_alert(
            alert_type="Potential Port Scan Attack",
            severity="HIGH",
            risk_score=8
        )
```

### 5.4 Risk Score Translation Matrix
| Numerical Score | SOC Severity Classification | Operational SLA / Action Required |
|:---:|:---:|:---|
| **9 – 10** | **CRITICAL** | Automated perimeter isolation; immediate incident escalation. |
| **7 – 8** | **HIGH** | Priority analyst triage within 15 minutes; quarantine review. |
| **4 – 6** | **MEDIUM** | Standard ticket assignment; log correlation within 2 hours. |
| **1 – 3** | **LOW** | Baseline operational telemetry logged for audit compliance. |

---

## 6. RELATIONAL DATABASE ER SPECIFICATION

1. **`users`**:
   - `id` (PK, Serial)
   - `username` (VARCHAR 80, Unique, Indexed)
   - `email` (VARCHAR 120, Unique, Indexed)
   - `password_hash` (VARCHAR 255, PBKDF2/SHA-256)
   - `role` (VARCHAR 30: 'Admin', 'Security Analyst', 'User')
   - `created_at` (TIMESTAMP)

2. **`devices`**:
   - `id` (PK, VARCHAR 64, e.g., 'LAPTOP-ALPHA-01')
   - `device_name` (VARCHAR 120)
   - `os_type` (VARCHAR 80)
   - `ip_address` (VARCHAR 64)
   - `api_key` (VARCHAR 128, Unique, Indexed)
   - `status` (VARCHAR 20: 'ONLINE', 'OFFLINE')
   - `last_seen` (TIMESTAMP)

3. **`security_events`**:
   - `id` (PK, Serial)
   - `device_id` (FK -> devices.id)
   - `event_type` (VARCHAR 64: 'FAILED_LOGIN', 'PORT_SCAN_ATTEMPT', 'SUSPICIOUS_PROCESS')
   - `source_ip` (VARCHAR 64, Indexed)
   - `destination_port` (Integer, Nullable)
   - `username` (VARCHAR 80, Nullable)
   - `process_name` (VARCHAR 120, Nullable)
   - `description` (TEXT)
   - `severity` (VARCHAR 20)
   - `raw_data` (TEXT JSON)
   - `timestamp` (TIMESTAMP, Indexed)

4. **`alerts`**:
   - `id` (PK, Serial)
   - `alert_type` (VARCHAR 80)
   - `severity` (VARCHAR 20)
   - `risk_score` (Integer: 1–10)
   - `source_ip` (VARCHAR 64)
   - `device_id` (VARCHAR 64)
   - `description` (TEXT)
   - `status` (VARCHAR 30: 'NEW', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE')
   - `created_at` (TIMESTAMP)

5. **`incidents`**:
   - `id` (PK, VARCHAR 64, e.g., 'INC-2026-0042')
   - `title` (VARCHAR 200)
   - `description` (TEXT)
   - `severity` (VARCHAR 20)
   - `assigned_analyst` (VARCHAR 80)
   - `status` (VARCHAR 30: 'OPEN', 'INVESTIGATING', 'CONTAINED', 'RESOLVED')
   - `resolution_notes` (TEXT)
   - `alert_id` (FK -> alerts.id)

6. **`blocked_ips`**:
   - `id` (PK, Serial)
   - `ip_address` (VARCHAR 64, Unique)
   - `reason` (VARCHAR 255)
   - `blocked_by` (VARCHAR 80)
   - `is_active` (Boolean)

---

## 7. EXPERIMENTAL RESULTS & EVALUATION

### Test Case Execution Summary:
- **Test Case 1 (Brute Force):** Simulated 6 consecutive failed authentications from IP `203.0.113.88`. At attempt #5, backend raised `Brute Force Attack Detected` alert with Severity `HIGH` and Risk Score `8`. Latency to dashboard visualization: < 1.2 seconds.
- **Test Case 2 (Port Scanning):** Dispatched 6 connection probes across distinct destination ports (21, 22, 80, 443, 3389, 8080). Engine aggregated events within the 3-minute sliding window and fired a `Potential Port Scan Attack` alert with Risk Score `8`.
- **Test Case 3 (Perimeter Blacklist):** Simulated ingress packet from pre-seeded IP `185.220.101.5`. Engine instantly triggered `Blacklisted IP Communication Detected` alert with Severity `CRITICAL` and Risk Score `10`.
- **Test Case 4 (Incident Escalation):** Verified 1-click transformation of Alert #1 into Incident Ticket `INC-2026-XXXX`, binding the current analyst and updating triage status to `INVESTIGATING`.

---

## 8. CONCLUSION & FUTURE SCOPE
The completed system demonstrates a robust, enterprise-grade architecture that bridges physical/virtual endpoint telemetry with cloud defense automation. It delivers immediate situational awareness to SOC operators through intuitive visualization while enforcing defensive security hygiene across all REST endpoints.

**Future Enhancements:**
1. Machine learning anomaly detection (isolation forests or autoencoders) for zero-day behavioral deviations.
2. Webhook notifications to Slack, Microsoft Teams, and PagerDuty for on-call analyst escalation.
3. Automated host containment (remotely instructing the agent daemon to block network adapters upon critical alert generation).
