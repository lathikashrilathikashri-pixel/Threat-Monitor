"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: Backend Configuration
FILE: backend/config.py
===================================================================================
WHAT THIS FILE DOES:
    Centralizes all configuration variables for the Flask backend. It dynamically 
    reads environment variables (such as DATABASE_URL, JWT_SECRET, CORS_ORIGINS) 
    and provides sane, secure defaults for both local development and cloud 
    production deployments (e.g. Render, Railway, Neon, Supabase).

WHY IT IS REQUIRED:
    1. Separation of Concerns: Secrets and deployment URLs should never be hard-coded 
       into logic files.
    2. Cloud Portability: Allows 1-click cloud deployment without modifying source code.
    3. Security Hardening: Enforces JWT expiration, CORS policy, and secret key controls.

HOW IT CONNECTS TO OTHER MODULES:
    - Imported by app.py to initialize Flask extensions, database engine, and CORS.
    - Uses .env file via python-dotenv if present.
===================================================================================
"""

import os
from datetime import timedelta

class Config:
    """Base application configuration."""
    
    # Secret key for signing sessions and cryptographic tokens
    SECRET_KEY = os.environ.get("API_SECRET") or os.environ.get("SECRET_KEY") or "cyber-soc-super-secret-key-2026-production"

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET") or "jwt-defense-guard-token-secret-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # Database Configuration:
    # Defaults to PostgreSQL when DATABASE_URL is set in cloud (e.g., Render/Railway/Neon).
    # Gracefully falls back to local SQLite so the project runs immediately without requiring local Postgres installation.
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url:
        # SQLAlchemy 1.4+ requires 'postgresql://' instead of legacy 'postgres://' supplied by some cloud providers
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        # Local fallback database
        SQLALCHEMY_DATABASE_URI = "sqlite:///cyber_soc.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS Allowed Origins (Comma-separated for cloud environments, or '*' for unrestricted)
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Threat Detection Engine Thresholds (Configurable SOC rules)
    BRUTE_FORCE_WINDOW_MINUTES = int(os.environ.get("BRUTE_FORCE_WINDOW_MINUTES", 5))
    BRUTE_FORCE_MAX_FAILURES = int(os.environ.get("BRUTE_FORCE_MAX_FAILURES", 5))
    PORT_SCAN_PORT_THRESHOLD = int(os.environ.get("PORT_SCAN_PORT_THRESHOLD", 5))
    PORT_SCAN_WINDOW_MINUTES = int(os.environ.get("PORT_SCAN_WINDOW_MINUTES", 3))

    # Known suspicious process names monitored on external endpoints
    SUSPICIOUS_PROCESS_NAMES = [
        "mimikatz.exe", "netcat", "nc.exe", "nmap", "wireshark.exe",
        "keylogger", "pwdump", "hydra", "metasploit", "meterpreter"
    ]


class ProductionConfig(Config):
    """Production cloud configuration."""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Local development configuration."""
    DEBUG = True
    TESTING = False


# Active configuration mapping
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig if os.environ.get("FLASK_ENV") != "production" else ProductionConfig
}
