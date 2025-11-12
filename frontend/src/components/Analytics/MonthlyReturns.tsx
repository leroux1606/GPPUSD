import React from 'react';
import { Trade } from '../../types';

interface MonthlyReturnsProps {
  trades: Trade[];
}

export function MonthlyReturns({ trades }: MonthlyReturnsProps) {
  const calculateMonthlyReturns = () => {
    const monthlyData: { [key: string]: number } = {};
    
    trades.forEach(trade => {
      if (trade.pnl) {
        const date = new Date(trade.timestamp);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        monthlyData[monthKey] = (monthlyData[monthKey] || 0) + trade.pnl;
      }
    });
    
    return monthlyData;
  };

  const monthlyReturns = calculateMonthlyReturns();
  const months = Object.keys(monthlyReturns).sort();
  const values = months.map(m => monthlyReturns[m]);
  const maxValue = Math.max(...values, 1);
  const minValue = Math.min(...values, -1);

  const getColor = (value: number) => {
    if (value === 0) return '#3b3b4d';
    if (value > 0) {
      const intensity = Math.min(value / maxValue, 1);
      return `rgba(38, 166, 154, ${0.3 + intensity * 0.7})`;
    } else {
      const intensity = Math.min(Math.abs(value) / Math.abs(minValue), 1);
      return `rgba(239, 83, 80, ${0.3 + intensity * 0.7})`;
    }
  };

  return (
    <div className="monthly-returns">
      <h3>Monthly Returns Heatmap</h3>
      <p className="chart-description">
        Visual representation of monthly performance. Green indicates profits, red indicates losses.
      </p>
      <div className="heatmap-container">
        <div className="heatmap-grid">
          {months.map((month, index) => (
            <div
              key={month}
              className="heatmap-cell"
              style={{ backgroundColor: getColor(monthlyReturns[month]) }}
              title={`${month}: ${monthlyReturns[month].toFixed(2)}%`}
            >
              <div className="month-label">{month.split('-')[1]}</div>
              <div className="month-value">{monthlyReturns[month].toFixed(1)}%</div>
            </div>
          ))}
        </div>
        <div className="heatmap-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ef5350' }}></span>
            <span>Losses</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#3b3b4d' }}></span>
            <span>Neutral</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#26a69a' }}></span>
            <span>Profits</span>
          </div>
        </div>
      </div>
    </div>
  );
}

