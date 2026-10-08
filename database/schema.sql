-- ===================================================================================
-- PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
-- MODULE: Relational Database Schema (PostgreSQL)
-- FILE: database/schema.sql
-- ===================================================================================

-- 1. Users Table (Identity & Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'Security Analyst',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 2. Devices Table (Monitored External Laptops, Workstations, VMs)
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(64) PRIMARY KEY,
    device_name VARCHAR(120) NOT NULL,
    os_type VARCHAR(80) DEFAULT 'Unknown',
    ip_address VARCHAR(64) NOT NULL,
    api_key VARCHAR(128) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'ONLINE',
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_devices_api_key ON devices(api_key);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);

-- 3. Security Events Table (Ingested Telemetry & Raw Security Logs)
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) REFERENCES devices(id) ON DELETE SET NULL,
    event_type VARCHAR(64) NOT NULL,
    source_ip VARCHAR(64) NOT NULL,
    destination_port INTEGER,
    username VARCHAR(80),
    process_name VARCHAR(120),
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'LOW',
    raw_data TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_source_ip ON security_events(source_ip);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity);

-- 4. Alerts Table (Correlated Threats Synthesized by Detection Engine)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    risk_score INTEGER NOT NULL,
    source_ip VARCHAR(64) NOT NULL,
    device_id VARCHAR(64),
    description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_source_ip ON alerts(source_ip);

-- 5. Incidents Table (Official Incident Response Tickets)
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    source VARCHAR(100) DEFAULT 'Detection Engine',
    assigned_analyst VARCHAR(80) DEFAULT 'Unassigned',
    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    resolution_notes TEXT DEFAULT '',
    alert_id INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_assigned_analyst ON incidents(assigned_analyst);

-- 6. Login Attempts Table (Audit Trail for Brute Force & Credential Stuffing)
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(64) NOT NULL,
    username VARCHAR(80) NOT NULL,
    success BOOLEAN NOT NULL,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_login_ip ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_time ON login_attempts(attempted_at DESC);

-- 7. Blocked IPs Table (Firewall / SOC Perimeter Blacklist)
CREATE TABLE IF NOT EXISTS blocked_ips (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(64) UNIQUE NOT NULL,
    reason VARCHAR(255) NOT NULL,
    blocked_by VARCHAR(80) DEFAULT 'Automated Defense',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_blocked_ip ON blocked_ips(ip_address);
