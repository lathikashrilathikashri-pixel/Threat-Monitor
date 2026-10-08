import React from 'react';

export default function StatCard({ title, value, subtitle, icon, type = 'normal' }) {
  return (
    <div className={`card stat-card ${type}`}>
      <div className="stat-header">
        <span className="stat-title">{title}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <div className="stat-value">{value}</div>
      {subtitle && <div className="stat-subtitle">{subtitle}</div>}
    </div>
  );
}
