"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Authentication & Authorization Middleware
FILE: backend/middleware.py
===================================================================================
WHAT THIS FILE DOES:
    Provides security guards and decorators:
    1. JWT Token Generator & Verifier (HS256 signature with expiration)
    2. Role-Based Access Control (RBAC: Admin, Security Analyst, User)
    3. Device Token / API Key Authenticator for external monitoring agents
    4. Safe parameter validation and security headers injector

WHY IT IS REQUIRED:
    Prevents unauthorized access to sensitive SOC endpoints, enforces least-privilege
    access control, and ensures that external agents are authenticated using unique
    device tokens.

HOW IT CONNECTS TO OTHER MODULES:
    - Wraps routes across auth_routes, alert_routes, incident_routes, device_routes.
    - Validates device API keys against records in backend/models.py.
    - Reads JWT_SECRET_KEY from backend/config.py.
===================================================================================
"""

from functools import wraps
from datetime import datetime, timezone, timedelta
import jwt
from flask import request, jsonify, current_app
try:
    from models import User, Device
    from config import Config
except (ImportError, ModuleNotFoundError):
    from backend.models import User, Device
    from backend.config import Config

def generate_jwt_token(user: User) -> str:
    """
    Creates a signed JSON Web Token (JWT) with user identity, role, and expiration.
    """
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + Config.JWT_ACCESS_TOKEN_EXPIRES
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token: str) -> dict | None:
    """Decodes and validates JWT signature and expiration timestamp."""
    try:
        return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def jwt_required(f):
    """
    Decorator requiring a valid JWT in the 'Authorization: Bearer <token>' header.
    Attaches payload data to request.current_user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "status": "error",
                "message": "Authentication required. Missing or malformed Bearer token."
            }), 401

        token = auth_header.split(" ")[1].strip()
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({
                "status": "error",
                "message": "Invalid or expired JWT token. Please re-authenticate."
            }), 401

        request.current_user = payload
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*allowed_roles):
    """
    Role-Based Access Control (RBAC) decorator.
    Ensures the authenticated user possesses one of the allowed roles.
    Example: @roles_required('Admin', 'Security Analyst')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            user_role = getattr(request, "current_user", {}).get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "status": "error",
                    "message": f"Access denied. Required roles: {list(allowed_roles)}. Your role: '{user_role}'."
                }), 403
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def device_or_jwt_required(db_session_getter):
    """
    Allows authentication either via:
    1. User Bearer JWT (for analysts submitting test events)
    2. External Device API Key via 'X-Device-Token' or 'X-API-Key'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for device token
            device_token = request.headers.get("X-Device-Token") or request.headers.get("X-API-Key")
            if device_token:
                session = db_session_getter()
                device = session.query(Device).filter(Device.api_key == device_token).first()
                if not device:
                    return jsonify({
                        "status": "error",
                        "message": "Unauthorized external device. Invalid device token/API key."
                    }), 401
                request.authenticated_device = device
                request.auth_type = "DEVICE"
                return f(*args, **kwargs)

            # Check for JWT
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1].strip()
                payload = decode_jwt_token(token)
                if payload:
                    request.current_user = payload
                    request.auth_type = "USER"
                    return f(*args, **kwargs)

            return jsonify({
                "status": "error",
                "message": "Unauthorized. Please provide a valid Bearer JWT or X-Device-Token."
            }), 401

        return decorated_function
    return decorator
