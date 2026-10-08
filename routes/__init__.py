"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Route Handlers Package
FILE: backend/routes/__init__.py
===================================================================================
WHAT THIS FILE DOES:
    Initializes the routes package and exports all blueprint factory functions:
    - create_auth_blueprint
    - create_event_blueprint
    - create_alert_blueprint
    - create_incident_blueprint
    - create_device_blueprint
    - create_dashboard_blueprint
    - create_blocked_ip_blueprint
    - create_user_blueprint

WHY IT IS REQUIRED:
    Makes backend/routes a recognized Python package that can be imported both as
    'from routes.auth_routes import ...' and 'from routes import create_auth_blueprint'.
    Guarantees compatibility in all WSGI environments (local, Docker, Render).
===================================================================================
"""

from .auth_routes import create_auth_blueprint
from .event_routes import create_event_blueprint
from .alert_routes import create_alert_blueprint
from .incident_routes import create_incident_blueprint
from .device_routes import create_device_blueprint
from .dashboard_routes import create_dashboard_blueprint
from .blocked_ip_routes import create_blocked_ip_blueprint
from .user_routes import create_user_blueprint

__all__ = [
    "create_auth_blueprint",
    "create_event_blueprint",
    "create_alert_blueprint",
    "create_incident_blueprint",
    "create_device_blueprint",
    "create_dashboard_blueprint",
    "create_blocked_ip_blueprint",
    "create_user_blueprint",
]
