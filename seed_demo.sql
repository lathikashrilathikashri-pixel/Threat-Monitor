-- ===================================================================================
-- PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
-- MODULE: Relational Database Demo Seed Data (PostgreSQL)
-- FILE: database/seed_demo.sql
-- ===================================================================================

-- 1. Insert Initial User Accounts (passwords hashed with PBKDF2/SHA256)
-- Default passwords:
--   admin    -> AdminSecure2026!
--   analyst1 -> AnalystPass2026!
--   auditor  -> AuditorPass2026!
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@soc-command.local', 'scrypt:32768:8:1$7f3A9...$placeholder_admin_hash', 'Admin'),
('analyst1', 'analyst1@soc-command.local', 'scrypt:32768:8:1$9z2B1...$placeholder_analyst_hash', 'Security Analyst'),
('auditor', 'auditor@soc-command.local', 'scrypt:32768:8:1$1q4C8...$placeholder_auditor_hash', 'User')
ON CONFLICT (username) DO NOTHING;

-- 2. Insert Registered External Endpoints
INSERT INTO devices (id, device_name, os_type, ip_address, api_key, status, last_seen) VALUES
('LAPTOP-SEC-AGENT-01', 'External ThinkPad T14 (Student Device)', 'Windows 11 Enterprise', '192.168.1.105', 'sec_dev_token_alpha_9921', 'ONLINE', CURRENT_TIMESTAMP),
('VM-KALI-DEFENSE-02', 'Linux Security Gateway VM', 'Ubuntu 24.04 LTS', '10.0.4.15', 'sec_dev_token_beta_3310', 'ONLINE', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

-- 3. Insert Perimeter IP Blacklist
INSERT INTO blocked_ips (ip_address, reason, blocked_by, is_active) VALUES
('185.220.101.5', 'Known Tor Exit Node / Malicious Brute Force Botnet', 'SOC Automated Defense', TRUE),
('45.143.200.12', 'Repeated Port Scanning & Web Vulnerability Probing', 'analyst1', TRUE)
ON CONFLICT (ip_address) DO NOTHING;

-- 4. Insert Sample Events
INSERT INTO security_events (device_id, event_type, source_ip, destination_port, username, process_name, description, severity, timestamp) VALUES
('LAPTOP-SEC-AGENT-01', 'FAILED_LOGIN', '185.220.101.5', NULL, 'administrator', NULL, 'Repeated failed RDP authentication attempt', 'HIGH', CURRENT_TIMESTAMP - INTERVAL '40 minutes'),
('LAPTOP-SEC-AGENT-01', 'PORT_SCAN_ATTEMPT', '45.143.200.12', 445, NULL, NULL, 'SYN packet probe detected across SMB and NetBIOS ports', 'HIGH', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
('VM-KALI-DEFENSE-02', 'SUSPICIOUS_PROCESS', '10.0.4.15', NULL, NULL, 'mimikatz.exe', 'Credential extraction tool execution detected in memory', 'HIGH', CURRENT_TIMESTAMP - INTERVAL '15 minutes'),
('LAPTOP-SEC-AGENT-01', 'SYSTEM_HEARTBEAT', '192.168.1.105', NULL, NULL, NULL, 'Normal endpoint health telemetry reported', 'LOW', CURRENT_TIMESTAMP - INTERVAL '2 minutes');

-- 5. Insert Alerts
INSERT INTO alerts (id, alert_type, severity, risk_score, source_ip, device_id, description, status, created_at) VALUES
(1, 'Brute Force Attack Detected', 'HIGH', 8, '185.220.101.5', 'LAPTOP-SEC-AGENT-01', 'Over 6 failed authentication attempts detected within 3 minutes from blacklisted IP.', 'NEW', CURRENT_TIMESTAMP - INTERVAL '39 minutes'),
(2, 'Suspicious Process Execution', 'HIGH', 8, '10.0.4.15', 'VM-KALI-DEFENSE-02', 'Unauthorized execution of mimikatz.exe detected on security node.', 'INVESTIGATING', CURRENT_TIMESTAMP - INTERVAL '14 minutes');

-- 6. Insert Incident Ticket
INSERT INTO incidents (id, title, description, severity, source, assigned_analyst, status, resolution_notes, alert_id, created_at) VALUES
('INC-2026-0042', 'Host Compromise Investigation on VM-KALI-DEFENSE-02', 'Execution of credential dumping binary mimikatz detected. Host isolated for forensic imaging.', 'HIGH', 'Alert #2 (Suspicious Process Execution)', 'analyst1', 'INVESTIGATING', 'Endpoint network interface quarantined. Memory dump captured for offline volatility analysis.', 2, CURRENT_TIMESTAMP - INTERVAL '12 minutes')
ON CONFLICT (id) DO NOTHING;
