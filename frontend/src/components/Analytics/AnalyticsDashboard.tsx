import React from 'react';
import { analyticsApi } from '../../services/api';
import { formatPercentage, formatCurrency } from '../../utils/formatters';

export function AnalyticsDashboard() {
  const [metrics, setMetrics] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const response = await analyticsApi.getPerformance();
      setMetrics(response.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading analytics...</div>;
  }

  if (!metrics) {
    return <div>No analytics data available</div>;
  }

  return (
    <div className="analytics-dashboard">
      <h2>Analytics Dashboard</h2>
      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Performance</h3>
          <div className="metric">
            <label>Total Return</label>
            <value className={metrics.total_return >= 0 ? 'positive' : 'negative'}>
              {formatPercentage(metrics.total_return)}
            </value>
          </div>
          <div className="metric">
            <label>Sharpe Ratio</label>
            <value>{metrics.sharpe_ratio?.toFixed(2) || 'N/A'}</value>
          </div>
          <div className="metric">
            <label>Max Drawdown</label>
            <value className="negative">{formatPercentage(metrics.max_drawdown)}</value>
          </div>
        </div>
        <div className="analytics-card">
          <h3>Trading Statistics</h3>
          <div className="metric">
            <label>Total Trades</label>
            <value>{metrics.total_trades}</value>
          </div>
          <div className="metric">
            <label>Win Rate</label>
            <value>{formatPercentage(metrics.win_rate)}</value>
          </div>
          <div className="metric">
            <label>Profit Factor</label>
            <value>{metrics.profit_factor?.toFixed(2) || 'N/A'}</value>
          </div>
        </div>
      </div>
    </div>
  );
}

