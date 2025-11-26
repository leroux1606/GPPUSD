import React, { useState, useEffect, useMemo } from 'react';
import { analyticsApi } from '../../services/api';
import { useTradingStore } from '../../store/tradingStore';
import { formatPercentage, formatCurrency } from '../../utils/formatters';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import { Trade, PerformanceMetrics } from '../../types';

interface AnalyticsDashboardProps {
  trades?: Trade[];
}

export function AnalyticsDashboard({ trades: propTrades }: AnalyticsDashboardProps) {
  const { closedTrades, positions } = useTradingStore();
  const [apiMetrics, setApiMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use prop trades or combine positions and closed trades from store
  const allTrades = useMemo(() => {
    if (propTrades && propTrades.length > 0) return propTrades;
    return [...closedTrades, ...positions.filter(p => p.status === 'closed')];
  }, [propTrades, closedTrades, positions]);

  // Calculate metrics from trades
  const calculatedMetrics = useMemo(() => {
    if (allTrades.length === 0) return null;

    const wins = allTrades.filter(t => t.pnl && t.pnl > 0);
    const losses = allTrades.filter(t => t.pnl && t.pnl < 0);
    
    const totalPnL = allTrades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const totalWins = wins.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const totalLosses = Math.abs(losses.reduce((sum, t) => sum + (t.pnl || 0), 0));

    const winRate = allTrades.length > 0 ? (wins.length / allTrades.length) * 100 : 0;
    const avgWin = wins.length > 0 ? totalWins / wins.length : 0;
    const avgLoss = losses.length > 0 ? totalLosses / losses.length : 0;
    const profitFactor = totalLosses > 0 ? totalWins / totalLosses : totalWins > 0 ? Infinity : 0;
    const expectancy = allTrades.length > 0 ? totalPnL / allTrades.length : 0;

    // Calculate win/loss streaks
    let currentStreak = 0;
    let longestWinStreak = 0;
    let longestLossStreak = 0;
    let isWinStreak = true;

    allTrades.forEach(trade => {
      if (trade.pnl && trade.pnl > 0) {
        if (isWinStreak) {
          currentStreak++;
        } else {
          longestLossStreak = Math.max(longestLossStreak, currentStreak);
          currentStreak = 1;
          isWinStreak = true;
        }
        longestWinStreak = Math.max(longestWinStreak, currentStreak);
      } else if (trade.pnl && trade.pnl < 0) {
        if (!isWinStreak) {
          currentStreak++;
        } else {
          longestWinStreak = Math.max(longestWinStreak, currentStreak);
          currentStreak = 1;
          isWinStreak = false;
        }
        longestLossStreak = Math.max(longestLossStreak, currentStreak);
      }
    });

    return {
      total_return: totalPnL,
      total_trades: allTrades.length,
      winning_trades: wins.length,
      losing_trades: losses.length,
      win_rate: winRate,
      avg_win: avgWin,
      avg_loss: avgLoss,
      profit_factor: profitFactor,
      expectancy: expectancy,
      longest_win_streak: longestWinStreak,
      longest_loss_streak: longestLossStreak,
    };
  }, [allTrades]);

  // Fetch API metrics on mount
  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await analyticsApi.getPerformance();
      if (response.data) {
        setApiMetrics(response.data);
      }
    } catch (err) {
      console.error('Error loading analytics:', err);
      // Don't set error if we have calculated metrics
      if (!calculatedMetrics) {
        setError('Failed to load analytics from server');
      }
    } finally {
      setLoading(false);
    }
  };

  // Use API metrics if available, otherwise use calculated
  const metrics = apiMetrics || calculatedMetrics;

  if (loading && !metrics) {
    return (
      <div className="analytics-dashboard">
        <h2>Analytics Dashboard</h2>
        <LoadingSpinner message="Loading analytics..." />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="analytics-dashboard">
        <h2>Analytics Dashboard</h2>
        <div className="no-data-message">
          <p>No trading data available.</p>
          <p>Complete some trades to see your performance analytics.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <h2>Analytics Dashboard</h2>
      
      {error && (
        <div className="analytics-error">
          <p>{error}</p>
          <button onClick={loadAnalytics}>Retry</button>
        </div>
      )}

      <div className="analytics-grid">
        {/* Performance Card */}
        <div className="analytics-card">
          <h3>Performance</h3>
          <div className="metric">
            <label>Total Return</label>
            <span className={`value ${metrics.total_return >= 0 ? 'positive' : 'negative'}`}>
              {typeof metrics.total_return === 'number' && metrics.total_return > 1000 
                ? formatCurrency(metrics.total_return)
                : formatPercentage(metrics.total_return)}
            </span>
          </div>
          {'sharpe_ratio' in metrics && (
            <div className="metric">
              <label>Sharpe Ratio</label>
              <span className="value">
                {metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
              </span>
            </div>
          )}
          {'max_drawdown' in metrics && (
            <div className="metric">
              <label>Max Drawdown</label>
              <span className="value negative">
                {formatPercentage(metrics.max_drawdown || 0)}
              </span>
            </div>
          )}
        </div>

        {/* Trading Statistics Card */}
        <div className="analytics-card">
          <h3>Trading Statistics</h3>
          <div className="metric">
            <label>Total Trades</label>
            <span className="value">{metrics.total_trades}</span>
          </div>
          <div className="metric">
            <label>Win Rate</label>
            <span className={`value ${metrics.win_rate >= 50 ? 'positive' : 'negative'}`}>
              {formatPercentage(metrics.win_rate)}
            </span>
          </div>
          <div className="metric">
            <label>Profit Factor</label>
            <span className={`value ${metrics.profit_factor >= 1 ? 'positive' : 'negative'}`}>
              {metrics.profit_factor === Infinity ? '∞' : metrics.profit_factor?.toFixed(2) || 'N/A'}
            </span>
          </div>
        </div>

        {/* Average Trade Card */}
        <div className="analytics-card">
          <h3>Average Trade</h3>
          <div className="metric">
            <label>Average Win</label>
            <span className="value positive">{formatCurrency(metrics.avg_win)}</span>
          </div>
          <div className="metric">
            <label>Average Loss</label>
            <span className="value negative">{formatCurrency(metrics.avg_loss)}</span>
          </div>
          <div className="metric">
            <label>Expectancy</label>
            <span className={`value ${metrics.expectancy >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(metrics.expectancy)}
            </span>
          </div>
        </div>

        {/* Streaks Card */}
        <div className="analytics-card">
          <h3>Streaks</h3>
          <div className="metric">
            <label>Longest Win Streak</label>
            <span className="value positive">{metrics.longest_win_streak || 0}</span>
          </div>
          <div className="metric">
            <label>Longest Loss Streak</label>
            <span className="value negative">{metrics.longest_loss_streak || 0}</span>
          </div>
          {'winning_trades' in metrics && (
            <>
              <div className="metric">
                <label>Winning Trades</label>
                <span className="value positive">{metrics.winning_trades}</span>
              </div>
              <div className="metric">
                <label>Losing Trades</label>
                <span className="value negative">{metrics.losing_trades}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
