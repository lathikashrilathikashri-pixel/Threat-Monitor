"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Interactive Swagger / OpenAPI Documentation
FILE: backend/swagger.py
===================================================================================
WHAT THIS FILE DOES:
    Provides an interactive Swagger UI portal accessible directly at /api/docs.
    Serves the complete OpenAPI 3.0 schema at /api/openapi.json detailing all 
    authentication schemes, request schemas, parameters, and responses.

WHY IT IS REQUIRED:
    Essential academic evaluation requirement. Allows college evaluators and external
    developers to test, verify, and understand the REST API without installing Postman.

HOW IT CONNECTS TO OTHER MODULES:
    - Registered as a blueprint in backend/app.py.
    - Documents every route in backend/routes/.
===================================================================================
"""

from flask import Blueprint, jsonify, render_template_string

swagger_bp = Blueprint("swagger", __name__, url_prefix="/api")

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Real-Time Cybersecurity Threat Monitoring & Incident Response API",
        "description": "SOC REST API for external telemetry ingestion, rule-based threat detection, automated alert triage, and incident response management.",
        "version": "1.0.0",
        "contact": {
            "name": "SOC Cyber Defense Operations",
            "email": "security@soc-platform.local"
        }
    },
    "servers": [
        {"url": "/", "description": "Current Server (Local or Cloud)"}
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your JWT token obtained from /api/auth/login"
            },
            "DeviceTokenAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Device-Token",
                "description": "Device API key for external Python security agents"
            }
        }
    },
    "paths": {
        "/api/auth/register": {
            "post": {
                "summary": "Register a new user",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "example": "analyst1"},
                                    "email": {"type": "string", "example": "analyst1@defense.org"},
                                    "password": {"type": "string", "example": "DefensePass2026!"},
                                    "role": {"type": "string", "example": "Security Analyst", "enum": ["Admin", "Security Analyst", "User"]}
                                },
                                "required": ["username", "email", "password"]
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "User registered"}}
            }
        },
        "/api/auth/login": {
            "post": {
                "summary": "Authenticate and obtain JWT",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "example": "admin"},
                                    "password": {"type": "string", "example": "AdminSecure2026!"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Authentication successful"}}
            }
        },
        "/api/dashboard/stats": {
            "get": {
                "summary": "Get SOC KPIs, charts, and threat score",
                "tags": ["SOC Dashboard"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "Dashboard telemetry data"}}
            }
        },
        "/api/events": {
            "get": {
                "summary": "List security events",
                "tags": ["Events"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "List of events"}}
            },
            "post": {
                "summary": "Ingest security telemetry from agent or simulation",
                "tags": ["Events"],
                "security": [{"DeviceTokenAuth": []}, {"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "device_id": {"type": "string", "example": "ENDPOINT-LAPTOP-001"},
                                    "event_type": {"type": "string", "example": "FAILED_LOGIN"},
                                    "source_ip": {"type": "string", "example": "192.168.1.45"},
                                    "username": {"type": "string", "example": "root"},
                                    "destination_port": {"type": "integer", "example": 22},
                                    "description": {"type": "string", "example": "Multiple failed SSH authentications"}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Event processed by detection engine"}}
            }
        },
        "/api/alerts": {
            "get": {
                "summary": "List correlated security alerts",
                "tags": ["Alerts"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "List of alerts"}}
            }
        },
        "/api/alerts/{id}/convert-incident": {
            "post": {
                "summary": "Escalate alert to official incident ticket",
                "tags": ["Alerts"],
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"201": {"description": "Incident ticket created"}}
            }
        },
        "/api/incidents": {
            "get": {
                "summary": "List tracked incidents",
                "tags": ["Incidents"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "List of incidents"}}
            }
        },
        "/api/devices": {
            "get": {
                "summary": "List registered monitoring devices",
                "tags": ["Devices"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "List of devices"}}
            },
            "post": {
                "summary": "Register a new external monitoring device",
                "tags": ["Devices"],
                "security": [{"BearerAuth": []}],
                "responses": {"201": {"description": "Device registered and token returned"}}
            }
        },
        "/api/devices/heartbeat": {
            "post": {
                "summary": "Send periodic heartbeat from Python agent",
                "tags": ["Devices"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "device_id": {"type": "string", "example": "ENDPOINT-LAPTOP-001"},
                                    "api_key": {"type": "string", "example": "sec_key_sample"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Heartbeat updated"}}
            }
        },
        "/api/blocked-ips": {
            "get": {
                "summary": "List blacklisted IPs",
                "tags": ["Blocked IPs"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "List of blocked IPs"}}
            },
            "post": {
                "summary": "Add IP address to blacklist",
                "tags": ["Blocked IPs"],
                "security": [{"BearerAuth": []}],
                "responses": {"201": {"description": "IP blacklisted"}}
            }
        }
    }
}

SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cybersecurity Threat Monitoring & Incident Response API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body { margin: 0; background-color: #0f172a; }
        .swagger-ui { background: #0f172a; color: #f8fafc; font-family: Inter, sans-serif; }
        .swagger-ui .topbar { display: none; }
        .swagger-ui .info .title { color: #38bdf8; }
        .swagger-ui .info p, .swagger-ui .info li { color: #94a3b8; }
        .swagger-ui .scheme-container { background: #1e293b; box-shadow: none; border-bottom: 1px solid #334155; }
        .swagger-ui .opblock { border-radius: 8px; border: 1px solid #334155; }
        .swagger-ui .opblock-tag { color: #f1f5f9; border-bottom: 1px solid #334155; }
        .swagger-ui .opblock .opblock-summary-operation-id, 
        .swagger-ui .opblock .opblock-summary-path,
        .swagger-ui .opblock .opblock-summary-description { color: #cbd5e1; }
        .swagger-ui table thead tr th { color: #94a3b8; }
        .swagger-ui .btn.authorize { color: #38bdf8; border-color: #38bdf8; }
        .swagger-ui .btn.authorize svg { fill: #38bdf8; }
        .swagger-ui input[type=text], .swagger-ui textarea { background: #0f172a; color: #f8fafc; border: 1px solid #475569; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout"
            });
        };
    </script>
</body>
</html>
"""

@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Returns the OpenAPI 3.0 specification as JSON."""
    return jsonify(OPENAPI_SPEC)

@swagger_bp.route("/docs", methods=["GET"])
def swagger_docs():
    """Serves the interactive Swagger UI page."""
    return render_template_string(SWAGGER_UI_HTML)
