import React from 'react';

const STRATEGY_DESCRIPTIONS: { [key: string]: { description: string; parameters: string[]; logic: string } } = {
  ma_crossover: {
    description: 'Moving Average Crossover strategy buys when fast MA crosses above slow MA (golden cross) and sells when fast MA crosses below slow MA (death cross).',
    parameters: ['fast_period', 'slow_period', 'ma_type'],
    logic: 'Buy: Fast MA > Slow MA AND previous Fast MA <= previous Slow MA\nSell: Fast MA < Slow MA AND previous Fast MA >= previous Slow MA',
  },
  rsi_divergence: {
    description: 'RSI Divergence strategy detects bullish divergence (price makes lower low, RSI makes higher low) and bearish divergence (price makes higher high, RSI makes lower high).',
    parameters: ['rsi_period', 'lookback', 'min_divergence_strength'],
    logic: 'Buy: Price makes lower low BUT RSI makes higher low\nSell: Price makes higher high BUT RSI makes lower high',
  },
  bollinger_breakout: {
    description: 'Bollinger Band Breakout strategy buys when price breaks above upper band and sells when price breaks below lower band, with volume confirmation.',
    parameters: ['period', 'std_dev', 'require_volume', 'volume_threshold'],
    logic: 'Buy: Price breaks above upper Bollinger Band\nSell: Price breaks below lower Bollinger Band',
  },
  macd_signal: {
    description: 'MACD Signal strategy buys when MACD line crosses above signal line and sells when MACD line crosses below signal line.',
    parameters: ['fast_period', 'slow_period', 'signal_period'],
    logic: 'Buy: MACD line crosses above signal line\nSell: MACD line crosses below signal line',
  },
  stochastic: {
    description: 'Stochastic Oscillator strategy buys when %K crosses above %D from oversold region and sells when %K crosses below %D from overbought region.',
    parameters: ['k_period', 'd_period', 'oversold', 'overbought'],
    logic: 'Buy: %K crosses above %D from oversold (< 20)\nSell: %K crosses below %D from overbought (> 80)',
  },
};

export function StrategyExplanation({ strategyType }: { strategyType: string }) {
  const strategy = STRATEGY_DESCRIPTIONS[strategyType];

  if (!strategy) {
    return <div>Strategy explanation not available</div>;
  }

  return (
    <div className="strategy-explanation">
      <h3>Strategy Explanation: {strategyType.replace('_', ' ').toUpperCase()}</h3>
      <div className="explanation-content">
        <div className="description-section">
          <h4>Description</h4>
          <p>{strategy.description}</p>
        </div>
        <div className="parameters-section">
          <h4>Parameters</h4>
          <ul>
            {strategy.parameters.map((param) => (
              <li key={param}>
                <strong>{param}</strong> - {getParameterDescription(param)}
              </li>
            ))}
          </ul>
        </div>
        <div className="logic-section">
          <h4>Trading Logic</h4>
          <pre>{strategy.logic}</pre>
        </div>
        <div className="visual-diagram">
          <h4>Visual Flow</h4>
          <div className="flow-diagram">
            <div className="flow-step">1. Calculate Indicators</div>
            <div className="flow-arrow">↓</div>
            <div className="flow-step">2. Check Entry Conditions</div>
            <div className="flow-arrow">↓</div>
            <div className="flow-step">3. Generate Buy/Sell Signal</div>
            <div className="flow-arrow">↓</div>
            <div className="flow-step">4. Execute Trade</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getParameterDescription(param: string): string {
  const descriptions: { [key: string]: string } = {
    fast_period: 'Period for fast moving average',
    slow_period: 'Period for slow moving average',
    ma_type: 'Type of moving average (SMA or EMA)',
    rsi_period: 'Period for RSI calculation',
    lookback: 'Number of bars to look back for divergence',
    period: 'Period for indicator calculation',
    std_dev: 'Standard deviation multiplier for Bollinger Bands',
    k_period: 'Period for %K line',
    d_period: 'Period for %D line',
    oversold: 'Oversold threshold (typically 20-30)',
    overbought: 'Overbought threshold (typically 70-80)',
  };
  return descriptions[param] || 'Parameter description not available';
}

