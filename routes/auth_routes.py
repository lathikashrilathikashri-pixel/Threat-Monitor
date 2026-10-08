"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Authentication & Identity Management Routes
FILE: backend/routes/auth_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Handles user onboarding, authentication, JWT issuing, and login attempt auditing:
    - POST /api/auth/register : Creates new SOC accounts with salted password hash
    - POST /api/auth/login    : Authenticates user, logs attempt, issues JWT
    - POST /api/auth/logout   : Invalidates client session
    - GET  /api/auth/me       : Returns current authenticated user profile

WHY IT IS REQUIRED:
    Provides identity security, protects endpoints with JWT tokens, and acts as 
    a primary sensor for Brute Force & Abnormal Login detection.

HOW IT CONNECTS TO OTHER MODULES:
    - Interacts with backend/models.py (User, LoginAttempt).
    - Triggers detection_engine.py to catch brute force attacks against the web portal.
    - Uses backend/middleware.py for token generation and @jwt_required guard.
===================================================================================
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
try:
    from models import User, LoginAttempt
    from middleware import generate_jwt_token, jwt_required
    from detection_engine import ThreatDetectionEngine
except (ImportError, ModuleNotFoundError):
    from backend.models import User, LoginAttempt
    from backend.middleware import generate_jwt_token, jwt_required
    from backend.detection_engine import ThreatDetectionEngine

def create_auth_blueprint(get_db_session):
    auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

    @auth_bp.route("/register", methods=["POST"])
    def register():
        """
        Registers a new user into the cybersecurity platform.
        Payload: { username, email, password, role (optional) }
        """
        session = get_db_session()
        data = request.get_json() or {}

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        role = data.get("role", "Security Analyst").strip()

        # Input validation
        if not username or len(username) < 3:
            return jsonify({"status": "error", "message": "Username must be at least 3 characters long."}), 400
        if not email or "@" not in email:
            return jsonify({"status": "error", "message": "Valid email address is required."}), 400
        if not password or len(password) < 6:
            return jsonify({"status": "error", "message": "Password must be at least 6 characters long."}), 400

        # Enforce valid roles
        valid_roles = ["Admin", "Security Analyst", "User"]
        if role not in valid_roles:
            role = "Security Analyst"

        # Check existing username/email
        if session.query(User).filter((User.username == username) | (User.email == email)).first():
            return jsonify({"status": "error", "message": "Username or email is already registered."}), 409

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()

        # Generate immediate login token
        token = generate_jwt_token(new_user)

        return jsonify({
            "status": "success",
            "message": "User registered successfully.",
            "token": token,
            "user": new_user.to_dict()
        }), 201

    @auth_bp.route("/login", methods=["POST"])
    def login():
        """
        Authenticates user, logs the attempt to login_attempts,
        triggers brute force detection if invalid, and issues JWT upon success.
        """
        session = get_db_session()
        data = request.get_json() or {}
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required."}), 400

        user = session.query(User).filter(User.username == username).first()
        is_authenticated = user is not None and user.check_password(password)

        # Audit log the authentication attempt
        attempt = LoginAttempt(
            ip_address=client_ip,
            username=username,
            success=is_authenticated,
            attempted_at=datetime.now(timezone.utc)
        )
        session.add(attempt)
        session.commit()

        detection_engine = ThreatDetectionEngine(session)

        # If authentication failed -> Check for Brute Force attack
        if not is_authenticated:
            bf_alert = detection_engine.check_brute_force(client_ip)
            if bf_alert:
                session.commit()
            return jsonify({
                "status": "error",
                "message": "Invalid username or password.",
                "security_notice": "Attempt logged for intrusion detection."
            }), 401

        # If authentication succeeded -> Check if preceded by multiple failures (credential compromise)
        abnormal_alert = detection_engine.check_abnormal_login(username, client_ip)
        if abnormal_alert:
            session.commit()

        # Authentication success: generate JWT
        token = generate_jwt_token(user)

        return jsonify({
            "status": "success",
            "message": "Authentication successful.",
            "token": token,
            "user": user.to_dict()
        }), 200

    @auth_bp.route("/logout", methods=["POST"])
    def logout():
        """Client-side token disposal endpoint."""
        return jsonify({
            "status": "success",
            "message": "Logged out successfully. Please discard client session token."
        }), 200

    @auth_bp.route("/me", methods=["GET"])
    @jwt_required
    def get_me():
        """Returns the profile of the currently logged-in user."""
        session = get_db_session()
        current_user_id = int(request.current_user.get("sub"))
        user = session.query(User).filter(User.id == current_user_id).first()
        if not user:
            return jsonify({"status": "error", "message": "User not found."}), 404

        return jsonify({
            "status": "success",
            "user": user.to_dict()
        }), 200

    return auth_bp
