import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import Modal from '../components/Modal';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [newDeviceId, setNewDeviceId] = useState('');
  const [newDeviceName, setNewDeviceName] = useState('');
  const [newOsType, setNewOsType] = useState('Windows 11');
  const [createdKey, setCreatedKey] = useState(null);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      const res = await api.devices.list();
      setDevices(res.devices || []);
    } catch (err) {
      console.error('Failed to load devices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await api.devices.register({
        id: newDeviceId || undefined,
        device_name: newDeviceName || 'Monitored External Laptop',
        os_type: newOsType
      });
      setCreatedKey(res);
      fetchDevices();
    } catch (err) {
      alert(`Registration failed: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to remove device ${id}?`)) return;
    try {
      await api.devices.delete(id);
      fetchDevices();
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Monitored External Endpoints</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Asset registry of external laptops, VMs, and servers reporting security telemetry
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary btn-sm" onClick={fetchDevices}>
            ↻ Refresh Fleet
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => { setCreatedKey(null); setIsRegisterOpen(true); }}>
            + Register New Device
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Device ID</th>
                <th>Host Name / Label</th>
                <th>Operating System</th>
                <th>Reported IP Address</th>
                <th>Device Token</th>
                <th>Last Heartbeat</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading devices fleet...
                  </td>
                </tr>
              ) : devices.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No devices registered. Click "+ Register New Device" above.
                  </td>
                </tr>
              ) : (
                devices.map((d) => (
                  <tr key={d.id}>
                    <td>
                      <span className={`badge ${d.status === 'ONLINE' ? 'badge-online' : 'badge-offline'}`}>
                        {d.status === 'ONLINE' && <span className="pulse-dot" style={{ marginRight: '4px' }}></span>}
                        {d.status}
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{d.id}</td>
                    <td style={{ fontWeight: 600 }}>{d.device_name}</td>
                    <td>{d.os_type}</td>
                    <td className="mono">{d.ip_address}</td>
                    <td className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {d.api_key.slice(0, 14)}...
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {d.last_seen ? new Date(d.last_seen).toLocaleTimeString() : 'Never'}
                    </td>
                    <td>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(d.id)}>
                        Remove
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Register Device Modal */}
      <Modal
        isOpen={isRegisterOpen}
        title="Register External Monitoring Endpoint"
        onClose={() => setIsRegisterOpen(false)}
      >
        {!createdKey ? (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="form-label">Custom Device ID (Optional)</label>
              <input
                type="text"
                className="form-input"
                value={newDeviceId}
                onChange={(e) => setNewDeviceId(e.target.value)}
                placeholder="e.g. STUDENT-LAPTOP-01"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Device Display Name</label>
              <input
                type="text"
                className="form-input"
                value={newDeviceName}
                onChange={(e) => setNewDeviceName(e.target.value)}
                placeholder="e.g. Dell XPS 15 (External Sensor)"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Operating System</label>
              <select
                className="form-select"
                value={newOsType}
                onChange={(e) => setNewOsType(e.target.value)}
              >
                <option value="Windows 11">Windows 11</option>
                <option value="Windows 10">Windows 10</option>
                <option value="Ubuntu 24.04 Linux">Ubuntu 24.04 Linux</option>
                <option value="Kali Linux 2024">Kali Linux 2024</option>
                <option value="macOS Sonoma">macOS Sonoma</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
              Register & Generate API Key
            </button>
          </form>
        ) : (
          <div>
            <div style={{
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              color: '#10b981',
              padding: '1rem',
              borderRadius: '8px',
              marginBottom: '1rem'
            }}>
              ✓ Device successfully registered!
            </div>

            <div className="form-group">
              <label className="form-label">Device Token / API Key (Copy this for agent.py):</label>
              <input
                type="text"
                className="form-input mono"
                value={createdKey.device_token}
                readOnly
              />
            </div>

            <div style={{ background: '#070b14', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Quick Setup Command for Second Laptop:
              </div>
              <code className="mono" style={{ fontSize: '0.78rem', color: '#38bdf8' }}>
                python security-agent/agent.py
              </code>
            </div>

            <button
              className="btn btn-secondary"
              style={{ width: '100%' }}
              onClick={() => setIsRegisterOpen(false)}
            >
              Done / Close
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
}
