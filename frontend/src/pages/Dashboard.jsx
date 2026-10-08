import React from 'react';
import StatCard from '../components/StatCard';
import SeverityBadge from '../components/SeverityBadge';

export default function Dashboard({ stats, onNavigateToAlerts, onNavigateToEvents, onNavigateToIncidents }) {
  const kpis = stats?.kpis || {
    total_events: 0,
    critical_alerts: 0,
    high_alerts: 0,
    medium_alerts: 0,
    low_events: 0,
    active_incidents: 0,
    online_devices: 0,
    total_devices: 0,
    failed_login_attempts: 0,
    blocked_ips_count: 0,
    overall_threat_score: 1.0
  };

  const threatScore = kpis.overall_threat_score || 1.0;
  let scoreColor = '#10b981';
  let threatLevelText = 'LOW THREAT LEVEL';
  let threatDesc = 'System status is normal. Standard baseline telemetry reported.';

  if (threatScore >= 9) {
    scoreColor = '#ef4444';
    threatLevelText = 'CRITICAL THREAT LEVEL';
    threatDesc = 'ACTIVE INTRUSION DETECTED! Immediate incident response containment required.';
  } else if (threatScore >= 7) {
    scoreColor = '#f97316';
    threatLevelText = 'HIGH RISK LEVEL';
    threatDesc = 'Multiple high-risk attack indicators identified (Brute Force or Port Scan).';
  } else if (threatScore >= 4) {
    scoreColor = '#eab308';
    threatLevelText = 'ELEVATED MONITORING';
    threatDesc = 'Anomalous telemetry detected. Security analysts advised to triage alerts.';
  }

  const timeline = stats?.charts?.events_over_time || [];
  const maxEvents = Math.max(1, ...timeline.map((t) => t.events));

  const severityDist = stats?.charts?.severity_distribution || [];
  const eventTypes = stats?.charts?.event_type_distribution || [];

  return (
    <div>
      {/* 1. Threat Score Banner */}
      <div className="threat-meter-banner">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: scoreColor
            }}>
              ● {threatLevelText}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>| AI & Rule Correlation Engine</span>
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '0.35rem' }}>
            Real-Time Cyber Threat Exposure Index
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '650px' }}>
            {threatDesc}
          </p>
        </div>

        <div className="threat-score-pill">
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
              Calculated Score
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 800, color: scoreColor }}>
              Scale: 1 — 10
            </div>
          </div>
          <div className="score-circle" style={{ borderColor: scoreColor, color: scoreColor, background: 'rgba(0,0,0,0.3)' }}>
            {threatScore}
          </div>
        </div>
      </div>

      {/* 2. Top Metric KPI Grid */}
      <div className="grid-4">
        <StatCard
          title="Total Events Ingested"
          value={kpis.total_events}
          subtitle="Real-time log ingestion stream"
          icon="📜"
        />
        <StatCard
          title="Critical Alerts"
          value={kpis.critical_alerts}
          subtitle="Immediate containment priority"
          icon="🚨"
          type={kpis.critical_alerts > 0 ? 'critical' : 'normal'}
        />
        <StatCard
          title="High Severity Threats"
          value={kpis.high_alerts}
          subtitle="Brute force & port scan detections"
          icon="⚠️"
          type={kpis.high_alerts > 0 ? 'high' : 'normal'}
        />
        <StatCard
          title="Active Incidents"
          value={kpis.active_incidents}
          subtitle="Open investigation tickets"
          icon="🛡️"
          type={kpis.active_incidents > 0 ? 'high' : 'normal'}
        />
        <StatCard
          title="Monitored Devices"
          value={`${kpis.online_devices} / ${kpis.total_devices}`}
          subtitle="Endpoints currently online"
          icon="💻"
          type="success"
        />
        <StatCard
          title="Failed Logins"
          value={kpis.failed_login_attempts}
          subtitle="Authentication anomalies recorded"
          icon="🔐"
          type={kpis.failed_login_attempts > 5 ? 'high' : 'normal'}
        />
        <StatCard
          title="Blacklisted IPs"
          value={kpis.blocked_ips_count}
          subtitle="Perimeter firewall blacklist"
          icon="⛔"
        />
        <StatCard
          title="Medium / Low Events"
          value={kpis.medium_alerts + kpis.low_events}
          subtitle="Baseline operational telemetry"
          icon="📊"
        />
      </div>

      {/* 3. Visual Charts Grid */}
      <div className="grid-2">
        {/* Events Timeline */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Telemetry Events Ingestion Timeline</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Past 7 Days</span>
          </div>
          <div className="chart-container">
            {timeline.map((item, idx) => {
              const heightPct = Math.round((item.events / maxEvents) * 100);
              return (
                <div key={idx} className="bar-col">
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 700 }}>
                    {item.events}
                  </div>
                  <div
                    className="bar-fill"
                    style={{ height: `${Math.max(8, heightPct * 1.5)}px` }}
                  ></div>
                  <div className="bar-label">{item.time}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Threat Severity Distribution */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Threat Severity Breakdown</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Engine Correlated</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', paddingTop: '0.5rem' }}>
            {severityDist.map((s, idx) => {
              const totalSev = severityDist.reduce((acc, curr) => acc + curr.value, 0) || 1;
              const pct = Math.round((s.value / totalSev) * 100);
              return (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 700, color: s.color }}>{s.name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{s.value} alerts ({pct}%)</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: s.color, borderRadius: '4px', transition: 'width 0.5s' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 4. Recent Correlated Alerts Table */}
      <div className="card" style={{ marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Live Threat Alert Stream</h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Correlated by SOC Detection Engine</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={onNavigateToAlerts}>
            View All Alerts ({stats?.kpis?.critical_alerts + stats?.kpis?.high_alerts} active) →
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Alert Type</th>
                <th>Severity</th>
                <th>Risk Score</th>
                <th>Source IP</th>
                <th>Target Device</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {(!stats?.recent_alerts || stats.recent_alerts.length === 0) ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2rem' }}>
                    No alerts triggered yet. Run <code>python simulate_events.py</code> to test.
                  </td>
                </tr>
              ) : (
                stats.recent_alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>#{alert.id}</td>
                    <td style={{ fontWeight: 700 }}>{alert.alert_type}</td>
                    <td><SeverityBadge severity={alert.severity} /></td>
                    <td>
                      <span className="mono" style={{
                        fontWeight: 800,
                        color: alert.risk_score >= 8 ? '#ef4444' : alert.risk_score >= 6 ? '#f97316' : '#38bdf8'
                      }}>
                        {alert.risk_score}/10
                      </span>
                    </td>
                    <td className="mono">{alert.source_ip}</td>
                    <td>{alert.device_id || 'Network Gateway'}</td>
                    <td>
                      <span className="badge badge-low" style={{ textTransform: 'capitalize' }}>
                        {alert.status.toLowerCase()}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : 'Recent'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
