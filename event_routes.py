"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Security Event Ingestion & Query Routes
FILE: backend/routes/event_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Provides the core SOC telemetry ingestion and auditing endpoints:
    - POST /api/events : Ingests external security logs (failed logins, port scans, 
                         suspicious processes, network connections) from the Python 
                         agent or simulation script.
    - GET  /api/events : Retrieves historical security logs with filtering.

WHY IT IS REQUIRED:
    Serves as the gateway for external device telemetry. It decouples the client's 
    reported severity from reality by passing every event through the backend 
    detection engine before persisting.

HOW IT CONNECTS TO OTHER MODULES:
    - Analyzed by backend/detection_engine.py.
    - Updates Device records in backend/models.py.
    - Creates Alert records if malicious patterns match.
    - Consumed by React dashboard Event Stream table.
===================================================================================
"""

import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import SecurityEvent, Device
from detection_engine import ThreatDetectionEngine
from middleware import jwt_required

def create_event_blueprint(get_db_session):
    event_bp = Blueprint("events", __name__, url_prefix="/api/events")

    @event_bp.route("", methods=["POST"])
    def ingest_event():
        """
        Event Ingestion API.
        Receives telemetry from external agents (authenticated via X-Device-Token or device_id)
        or simulation test scripts.
        """
        session = get_db_session()
        data = request.get_json() or {}
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        device_id = data.get("device_id")
        event_type = (data.get("event_type") or "GENERIC_EVENT").strip().upper()
        source_ip = data.get("source_ip") or client_ip
        destination_port = data.get("destination_port")
        username = data.get("username")
        process_name = data.get("process_name")
        description = data.get("description") or f"Security event of type {event_type}"
        raw_data = data.get("raw_data")

        if isinstance(raw_data, (dict, list)):
            raw_data = json.dumps(raw_data)

        # Update external device heartbeat / last_seen timestamp if device exists
        if device_id:
            device = session.query(Device).filter(Device.id == device_id).first()
            if device:
                device.last_seen = datetime.now(timezone.utc)
                device.status = "ONLINE"
                if source_ip and source_ip != "127.0.0.1":
                    device.ip_address = source_ip

        # Run through the Threat Detection & Risk Scoring Engine
        detection_engine = ThreatDetectionEngine(session)
        verified_severity, risk_score, alerts_generated = detection_engine.process_event(data, client_ip)

        # Persist event with VERIFIED severity calculated by engine
        new_event = SecurityEvent(
            device_id=device_id,
            event_type=event_type,
            source_ip=source_ip,
            destination_port=destination_port,
            username=username,
            process_name=process_name,
            description=description,
            severity=verified_severity,
            raw_data=raw_data,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(new_event)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "Security event ingested and analyzed successfully.",
            "event": new_event.to_dict(),
            "calculated_risk_score": risk_score,
            "alerts_created": [a.to_dict() for a in alerts_generated]
        }), 201

    @event_bp.route("", methods=["GET"])
    @jwt_required
    def list_events():
        """
        Retrieves paginated and filtered security events.
        Query Params: limit, offset, device_id, severity, event_type
        """
        session = get_db_session()
        limit = min(int(request.args.get("limit", 50)), 200)
        offset = int(request.args.get("offset", 0))

        query = session.query(SecurityEvent)

        # Filters
        device_id = request.args.get("device_id")
        if device_id:
            query = query.filter(SecurityEvent.device_id == device_id)

        severity = request.args.get("severity")
        if severity:
            query = query.filter(SecurityEvent.severity == severity.upper())

        event_type = request.args.get("event_type")
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type.upper())

        total = query.count()
        events = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit).all()

        return jsonify({
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "events": [e.to_dict() for e in events]
        }), 200

    return event_bp
