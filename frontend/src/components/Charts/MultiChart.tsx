import React from 'react';
import { TradingChart } from './TradingChart';
import { useUIStore } from '../../store/uiStore';
import { TIMEFRAMES } from '../../utils/constants';

export function TimeframeSelector() {
  const { selectedTimeframe, setTimeframe } = useUIStore();

  return (
    <div className="timeframe-selector">
      {TIMEFRAMES.map((tf) => (
        <button
          key={tf}
          className={selectedTimeframe === tf ? 'active' : ''}
          onClick={() => setTimeframe(tf)}
        >
          {tf}
        </button>
      ))}
    </div>
  );
}

export function MultiChart() {
  return (
    <div className="multi-chart">
      <TimeframeSelector />
      <div className="chart-grid">
        <div className="chart-panel">
          <h3>Main Chart</h3>
          <TradingChart />
        </div>
      </div>
    </div>
  );
}

