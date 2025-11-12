import React, { useState } from 'react';
import { backtestApi } from '../../services/api';
import { Strategy } from '../../types';

interface ParameterOptimizerProps {
  strategy: Strategy | null;
}

export function ParameterOptimizer({ strategy }: ParameterOptimizerProps) {
  const [paramRanges, setParamRanges] = useState<{ [key: string]: { min: number; max: number; step: number } }>({});
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (strategy) {
      const ranges: { [key: string]: { min: number; max: number; step: number } } = {};
      Object.entries(strategy.params).forEach(([key, value]) => {
        if (typeof value === 'number') {
          ranges[key] = { min: value * 0.5, max: value * 2, step: value * 0.1 };
        }
      });
      setParamRanges(ranges);
    }
  }, [strategy]);

  const handleOptimize = async () => {
    if (!strategy) return;

    setLoading(true);
    try {
      const paramGrid: { [key: string]: number[] } = {};
      Object.entries(paramRanges).forEach(([key, range]) => {
        const values = [];
        for (let i = range.min; i <= range.max; i += range.step) {
          values.push(Math.round(i * 10) / 10);
        }
        paramGrid[key] = values;
      });

      const config = {
        strategy_type: strategy.type,
        param_grid: paramGrid,
        timeframe: '1h',
        start_date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        initial_capital: 10000,
        commission: 0.0001,
      };

      const response = await backtestApi.optimize(config);
      setResults(response.data.top_results || []);
    } catch (error) {
      console.error('Optimization error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!strategy) {
    return <div>Select a strategy to optimize</div>;
  }

  return (
    <div className="parameter-optimizer">
      <h3>Parameter Optimization</h3>
      <p className="description">
        Optimize strategy parameters using grid search. Test different parameter combinations to find the best performance.
      </p>
      
      <div className="param-ranges">
        <h4>Parameter Ranges</h4>
        {Object.entries(paramRanges).map(([key, range]) => (
          <div key={key} className="param-range">
            <label>{key}</label>
            <div className="range-inputs">
              <input
                type="number"
                value={range.min}
                onChange={(e) =>
                  setParamRanges({
                    ...paramRanges,
                    [key]: { ...range, min: parseFloat(e.target.value) },
                  })
                }
                placeholder="Min"
              />
              <span>to</span>
              <input
                type="number"
                value={range.max}
                onChange={(e) =>
                  setParamRanges({
                    ...paramRanges,
                    [key]: { ...range, max: parseFloat(e.target.value) },
                  })
                }
                placeholder="Max"
              />
              <input
                type="number"
                value={range.step}
                onChange={(e) =>
                  setParamRanges({
                    ...paramRanges,
                    [key]: { ...range, step: parseFloat(e.target.value) },
                  })
                }
                placeholder="Step"
              />
            </div>
          </div>
        ))}
      </div>

      <button onClick={handleOptimize} disabled={loading} className="optimize-btn">
        {loading ? 'Optimizing...' : 'Run Optimization'}
      </button>

      {results.length > 0 && (
        <div className="optimization-results">
          <h4>Top Results</h4>
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Parameters</th>
                <th>Total Return</th>
                <th>Sharpe Ratio</th>
                <th>Max Drawdown</th>
              </tr>
            </thead>
            <tbody>
              {results.slice(0, 10).map((result, index) => (
                <tr key={index}>
                  <td>{index + 1}</td>
                  <td>
                    <pre>{JSON.stringify(result.params, null, 2)}</pre>
                  </td>
                  <td className={result.total_return >= 0 ? 'positive' : 'negative'}>
                    {result.total_return?.toFixed(2)}%
                  </td>
                  <td>{result.sharpe_ratio?.toFixed(2)}</td>
                  <td className="negative">{result.max_drawdown?.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

