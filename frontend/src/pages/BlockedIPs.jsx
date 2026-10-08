import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Modal from '../components/Modal';

export default function BlockedIPs() {
  const [blockedList, setBlockedList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [ipAddress, setIpAddress] = useState('');
  const [reason, setReason] = useState('');

  const fetchBlocked = async () => {
    try {
      setLoading(true);
      const res = await api.blockedIps.list();
      setBlockedList(res.blocked_ips || []);
    } catch (err) {
      console.error('Failed to load blacklist:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBlocked();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await api.blockedIps.add(ipAddress, reason);
      setIsAddOpen(false);
      setIpAddress('');
      setReason('');
      fetchBlocked();
    } catch (err) {
      alert(`Blacklist addition failed: ${err.message}`);
    }
  };

  const handleRemove = async (id, ip) => {
    if (!window.confirm(`Unblock IP address ${ip}?`)) return;
    try {
      await api.blockedIps.remove(id);
      fetchBlocked();
    } catch (err) {
      alert(`Unblock failed: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Perimeter Blacklist & Blocked IPs</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Active network containment list. Any telemetry from blacklisted IPs triggers immediate CRITICAL alert.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary btn-sm" onClick={fetchBlocked}>
            ↻ Refresh
          </button>
          <button className="btn btn-danger btn-sm" onClick={() => setIsAddOpen(true)}>
            + Blacklist Malicious IP
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Blacklisted IP</th>
                <th>Justification / Reason</th>
                <th>Enforcing Analyst</th>
                <th>Status</th>
                <th>Blocked At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading perimeter blacklist...
                  </td>
                </tr>
              ) : blockedList.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No IPs currently blacklisted.
                  </td>
                </tr>
              ) : (
                blockedList.map((item) => (
                  <tr key={item.id}>
                    <td className="mono" style={{ color: '#ef4444', fontWeight: 700 }}>{item.ip_address}</td>
                    <td>{item.reason}</td>
                    <td>🛡️ {item.blocked_by}</td>
                    <td>
                      <span className="badge badge-critical">ACTIVE DEFENSE</span>
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" onClick={() => handleRemove(item.id, item.ip_address)}>
                        Unblock IP
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add IP Modal */}
      <Modal
        isOpen={isAddOpen}
        title="Add Malicious IP to Perimeter Blacklist"
        onClose={() => setIsAddOpen(false)}
      >
        <form onSubmit={handleAdd}>
          <div className="form-group">
            <label className="form-label">Malicious IP Address (IPv4)</label>
            <input
              type="text"
              className="form-input mono"
              value={ipAddress}
              onChange={(e) => setIpAddress(e.target.value)}
              placeholder="e.g. 198.51.100.99"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Blocking Justification / Threat Intel Reason</label>
            <textarea
              className="form-textarea"
              rows="3"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Repeated SSH brute force attacks observed targeting port 22..."
              required
            ></textarea>
          </div>

          <button type="submit" className="btn btn-danger" style={{ width: '100%' }}>
            Enforce IP Block
          </button>
        </form>
      </Modal>
    </div>
  );
}
