import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWebSocket } from '../../hooks/useWebSocket';

interface NavLink {
  path: string;
  label: string;
}

const NAV_LINKS: NavLink[] = [
  { path: '/', label: 'Dashboard' },
  { path: '/charts', label: 'Charts' },
  { path: '/strategies', label: 'Strategies' },
  { path: '/backtesting', label: 'Backtesting' },
  { path: '/trading', label: 'Trading' },
  { path: '/analytics', label: 'Analytics' },
];

export function Navbar() {
  const location = useLocation();
  const { isConnected, connectionState, reconnect } = useWebSocket();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">
          <span className="brand-icon">💷</span>
          <span className="brand-text">GBP/USD Trading</span>
        </Link>
      </div>
      <div className="nav-links">
        {NAV_LINKS.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className={isActive(link.path) ? 'active' : ''}
          >
            {link.label}
          </Link>
        ))}
      </div>
      <div className="nav-status">
        <button
          className={`connection-indicator ${connectionState}`}
          onClick={reconnect}
          title={`Status: ${connectionState}. Click to reconnect.`}
        >
          <span className="status-dot" />
          <span className="status-text">
            {connectionState === 'connected' ? 'Live' : 
             connectionState === 'reconnecting' ? 'Reconnecting...' : 'Offline'}
          </span>
        </button>
      </div>
    </nav>
  );
}
