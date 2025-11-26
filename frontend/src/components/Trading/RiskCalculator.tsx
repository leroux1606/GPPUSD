import React, { useState, useMemo } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { useTradingStore } from '../../store/tradingStore';
import { formatCurrency, formatPrice, formatPercentage } from '../../utils/formatters';

interface RiskInputs {
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  lotSize: number;
  side: 'buy' | 'sell';
  accountRiskPercent: number;
}

export function RiskCalculator() {
  const { price } = useLiveData();
  const { balance } = useTradingStore();
  
  const [inputs, setInputs] = useState<RiskInputs>({
    entryPrice: 1.25,
    stopLoss: 1.245,
    takeProfit: 1.26,
    lotSize: 0.1,
    side: 'buy',
    accountRiskPercent: 1,
  });

  // Use live price as default entry
  React.useEffect(() => {
    if (price?.mid && inputs.entryPrice === 1.25) {
      const mid = price.mid;
      setInputs((prev) => ({
        ...prev,
        entryPrice: mid,
        stopLoss: mid - 0.005,
        takeProfit: mid + 0.01,
      }));
    }
  }, [price?.mid]);

  const calculations = useMemo(() => {
    const { entryPrice, stopLoss, takeProfit, lotSize, side } = inputs;
    const pipValue = 0.0001;
    const pipValuePerLot = 10; // $10 per pip for standard lot GBP/USD

    // Calculate pip distances
    let slPips: number;
    let tpPips: number;

    if (side === 'buy') {
      slPips = (entryPrice - stopLoss) / pipValue;
      tpPips = (takeProfit - entryPrice) / pipValue;
    } else {
      slPips = (stopLoss - entryPrice) / pipValue;
      tpPips = (entryPrice - takeProfit) / pipValue;
    }

    // Calculate dollar amounts
    const riskDollars = Math.abs(slPips) * pipValuePerLot * lotSize;
    const rewardDollars = Math.abs(tpPips) * pipValuePerLot * lotSize;
    const riskRewardRatio = slPips !== 0 ? Math.abs(tpPips / slPips) : 0;

    // Calculate risk as percentage of balance
    const riskPercent = (riskDollars / balance) * 100;
    const rewardPercent = (rewardDollars / balance) * 100;

    // Calculate optimal lot size based on account risk percentage
    const maxRiskDollars = (inputs.accountRiskPercent / 100) * balance;
    const optimalLotSize = Math.abs(slPips) > 0 
      ? maxRiskDollars / (Math.abs(slPips) * pipValuePerLot)
      : 0;

    // Validate SL/TP positions
    let slValid = true;
    let tpValid = true;
    
    if (side === 'buy') {
      slValid = stopLoss < entryPrice;
      tpValid = takeProfit > entryPrice;
    } else {
      slValid = stopLoss > entryPrice;
      tpValid = takeProfit < entryPrice;
    }

    return {
      slPips: Math.abs(slPips),
      tpPips: Math.abs(tpPips),
      riskDollars,
      rewardDollars,
      riskRewardRatio,
      riskPercent,
      rewardPercent,
      optimalLotSize,
      slValid,
      tpValid,
      isValid: slValid && tpValid,
    };
  }, [inputs, balance]);

  const handleInputChange = (field: keyof RiskInputs, value: number | string) => {
    setInputs((prev) => ({
      ...prev,
      [field]: typeof value === 'string' ? parseFloat(value) || 0 : value,
    }));
  };

  return (
    <div className="risk-calculator">
      <h3>Risk Calculator</h3>
      
      <div className="calculator-form">
        {/* Side Selection */}
        <div className="form-row">
          <label>Trade Direction</label>
          <div className="side-toggle">
            <button
              className={inputs.side === 'buy' ? 'active buy' : ''}
              onClick={() => setInputs((prev) => ({ ...prev, side: 'buy' }))}
            >
              BUY
            </button>
            <button
              className={inputs.side === 'sell' ? 'active sell' : ''}
              onClick={() => setInputs((prev) => ({ ...prev, side: 'sell' }))}
            >
              SELL
            </button>
          </div>
        </div>

        {/* Entry Price */}
        <div className="form-row">
          <label>Entry Price</label>
          <input
            type="number"
            step="0.00001"
            value={inputs.entryPrice}
            onChange={(e) => handleInputChange('entryPrice', e.target.value)}
          />
          {price && (
            <button
              className="use-current"
              onClick={() => handleInputChange('entryPrice', inputs.side === 'buy' ? price.ask : price.bid)}
            >
              Use Current
            </button>
          )}
        </div>

        {/* Stop Loss */}
        <div className="form-row">
          <label>Stop Loss</label>
          <input
            type="number"
            step="0.00001"
            value={inputs.stopLoss}
            onChange={(e) => handleInputChange('stopLoss', e.target.value)}
            className={!calculations.slValid ? 'invalid' : ''}
          />
          <span className="pip-value">
            {calculations.slPips.toFixed(1)} pips
          </span>
        </div>

        {/* Take Profit */}
        <div className="form-row">
          <label>Take Profit</label>
          <input
            type="number"
            step="0.00001"
            value={inputs.takeProfit}
            onChange={(e) => handleInputChange('takeProfit', e.target.value)}
            className={!calculations.tpValid ? 'invalid' : ''}
          />
          <span className="pip-value">
            {calculations.tpPips.toFixed(1)} pips
          </span>
        </div>

        {/* Lot Size */}
        <div className="form-row">
          <label>Lot Size</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={inputs.lotSize}
            onChange={(e) => handleInputChange('lotSize', e.target.value)}
          />
        </div>

        {/* Account Risk % */}
        <div className="form-row">
          <label>Account Risk %</label>
          <input
            type="number"
            step="0.5"
            min="0.1"
            max="10"
            value={inputs.accountRiskPercent}
            onChange={(e) => handleInputChange('accountRiskPercent', e.target.value)}
          />
        </div>
      </div>

      {/* Validation Warning */}
      {!calculations.isValid && (
        <div className="validation-warning">
          ⚠️ Invalid SL/TP placement for {inputs.side.toUpperCase()} order
        </div>
      )}

      {/* Results */}
      <div className="risk-results">
        <div className="result-row">
          <div className="risk-metric negative">
            <label>Risk</label>
            <span className="value">{formatCurrency(calculations.riskDollars)}</span>
            <span className="percent">({formatPercentage(calculations.riskPercent)})</span>
          </div>
          <div className="risk-metric positive">
            <label>Reward</label>
            <span className="value">{formatCurrency(calculations.rewardDollars)}</span>
            <span className="percent">({formatPercentage(calculations.rewardPercent)})</span>
          </div>
        </div>

        <div className="result-row">
          <div className="risk-metric">
            <label>Risk:Reward Ratio</label>
            <span className={`value ${calculations.riskRewardRatio >= 1 ? 'positive' : 'negative'}`}>
              1:{calculations.riskRewardRatio.toFixed(2)}
            </span>
          </div>
          <div className="risk-metric">
            <label>Optimal Lot Size</label>
            <span className="value">
              {calculations.optimalLotSize.toFixed(2)} lots
            </span>
            <button
              className="use-optimal"
              onClick={() => handleInputChange('lotSize', calculations.optimalLotSize)}
            >
              Use
            </button>
          </div>
        </div>

        <div className="result-row">
          <div className="risk-metric">
            <label>Account Balance</label>
            <span className="value">{formatCurrency(balance)}</span>
          </div>
          <div className="risk-metric">
            <label>Max Risk ({inputs.accountRiskPercent}%)</label>
            <span className="value">
              {formatCurrency((inputs.accountRiskPercent / 100) * balance)}
            </span>
          </div>
        </div>
      </div>

      {/* Risk Warning */}
      {calculations.riskPercent > 2 && (
        <div className="risk-warning">
          ⚠️ Risk exceeds 2% of account. Consider reducing lot size.
        </div>
      )}
    </div>
  );
}
