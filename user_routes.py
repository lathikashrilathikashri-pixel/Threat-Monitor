"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: User & Role Management Routes
FILE: backend/routes/user_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Provides role-based administration for platform accounts:
    - GET   /api/users          : Lists registered users and assigned roles
    - PATCH /api/users/<id>/role : Promotes or updates user permissions (Admin only)

WHY IT IS REQUIRED:
    Implements Role-Based Access Control (RBAC) governance required for academic 
    evaluation and cybersecurity audit compliance.

HOW IT CONNECTS TO OTHER MODULES:
    - Queries backend/models.py User table.
    - Protected by @roles_required('Admin') in backend/middleware.py.
===================================================================================
"""

from flask import Blueprint, request, jsonify
from models import User
from middleware import jwt_required, roles_required

def create_user_blueprint(get_db_session):
    user_bp = Blueprint("users", __name__, url_prefix="/api/users")

    @user_bp.route("", methods=["GET"])
    @jwt_required
    def list_users():
        """Lists registered platform users."""
        session = get_db_session()
        users = session.query(User).order_by(User.created_at.desc()).all()
        return jsonify({
            "status": "success",
            "total": len(users),
            "users": [u.to_dict() for u in users]
        }), 200

    @user_bp.route("/<int:user_id>/role", methods=["PATCH"])
    @roles_required("Admin")
    def update_role(user_id):
        """Admin-only endpoint to promote or alter user role."""
        session = get_db_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found."}), 404

        data = request.get_json() or {}
        new_role = data.get("role")
        valid_roles = ["Admin", "Security Analyst", "User"]

        if new_role not in valid_roles:
            return jsonify({"status": "error", "message": f"Invalid role. Options: {valid_roles}"}), 400

        user.role = new_role
        session.commit()

        return jsonify({
            "status": "success",
            "message": f"User '{user.username}' role updated to '{new_role}'.",
            "user": user.to_dict()
        }), 200

    return user_bp
