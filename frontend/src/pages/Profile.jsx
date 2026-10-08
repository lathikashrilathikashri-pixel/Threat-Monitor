import React, { useState } from 'react';

export default function Profile({ user }) {
  const token = localStorage.getItem('soc_token') || 'No active token';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(token);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Analyst Credentials & Security Profile</h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Session context, authentication status, and cryptographic token verification
        </p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem'
            }}>
              👤
            </div>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{user?.username}</h3>
              <div style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem' }}>{user?.role}</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.88rem' }}>
            <div><strong>Email:</strong> {user?.email}</div>
            <div><strong>User ID:</strong> #{user?.id}</div>
            <div><strong>Session Status:</strong> <span style={{ color: '#10b981' }}>● Active (Authenticated)</span></div>
            <div><strong>Algorithm:</strong> HMAC SHA-256 (JWT Token)</div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem' }}>
            Active Bearer JWT Token
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Used for authenticating REST requests and testing with Postman or curl.
          </p>

          <textarea
            className="form-textarea mono"
            rows="6"
            readOnly
            value={token}
            style={{ fontSize: '0.75rem', wordBreak: 'break-all', marginBottom: '1rem' }}
          ></textarea>

          <button className="btn btn-secondary btn-sm" onClick={handleCopy}>
            {copied ? '✓ Token Copied to Clipboard!' : '📋 Copy Bearer Token'}
          </button>
        </div>
      </div>
    </div>
  );
}
