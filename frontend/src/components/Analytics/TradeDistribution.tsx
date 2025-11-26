import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Trade } from '../../types';

interface TradeDistributionProps {
  trades: Trade[];
}

const COLORS = {
  wins: '#26a69a',
  losses: '#ef5350',
  breakeven: '#9ca3af',
};

export function TradeDistribution({ trades }: TradeDistributionProps) {
  const { winLossData, distributionData, totals } = useMemo(() => {
    const wins = trades.filter(t => t.pnl && t.pnl > 0);
    const losses = trades.filter(t => t.pnl && t.pnl < 0);
    const breakeven = trades.filter(t => !t.pnl || t.pnl === 0);

    const pieData = [
      { name: 'Wins', value: wins.length, color: COLORS.wins },
      { name: 'Losses', value: losses.length, color: COLORS.losses },
      { name: 'Breakeven', value: breakeven.length, color: COLORS.breakeven },
    ].filter(d => d.value > 0);

    // Calculate P&L distribution by range
    const winAmounts = wins.map(t => t.pnl!);
    const lossAmounts = losses.map(t => Math.abs(t.pnl!));

    const ranges = [
      { min: 0, max: 25, label: '$0-25' },
      { min: 25, max: 50, label: '$25-50' },
      { min: 50, max: 100, label: '$50-100' },
      { min: 100, max: 200, label: '$100-200' },
      { min: 200, max: 500, label: '$200-500' },
      { min: 500, max: Infinity, label: '$500+' },
    ];

    const barData = ranges.map(range => ({
      range: range.label,
      wins: winAmounts.filter(a => a > range.min && a <= range.max).length,
      losses: lossAmounts.filter(a => a > range.min && a <= range.max).length,
    }));

    return {
      winLossData: pieData,
      distributionData: barData,
      totals: {
        wins: wins.length,
        losses: losses.length,
        breakeven: breakeven.length,
        totalPnL: trades.reduce((sum, t) => sum + (t.pnl || 0), 0),
      },
    };
  }, [trades]);

  // Custom tooltip for pie chart
  const PieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = trades.length;
      const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : 0;
      return (
        <div className="chart-tooltip">
          <p style={{ color: data.payload.color }}>{data.name}</p>
          <p>{data.value} trades ({percentage}%)</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const BarTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value} trades
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Custom label for pie chart
  const renderPieLabel = ({ name, percent }: any) => {
    if (percent < 0.05) return null; // Don't show labels for very small slices
    return `${name}: ${(percent * 100).toFixed(0)}%`;
  };

  if (trades.length === 0) {
    return (
      <div className="trade-distribution">
        <h3>Trade Distribution Analysis</h3>
        <p className="chart-description">
          Complete some trades to see your win/loss distribution and P&L breakdown.
        </p>
        <div className="distribution-charts placeholder">
          <div className="chart-panel">
            <h4>Win/Loss Distribution</h4>
            <div className="placeholder-chart">
              <p>No data available</p>
            </div>
          </div>
          <div className="chart-panel">
            <h4>P&L Distribution by Range</h4>
            <div className="placeholder-chart">
              <p>No data available</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="trade-distribution">
      <h3>Trade Distribution Analysis</h3>
      <p className="chart-description">
        Breakdown of your trading performance by outcome and profit/loss ranges.
      </p>

      <div className="distribution-summary">
        <div className="summary-stat">
          <span className="stat-value positive">{totals.wins}</span>
          <span className="stat-label">Wins</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value negative">{totals.losses}</span>
          <span className="stat-label">Losses</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value neutral">{totals.breakeven}</span>
          <span className="stat-label">Breakeven</span>
        </div>
        <div className="summary-stat">
          <span className={`stat-value ${totals.totalPnL >= 0 ? 'positive' : 'negative'}`}>
            ${totals.totalPnL.toFixed(2)}
          </span>
          <span className="stat-label">Total P&L</span>
        </div>
      </div>

      <div className="distribution-charts">
        <div className="chart-panel">
          <h4>Win/Loss Distribution</h4>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={winLossData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderPieLabel}
                outerRadius={100}
                innerRadius={40}
                fill="#8884d8"
                dataKey="value"
                paddingAngle={2}
              >
                {winLossData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<PieTooltip />} />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value, entry: any) => (
                  <span style={{ color: entry.color }}>{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-panel">
          <h4>P&L Distribution by Range</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={distributionData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3b3b4d" />
              <XAxis
                dataKey="range"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                axisLine={{ stroke: '#3b3b4d' }}
              />
              <YAxis
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                axisLine={{ stroke: '#3b3b4d' }}
                allowDecimals={false}
              />
              <Tooltip content={<BarTooltip />} />
              <Legend
                formatter={(value) => (
                  <span style={{ color: value === 'wins' ? COLORS.wins : COLORS.losses }}>
                    {value.charAt(0).toUpperCase() + value.slice(1)}
                  </span>
                )}
              />
              <Bar dataKey="wins" fill={COLORS.wins} name="wins" radius={[4, 4, 0, 0]} />
              <Bar dataKey="losses" fill={COLORS.losses} name="losses" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
