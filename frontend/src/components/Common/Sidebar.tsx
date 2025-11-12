import React from 'react';
import { useUIStore } from '../../store/uiStore';

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
      <button onClick={toggleSidebar} className="toggle-btn">
        {sidebarOpen ? '◀' : '▶'}
      </button>
      {sidebarOpen && (
        <nav>
          <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/charts">Charts</a></li>
            <li><a href="/strategies">Strategies</a></li>
            <li><a href="/backtesting">Backtesting</a></li>
            <li><a href="/trading">Trading</a></li>
            <li><a href="/analytics">Analytics</a></li>
          </ul>
        </nav>
      )}
    </aside>
  );
}

