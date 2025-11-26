import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import { formatCurrency } from '../../utils/formatters';

interface EquityCurveProps {
  equityCurve: number[];
  timestamps?: string[];
  initialCapital?: number;
}

interface EquityData {
  index: number;
  time: string | number;
  equity: number;
  return: number;
  drawdown: number;
}

export function EquityCurve({ equityCurve, timestamps, initialCapital = 10000 }: EquityCurveProps) {
  const { chartData, stats } = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) {
      return { chartData: [], stats: { peak: 0, low: 0, final: 0, totalReturn: 0 } };
    }

    const data: EquityData[] = [];
    let peak = equityCurve[0];
    let low = equityCurve[0];

    for (let i = 0; i < equityCurve.length; i++) {
      const equity = equityCurve[i];
      peak = Math.max(peak, equity);
      low = Math.min(low, equity);
      
      const returnPct = ((equity - initialCapital) / initialCapital) * 100;
      const drawdown = peak > 0 ? ((equity - peak) / peak) * 100 : 0;

      data.push({
        index: i,
        time: timestamps?.[i] || i,
        equity: equity,
        return: returnPct,
        drawdown: drawdown,
      });
    }

    const final = equityCurve[equityCurve.length - 1];
    const totalReturn = ((final - initialCapital) / initialCapital) * 100;

    return {
      chartData: data,
      stats: { peak, low, final, totalReturn },
    };
  }, [equityCurve, timestamps, initialCapital]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as EquityData;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">Period: {data.time}</p>
          <p className="tooltip-value">
            Equity: {formatCurrency(data.equity)}
          </p>
          <p className={`tooltip-value ${data.return >= 0 ? 'positive' : 'negative'}`}>
            Return: {data.return.toFixed(2)}%
          </p>
          {data.drawdown < 0 && (
            <p className="tooltip-value negative">
              Drawdown: {data.drawdown.toFixed(2)}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="equity-curve">
        <h3>Equity Curve</h3>
        <p className="chart-description">
          Run a backtest to see your strategy's equity curve over time.
        </p>
        <div className="chart-placeholder">
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="equity-curve">
      <h3>Equity Curve</h3>
      <p className="chart-description">
        Shows how your portfolio value changed over the backtest period.
      </p>

      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#26a69a" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#26a69a" stopOpacity={0} />
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
            tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={initialCapital}
            stroke="#6b7280"
            strokeDasharray="5 5"
            label={{ value: 'Initial', fill: '#6b7280', fontSize: 10 }}
          />
          <Area
            type="monotone"
            dataKey="equity"
            stroke="transparent"
            fill="url(#equityGradient)"
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#26a69a"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#26a69a' }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="equity-stats">
        <div className="stat">
          <label>Initial Capital</label>
          <span className="value">{formatCurrency(initialCapital)}</span>
        </div>
        <div className="stat">
          <label>Final Value</label>
          <span className={`value ${stats.final >= initialCapital ? 'positive' : 'negative'}`}>
            {formatCurrency(stats.final)}
          </span>
        </div>
        <div className="stat">
          <label>Peak Value</label>
          <span className="value positive">{formatCurrency(stats.peak)}</span>
        </div>
        <div className="stat">
          <label>Total Return</label>
          <span className={`value ${stats.totalReturn >= 0 ? 'positive' : 'negative'}`}>
            {stats.totalReturn >= 0 ? '+' : ''}{stats.totalReturn.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}
