"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Blocked IP / Blacklist Management Routes
FILE: backend/routes/blocked_ip_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Manages the active threat perimeter blacklist:
    - GET    /api/blocked-ips      : Lists all active and inactive blocked IPs
    - POST   /api/blocked-ips      : Adds a malicious IP to the blacklist
    - DELETE /api/blocked-ips/<id> : Unblocks / removes an IP from the blacklist

WHY IT IS REQUIRED:
    Provides direct containment capability. When an analyst identifies a malicious 
    IP scanning or brute forcing, they can immediately blacklist it. Any future 
    traffic from this IP triggers an automatic CRITICAL severity alert.

HOW IT CONNECTS TO OTHER MODULES:
    - Writes to BlockedIP table in backend/models.py.
    - Queried by backend/detection_engine.py on every incoming event.
    - Managed via the React frontend Blocked IPs page.
===================================================================================
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import BlockedIP
from middleware import jwt_required, roles_required

def create_blocked_ip_blueprint(get_db_session):
    ip_bp = Blueprint("blocked_ips", __name__, url_prefix="/api/blocked-ips")

    @ip_bp.route("", methods=["GET"])
    @jwt_required
    def list_blocked_ips():
        """Lists all blacklisted IP addresses."""
        session = get_db_session()
        ips = session.query(BlockedIP).order_by(BlockedIP.created_at.desc()).all()
        return jsonify({
            "status": "success",
            "total": len(ips),
            "blocked_ips": [ip.to_dict() for ip in ips]
        }), 200

    @ip_bp.route("", methods=["POST"])
    @roles_required("Admin", "Security Analyst")
    def add_blocked_ip():
        """Adds a suspicious or attacking IP address to the blacklist."""
        session = get_db_session()
        data = request.get_json() or {}

        ip_address = (data.get("ip_address") or "").strip()
        reason = (data.get("reason") or "Identified by analyst as malicious").strip()
        blocked_by = getattr(request, "current_user", {}).get("username", "SOC Analyst")

        if not ip_address:
            return jsonify({"status": "error", "message": "IP address is required."}), 400

        # Check existing
        existing = session.query(BlockedIP).filter(BlockedIP.ip_address == ip_address).first()
        if existing:
            existing.is_active = True
            existing.reason = reason
            session.commit()
            return jsonify({
                "status": "success",
                "message": f"IP {ip_address} was already in blacklist; marked active.",
                "blocked_ip": existing.to_dict()
            }), 200

        new_blocked = BlockedIP(
            ip_address=ip_address,
            reason=reason,
            blocked_by=blocked_by,
            is_active=True
        )
        session.add(new_blocked)
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"IP {ip_address} successfully added to blacklist.",
            "blocked_ip": new_blocked.to_dict()
        }), 201

    @ip_bp.route("/<int:ip_id>", methods=["DELETE"])
    @roles_required("Admin", "Security Analyst")
    def remove_blocked_ip(ip_id):
        """Unblocks an IP address."""
        session = get_db_session()
        blocked = session.query(BlockedIP).filter(BlockedIP.id == ip_id).first()
        if not blocked:
            return jsonify({"status": "error", "message": "Blocked IP record not found."}), 404

        session.delete(blocked)
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"IP {blocked.ip_address} removed from blacklist."
        }), 200

    return ip_bp
