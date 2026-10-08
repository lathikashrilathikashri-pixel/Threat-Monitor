"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Alert Triage & Escalation Routes
FILE: backend/routes/alert_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Manages the lifecycle of security alerts:
    - GET   /api/alerts                    : Lists alerts with risk scores & statuses
    - GET   /api/alerts/<id>               : Retrieves single alert detail
    - POST  /api/alerts                    : Manual alert creation by security analysts
    - PATCH /api/alerts/<id>               : Updates alert status (NEW, INVESTIGATING, 
                                             RESOLVED, FALSE_POSITIVE)
    - POST  /api/alerts/<id>/convert-incident : Escalates alert directly to Incident

WHY IT IS REQUIRED:
    Alert management is the focal workflow of a Security Analyst. It allows analysts
    to filter by severity, triage false positives, and escalate high-risk threats.

HOW IT CONNECTS TO OTHER MODULES:
    - Reads and updates Alert records in backend/models.py.
    - Creates Incident records in backend/models.py upon escalation.
    - Protected by JWT authentication and RBAC in backend/middleware.py.
===================================================================================
"""

from datetime import datetime, timezone
import uuid
from flask import Blueprint, request, jsonify
from models import Alert, Incident
from middleware import jwt_required, roles_required

def create_alert_blueprint(get_db_session):
    alert_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

    @alert_bp.route("", methods=["GET"])
    @jwt_required
    def list_alerts():
        """
        Retrieves security alerts, sorted by latest first.
        Query Params: status, severity, limit, offset
        """
        session = get_db_session()
        limit = min(int(request.args.get("limit", 50)), 200)
        offset = int(request.args.get("offset", 0))

        query = session.query(Alert)

        status = request.args.get("status")
        if status:
            query = query.filter(Alert.status == status.upper())

        severity = request.args.get("severity")
        if severity:
            query = query.filter(Alert.severity == severity.upper())

        total = query.count()
        alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()

        return jsonify({
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "alerts": [a.to_dict() for a in alerts]
        }), 200

    @alert_bp.route("/<int:alert_id>", methods=["GET"])
    @jwt_required
    def get_alert(alert_id):
        """Fetches individual alert details."""
        session = get_db_session()
        alert = session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return jsonify({"status": "error", "message": "Alert not found."}), 404

        return jsonify({"status": "success", "alert": alert.to_dict()}), 200

    @alert_bp.route("", methods=["POST"])
    @roles_required("Admin", "Security Analyst")
    def create_alert():
        """Creates a manual alert by an authenticated analyst."""
        session = get_db_session()
        data = request.get_json() or {}

        alert_type = data.get("alert_type") or "Manual Security Notice"
        severity = (data.get("severity") or "MEDIUM").upper()
        risk_score = int(data.get("risk_score") or 5)
        source_ip = data.get("source_ip") or "127.0.0.1"
        device_id = data.get("device_id")
        description = data.get("description") or "Analyst submitted security alert."

        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            risk_score=risk_score,
            source_ip=source_ip,
            device_id=device_id,
            description=description,
            status="NEW"
        )
        session.add(alert)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "Alert created successfully.",
            "alert": alert.to_dict()
        }), 201

    @alert_bp.route("/<int:alert_id>", methods=["PATCH"])
    @roles_required("Admin", "Security Analyst")
    def update_alert_status(alert_id):
        """
        Updates alert triage status.
        Valid statuses: NEW, INVESTIGATING, RESOLVED, FALSE_POSITIVE
        """
        session = get_db_session()
        alert = session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return jsonify({"status": "error", "message": "Alert not found."}), 404

        data = request.get_json() or {}
        new_status = data.get("status")

        valid_statuses = ["NEW", "INVESTIGATING", "RESOLVED", "FALSE_POSITIVE"]
        if new_status and new_status.upper() in valid_statuses:
            alert.status = new_status.upper()
            alert.updated_at = datetime.now(timezone.utc)
            session.commit()
            return jsonify({
                "status": "success",
                "message": f"Alert #{alert_id} status updated to {alert.status}.",
                "alert": alert.to_dict()
            }), 200

        return jsonify({
            "status": "error",
            "message": f"Invalid status. Allowed values: {valid_statuses}."
        }), 400

    @alert_bp.route("/<int:alert_id>/convert-incident", methods=["POST"])
    @roles_required("Admin", "Security Analyst")
    def convert_to_incident(alert_id):
        """
        Escalates an Alert into an Incident Response ticket.
        """
        session = get_db_session()
        alert = session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return jsonify({"status": "error", "message": "Alert not found."}), 404

        # Generate unique incident ID
        year = datetime.now().year
        random_suffix = str(uuid.uuid4())[:6].upper()
        incident_id = f"INC-{year}-{random_suffix}"

        current_analyst = getattr(request, "current_user", {}).get("username", "SOC Analyst")

        # Create Incident ticket
        incident = Incident(
            id=incident_id,
            title=f"Incident: {alert.alert_type} on {alert.source_ip}",
            description=alert.description,
            severity=alert.severity,
            source=f"Alert #{alert.id} ({alert.alert_type})",
            assigned_analyst=current_analyst,
            status="OPEN",
            resolution_notes=f"Escalated from Alert #{alert.id} by {current_analyst} for detailed investigation.",
            alert_id=alert.id
        )

        # Mark alert as currently under investigation
        alert.status = "INVESTIGATING"
        alert.updated_at = datetime.now(timezone.utc)

        session.add(incident)
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"Alert escalated to incident ticket {incident_id}.",
            "incident": incident.to_dict(),
            "alert": alert.to_dict()
        }), 201

    return alert_bp
