/**
 * ===================================================================================
 * PROJECT: Real-Time Cybersecurity Threat Monitoring & Incident Response System
 * MODULE: Frontend API Client
 * FILE: frontend/src/api/client.js
 * ===================================================================================
 * WHAT THIS FILE DOES:
 *   Wraps standard Fetch API calls with automatic Bearer JWT attachment, baseURL 
 *   routing, and error parsing. Handles both local development and live cloud endpoints.
 * 
 * WHY IT IS REQUIRED:
 *   Centralizes network requests and security token management across all React views.
 * ===================================================================================
 */

const API_BASE = import.meta.env.VITE_API_URL 
  ? import.meta.env.VITE_API_URL.replace(/\/$/, '') 
  : '';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('soc_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers
  };

  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, { ...options, headers });
    
    // Auto logout on token expiration
    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      localStorage.removeItem('soc_token');
      localStorage.removeItem('soc_user');
      window.location.hash = '#/login';
    }

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.message || `HTTP ${response.status}: Request failed.`);
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  auth: {
    login: (username, password) => 
      request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
    register: (username, email, password, role) => 
      request('/api/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password, role }) }),
    logout: () => 
      request('/api/auth/logout', { method: 'POST' }),
    me: () => 
      request('/api/auth/me')
  },
  dashboard: {
    getStats: () => request('/api/dashboard/stats')
  },
  events: {
    list: (params = '') => request(`/api/events${params}`),
    ingest: (eventData) => request('/api/events', { method: 'POST', body: JSON.stringify(eventData) })
  },
  alerts: {
    list: (params = '') => request(`/api/alerts${params}`),
    get: (id) => request(`/api/alerts/${id}`),
    updateStatus: (id, status) => request(`/api/alerts/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
    convertToIncident: (id) => request(`/api/alerts/${id}/convert-incident`, { method: 'POST' })
  },
  incidents: {
    list: (params = '') => request(`/api/incidents${params}`),
    create: (data) => request('/api/incidents', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/api/incidents/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
  },
  devices: {
    list: () => request('/api/devices'),
    register: (data) => request('/api/devices', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/devices/${id}`, { method: 'DELETE' })
  },
  blockedIps: {
    list: () => request('/api/blocked-ips'),
    add: (ip_address, reason) => request('/api/blocked-ips', { method: 'POST', body: JSON.stringify({ ip_address, reason }) }),
    remove: (id) => request(`/api/blocked-ips/${id}`, { method: 'DELETE' })
  },
  users: {
    list: () => request('/api/users'),
    updateRole: (id, role) => request(`/api/users/${id}/role`, { method: 'PATCH', body: JSON.stringify({ role }) })
  }
};
