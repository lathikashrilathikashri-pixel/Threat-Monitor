import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';
import Modal from '../components/Modal';

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Form states for updating incident
  const [editStatus, setEditStatus] = useState('');
  const [editAnalyst, setEditAnalyst] = useState('');
  const [editNotes, setEditNotes] = useState('');

  // Form state for creating new incident
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSev, setNewSev] = useState('HIGH');

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const res = await api.incidents.list();
      setIncidents(res.incidents || []);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const openEditModal = (inc) => {
    setSelectedIncident(inc);
    setEditStatus(inc.status);
    setEditAnalyst(inc.assigned_analyst || '');
    setEditNotes(inc.resolution_notes || '');
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!selectedIncident) return;
    try {
      await api.incidents.update(selectedIncident.id, {
        status: editStatus,
        assigned_analyst: editAnalyst,
        resolution_notes: editNotes
      });
      setSelectedIncident(null);
      fetchIncidents();
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.incidents.create({
        title: newTitle,
        description: newDesc,
        severity: newSev
      });
      setIsCreateOpen(false);
      setNewTitle('');
      setNewDesc('');
      fetchIncidents();
    } catch (err) {
      alert(`Creation failed: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Cybersecurity Incident Response Tickets</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Containment, forensic investigation, and eradication lifecycle management
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary btn-sm" onClick={fetchIncidents}>
            ↻ Refresh
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setIsCreateOpen(true)}>
            + Create New Incident
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Assigned Analyst</th>
                <th>Origin / Source</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading incidents...
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No open incidents. Escalate high-risk alerts from the Alerts tab.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr key={inc.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{inc.id}</td>
                    <td style={{ fontWeight: 600 }}>{inc.title}</td>
                    <td><SeverityBadge severity={inc.severity} /></td>
                    <td>
                      <span className={`badge ${
                        inc.status === 'RESOLVED' ? 'badge-online' :
                        inc.status === 'CONTAINED' ? 'badge-medium' :
                        inc.status === 'INVESTIGATING' ? 'badge-high' : 'badge-critical'
                      }`}>
                        {inc.status}
                      </span>
                    </td>
                    <td>👤 {inc.assigned_analyst || 'Unassigned'}</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{inc.source}</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {inc.created_at ? new Date(inc.created_at).toLocaleDateString() : 'Recent'}
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" onClick={() => openEditModal(inc)}>
                        Manage / Notes
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Incident & Forensics Modal */}
      <Modal
        isOpen={!!selectedIncident}
        title={`Incident Ticket: ${selectedIncident?.id}`}
        onClose={() => setSelectedIncident(null)}
      >
        {selectedIncident && (
          <form onSubmit={handleUpdate}>
            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>{selectedIncident.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {selectedIncident.description}
              </p>
            </div>

            <div className="form-group">
              <label className="form-label">Incident Lifecycle Status</label>
              <select
                className="form-select"
                value={editStatus}
                onChange={(e) => setEditStatus(e.target.value)}
              >
                <option value="OPEN">OPEN (Initial Triage)</option>
                <option value="INVESTIGATING">INVESTIGATING (Forensic Analysis)</option>
                <option value="CONTAINED">CONTAINED (Threat Isolated / Quarantined)</option>
                <option value="RESOLVED">RESOLVED (Eradicated & Closed)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Lead Assigned Analyst</label>
              <input
                type="text"
                className="form-input"
                value={editAnalyst}
                onChange={(e) => setEditAnalyst(e.target.value)}
                placeholder="e.g. analyst1"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Forensic Resolution & Remediation Notes</label>
              <textarea
                className="form-textarea"
                rows="4"
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                placeholder="Document quarantine steps, compromised artifacts, host memory findings, and firewall rules added..."
              ></textarea>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
              Save Incident Updates
            </button>
          </form>
        )}
      </Modal>

      {/* Create New Incident Modal */}
      <Modal
        isOpen={isCreateOpen}
        title="Create New Cybersecurity Incident Ticket"
        onClose={() => setIsCreateOpen(false)}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">Incident Title</label>
            <input
              type="text"
              className="form-input"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Host Compromise on External ThinkPad"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Incident Severity</label>
            <select
              className="form-select"
              value={newSev}
              onChange={(e) => setNewSev(e.target.value)}
            >
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Detailed Incident Description</label>
            <textarea
              className="form-textarea"
              rows="3"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Describe attack indicators, affected hosts, and observed behavior..."
              required
            ></textarea>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
            Submit Incident Ticket
          </button>
        </form>
      </Modal>
    </div>
  );
}
