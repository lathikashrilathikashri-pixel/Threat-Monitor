"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Incident Response Management Routes
FILE: backend/routes/incident_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Provides full lifecycle management for Security Incidents:
    - GET   /api/incidents      : Lists all tracked security incidents
    - GET   /api/incidents/<id> : Incident details and linked alert history
    - POST  /api/incidents      : Creates new incident ticket
    - PATCH /api/incidents/<id> : Updates lifecycle status (OPEN, INVESTIGATING, 
                                  CONTAINED, RESOLVED), analyst assignment, and 
                                  forensic resolution notes.

WHY IT IS REQUIRED:
    Incident Response (IR) is the core operational phase following threat detection.
    Allows analysts to assign tasks, document containment actions, and maintain a 
    forensic audit trail for compliance and reporting.

HOW IT CONNECTS TO OTHER MODULES:
    - Reads and updates Incident records in backend/models.py.
    - Linked to originating Alert records.
    - Displayed in React dashboard Incidents tab.
===================================================================================
"""

from datetime import datetime, timezone
import uuid
from flask import Blueprint, request, jsonify
try:
    from models import Incident
    from middleware import jwt_required, roles_required
except (ImportError, ModuleNotFoundError):
    from backend.models import Incident
    from backend.middleware import jwt_required, roles_required

def create_incident_blueprint(get_db_session):
    incident_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")

    @incident_bp.route("", methods=["GET"])
    @jwt_required
    def list_incidents():
        """
        Retrieves security incidents.
        Query Params: status, severity, limit, offset
        """
        session = get_db_session()
        limit = min(int(request.args.get("limit", 50)), 200)
        offset = int(request.args.get("offset", 0))

        query = session.query(Incident)

        status = request.args.get("status")
        if status:
            query = query.filter(Incident.status == status.upper())

        severity = request.args.get("severity")
        if severity:
            query = query.filter(Incident.severity == severity.upper())

        total = query.count()
        incidents = query.order_by(Incident.created_at.desc()).offset(offset).limit(limit).all()

        return jsonify({
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "incidents": [inc.to_dict() for inc in incidents]
        }), 200

    @incident_bp.route("/<string:incident_id>", methods=["GET"])
    @jwt_required
    def get_incident(incident_id):
        """Fetches a specific incident by ID."""
        session = get_db_session()
        incident = session.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return jsonify({"status": "error", "message": "Incident not found."}), 404

        return jsonify({"status": "success", "incident": incident.to_dict()}), 200

    @incident_bp.route("", methods=["POST"])
    @roles_required("Admin", "Security Analyst")
    def create_incident():
        """Creates a standalone security incident ticket."""
        session = get_db_session()
        data = request.get_json() or {}

        title = data.get("title")
        description = data.get("description")
        severity = (data.get("severity") or "MEDIUM").upper()
        source = data.get("source") or "Manual Analyst Investigation"
        assigned_analyst = data.get("assigned_analyst") or getattr(request, "current_user", {}).get("username", "SOC Analyst")

        if not title or not description:
            return jsonify({"status": "error", "message": "Title and description are required."}), 400

        year = datetime.now().year
        random_suffix = str(uuid.uuid4())[:6].upper()
        incident_id = f"INC-{year}-{random_suffix}"

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            assigned_analyst=assigned_analyst,
            status="OPEN",
            resolution_notes=data.get("resolution_notes", "")
        )
        session.add(incident)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "Incident ticket created successfully.",
            "incident": incident.to_dict()
        }), 201

    @incident_bp.route("/<string:incident_id>", methods=["PATCH"])
    @roles_required("Admin", "Security Analyst")
    def update_incident(incident_id):
        """
        Updates status (OPEN, INVESTIGATING, CONTAINED, RESOLVED), 
        assigned analyst, or forensic resolution notes.
        """
        session = get_db_session()
        incident = session.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return jsonify({"status": "error", "message": "Incident not found."}), 404

        data = request.get_json() or {}

        # Validate status if provided
        if "status" in data:
            valid_statuses = ["OPEN", "INVESTIGATING", "CONTAINED", "RESOLVED"]
            status = data["status"].upper()
            if status not in valid_statuses:
                return jsonify({"status": "error", "message": f"Invalid status. Choose from: {valid_statuses}."}), 400
            incident.status = status

        if "assigned_analyst" in data:
            incident.assigned_analyst = data["assigned_analyst"]

        if "resolution_notes" in data:
            incident.resolution_notes = data["resolution_notes"]

        if "severity" in data:
            incident.severity = data["severity"].upper()

        incident.updated_at = datetime.now(timezone.utc)
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"Incident {incident_id} updated successfully.",
            "incident": incident.to_dict()
        }), 200

    return incident_bp
