import React, { useState } from 'react';
import { api } from '../api/client';

export default function Register({ onRegisterSuccess, switchToLogin }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Security Analyst');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.auth.register(username, email, password, role);
      localStorage.setItem('soc_token', data.token);
      localStorage.setItem('soc_user', JSON.stringify(data.user));
      onRegisterSuccess(data.user);
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      background: 'radial-gradient(circle at 50% 30%, rgba(139, 92, 246, 0.15) 0%, transparent 60%)'
    }}>
      <div className="card" style={{ maxWidth: '440px', width: '100%', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div style={{
            width: '56px',
            height: '56px',
            background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
            borderRadius: '16px',
            margin: '0 auto 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.8rem',
            boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)'
          }}>
            📝
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>OPERATOR REGISTRATION</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Provision New Defense Credentials
          </p>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            color: '#ef4444',
            padding: '0.75rem',
            borderRadius: '8px',
            fontSize: '0.82rem',
            marginBottom: '1.25rem'
          }}>
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. analyst_john"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Security Email</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@soc-command.local"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password (Min 6 Characters)</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Platform Role</label>
            <select
              className="form-select"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="Security Analyst">Security Analyst (Monitor & Triage)</option>
              <option value="Admin">Admin (Full Control)</option>
              <option value="User">User (Auditor / Read-Only)</option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.85rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Creating Credentials...' : 'Create Account & Sign In →'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <button
            onClick={switchToLogin}
            style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', fontWeight: 700 }}
          >
            Sign In Here
          </button>
        </div>
      </div>
    </div>
  );
}
