"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Central Flask Application Entry Point & WSGI Factory
FILE: app.py (Repository Root)
===================================================================================
WHAT THIS FILE DOES:
    Initializes and configures the Flask web application, database engine,
    security headers, CORS policy, blueprint routes, and error handlers.
    Exposes the WSGI application object 'app' for Gunicorn production execution:
    
        gunicorn app:app

WHY IT IS REQUIRED:
    Serves as the root runtime entry point on Render, Docker, and local development.
    Integrates all route modules from routes/ package and exposes REST endpoints.

HOW IT CONNECTS TO OTHER MODULES:
    - Imports Config from config.py
    - Imports SQLAlchemy Base & Models from models.py
    - Imports all route blueprints from routes/ package
    - Seeds default SOC data using seed.py
    - Serves Swagger OpenAPI UI from swagger.py
===================================================================================
"""

import sys
import os

# Guarantee that the repository root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Application imports
from config import Config
from models import Base
from seed import seed_database
from swagger import swagger_bp

# Route blueprint imports from routes/ package
from routes.auth_routes import create_auth_blueprint
from routes.event_routes import create_event_blueprint
from routes.alert_routes import create_alert_blueprint
from routes.incident_routes import create_incident_blueprint
from routes.device_routes import create_device_blueprint
from routes.dashboard_routes import create_dashboard_blueprint
from routes.blocked_ip_routes import create_blocked_ip_blueprint
from routes.user_routes import create_user_blueprint


def create_app(config_class=Config):
    """Application factory pattern for testability and clean architecture."""
    # Locate frontend static build directory if present
    frontend_dist_dir = os.path.abspath(os.path.join(ROOT_DIR, "frontend", "dist"))
    
    app = Flask(
        __name__, 
        static_folder=frontend_dist_dir if os.path.exists(frontend_dist_dir) else None,
        static_url_path=""
    )
    app.config.from_object(config_class)

    # 1. Enable Cross-Origin Resource Sharing (CORS) for external devices and frontend
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Device-Token", "X-API-Key"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    # 2. Initialize Database Engine & Session
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], pool_pre_ping=True)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Create tables and seed starter data
    with app.app_context():
        Base.metadata.create_all(bind=engine)
        session = db_session()
        try:
            seed_database(session)
        except Exception as e:
            session.rollback()
            print(f"[!] Warning while seeding database: {e}")
        finally:
            session.close()

    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()

    def get_session():
        return db_session()

    # 3. Register Blueprints
    app.register_blueprint(swagger_bp)
    app.register_blueprint(create_auth_blueprint(get_session))
    app.register_blueprint(create_event_blueprint(get_session))
    app.register_blueprint(create_alert_blueprint(get_session))
    app.register_blueprint(create_incident_blueprint(get_session))
    app.register_blueprint(create_device_blueprint(get_session))
    app.register_blueprint(create_dashboard_blueprint(get_session))
    app.register_blueprint(create_blocked_ip_blueprint(get_session))
    app.register_blueprint(create_user_blueprint(get_session))

    # 4. Security Hardening Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # 5. Health Check & Root Route
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "service": "Real-Time Cybersecurity Threat Monitoring & Incident Response System",
            "database": "connected",
            "cloud_ready": True
        }), 200

    # Serve static frontend or informative SOC landing portal
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, path)) and path != "":
            return send_from_directory(app.static_folder, path)
        elif app.static_folder and os.path.exists(os.path.join(app.static_folder, "index.html")):
            return send_from_directory(app.static_folder, "index.html")
        else:
            # Fallback redirect to API documentation and system status
            return jsonify({
                "system": "Real-Time Cybersecurity Threat Monitoring and Incident Response Platform",
                "status": "Operational",
                "api_docs": "/api/docs",
                "health_check": "/api/health",
                "instructions": "Visit /api/docs for interactive Swagger UI, or start the React frontend dashboard."
            }), 200

    # 6. Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "error", "message": "Internal server error occurred."}), 500

    return app


# WSGI Application entry for Gunicorn: gunicorn app:app
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[*] Cybersecurity SOC Platform backend listening on http://{host}:{port}")
    print(f"[*] Interactive Swagger API documentation: http://localhost:{port}/api/docs")
    app.run(host=host, port=port, debug=False)
