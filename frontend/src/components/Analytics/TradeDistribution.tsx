import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Trade } from '../../types';

interface TradeDistributionProps {
  trades: Trade[];
}

export function TradeDistribution({ trades }: TradeDistributionProps) {
  const winLossData = [
    { name: 'Wins', value: trades.filter(t => t.pnl && t.pnl > 0).length, color: '#26a69a' },
    { name: 'Losses', value: trades.filter(t => t.pnl && t.pnl < 0).length, color: '#ef5350' },
    { name: 'Breakeven', value: trades.filter(t => !t.pnl || t.pnl === 0).length, color: '#9ca3af' },
  ];

  const winAmounts = trades.filter(t => t.pnl && t.pnl > 0).map(t => t.pnl!);
  const lossAmounts = trades.filter(t => t.pnl && t.pnl < 0).map(t => Math.abs(t.pnl!));

  const distributionData = [
    { range: '0-50', wins: winAmounts.filter(a => a <= 50).length, losses: lossAmounts.filter(a => a <= 50).length },
    { range: '50-100', wins: winAmounts.filter(a => a > 50 && a <= 100).length, losses: lossAmounts.filter(a => a > 50 && a <= 100).length },
    { range: '100-200', wins: winAmounts.filter(a => a > 100 && a <= 200).length, losses: lossAmounts.filter(a => a > 100 && a <= 200).length },
    { range: '200+', wins: winAmounts.filter(a => a > 200).length, losses: lossAmounts.filter(a => a > 200).length },
  ];

  return (
    <div className="trade-distribution">
      <h3>Trade Distribution Analysis</h3>
      <div className="distribution-charts">
        <div className="chart-panel">
          <h4>Win/Loss Distribution</h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={winLossData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {winLossData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-panel">
          <h4>P&L Distribution by Range</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="wins" fill="#26a69a" name="Wins" />
              <Bar dataKey="losses" fill="#ef5350" name="Losses" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

