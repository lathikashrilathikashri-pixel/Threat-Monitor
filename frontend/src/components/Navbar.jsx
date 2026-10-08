import React from 'react';

export default function Navbar({ user, onLogout, lastUpdated, onRefresh, autoRefresh, setAutoRefresh }) {
  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem' }}>
          <span className="pulse-dot"></span>
          <span style={{ color: 'var(--text-muted)' }}>SOC Status:</span>
          <span style={{ color: '#10b981', fontWeight: 700 }}>LIVE CLOUD MONITORING</span>
        </div>
        {lastUpdated && (
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Updated: {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setAutoRefresh(!autoRefresh)}
          style={{ fontSize: '0.75rem' }}
          title="Toggle auto-refresh every 5 seconds"
        >
          {autoRefresh ? '🔄 Auto: ON (5s)' : '⏸️ Auto: OFF'}
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          title="Manual refresh"
        >
          ↻ Refresh
        </button>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.5rem', borderLeft: '1px solid var(--border-subtle)' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700 }}>{user.username}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)' }}>{user.role}</div>
            </div>
            <button className="btn btn-danger btn-sm" onClick={onLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
