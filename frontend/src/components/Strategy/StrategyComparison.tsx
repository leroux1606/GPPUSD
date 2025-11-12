import React, { useState } from 'react';
import { strategyApi, backtestApi } from '../../services/api';
import { Strategy } from '../../types';

interface StrategyComparisonProps {
  strategies: Strategy[];
}

export function StrategyComparison({ strategies }: StrategyComparisonProps) {
  const [results, setResults] = useState<{ [key: string]: any }>({});
  const [loading, setLoading] = useState<string[]>([]);

  const runComparison = async (strategyId: string) => {
    setLoading([...loading, strategyId]);
    try {
      const strategy = strategies.find(s => s.id === strategyId);
      if (!strategy) return;

      const config = {
        strategy_type: strategy.type,
        params: strategy.params,
        timeframe: '1h',
        start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        initial_capital: 10000,
        commission: 0.0001,
      };

      const response = await backtestApi.run(config);
      setResults({ ...results, [strategyId]: response.data.results });
    } catch (error) {
      console.error('Comparison error:', error);
    } finally {
      setLoading(loading.filter(id => id !== strategyId));
    }
  };

  return (
    <div className="strategy-comparison">
      <h3>Strategy Comparison</h3>
      <p className="description">
        Compare multiple strategies side-by-side. Run backtests to see performance metrics.
      </p>
      <div className="comparison-table">
        <table>
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Total Return</th>
              <th>Sharpe Ratio</th>
              <th>Max Drawdown</th>
              <th>Win Rate</th>
              <th>Total Trades</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy) => {
              const result = results[strategy.id!];
              const isLoading = loading.includes(strategy.id!);
              return (
                <tr key={strategy.id}>
                  <td>{strategy.name}</td>
                  <td className={result?.total_return >= 0 ? 'positive' : 'negative'}>
                    {result ? `${result.total_return?.toFixed(2)}%` : '-'}
                  </td>
                  <td>{result ? result.sharpe_ratio?.toFixed(2) : '-'}</td>
                  <td className="negative">
                    {result ? `${result.max_drawdown?.toFixed(2)}%` : '-'}
                  </td>
                  <td>{result ? `${result.win_rate?.toFixed(1)}%` : '-'}</td>
                  <td>{result ? result.total_trades : '-'}</td>
                  <td>
                    <button
                      onClick={() => runComparison(strategy.id!)}
                      disabled={isLoading}
                    >
                      {isLoading ? 'Running...' : 'Run Backtest'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

