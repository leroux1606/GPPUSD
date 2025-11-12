import React from 'react';
import { Link } from 'react-router-dom';

export function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">GBP/USD Trading</Link>
      </div>
      <div className="nav-links">
        <Link to="/">Dashboard</Link>
        <Link to="/charts">Charts</Link>
        <Link to="/strategies">Strategies</Link>
        <Link to="/backtesting">Backtesting</Link>
        <Link to="/trading">Trading</Link>
        <Link to="/analytics">Analytics</Link>
      </div>
    </nav>
  );
}

