import React, { useState } from 'react';

const INDICATOR_INFO: { [key: string]: { name: string; description: string; usage: string; formula?: string } } = {
  sma: {
    name: 'Simple Moving Average',
    description: 'Average of closing prices over a specified period. Smooths out price fluctuations.',
    usage: 'Buy when price crosses above SMA, sell when price crosses below SMA.',
    formula: 'SMA = (P1 + P2 + ... + Pn) / n',
  },
  ema: {
    name: 'Exponential Moving Average',
    description: 'Weighted moving average that gives more weight to recent prices. More responsive than SMA.',
    usage: 'Similar to SMA but reacts faster to price changes.',
    formula: 'EMA = Price(t) × k + EMA(y) × (1 – k) where k = 2/(n+1)',
  },
  macd: {
    name: 'Moving Average Convergence Divergence',
    description: 'Shows relationship between two moving averages. MACD line = Fast EMA - Slow EMA.',
    usage: 'Buy when MACD crosses above signal line, sell when MACD crosses below signal line.',
  },
  rsi: {
    name: 'Relative Strength Index',
    description: 'Momentum oscillator measuring speed and magnitude of price changes. Range: 0-100.',
    usage: 'Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).',
    formula: 'RSI = 100 - (100 / (1 + RS)) where RS = Avg Gain / Avg Loss',
  },
  bollinger_bands: {
    name: 'Bollinger Bands',
    description: 'Volatility bands placed above and below moving average. Band width adjusts to volatility.',
    usage: 'Buy when price touches lower band, sell when price touches upper band.',
    formula: 'Upper = SMA + (StdDev × 2)\nLower = SMA - (StdDev × 2)',
  },
  atr: {
    name: 'Average True Range',
    description: 'Measures market volatility by calculating average of true ranges over a period.',
    usage: 'Use for stop loss placement (typically 2x ATR from entry).',
  },
  stochastic: {
    name: 'Stochastic Oscillator',
    description: 'Compares closing price to price range over a period. Range: 0-100.',
    usage: 'Buy when %K crosses above %D from oversold, sell when %K crosses below %D from overbought.',
  },
  cci: {
    name: 'Commodity Channel Index',
    description: 'Identifies cyclical trends. Values above +100 indicate overbought, below -100 oversold.',
    usage: 'Buy when CCI < -100, sell when CCI > +100.',
  },
  adx: {
    name: 'Average Directional Index',
    description: 'Measures trend strength regardless of direction. Values above 25 indicate strong trend.',
    usage: 'Use to filter trades - only trade when ADX > 25 (strong trend).',
  },
};

export function IndicatorInfo({ indicatorName }: { indicatorName: string }) {
  const info = INDICATOR_INFO[indicatorName.toLowerCase()];

  if (!info) {
    return null;
  }

  return (
    <div className="indicator-info-tooltip">
      <div className="indicator-header">
        <h4>{info.name}</h4>
        <span className="indicator-badge">{indicatorName.toUpperCase()}</span>
      </div>
      <div className="indicator-description">
        <p><strong>Description:</strong> {info.description}</p>
        <p><strong>Usage:</strong> {info.usage}</p>
        {info.formula && (
          <div className="indicator-formula">
            <strong>Formula:</strong>
            <pre>{info.formula}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export function IndicatorHelp() {
  const [selectedIndicator, setSelectedIndicator] = useState<string>('');

  return (
    <div className="indicator-help">
      <h3>Technical Indicators Guide</h3>
      <p className="description">
        Learn about each technical indicator, how it's calculated, and how to use it in your trading strategies.
      </p>
      <div className="indicator-selector">
        <select value={selectedIndicator} onChange={(e) => setSelectedIndicator(e.target.value)}>
          <option value="">Select an indicator...</option>
          {Object.keys(INDICATOR_INFO).map((key) => (
            <option key={key} value={key}>
              {INDICATOR_INFO[key].name}
            </option>
          ))}
        </select>
      </div>
      {selectedIndicator && <IndicatorInfo indicatorName={selectedIndicator} />}
    </div>
  );
}

