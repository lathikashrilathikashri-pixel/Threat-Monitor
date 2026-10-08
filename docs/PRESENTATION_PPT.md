# Academic Project Presentation Slides (10-Slide Deck)

**Project Title:** Real-Time Cybersecurity Threat Monitoring and Incident Response System  
**Presenter:** 2nd-Year B.Sc Computer Science with Cyber Security Student  
**Evaluation:** Academic Final Evaluation / Viva Voce  

---

## 📽️ SLIDE 1: Title & Introduction
- **Slide Heading:** Real-Time Cybersecurity Threat Monitoring and Incident Response System
- **Subtitle:** An End-to-End Cloud-Native SOC Architecture with External Endpoint Telemetry & Rule-Based Detection
- **Key Points:**
  - Student Name & Register Number: [Your Name / Reg. No.]
  - Degree: B.Sc Computer Science with Cyber Security
  - Academic Advisor / Guide: [Faculty Guide Name]
- **Speaker Talking Points:**
  > "Respected evaluators, today I present my cybersecurity project: an end-to-end, real-time threat monitoring and incident response platform. Unlike simple localhost applications, this system is architected for live cloud deployment, ingesting live security telemetry from an external laptop over the internet, detecting malicious attacks in real-time, and presenting an actionable command center for security analysts."

---

## 📽️ SLIDE 2: Problem Statement
- **Slide Heading:** Problem Statement & Industry Motivation
- **Key Points:**
  - Modern networks face automated brute-force attacks, horizontal port scans, and credential stuffing every minute.
  - Endpoint devices operate as disconnected silos with zero centralized security visibility.
  - SOC analysts suffer from severe **Alert Fatigue** due to unprioritized, noisy raw logs.
  - Academic projects often rely on localhost mockups that fail to demonstrate true cross-network client-server communication.
- **Speaker Talking Points:**
  > "In enterprise environments, security analysts cannot review thousands of raw syslog entries manually. The core challenge is converting noisy raw telemetry into prioritized, actionable alerts with clear risk scoring, and immediately bridging detection with incident response workflows."

---

## 📽️ SLIDE 3: Project Objectives
- **Slide Heading:** Project Objectives
- **Key Points:**
  - **Autonomous Agent:** Build a lightweight Python agent to gather live host metrics, network sockets, and process signatures from external laptops.
  - **Secure Ingestion API:** Develop a Flask REST API fortified with JWT authentication, device tokens, and CORS governance.
  - **Deterministic Detection Engine:** Implement 6 rule-based threat detection heuristics for brute force, port scans, blacklisted IPs, and offensive tools.
  - **Dynamic Risk Scoring:** Compute multi-factor risk scores from 1 (Low) to 10 (Critical).
  - **SOC Command Center:** Build a responsive dark-mode React operations dashboard with live polling, triage, and incident ticket tracking.
- **Speaker Talking Points:**
  > "Our primary objective was to deliver a complete pipeline: from an external physical device, through the public internet, into a cloud backend with threat correlation, ending in a live dashboard with triage capabilities."

---

## 📽️ SLIDE 4: Existing vs. Proposed System
- **Slide Heading:** Comparative Analysis: Existing vs. Proposed System
| Parameter | Existing / Traditional Approach | Proposed Cloud SOC System |
|:---|:---|:---|
| **Deployment Model** | Localhost only (`127.0.0.1`), mock databases | Live Cloud Deployment (Render + PostgreSQL + Vercel) |
| **Telemetry Source** | Hardcoded static files or manual entry | Autonomous Python Agent on physical external laptop |
| **Detection Logic** | Static thresholds or manual queries | Automated Rule Engine with sliding-window correlation |
| **Risk Scoring** | Static or missing | Dynamic Multi-Factor Risk Score (1 to 10 scale) |
| **Response Integration** | Separate ticketing system or email | Native 1-click Alert-to-Incident conversion |
| **Security Controls** | Plaintext credentials, unauthenticated routes | Salted PBKDF2 hashing, JWT RBAC, Security Headers |

---

## 📽️ SLIDE 5: System Architecture & Data Flow
- **Slide Heading:** End-to-End System Architecture
- **Visual Flow:**
  ```text
  [ External Laptop / VM ]
             ↓ (HTTPS Telemetry / Device Token)
     [ Public Internet ]
             ↓
    [ Cloud Flask API ] ←→ [ PostgreSQL Database ]
             ↓
  [ Threat Detection Engine ]
             ↓
      [ Alert Created ]
             ↓
  [ Live React SOC Dashboard ]
             ↓
    [ Incident Ticket ]
  ```
- **Key Architecture Highlights:**
  - Decoupled micro-agent design.
  - Client-supplied severity is never trusted; recalculated on the server.
  - Full relational audit persistence with foreign keys and indexing.

---

## 📽️ SLIDE 6: Technologies & Security Hardening
- **Slide Heading:** Technology Stack & Security Controls
- **Technologies Employed:**
  - **Frontend:** React.js, Vite, Vanilla CSS SOC Design System, Responsive Glassmorphism.
  - **Backend:** Python 3, Flask, SQLAlchemy ORM, Gunicorn WSGI.
  - **Database:** PostgreSQL (Cloud instance with connection pooling).
  - **Agent:** Python `requests`, `psutil`, `socket`.
  - **API Documentation:** Interactive OpenAPI 3.0 & Swagger UI at `/api/docs`.
- **Defensive Hardening Implemented:**
  - Salted PBKDF2/SHA-256 password hashing (Werkzeug).
  - Cryptographic HMAC-SHA256 JWT tokens with 12-hour expiration.
  - Strict CORS policy and parameterized SQL queries preventing SQLi.
  - Security response headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.

---

## 📽️ SLIDE 7: Threat Detection & Risk Scoring Engine
- **Slide Heading:** Defensive Detection Rules & Scoring Heuristics
- **Key Rules:**
  1. **Brute Force Detection:** Triggers `HIGH` alert (Risk Score: 8) when >5 failed logins occur from the same IP within 5 minutes.
  2. **Perimeter Blacklist Enforcement:** Inbound/outbound traffic from blacklisted IPs triggers an immediate `CRITICAL` alert (Score: 10).
  3. **Port Scan Detection:** Devices probing >5 distinct destination ports within 3 minutes trigger a `HIGH` alert (Score: 8).
  4. **Abnormal Login Sequence:** Repeated failed logins followed immediately by success triggers a credential compromise alert (Score: 7).
  5. **Suspicious Process Execution:** Detects signatures such as `mimikatz.exe`, `netcat`, and `nmap`.
- **Risk Score Spectrum:**
  - 🟢 **1 – 3 (LOW):** Normal operational baseline.
  - 🟡 **4 – 6 (MEDIUM):** Elevated monitoring required.
  - 🟠 **7 – 8 (HIGH):** High probability of active intrusion.
  - 🔴 **9 – 10 (CRITICAL):** Immediate containment priority.

---

## 📽️ SLIDE 8: External Device Integration (Python Agent)
- **Slide Heading:** External Device Telemetry & Agent Lifecycle
- **Key Agent Capabilities:**
  - Continuous background daemon execution on Windows, Linux, or VMs.
  - **Heartbeat Sensor:** Posts health status every 30 seconds to `/api/devices/heartbeat`.
  - **Network & Process Auditing:** Continuously inspects open TCP/UDP sockets and process tree.
  - **Network Resilience:** 3-stage exponential backoff retry on transient network drops.
  - **Safe Simulation Suite:** `simulate_events.py` allows non-destructive attack demonstrations in front of examiners.

---

## 📽️ SLIDE 9: Live Demonstration & Results
- **Slide Heading:** Experimental Results & Live Demonstration
- **Demonstrated Scenarios:**
  - **Scenario A:** Failed authentication sequence triggers live "Brute Force Attack Detected" alert on the dashboard within 1.2 seconds.
  - **Scenario B:** Port scan simulation raises "Potential Port Scan Attack" notification.
  - **Scenario C:** Blacklisted IP communication immediately generates a CRITICAL banner.
  - **Scenario D:** Analyst converts alert to official ticket `INC-2026-0042` with forensic notes.

---

## 📽️ SLIDE 10: Conclusion & Future Scope
- **Slide Heading:** Conclusion & Future Scope
- **Conclusion:**
  - Successfully demonstrated a real-world, cloud-ready Level 5 cybersecurity monitoring platform.
  - Fully fulfills college requirements: cross-device internet communication, multi-factor risk scoring, and integrated incident response.
- **Future Enhancements:**
  - Machine learning anomaly detection (Isolation Forests) for zero-day heuristics.
  - Webhook integration with Slack and PagerDuty for on-call notification.
  - Remote agent containment commands to automatically isolate compromised interfaces.

---

## 🎓 Viva Voce: Expected Questions & Model Answers

### Q1: Why did you not trust the severity sent by the external agent?
> **Answer:** In cybersecurity, the principle of **Zero Trust** mandates that all client input is untrusted. A compromised endpoint or an attacker could send malicious logs claiming they are "LOW" severity to evade analyst detection. The backend threat detection engine must independently inspect the payload, calculate repetition and IP reputation, and assign verified severity.

### Q2: How does the sliding window for brute force detection work?
> **Answer:** The engine queries login attempts where `attempted_at >= current_time - 5 minutes` filtered by the source IP. If the count exceeds the threshold of 5, the alert is triggered. This prevents false alarms from sporadic failed logins while catching rapid automated dictionary attacks.

### Q3: How are passwords stored and authenticated securely?
> **Answer:** Passwords are never stored in plaintext. They are salted and hashed using PBKDF2 with SHA-256 via Werkzeug. During authentication, `check_password_hash` computes the one-way cryptographic hash of the input and compares it in constant time to prevent timing attacks.
