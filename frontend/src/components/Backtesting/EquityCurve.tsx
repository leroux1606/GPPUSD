import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface EquityCurveProps {
  equityCurve: number[];
  timestamps?: string[];
}

export function EquityCurve({ equityCurve, timestamps }: EquityCurveProps) {
  const data = equityCurve.map((value, index) => ({
    time: timestamps?.[index] || index,
    equity: value,
  }));

  return (
    <div className="equity-curve">
      <h3>Equity Curve</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="equity" stroke="#26a69a" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

