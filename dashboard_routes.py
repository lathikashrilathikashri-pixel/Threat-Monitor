"""
===================================================================================
PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
MODULE: SOC Dashboard Aggregation Routes
FILE: backend/routes/dashboard_routes.py
===================================================================================
WHAT THIS FILE DOES:
    Provides high-performance aggregated metrics, risk KPIs, and time-series data
    for the real-time SOC command dashboard:
    - GET /api/dashboard/stats : Returns live metrics, threat distributions, 
                                 fleet status, and recent security events.

WHY IT IS REQUIRED:
    Powers the SOC dashboard visualization, enabling security analysts to spot
    anomalies at a glance without making dozens of fragmented database calls.

HOW IT CONNECTS TO OTHER MODULES:
    - Aggregates data from SecurityEvent, Alert, Incident, Device, LoginAttempt, 
      and BlockedIP tables in backend/models.py.
    - Consumed by React frontend Dashboard page (pages/Dashboard.jsx) and charts.
===================================================================================
"""

from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify
from sqlalchemy import func
from models import SecurityEvent, Alert, Incident, Device, LoginAttempt, BlockedIP
from middleware import jwt_required

def create_dashboard_blueprint(get_db_session):
    dash_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

    @dash_bp.route("/stats", methods=["GET"])
    @jwt_required
    def get_dashboard_stats():
        """Aggregates all SOC metrics for the visual dashboard."""
        session = get_db_session()

        # 1. Event & Alert KPI Counters
        total_events = session.query(func.count(SecurityEvent.id)).scalar() or 0
        critical_alerts = session.query(func.count(Alert.id)).filter(Alert.severity == "CRITICAL", Alert.status != "RESOLVED").scalar() or 0
        high_alerts = session.query(func.count(Alert.id)).filter(Alert.severity == "HIGH", Alert.status != "RESOLVED").scalar() or 0
        medium_alerts = session.query(func.count(Alert.id)).filter(Alert.severity == "MEDIUM", Alert.status != "RESOLVED").scalar() or 0
        low_events = session.query(func.count(SecurityEvent.id)).filter(SecurityEvent.severity == "LOW").scalar() or 0

        # 2. Incident & Fleet Counters
        active_incidents = session.query(func.count(Incident.id)).filter(Incident.status.in_(["OPEN", "INVESTIGATING", "CONTAINED"])).scalar() or 0
        total_devices = session.query(func.count(Device.id)).scalar() or 0
        
        # Calculate online devices (heartbeat in last 3 minutes)
        three_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=3)
        online_devices = session.query(func.count(Device.id)).filter(Device.last_seen >= three_mins_ago).scalar() or 0

        # 3. Failed Logins & Threat Scores
        failed_logins = session.query(func.count(LoginAttempt.id)).filter(LoginAttempt.success == False).scalar() or 0
        blocked_ips_count = session.query(func.count(BlockedIP.id)).filter(BlockedIP.is_active == True).scalar() or 0

        # Calculate systemic risk score (1-10)
        overall_threat_score = 1
        if critical_alerts > 0:
            overall_threat_score = 9 + min(1, critical_alerts * 0.1)
        elif high_alerts > 0:
            overall_threat_score = 7 + min(1.5, high_alerts * 0.2)
        elif medium_alerts > 0:
            overall_threat_score = 4 + min(2, medium_alerts * 0.2)
        elif failed_logins > 5:
            overall_threat_score = 3
        overall_threat_score = round(min(10.0, float(overall_threat_score)), 1)

        # 4. Severity Distribution (for Pie/Donut Chart)
        severity_dist = [
            {"name": "CRITICAL", "value": critical_alerts, "color": "#ef4444"},
            {"name": "HIGH", "value": high_alerts, "color": "#f97316"},
            {"name": "MEDIUM", "value": medium_alerts, "color": "#eab308"},
            {"name": "LOW", "value": max(1, low_events), "color": "#3b82f6"}
        ]

        # 5. Event Type Distribution (for Bar Chart)
        type_counts = (
            session.query(SecurityEvent.event_type, func.count(SecurityEvent.id))
            .group_by(SecurityEvent.event_type)
            .order_by(func.count(SecurityEvent.id).desc())
            .limit(6)
            .all()
        )
        event_types = [{"name": row[0], "count": row[1]} for row in type_counts]
        if not event_types:
            event_types = [
                {"name": "FAILED_LOGIN", "count": failed_logins},
                {"name": "PORT_SCAN", "count": 0},
                {"name": "PROCESS_ANOMALY", "count": 0}
            ]

        # 6. Events Over Time (hourly or daily buckets for Timeline Chart)
        events_timeline = []
        now = datetime.now(timezone.utc)
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_count = (
                session.query(func.count(SecurityEvent.id))
                .filter(SecurityEvent.timestamp >= day_start, SecurityEvent.timestamp < day_end)
                .scalar() or 0
            )
            events_timeline.append({
                "time": day_start.strftime("%b %d"),
                "events": day_count
            })

        # 7. Recent Alerts (latest 5)
        recent_alerts = (
            session.query(Alert)
            .order_by(Alert.created_at.desc())
            .limit(5)
            .all()
        )

        # 8. Recent Events (latest 5)
        recent_events = (
            session.query(SecurityEvent)
            .order_by(SecurityEvent.timestamp.desc())
            .limit(5)
            .all()
        )

        return jsonify({
            "status": "success",
            "kpis": {
                "total_events": total_events,
                "critical_alerts": critical_alerts,
                "high_alerts": high_alerts,
                "medium_alerts": medium_alerts,
                "low_events": low_events,
                "active_incidents": active_incidents,
                "online_devices": online_devices,
                "total_devices": total_devices,
                "failed_login_attempts": failed_logins,
                "blocked_ips_count": blocked_ips_count,
                "overall_threat_score": overall_threat_score
            },
            "charts": {
                "severity_distribution": severity_dist,
                "event_type_distribution": event_types,
                "events_over_time": events_timeline
            },
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "recent_events": [e.to_dict() for e in recent_events]
        }), 200

    return dash_bp
