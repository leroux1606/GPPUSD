import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUIStore } from '../../store/uiStore';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/charts', label: 'Charts', icon: '📈' },
  { path: '/strategies', label: 'Strategies', icon: '🎯' },
  { path: '/backtesting', label: 'Backtesting', icon: '📉' },
  { path: '/trading', label: 'Trading', icon: '💹' },
  { path: '/analytics', label: 'Analytics', icon: '📋' },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
      <button onClick={toggleSidebar} className="toggle-btn" aria-label="Toggle sidebar">
        {sidebarOpen ? '◀' : '▶'}
      </button>
      {sidebarOpen && (
        <nav className="sidebar-nav">
          <ul>
            {NAV_ITEMS.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </aside>
  );
}
