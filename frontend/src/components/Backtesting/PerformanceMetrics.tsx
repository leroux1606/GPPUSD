import React from 'react';
import { PerformanceMetrics, BacktestResult } from '../../types';
import { formatPercentage, formatCurrency } from '../../utils/formatters';

interface PerformanceMetricsProps {
  metrics: PerformanceMetrics | BacktestResult;
}

export function PerformanceMetricsDisplay({ metrics }: PerformanceMetricsProps) {
  return (
    <div className="performance-metrics">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <label>Total Return</label>
          <span className={metrics.total_return >= 0 ? 'positive' : 'negative'}>
            {formatPercentage(metrics.total_return)}
          </span>
        </div>
        <div className="metric-card">
          <label>Annual Return</label>
          <span className={(metrics.annual_return ?? 0) >= 0 ? 'positive' : 'negative'}>
            {formatPercentage(metrics.annual_return ?? 0)}
          </span>
        </div>
        <div className="metric-card">
          <label>Sharpe Ratio</label>
          <span>{metrics.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
        </div>
        <div className="metric-card">
          <label>Sortino Ratio</label>
          <span>{metrics.sortino_ratio?.toFixed(2) || 'N/A'}</span>
        </div>
        <div className="metric-card">
          <label>Calmar Ratio</label>
          <span>{metrics.calmar_ratio?.toFixed(2) || 'N/A'}</span>
        </div>
        <div className="metric-card">
          <label>Max Drawdown</label>
          <span className="negative">{formatPercentage(metrics.max_drawdown)}</span>
        </div>
        <div className="metric-card">
          <label>Win Rate</label>
          <span>{formatPercentage(metrics.win_rate)}</span>
        </div>
        <div className="metric-card">
          <label>Profit Factor</label>
          <span>{metrics.profit_factor?.toFixed(2) || 'N/A'}</span>
        </div>
        <div className="metric-card">
          <label>Total Trades</label>
          <span>{metrics.total_trades}</span>
        </div>
        <div className="metric-card">
          <label>Avg Win</label>
          <span className="positive">{formatCurrency(metrics.avg_win)}</span>
        </div>
        <div className="metric-card">
          <label>Avg Loss</label>
          <span className="negative">{formatCurrency(metrics.avg_loss)}</span>
        </div>
        <div className="metric-card">
          <label>Expectancy</label>
          <span className={metrics.expectancy >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(metrics.expectancy)}
          </span>
        </div>
        <div className="metric-card">
          <label>Longest Win Streak</label>
          <span>{metrics.longest_win_streak}</span>
        </div>
        <div className="metric-card">
          <label>Longest Loss Streak</label>
          <span>{metrics.longest_loss_streak}</span>
        </div>
      </div>
    </div>
  );
}

