import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

export default function Users({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.users.list();
      setUsers(res.users || []);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.users.updateRole(userId, newRole);
      fetchUsers();
    } catch (err) {
      alert(`Role change failed: ${err.message}`);
    }
  };

  const isAdmin = currentUser?.role === 'Admin';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>User Accounts & RBAC Governance</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Role-Based Access Control matrix (Admin, Security Analyst, User)
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={fetchUsers}>
          ↻ Refresh Users
        </button>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>User ID</th>
                <th>Username</th>
                <th>Security Email</th>
                <th>Assigned Role</th>
                <th>Account Created</th>
                {isAdmin && <th>Role Governance</th>}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading platform users...
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>#{u.id}</td>
                    <td style={{ fontWeight: 700 }}>{u.username}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`badge ${
                        u.role === 'Admin' ? 'badge-critical' :
                        u.role === 'Security Analyst' ? 'badge-low' : 'badge-medium'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    {isAdmin && (
                      <td>
                        <select
                          className="form-select"
                          style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', width: 'auto' }}
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        >
                          <option value="Admin">Admin</option>
                          <option value="Security Analyst">Security Analyst</option>
                          <option value="User">User (Read-Only)</option>
                        </select>
                      </td>
                    )}
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
