import React, { useMemo } from 'react';
import { Trade } from '../../types';

interface MonthlyReturnsProps {
  trades: Trade[];
  initialBalance?: number;
}

interface MonthData {
  month: string;
  year: number;
  monthNum: number;
  return: number;
  trades: number;
  pnl: number;
}

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export function MonthlyReturns({ trades, initialBalance = 10000 }: MonthlyReturnsProps) {
  const { monthlyData, years, maxReturn, minReturn } = useMemo(() => {
    const monthlyMap = new Map<string, MonthData>();
    
    trades.forEach(trade => {
      if (!trade.timestamp || trade.pnl === undefined) return;
      
      const date = new Date(trade.close_timestamp || trade.timestamp);
      const year = date.getFullYear();
      const month = date.getMonth();
      const key = `${year}-${month}`;
      
      const existing = monthlyMap.get(key) || {
        month: MONTH_NAMES[month],
        year,
        monthNum: month,
        return: 0,
        trades: 0,
        pnl: 0,
      };
      
      existing.pnl += trade.pnl;
      existing.trades += 1;
      monthlyMap.set(key, existing);
    });

    // Calculate returns as percentage
    monthlyMap.forEach((data, key) => {
      data.return = (data.pnl / initialBalance) * 100;
    });

    const data = Array.from(monthlyMap.values()).sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year;
      return a.monthNum - b.monthNum;
    });

    const uniqueYears = [...new Set(data.map(d => d.year))].sort();
    const returns = data.map(d => d.return);
    
    return {
      monthlyData: data,
      years: uniqueYears,
      maxReturn: Math.max(...returns, 1),
      minReturn: Math.min(...returns, -1),
    };
  }, [trades, initialBalance]);

  // Get color based on return value
  const getColor = (value: number): string => {
    if (value === 0) return '#3b3b4d';
    if (value > 0) {
      const intensity = Math.min(Math.abs(value) / Math.abs(maxReturn), 1);
      return `rgba(38, 166, 154, ${0.3 + intensity * 0.7})`;
    } else {
      const intensity = Math.min(Math.abs(value) / Math.abs(minReturn), 1);
      return `rgba(239, 83, 80, ${0.3 + intensity * 0.7})`;
    }
  };

  // Create grid data organized by year and month
  const gridData = useMemo(() => {
    if (years.length === 0) return [];
    
    return years.map(year => ({
      year,
      months: MONTH_NAMES.map((name, idx) => {
        const data = monthlyData.find(d => d.year === year && d.monthNum === idx);
        return {
          name,
          monthNum: idx,
          return: data?.return || 0,
          trades: data?.trades || 0,
          pnl: data?.pnl || 0,
          hasData: !!data,
        };
      }),
    }));
  }, [years, monthlyData]);

  if (trades.length === 0) {
    return (
      <div className="monthly-returns">
        <h3>Monthly Returns Heatmap</h3>
        <p className="chart-description">
          Complete some trades to see your monthly performance breakdown.
        </p>
        <div className="no-data-placeholder">
          <div className="heatmap-preview">
            {MONTH_NAMES.map((month) => (
              <div
                key={month}
                className="heatmap-cell placeholder"
                style={{ backgroundColor: '#2b2b43' }}
              >
                <div className="month-label">{month}</div>
                <div className="month-value">-</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="monthly-returns">
      <h3>Monthly Returns Heatmap</h3>
      <p className="chart-description">
        Visual representation of monthly performance. Green indicates profits, red indicates losses.
        Hover over cells for details.
      </p>
      
      <div className="heatmap-container">
        {/* Year labels and month grid */}
        <div className="heatmap-years">
          {gridData.map(({ year, months }) => (
            <div key={year} className="year-row">
              <div className="year-label">{year}</div>
              <div className="heatmap-grid">
                {months.map((month) => (
                  <div
                    key={`${year}-${month.monthNum}`}
                    className={`heatmap-cell ${month.hasData ? '' : 'no-data'}`}
                    style={{ backgroundColor: month.hasData ? getColor(month.return) : '#2b2b43' }}
                    title={month.hasData 
                      ? `${month.name} ${year}\nReturn: ${month.return.toFixed(2)}%\nP&L: $${month.pnl.toFixed(2)}\nTrades: ${month.trades}`
                      : `${month.name} ${year}\nNo trades`
                    }
                  >
                    <div className="month-label">{month.name}</div>
                    <div className="month-value">
                      {month.hasData ? `${month.return.toFixed(1)}%` : '-'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="heatmap-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#ef5350' }}></span>
            <span>Losses</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#3b3b4d' }}></span>
            <span>No Data</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#26a69a' }}></span>
            <span>Profits</span>
          </div>
        </div>

        {/* Summary stats */}
        <div className="heatmap-summary">
          <div className="summary-stat">
            <label>Best Month</label>
            <span className="value positive">
              {maxReturn > 0 ? `+${maxReturn.toFixed(2)}%` : '-'}
            </span>
          </div>
          <div className="summary-stat">
            <label>Worst Month</label>
            <span className="value negative">
              {minReturn < 0 ? `${minReturn.toFixed(2)}%` : '-'}
            </span>
          </div>
          <div className="summary-stat">
            <label>Profitable Months</label>
            <span className="value">
              {monthlyData.filter(d => d.return > 0).length} / {monthlyData.length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
