import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';

export default function Alerts({ onNavigateToIncidents }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [actionMessage, setActionMessage] = useState('');

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      let query = '?limit=100';
      if (statusFilter) query += `&status=${statusFilter}`;
      if (severityFilter) query += `&severity=${severityFilter}`;

      const res = await api.alerts.list(query);
      setAlerts(res.alerts || []);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const handleUpdateStatus = async (alertId, newStatus) => {
    try {
      await api.alerts.updateStatus(alertId, newStatus);
      setActionMessage(`Alert #${alertId} status updated to ${newStatus}.`);
      fetchAlerts();
      setTimeout(() => setActionMessage(''), 4000);
    } catch (err) {
      alert(`Error updating alert: ${err.message}`);
    }
  };

  const handleConvertToIncident = async (alertId) => {
    try {
      const res = await api.alerts.convertToIncident(alertId);
      setActionMessage(`Alert #${alertId} successfully escalated to ${res.incident.id}!`);
      fetchAlerts();
      setTimeout(() => {
        setActionMessage('');
        if (onNavigateToIncidents) onNavigateToIncidents();
      }, 2500);
    } catch (err) {
      alert(`Error escalating alert: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Correlated Security Alerts & Triage</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Threats prioritized by multi-factor risk scoring engine
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchAlerts}>
          ↻ Refresh Alerts
        </button>
      </div>

      {actionMessage && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#10b981',
          padding: '0.85rem 1.25rem',
          borderRadius: '8px',
          fontSize: '0.85rem',
          marginBottom: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          🛡️ {actionMessage}
        </div>
      )}

      {/* Filter Header */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <select
            className="form-select"
            style={{ flex: 1, minWidth: '180px' }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Alert Statuses</option>
            <option value="NEW">New (Unreviewed)</option>
            <option value="INVESTIGATING">Under Investigation</option>
            <option value="RESOLVED">Resolved</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>

          <select
            className="form-select"
            style={{ flex: 1, minWidth: '180px' }}
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical (Score 9-10)</option>
            <option value="HIGH">High (Score 7-8)</option>
            <option value="MEDIUM">Medium (Score 4-6)</option>
            <option value="LOW">Low (Score 1-3)</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Alert</th>
                <th>Classification</th>
                <th>Severity</th>
                <th>Risk Score</th>
                <th>Source IP</th>
                <th>Target Device</th>
                <th>Status</th>
                <th>Description</th>
                <th>Triage Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading security alerts...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No alerts found for current criteria.
                  </td>
                </tr>
              ) : (
                alerts.map((a) => (
                  <tr key={a.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>#{a.id}</td>
                    <td style={{ fontWeight: 700 }}>{a.alert_type}</td>
                    <td><SeverityBadge severity={a.severity} /></td>
                    <td>
                      <span className="mono" style={{
                        fontWeight: 800,
                        fontSize: '0.9rem',
                        color: a.risk_score >= 8 ? '#ef4444' : a.risk_score >= 6 ? '#f97316' : '#38bdf8'
                      }}>
                        {a.risk_score}/10
                      </span>
                    </td>
                    <td className="mono">{a.source_ip}</td>
                    <td>{a.device_id || 'Gateway'}</td>
                    <td>
                      <select
                        className="form-select"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', width: 'auto' }}
                        value={a.status}
                        onChange={(e) => handleUpdateStatus(a.id, e.target.value)}
                      >
                        <option value="NEW">NEW</option>
                        <option value="INVESTIGATING">INVESTIGATING</option>
                        <option value="RESOLVED">RESOLVED</option>
                        <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
                      </select>
                    </td>
                    <td style={{ maxWidth: '280px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {a.description}
                    </td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleConvertToIncident(a.id)}
                        title="Escalate alert to official incident investigation"
                      >
                        ⚡ Escalate →
                      </button>
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
