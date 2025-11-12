import React, { useState } from 'react';
import { backtestApi } from '../../services/api';
import { formatPercentage, formatCurrency } from '../../utils/formatters';

interface BacktestConfig {
  strategy_type: string;
  params: Record<string, any>;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission: number;
}

interface BacktestPanelProps {
  onResultsChange?: (results: any) => void;
}

export function BacktestPanel({ onResultsChange }: BacktestPanelProps) {
  const [config, setConfig] = useState<BacktestConfig>({
    strategy_type: 'ma_crossover',
    params: { fast_period: 10, slow_period: 30 },
    timeframe: '1h',
    start_date: '',
    end_date: '',
    initial_capital: 10000,
    commission: 0.0001,
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    try {
      const response = await backtestApi.run(config);
      setResults(response.data.results);
      onResultsChange?.(response.data.results);
    } catch (error) {
      console.error('Backtest error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="backtest-panel">
      <h2>Backtest Configuration</h2>
      <div className="config-form">
        <div>
          <label>Strategy</label>
          <select
            value={config.strategy_type}
            onChange={(e) => setConfig({ ...config, strategy_type: e.target.value })}
          >
            <option value="ma_crossover">Moving Average Crossover</option>
            <option value="rsi_divergence">RSI Divergence</option>
            <option value="bollinger_breakout">Bollinger Breakout</option>
          </select>
        </div>
        <div>
          <label>Timeframe</label>
          <select
            value={config.timeframe}
            onChange={(e) => setConfig({ ...config, timeframe: e.target.value })}
          >
            <option value="1m">1 Minute</option>
            <option value="5m">5 Minutes</option>
            <option value="15m">15 Minutes</option>
            <option value="1h">1 Hour</option>
            <option value="4h">4 Hours</option>
            <option value="1d">1 Day</option>
          </select>
        </div>
        <div>
          <label>Start Date</label>
          <input
            type="date"
            value={config.start_date}
            onChange={(e) => setConfig({ ...config, start_date: e.target.value })}
          />
        </div>
        <div>
          <label>End Date</label>
          <input
            type="date"
            value={config.end_date}
            onChange={(e) => setConfig({ ...config, end_date: e.target.value })}
          />
        </div>
        <div>
          <label>Initial Capital</label>
          <input
            type="number"
            value={config.initial_capital}
            onChange={(e) =>
              setConfig({ ...config, initial_capital: parseFloat(e.target.value) })
            }
          />
        </div>
        <button onClick={handleRun} disabled={loading}>
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
      </div>

      {results && (
        <div className="backtest-results">
          <h3>Results</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <label>Total Return</label>
              <value className={results.total_return >= 0 ? 'positive' : 'negative'}>
                {formatPercentage(results.total_return)}
              </value>
            </div>
            <div className="metric-card">
              <label>Sharpe Ratio</label>
              <value>{results.sharpe_ratio?.toFixed(2) || 'N/A'}</value>
            </div>
            <div className="metric-card">
              <label>Max Drawdown</label>
              <value className="negative">{formatPercentage(results.max_drawdown)}</value>
            </div>
            <div className="metric-card">
              <label>Win Rate</label>
              <value>{formatPercentage(results.win_rate)}</value>
            </div>
            <div className="metric-card">
              <label>Total Trades</label>
              <value>{results.total_trades}</value>
            </div>
            <div className="metric-card">
              <label>Profit Factor</label>
              <value>{results.profit_factor?.toFixed(2) || 'N/A'}</value>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

