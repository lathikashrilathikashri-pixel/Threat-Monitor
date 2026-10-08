import React from 'react';

export default function SeverityBadge({ severity }) {
  const sev = (severity || 'LOW').toUpperCase();
  let badgeClass = 'badge-low';
  let icon = 'ℹ️';

  if (sev === 'CRITICAL') {
    badgeClass = 'badge-critical';
    icon = '🚨';
  } else if (sev === 'HIGH') {
    badgeClass = 'badge-high';
    icon = '⚠️';
  } else if (sev === 'MEDIUM') {
    badgeClass = 'badge-medium';
    icon = '⚡';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span>{icon}</span> {sev}
    </span>
  );
}
