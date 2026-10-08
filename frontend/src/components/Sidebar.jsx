import React from 'react';

export default function Sidebar({ activeTab, setActiveTab, alertCount = 0, incidentCount = 0 }) {
  const menuItems = [
    { id: 'dashboard', label: 'SOC Dashboard', icon: '📊' },
    { id: 'events', label: 'Security Events', icon: '📜' },
    { id: 'alerts', label: 'Alerts & Triage', icon: '🚨', badge: alertCount },
    { id: 'incidents', label: 'Incident Response', icon: '🛡️', badge: incidentCount },
    { id: 'devices', label: 'Monitored Devices', icon: '💻' },
    { id: 'blocked-ips', label: 'Perimeter Blacklist', icon: '⛔' },
    { id: 'users', label: 'User Roles & RBAC', icon: '👥' },
    { id: 'profile', label: 'Analyst Profile', icon: '👤' },
    { id: 'docs', label: 'API Reference', icon: '📖' },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">🛡️</div>
        <div className="brand-text">
          <h1>CYBER DEFENSE</h1>
          <p>SOC COMMAND CENTER</p>
        </div>
      </div>

      <ul className="nav-menu">
        {menuItems.map((item) => (
          <li key={item.id} className="nav-item">
            <button
              className={activeTab === item.id ? 'active' : ''}
              onClick={() => setActiveTab(item.id)}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
              {item.badge > 0 && <span className="nav-badge">{item.badge}</span>}
            </button>
          </li>
        ))}
      </ul>

      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
        <div>DEFENSE ENGINE v1.0</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
          <span className="pulse-dot"></span> Telemetry Ingestion Active
        </div>
      </div>
    </aside>
  );
}
