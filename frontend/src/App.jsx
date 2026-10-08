import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Alerts from './pages/Alerts';
import Incidents from './pages/Incidents';
import Devices from './pages/Devices';
import BlockedIPs from './pages/BlockedIPs';
import Users from './pages/Users';
import Profile from './pages/Profile';
import Docs from './pages/Docs';
import Login from './pages/Login';
import Register from './pages/Register';
import { api } from './api/client';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('soc_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [authView, setAuthView] = useState('login'); // 'login' or 'register'
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Polling dashboard telemetry
  const refreshStats = async () => {
    if (!currentUser) return;
    try {
      const data = await api.dashboard.getStats();
      setStats(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to update stats:', err);
    }
  };

  useEffect(() => {
    refreshStats();
  }, [currentUser]);

  useEffect(() => {
    if (!autoRefresh || !currentUser) return;
    const interval = setInterval(refreshStats, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, currentUser]);

  const handleLogout = async () => {
    try {
      await api.auth.logout();
    } catch (e) {
      // ignore
    }
    localStorage.removeItem('soc_token');
    localStorage.removeItem('soc_user');
    setCurrentUser(null);
    setAuthView('login');
  };

  // If unauthenticated, show Login or Register view
  if (!currentUser) {
    if (authView === 'register') {
      return (
        <Register
          onRegisterSuccess={(user) => setCurrentUser(user)}
          switchToLogin={() => setAuthView('login')}
        />
      );
    }
    return (
      <Login
        onLoginSuccess={(user) => setCurrentUser(user)}
        switchToRegister={() => setAuthView('register')}
      />
    );
  }

  const alertBadgeCount = stats?.kpis?.critical_alerts + stats?.kpis?.high_alerts || 0;
  const incidentBadgeCount = stats?.kpis?.active_incidents || 0;

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        alertCount={alertBadgeCount}
        incidentCount={incidentBadgeCount}
      />

      <div className="main-content">
        <Navbar
          user={currentUser}
          onLogout={handleLogout}
          lastUpdated={lastUpdated}
          onRefresh={refreshStats}
          autoRefresh={autoRefresh}
          setAutoRefresh={setAutoRefresh}
        />

        <main className="page-body">
          {activeTab === 'dashboard' && (
            <Dashboard
              stats={stats}
              onNavigateToAlerts={() => setActiveTab('alerts')}
              onNavigateToEvents={() => setActiveTab('events')}
              onNavigateToIncidents={() => setActiveTab('incidents')}
            />
          )}

          {activeTab === 'events' && <Events />}

          {activeTab === 'alerts' && (
            <Alerts onNavigateToIncidents={() => setActiveTab('incidents')} />
          )}

          {activeTab === 'incidents' && <Incidents />}

          {activeTab === 'devices' && <Devices />}

          {activeTab === 'blocked-ips' && <BlockedIPs />}

          {activeTab === 'users' && <Users currentUser={currentUser} />}

          {activeTab === 'profile' && <Profile user={currentUser} />}

          {activeTab === 'docs' && <Docs />}
        </main>
      </div>
    </div>
  );
}
