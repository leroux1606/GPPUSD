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
  const { connected } = useWebSocket();

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
        <div className={`connection-indicator ${connected ? 'connected' : 'offline'}`}>
          <span className="status-dot" />
          <span className="status-text">{connected ? 'Live' : 'Offline'}</span>
        </div>
      </div>
    </nav>
  );
}
