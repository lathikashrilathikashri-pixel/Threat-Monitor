"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Device Management & Heartbeat Routes
FILE: backend/routes/device_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Manages external endpoint assets (monitored laptops, VMs, workstations):
    - GET    /api/devices           : Lists registered endpoints with ONLINE/OFFLINE health
    - POST   /api/devices           : Registers new monitoring device & issues API key
    - POST   /api/devices/heartbeat : Receives periodic health telemetry from Python agent
    - DELETE /api/devices/<id>      : Decommissions device (Admin role required)

WHY IT IS REQUIRED:
    External device integration requires an asset registry, authentication tokens,
    and liveness checking so analysts know which external sensors are actively reporting.

HOW IT CONNECTS TO OTHER MODULES:
    - Stores Device objects in backend/models.py.
    - Python agent (security-agent/agent.py) calls /heartbeat periodically.
    - Used by React dashboard Devices page to show live fleet status.
===================================================================================
"""

import secrets
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
try:
    from models import Device
    from middleware import jwt_required, roles_required
except (ImportError, ModuleNotFoundError):
    from backend.models import Device
    from backend.middleware import jwt_required, roles_required

def create_device_blueprint(get_db_session):
    device_bp = Blueprint("devices", __name__, url_prefix="/api/devices")

    @device_bp.route("", methods=["GET"])
    @jwt_required
    def list_devices():
        """Returns all registered devices with their live online/offline status."""
        session = get_db_session()
        devices = session.query(Device).order_by(Device.created_at.desc()).all()
        return jsonify({
            "status": "success",
            "total": len(devices),
            "devices": [d.to_dict() for d in devices]
        }), 200

    @device_bp.route("", methods=["POST"])
    @roles_required("Admin", "Security Analyst")
    def register_device():
        """
        Registers a new external device/laptop and generates an API token.
        Payload: { id, device_name, os_type, ip_address }
        """
        session = get_db_session()
        data = request.get_json() or {}

        device_id = (data.get("id") or f"DEV-{secrets.token_hex(4).upper()}").strip()
        device_name = (data.get("device_name") or "External Security Node").strip()
        os_type = data.get("os_type") or "Windows / Linux"
        ip_address = data.get("ip_address") or request.headers.get("X-Forwarded-For", request.remote_addr)

        # Check for duplicate ID
        existing = session.query(Device).filter(Device.id == device_id).first()
        if existing:
            return jsonify({"status": "error", "message": f"Device ID '{device_id}' already registered."}), 409

        # Generate cryptographically secure API key
        api_key = f"sec_key_{secrets.token_hex(20)}"

        new_device = Device(
            id=device_id,
            device_name=device_name,
            os_type=os_type,
            ip_address=ip_address,
            api_key=api_key,
            status="ONLINE",
            last_seen=datetime.now(timezone.utc)
        )
        session.add(new_device)
        session.commit()

        return jsonify({
            "status": "success",
            "message": "Device registered successfully.",
            "device": new_device.to_dict(),
            "device_token": api_key,
            "instructions": f"Configure agent with SERVER_URL and DEVICE_TOKEN='{api_key}'"
        }), 201

    @device_bp.route("/heartbeat", methods=["POST"])
    def heartbeat():
        """
        Heartbeat endpoint for the lightweight Python Security Agent.
        Verifies device API key (via header or payload), updates last_seen timestamp.
        """
        session = get_db_session()
        data = request.get_json() or {}
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        device_id = data.get("device_id")
        api_key = request.headers.get("X-Device-Token") or request.headers.get("X-API-Key") or data.get("api_key")

        if not device_id or not api_key:
            return jsonify({"status": "error", "message": "device_id and api_key/X-Device-Token are required."}), 400

        device = session.query(Device).filter(Device.id == device_id).first()
        if not device or device.api_key != api_key:
            return jsonify({"status": "error", "message": "Invalid device credentials."}), 401

        # Refresh heartbeat and IP
        device.last_seen = datetime.now(timezone.utc)
        device.status = "ONLINE"
        if client_ip and client_ip != "127.0.0.1":
            device.ip_address = client_ip

        if data.get("os_type"):
            device.os_type = data["os_type"]

        session.commit()

        return jsonify({
            "status": "success",
            "message": "Heartbeat received.",
            "server_time": datetime.now(timezone.utc).isoformat(),
            "device_status": "ONLINE"
        }), 200

    @device_bp.route("/<string:device_id>", methods=["DELETE"])
    @roles_required("Admin")
    def delete_device(device_id):
        """Deletes a device from the monitored fleet (Admin only)."""
        session = get_db_session()
        device = session.query(Device).filter(Device.id == device_id).first()
        if not device:
            return jsonify({"status": "error", "message": "Device not found."}), 404

        session.delete(device)
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"Device {device_id} removed from registry."
        }), 200

    return device_bp
