"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Database Models (SQLAlchemy ORM)
FILE: backend/models.py
===================================================================================
WHAT THIS FILE DOES:
    Defines the relational database schema using SQLAlchemy ORM:
    - User (Admins, Analysts, Standard users with salted password hashing)
    - Device (Monitored external laptops/VMs with API keys and heartbeat tracking)
    - SecurityEvent (Raw logs ingested from agents or simulation)
    - Alert (Engine-correlated alerts with risk scores & triage lifecycle)
    - Incident (Official security incidents with analyst assignments and notes)
    - LoginAttempt (Audit trail for brute force and abnormal authentication detection)
    - BlockedIP (SOC blacklist for proactive network perimeter defense)

WHY IT IS REQUIRED:
    Essential for persistent security audit logs, relational integrity, 
    SQL injection protection via parameterized queries, and clean JSON serialization.

HOW IT CONNECTS TO OTHER MODULES:
    - Used by detection_engine.py to correlate past events and create alerts.
    - Used by all route handlers in backend/routes/ to read/write persistent data.
    - Initialized in app.py via db.init_app(app).
===================================================================================
"""

from datetime import datetime, timezone
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """
    User entity representing SOC personnel and system operators.
    Roles:
      - Admin: Full system access (device management, user roles, system configs)
      - Security Analyst: Monitor SOC dashboard, triage alerts, manage incidents
      - User: Read-only visibility to permitted security metrics
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="Security Analyst")  # Admin, Security Analyst, User
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str):
        """Generates a secure PBKDF2/sha256 salted password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies supplied password against stored cryptographic hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Device(Base):
    """
    Monitored external endpoints (laptops, virtual machines, servers)
    running the Python Security Monitoring Agent.
    """
    __tablename__ = "devices"

    id = Column(String(64), primary_key=True)  # e.g., "ENDPOINT-LAPTOP-001"
    device_name = Column(String(120), nullable=False)
    os_type = Column(String(80), default="Unknown")  # Windows 11, Ubuntu 24.04, etc.
    ip_address = Column(String(64), nullable=False)
    api_key = Column(String(128), unique=True, nullable=False, index=True)
    status = Column(String(20), default="ONLINE")  # ONLINE, OFFLINE
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    events = relationship("SecurityEvent", back_populates="device", cascade="all, delete-orphan")

    def to_dict(self):
        # Calculate online status dynamically (offline if no heartbeat in last 3 minutes)
        is_online = False
        if self.last_seen:
            diff = (datetime.now(timezone.utc) - self.last_seen.replace(tzinfo=timezone.utc)).total_seconds()
            is_online = (diff < 180)  # within 3 minutes

        return {
            "id": self.id,
            "device_name": self.device_name,
            "os_type": self.os_type,
            "ip_address": self.ip_address,
            "api_key": self.api_key,
            "status": "ONLINE" if is_online else "OFFLINE",
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SecurityEvent(Base):
    """
    Raw security telemetry logs ingested from external devices or simulation scripts.
    """
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.id"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)  # FAILED_LOGIN, PORT_SCAN, etc.
    source_ip = Column(String(64), nullable=False, index=True)
    destination_port = Column(Integer, nullable=True)
    username = Column(String(80), nullable=True)
    process_name = Column(String(120), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    raw_data = Column(Text, nullable=True)  # JSON payload string
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    device = relationship("Device", back_populates="events")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "event_type": self.event_type,
            "source_ip": self.source_ip,
            "destination_port": self.destination_port,
            "username": self.username,
            "process_name": self.process_name,
            "description": self.description,
            "severity": self.severity,
            "raw_data": self.raw_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class Alert(Base):
    """
    Actionable security alerts synthesized by the Threat Detection Engine.
    Includes dynamic risk scores (1-10) and lifecycle status tracking.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(80), nullable=False, index=True)  # Brute Force, Port Scan, Blocked IP, etc.
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Integer, nullable=False)  # 1 to 10
    source_ip = Column(String(64), nullable=False, index=True)
    device_id = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="NEW")  # NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    incidents = relationship("Incident", back_populates="alert")

    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "source_ip": self.source_ip,
            "device_id": self.device_id,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Incident(Base):
    """
    Official cybersecurity incident tickets created when an alert is escalated 
    or when active malicious engagement requires containment and remediation.
    """
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True)  # e.g., "INC-2026-0042"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    source = Column(String(100), default="Detection Engine")
    assigned_analyst = Column(String(80), default="Unassigned")
    status = Column(String(30), nullable=False, default="OPEN")  # OPEN, INVESTIGATING, CONTAINED, RESOLVED
    resolution_notes = Column(Text, default="")
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    alert = relationship("Alert", back_populates="incidents")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "source": self.source,
            "assigned_analyst": self.assigned_analyst,
            "status": self.status,
            "resolution_notes": self.resolution_notes,
            "alert_id": self.alert_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class LoginAttempt(Base):
    """
    Granular audit log of all authentication requests to detect 
    credential stuffing, brute force, and anomalous login sequences.
    """
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(64), nullable=False, index=True)
    username = Column(String(80), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "username": self.username,
            "success": self.success,
            "attempted_at": self.attempted_at.isoformat() if self.attempted_at else None
        }


class BlockedIP(Base):
    """
    IP Blacklist configured by SOC analysts or automated containment rules.
    Any telemetry or request from a blacklisted IP triggers immediate CRITICAL alert.
    """
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(64), unique=True, nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    blocked_by = Column(String(80), default="Automated Defense")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "reason": self.reason,
            "blocked_by": self.blocked_by,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
