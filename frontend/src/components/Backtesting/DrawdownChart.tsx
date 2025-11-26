import React, { useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface DrawdownChartProps {
  equityCurve: number[];
  timestamps?: string[];
}

interface DrawdownData {
  index: number;
  time: string | number;
  drawdown: number;
  equity: number;
  peak: number;
}

export function DrawdownChart({ equityCurve, timestamps }: DrawdownChartProps) {
  const { drawdownData, stats } = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) {
      return { drawdownData: [], stats: { max: 0, avg: 0, current: 0 } };
    }

    const data: DrawdownData[] = [];
    let peak = equityCurve[0];
    let maxDrawdown = 0;
    let totalDrawdown = 0;
    let drawdownCount = 0;

    for (let i = 0; i < equityCurve.length; i++) {
      const equity = equityCurve[i];
      
      // Update peak
      if (equity > peak) {
        peak = equity;
      }

      // Calculate drawdown as percentage
      const drawdown = peak > 0 ? ((equity - peak) / peak) * 100 : 0;
      
      data.push({
        index: i,
        time: timestamps?.[i] || i,
        drawdown: drawdown,
        equity: equity,
        peak: peak,
      });

      // Track statistics
      if (drawdown < 0) {
        maxDrawdown = Math.min(maxDrawdown, drawdown);
        totalDrawdown += Math.abs(drawdown);
        drawdownCount++;
      }
    }

    const avgDrawdown = drawdownCount > 0 ? -(totalDrawdown / drawdownCount) : 0;
    const currentDrawdown = data.length > 0 ? data[data.length - 1].drawdown : 0;

    return {
      drawdownData: data,
      stats: {
        max: maxDrawdown,
        avg: avgDrawdown,
        current: currentDrawdown,
      },
    };
  }, [equityCurve, timestamps]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as DrawdownData;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">Period: {data.time}</p>
          <p className="tooltip-value negative">
            Drawdown: {data.drawdown.toFixed(2)}%
          </p>
          <p className="tooltip-value">
            Equity: ${data.equity.toFixed(2)}
          </p>
          <p className="tooltip-value">
            Peak: ${data.peak.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  // Get color based on drawdown severity
  const getDrawdownColor = (drawdown: number): string => {
    if (drawdown > -5) return '#26a69a';
    if (drawdown > -10) return '#ff9800';
    return '#ef5350';
  };

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="drawdown-chart">
        <h3>Drawdown Analysis</h3>
        <p className="chart-description">No equity data available to calculate drawdowns.</p>
      </div>
    );
  }

  return (
    <div className="drawdown-chart">
      <h3>Drawdown Analysis</h3>
      <p className="chart-description">
        Drawdown shows the decline from peak equity. Lower values (more negative) indicate larger drawdowns.
      </p>
      
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={drawdownData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef5350" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ef5350" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#3b3b4d" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickLine={{ stroke: '#3b3b4d' }}
            axisLine={{ stroke: '#3b3b4d' }}
          />
          <YAxis
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickLine={{ stroke: '#3b3b4d' }}
            axisLine={{ stroke: '#3b3b4d' }}
            tickFormatter={(value) => `${value.toFixed(0)}%`}
            domain={['auto', 0]}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#4b5563" strokeDasharray="3 3" />
          <ReferenceLine
            y={-5}
            stroke="#ff9800"
            strokeDasharray="5 5"
            label={{ value: '-5%', fill: '#ff9800', fontSize: 10 }}
          />
          <ReferenceLine
            y={-10}
            stroke="#ef5350"
            strokeDasharray="5 5"
            label={{ value: '-10%', fill: '#ef5350', fontSize: 10 }}
          />
          <Area
            type="monotone"
            dataKey="drawdown"
            stroke="#ef5350"
            fill="url(#drawdownGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="drawdown-stats">
        <div className="stat">
          <label>Max Drawdown</label>
          <span className={`value negative`}>
            {stats.max.toFixed(2)}%
          </span>
        </div>
        <div className="stat">
          <label>Average Drawdown</label>
          <span className={`value ${stats.avg < 0 ? 'negative' : ''}`}>
            {stats.avg.toFixed(2)}%
          </span>
        </div>
        <div className="stat">
          <label>Current Drawdown</label>
          <span className={`value ${stats.current < 0 ? 'negative' : 'positive'}`}>
            {stats.current.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}
