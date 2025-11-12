import React, { useState } from 'react';
import { tradingApi } from '../../services/api';
import { useTradingStore } from '../../store';
import { calculatePnL, calculateRiskReward } from '../../utils/calculations';

export function RiskCalculator() {
  const [entryPrice, setEntryPrice] = useState(1.2500);
  const [stopLoss, setStopLoss] = useState(1.2450);
  const [takeProfit, setTakeProfit] = useState(1.2600);
  const [size, setSize] = useState(0.01);
  const [side, setSide] = useState<'buy' | 'sell'>('buy');

  const risk = Math.abs(entryPrice - stopLoss) * 10000 * size * 10; // In dollars
  const reward = Math.abs(takeProfit - entryPrice) * 10000 * size * 10;
  const riskRewardRatio = reward / risk;

  return (
    <div className="risk-calculator">
      <h3>Risk Calculator</h3>
      <div className="calculator-form">
        <div>
          <label>Side</label>
          <select value={side} onChange={(e) => setSide(e.target.value as 'buy' | 'sell')}>
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </div>
        <div>
          <label>Entry Price</label>
          <input
            type="number"
            step="0.0001"
            value={entryPrice}
            onChange={(e) => setEntryPrice(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label>Stop Loss</label>
          <input
            type="number"
            step="0.0001"
            value={stopLoss}
            onChange={(e) => setStopLoss(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label>Take Profit</label>
          <input
            type="number"
            step="0.0001"
            value={takeProfit}
            onChange={(e) => setTakeProfit(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label>Lot Size</label>
          <input
            type="number"
            step="0.01"
            value={size}
            onChange={(e) => setSize(parseFloat(e.target.value))}
          />
        </div>
      </div>
      <div className="risk-results">
        <div className="risk-metric">
          <label>Risk</label>
          <value className="negative">${risk.toFixed(2)}</value>
        </div>
        <div className="risk-metric">
          <label>Reward</label>
          <value className="positive">${reward.toFixed(2)}</value>
        </div>
        <div className="risk-metric">
          <label>Risk/Reward Ratio</label>
          <value>{riskRewardRatio.toFixed(2)}</value>
        </div>
      </div>
    </div>
  );
}

