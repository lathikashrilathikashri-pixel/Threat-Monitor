import React, { useState } from 'react';
import { api } from '../api/client';

export default function Login({ onLoginSuccess, switchToRegister }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('AdminSecure2026!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.auth.login(username, password);
      localStorage.setItem('soc_token', data.token);
      localStorage.setItem('soc_user', JSON.stringify(data.user));
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.message || 'Login failed. Check username and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (user, pass) => {
    setUsername(user);
    setPassword(pass);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      background: 'radial-gradient(circle at 50% 30%, rgba(6, 182, 212, 0.15) 0%, transparent 60%)'
    }}>
      <div className="card" style={{ maxWidth: '440px', width: '100%', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '56px',
            height: '56px',
            background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
            borderRadius: '16px',
            margin: '0 auto 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.8rem',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)'
          }}>
            🛡️
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.02em' }}>SOC PORTAL ACCESS</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Real-Time Threat Monitoring & Incident Response System
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
            <label className="form-label">Operator / Analyst Username</label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. admin"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Security Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.85rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Enter SOC Command Center →'}
          </button>
        </form>

        <div style={{ marginTop: '1.75rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '0.65rem', textTransform: 'uppercase', fontWeight: 700 }}>
            Quick Demo Accounts (College Evaluation):
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickDemo('admin', 'AdminSecure2026!')}
            >
              👑 Admin
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickDemo('analyst1', 'AnalystPass2026!')}
            >
              🔍 Analyst
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleQuickDemo('auditor', 'AuditorPass2026!')}
            >
              👁️ Read-Only
            </button>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Need a new SOC account?{' '}
          <button
            onClick={switchToRegister}
            style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', fontWeight: 700 }}
          >
            Register Here
          </button>
        </div>
      </div>
    </div>
  );
}
