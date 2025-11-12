import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface DrawdownChartProps {
  equityCurve: number[];
  timestamps?: string[];
}

export function DrawdownChart({ equityCurve, timestamps }: DrawdownChartProps) {
  const calculateDrawdowns = () => {
    if (!equityCurve || equityCurve.length === 0) return [];
    
    const drawdowns: number[] = [];
    let peak = equityCurve[0];
    
    for (let i = 0; i < equityCurve.length; i++) {
      if (equityCurve[i] > peak) {
        peak = equityCurve[i];
      }
      const drawdown = ((equityCurve[i] - peak) / peak) * 100;
      drawdowns.push(drawdown);
    }
    
    return drawdowns;
  };

  const drawdowns = calculateDrawdowns();
  const data = drawdowns.map((dd, index) => ({
    time: timestamps?.[index] || index,
    drawdown: dd,
  }));

  return (
    <div className="drawdown-chart">
      <h3>Drawdown Analysis</h3>
      <p className="chart-description">
        Drawdown shows the decline from peak equity. Lower values (more negative) indicate larger drawdowns.
      </p>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis label={{ value: 'Drawdown %', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
          <Bar dataKey="drawdown">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.drawdown < -10 ? '#ef5350' : entry.drawdown < -5 ? '#ff9800' : '#26a69a'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="drawdown-stats">
        <div className="stat">
          <label>Max Drawdown</label>
          <value className="negative">{Math.min(...drawdowns).toFixed(2)}%</value>
        </div>
        <div className="stat">
          <label>Avg Drawdown</label>
          <value>{drawdowns.filter(d => d < 0).reduce((a, b) => a + b, 0) / drawdowns.filter(d => d < 0).length || 0}</value>
        </div>
      </div>
    </div>
  );
}

