import React from 'react';
import { PerformanceMetrics } from '../../types';
import { formatPercentage, formatCurrency } from '../../utils/formatters';

interface PerformanceMetricsProps {
  metrics: PerformanceMetrics;
}

export function PerformanceMetricsDisplay({ metrics }: PerformanceMetricsProps) {
  return (
    <div className="performance-metrics">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <label>Total Return</label>
          <value className={metrics.total_return >= 0 ? 'positive' : 'negative'}>
            {formatPercentage(metrics.total_return)}
          </value>
        </div>
        <div className="metric-card">
          <label>Annual Return</label>
          <value className={metrics.annual_return >= 0 ? 'positive' : 'negative'}>
            {formatPercentage(metrics.annual_return)}
          </value>
        </div>
        <div className="metric-card">
          <label>Sharpe Ratio</label>
          <value>{metrics.sharpe_ratio?.toFixed(2) || 'N/A'}</value>
        </div>
        <div className="metric-card">
          <label>Sortino Ratio</label>
          <value>{metrics.sortino_ratio?.toFixed(2) || 'N/A'}</value>
        </div>
        <div className="metric-card">
          <label>Calmar Ratio</label>
          <value>{metrics.calmar_ratio?.toFixed(2) || 'N/A'}</value>
        </div>
        <div className="metric-card">
          <label>Max Drawdown</label>
          <value className="negative">{formatPercentage(metrics.max_drawdown)}</value>
        </div>
        <div className="metric-card">
          <label>Win Rate</label>
          <value>{formatPercentage(metrics.win_rate)}</value>
        </div>
        <div className="metric-card">
          <label>Profit Factor</label>
          <value>{metrics.profit_factor?.toFixed(2) || 'N/A'}</value>
        </div>
        <div className="metric-card">
          <label>Total Trades</label>
          <value>{metrics.total_trades}</value>
        </div>
        <div className="metric-card">
          <label>Avg Win</label>
          <value className="positive">{formatCurrency(metrics.avg_win)}</value>
        </div>
        <div className="metric-card">
          <label>Avg Loss</label>
          <value className="negative">{formatCurrency(metrics.avg_loss)}</value>
        </div>
        <div className="metric-card">
          <label>Expectancy</label>
          <value className={metrics.expectancy >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(metrics.expectancy)}
          </value>
        </div>
        <div className="metric-card">
          <label>Longest Win Streak</label>
          <value>{metrics.longest_win_streak}</value>
        </div>
        <div className="metric-card">
          <label>Longest Loss Streak</label>
          <value>{metrics.longest_loss_streak}</value>
        </div>
      </div>
    </div>
  );
}

