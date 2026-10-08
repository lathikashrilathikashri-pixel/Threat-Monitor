# Live Viva Demonstration Guide (College Evaluation Script)

Follow this step-by-step walkthrough during your college viva / practical evaluation to clearly demonstrate the required pipeline:

```text
External Device → Internet → Live Frontend → Backend API → Database → Detection Engine → Alert → Dashboard → Incident
```

---

## 🛠️ Step 0: Pre-Demo Setup (Before the Evaluators Sit Down)

1. **Laptop 1 (Presentation Screen / Projector):**
   - Open your live frontend URL (or local dashboard at `http://localhost:5000`).
   - Log in as **Admin** (`admin` / `AdminSecure2026!`).
   - Leave the **SOC Dashboard** open with auto-refresh turned **ON**.
2. **Laptop 2 or Mobile Phone (External Sensor Device):**
   - Have the `security-agent` folder open in terminal.
   - Set `$env:SERVER_URL = "https://your-backend.onrender.com"` (or local IP if on same WiFi).

---

## 🎬 STEP 1: Introduce the System Architecture (1 Minute)
**What to say to the professors:**
> "Respected examiners, our project is a **Real-Time Cybersecurity Threat Monitoring and Incident Response System**. Rather than running isolated code on localhost, our system consists of two separate machines:
> 1. This presentation laptop is viewing our live cloud SOC dashboard.
> 2. This second external laptop is acting as a monitored workstation running our autonomous Python security agent.
> I will now demonstrate real-time telemetry ingestion, threat detection, risk score calculation, and incident escalation."

---

## 🎬 STEP 2: Demonstrate Endpoint Heartbeat & Asset Fleet (1 Minute)
**What to do:**
1. On the Dashboard, navigate to the **Monitored Devices** tab.
2. Show that `LAPTOP-SEC-AGENT-01` is listed.
3. On Laptop 2, start the continuous agent daemon:
   ```bash
   python agent.py
   ```
4. Show the professors that the device status indicator shows a **glowing green pulse (ONLINE)** and the "Last Heartbeat" timestamp updates every 30 seconds.

**What to explain:**
> "The external agent uses an encrypted device token header (`X-Device-Token`) to authenticate with the cloud REST API and transmit heartbeats and socket information without human intervention."

---

## 🎬 STEP 3: Trigger the Live Brute Force Attack Scenario (2 Minutes)
**What to do:**
1. Switch your projector screen back to the **SOC Dashboard**.
2. Point out the current **Calculated Risk Score** (currently normal/low).
3. On Laptop 2 (the external device), run the safe simulation tool:
   ```bash
   python simulate_events.py
   ```
4. Choose **Option 1: Run Brute Force Attack Simulation**.
5. The terminal will output 6 failed authentication events from attacker IP `203.0.113.88`.

**What happens on the Dashboard (Projector):**
- Within 2 seconds, the Risk Score meter turns **Orange/Red** and jumps to **8/10 (HIGH RISK LEVEL)**.
- Under **Live Threat Alert Stream**, a new alert flashes:
  - **Alert Type:** `Brute Force Attack Detected`
  - **Severity:** `HIGH`
  - **Risk Score:** `8/10`
  - **Description:** `Detected 6 repeated failed authentication attempts from IP 203.0.113.88 within 5 minutes.`

**What to explain to the professors:**
> "Notice that the external device merely sent raw authentication logs. The backend Threat Detection Engine analyzed the sliding time window, detected that failed logins exceeded our threshold of 5 within 5 minutes, calculated the risk score of 8, and published an actionable alert to the SOC dashboard."

---

## 🎬 STEP 4: Demonstrate Port Scan & Perimeter Blacklist Detection (1 Minute)
**What to do:**
1. On Laptop 2, run Option 3: **Blacklisted IP Detection Simulation**.
2. Immediately observe the dashboard:
   - A **CRITICAL (Score 10/10)** alert appears: `Blacklisted IP Communication Detected`.
3. Explain:
   > "Our platform maintains an active perimeter blacklist table. When telemetry originated from known botnet IP `185.220.101.5`, our engine immediately prioritized it as CRITICAL without waiting for repetition."

---

## 🎬 STEP 5: Demonstrate Alert Triage & Incident Escalation (2 Minutes)
**What to do:**
1. Click the **Alerts & Triage** tab on the sidebar.
2. Show the newly generated `Brute Force Attack Detected` alert.
3. Change its triage status from `NEW` to `INVESTIGATING`.
4. Click the blue **⚡ Escalate →** button next to the alert.
5. Notice that the system automatically routes to the **Incident Response** tab and displays:
   - **Ticket ID:** `INC-2026-XXXX`
   - **Title:** `Incident: Brute Force Attack Detected on 203.0.113.88`
   - **Assigned Analyst:** `admin`
   - **Status:** `OPEN`
6. Click **Manage / Notes** on the incident ticket.
7. Update the status to `CONTAINED` and type resolution notes:
   `"Attacker IP 203.0.113.88 added to perimeter blacklist firewall. Endpoint credentials rotated."`
8. Click **Save Incident Updates**.

**What to explain to the professors:**
> "This demonstrates closed-loop Incident Response (IR). The alert was not simply discarded; it was formally converted into a trackable forensic incident ticket with assigned ownership and remediation documentation."

---

## 🎬 STEP 6: Conclude with API Documentation & RBAC (1 Minute)
1. Click the **API Reference** tab on the sidebar (or open `/api/docs`).
2. Show the interactive Swagger UI documenting all endpoints (`POST /api/events`, `GET /api/alerts`, `POST /api/auth/login`).
3. Click the **User Roles & RBAC** tab to demonstrate Role-Based Access Control governance.

**Conclusion statement:**
> "In summary, our system successfully satisfies all Level 5 cybersecurity requirements: external cross-network telemetry ingestion, zero-trust severity verification, rule-based threat correlation, dynamic risk scoring, live SOC visualization, and an integrated incident response workflow."
