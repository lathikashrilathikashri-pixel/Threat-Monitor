import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import SeverityBadge from '../components/SeverityBadge';
import Modal from '../components/Modal';

export default function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterType, setFilterType] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      let query = '?limit=100';
      if (filterSeverity) query += `&severity=${filterSeverity}`;
      if (filterType) query += `&event_type=${filterType}`;

      const res = await api.events.list(query);
      setEvents(res.events || []);
    } catch (err) {
      console.error('Failed to load events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [filterSeverity, filterType]);

  const filteredEvents = events.filter((e) => {
    const s = searchTerm.toLowerCase();
    return (
      (e.source_ip && e.source_ip.toLowerCase().includes(s)) ||
      (e.device_id && e.device_id.toLowerCase().includes(s)) ||
      (e.event_type && e.event_type.toLowerCase().includes(s)) ||
      (e.description && e.description.toLowerCase().includes(s)) ||
      (e.username && e.username.toLowerCase().includes(s))
    );
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Telemetry Security Events</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Real-time audit stream ingested from external endpoint agents
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchEvents}>
          ↻ Refresh Stream
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            className="form-input"
            style={{ flex: 2, minWidth: '220px' }}
            placeholder="🔍 Search by IP, device, user, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            className="form-select"
            style={{ flex: 1, minWidth: '150px' }}
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            className="form-select"
            style={{ flex: 1, minWidth: '180px' }}
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">All Event Types</option>
            <option value="FAILED_LOGIN">Failed Logins</option>
            <option value="PORT_SCAN_ATTEMPT">Port Scans</option>
            <option value="SUSPICIOUS_PROCESS">Suspicious Process</option>
            <option value="BLOCKED_IP_ACCESS">Blocked IP Access</option>
            <option value="SYSTEM_HEARTBEAT">Heartbeat Telemetry</option>
          </select>
        </div>
      </div>

      {/* Events Table */}
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Device ID</th>
                <th>Event Type</th>
                <th>Source IP</th>
                <th>Target / User</th>
                <th>Verified Severity</th>
                <th>Description</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading security events...
                  </td>
                </tr>
              ) : filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No events match current filter.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => (
                  <tr key={evt.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>#{evt.id}</td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
                      {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>{evt.device_id || 'EXTERNAL'}</td>
                    <td><span className="mono" style={{ fontWeight: 700, fontSize: '0.8rem' }}>{evt.event_type}</span></td>
                    <td className="mono">{evt.source_ip}</td>
                    <td>{evt.username || (evt.destination_port ? `Port ${evt.destination_port}` : 'N/A')}</td>
                    <td><SeverityBadge severity={evt.severity} /></td>
                    <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {evt.description}
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" onClick={() => setSelectedEvent(evt)}>
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Event Details Inspection Modal */}
      <Modal
        isOpen={!!selectedEvent}
        title={`Telemetry Event #${selectedEvent?.id} Inspection`}
        onClose={() => setSelectedEvent(null)}
      >
        {selectedEvent && (
          <div>
            <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <SeverityBadge severity={selectedEvent.severity} />
              <span className="mono" style={{ fontWeight: 700 }}>{selectedEvent.event_type}</span>
            </div>
            <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>{selectedEvent.description}</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <div><strong>Device:</strong> {selectedEvent.device_id || 'External Host'}</div>
              <div><strong>Source IP:</strong> <code className="mono">{selectedEvent.source_ip}</code></div>
              <div><strong>User:</strong> {selectedEvent.username || 'N/A'}</div>
              <div><strong>Dest Port:</strong> {selectedEvent.destination_port || 'N/A'}</div>
              <div><strong>Process:</strong> {selectedEvent.process_name || 'N/A'}</div>
              <div><strong>Logged At:</strong> {new Date(selectedEvent.timestamp).toLocaleString()}</div>
            </div>

            {selectedEvent.raw_data && (
              <div>
                <label className="form-label">Raw Telemetry JSON Payload:</label>
                <pre style={{
                  background: '#070b14',
                  padding: '1rem',
                  borderRadius: '8px',
                  fontSize: '0.75rem',
                  overflowX: 'auto',
                  border: '1px solid var(--border-subtle)'
                }}>
                  {typeof selectedEvent.raw_data === 'string'
                    ? selectedEvent.raw_data
                    : JSON.stringify(selectedEvent.raw_data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
