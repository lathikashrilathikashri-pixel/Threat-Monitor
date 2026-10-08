import React from 'react';

export default function Docs() {
  const docsUrl = window.location.origin + '/api/docs';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Interactive REST API Documentation</h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            OpenAPI 3.0 specification & Swagger UI explorer for academic evaluation
          </p>
        </div>
        <a
          href="/api/docs"
          target="_blank"
          rel="noreferrer"
          className="btn btn-primary btn-sm"
        >
          ↗ Open Standalone Swagger UI
        </a>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Endpoints Overview
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          All endpoints support standard JSON request bodies and require Bearer JWT authentication or X-Device-Token API keys.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ background: '#070b14', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="badge badge-low" style={{ marginBottom: '0.5rem' }}>AUTH</span>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.35rem' }}>POST /api/auth/login</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>POST /api/auth/register</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>GET /api/auth/me</div>
          </div>

          <div style={{ background: '#070b14', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="badge badge-high" style={{ marginBottom: '0.5rem' }}>TELEMETRY</span>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.35rem' }}>POST /api/events</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>GET /api/events</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>POST /api/devices/heartbeat</div>
          </div>

          <div style={{ background: '#070b14', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span className="badge badge-critical" style={{ marginBottom: '0.5rem' }}>TRIAGE & IR</span>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.35rem' }}>GET /api/alerts</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>POST /api/alerts/{'{id}'}/convert-incident</div>
            <div className="mono" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>GET /api/incidents</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden', height: '650px' }}>
        <iframe
          src="/api/docs"
          title="Swagger UI"
          style={{ width: '100%', height: '100%', border: 'none' }}
        ></iframe>
      </div>
    </div>
  );
}
