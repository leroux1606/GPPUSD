import React, { useState, useMemo } from 'react';
import { tradingApi } from '../../services/api';
import { useTradingStore } from '../../store/tradingStore';
import { useLiveData } from '../../hooks/useLiveData';
import { formatCurrency, formatPrice } from '../../utils/formatters';
import { InlineSpinner } from '../Common/LoadingSpinner';

interface OrderFormData {
  side: 'buy' | 'sell';
  size: number;
  stopLossPips: number;
  takeProfitPips: number;
  orderType: 'market' | 'limit';
  limitPrice: number | null;
}

export function OrderEntry() {
  const { addPosition, setError, balance } = useTradingStore();
  const { price } = useLiveData();
  
  const [form, setForm] = useState<OrderFormData>({
    side: 'buy',
    size: 0.01,
    stopLossPips: 20,
    takeProfitPips: 40,
    orderType: 'market',
    limitPrice: null,
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Calculate SL/TP prices based on current price and pips
  const calculations = useMemo(() => {
    if (!price) return null;

    const entryPrice = form.side === 'buy' ? price.ask : price.bid;
    const pipValue = 0.0001; // For GBP/USD
    
    let stopLoss: number;
    let takeProfit: number;
    
    if (form.side === 'buy') {
      stopLoss = entryPrice - (form.stopLossPips * pipValue);
      takeProfit = entryPrice + (form.takeProfitPips * pipValue);
    } else {
      stopLoss = entryPrice + (form.stopLossPips * pipValue);
      takeProfit = entryPrice - (form.takeProfitPips * pipValue);
    }

    // Risk calculation (simplified)
    const riskAmount = form.stopLossPips * 10 * form.size; // $10 per pip per lot
    const rewardAmount = form.takeProfitPips * 10 * form.size;
    const riskPercent = (riskAmount / balance) * 100;
    const riskRewardRatio = form.stopLossPips > 0 ? form.takeProfitPips / form.stopLossPips : 0;

    return {
      entryPrice,
      stopLoss,
      takeProfit,
      riskAmount,
      rewardAmount,
      riskPercent,
      riskRewardRatio,
    };
  }, [price, form, balance]);

  const handleSubmit = async () => {
    if (!price || !calculations) {
      setFeedback({ type: 'error', message: 'No price data available' });
      return;
    }

    if (form.size <= 0) {
      setFeedback({ type: 'error', message: 'Invalid lot size' });
      return;
    }

    setIsSubmitting(true);
    setFeedback(null);

    try {
      const order = {
        symbol: 'GBP_USD',
        side: form.side,
        size: form.size,
        type: form.orderType,
        price: form.orderType === 'limit' ? form.limitPrice : undefined,
        stop_loss: form.stopLossPips > 0 ? calculations.stopLoss : undefined,
        take_profit: form.takeProfitPips > 0 ? calculations.takeProfit : undefined,
      };

      const response = await tradingApi.openPosition(order);

      addPosition({
        id: response.data.order_id || `trade_${Date.now()}`,
        symbol: 'GBP_USD',
        side: form.side,
        size: form.size,
        entry_price: calculations.entryPrice,
        stop_loss: calculations.stopLoss,
        take_profit: calculations.takeProfit,
        timestamp: new Date().toISOString(),
        status: 'open',
      });

      setFeedback({
        type: 'success',
        message: `${form.side.toUpperCase()} order placed successfully`,
      });

      // Reset form
      setForm((prev) => ({ ...prev, size: 0.01, stopLossPips: 20, takeProfitPips: 40 }));
      setTimeout(() => setFeedback(null), 3000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to place order';
      setFeedback({ type: 'error', message: errorMessage });
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="order-entry">
      <h3>Place Order</h3>

      {/* Side Selector */}
      <div className="side-selector">
        <button
          className={form.side === 'buy' ? 'active buy' : ''}
          onClick={() => setForm((prev) => ({ ...prev, side: 'buy' }))}
          disabled={isSubmitting}
        >
          BUY
        </button>
        <button
          className={form.side === 'sell' ? 'active sell' : ''}
          onClick={() => setForm((prev) => ({ ...prev, side: 'sell' }))}
          disabled={isSubmitting}
        >
          SELL
        </button>
      </div>

      {/* Order Form */}
      <div className="order-form">
        <div className="form-group">
          <label>Lot Size</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            max="100"
            value={form.size}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                size: Math.max(0.01, parseFloat(e.target.value) || 0.01),
              }))
            }
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label>Stop Loss (pips)</label>
          <input
            type="number"
            step="1"
            min="0"
            max="1000"
            value={form.stopLossPips}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                stopLossPips: Math.max(0, parseInt(e.target.value) || 0),
              }))
            }
            disabled={isSubmitting}
          />
          {calculations && form.stopLossPips > 0 && (
            <span className="calculated-price">
              @ {formatPrice(calculations.stopLoss)}
            </span>
          )}
        </div>

        <div className="form-group">
          <label>Take Profit (pips)</label>
          <input
            type="number"
            step="1"
            min="0"
            max="1000"
            value={form.takeProfitPips}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                takeProfitPips: Math.max(0, parseInt(e.target.value) || 0),
              }))
            }
            disabled={isSubmitting}
          />
          {calculations && form.takeProfitPips > 0 && (
            <span className="calculated-price">
              @ {formatPrice(calculations.takeProfit)}
            </span>
          )}
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          className="advanced-toggle"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>

        {showAdvanced && (
          <div className="advanced-options">
            <div className="form-group">
              <label>Order Type</label>
              <select
                value={form.orderType}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    orderType: e.target.value as 'market' | 'limit',
                  }))
                }
                disabled={isSubmitting}
              >
                <option value="market">Market</option>
                <option value="limit">Limit</option>
              </select>
            </div>

            {form.orderType === 'limit' && (
              <div className="form-group">
                <label>Limit Price</label>
                <input
                  type="number"
                  step="0.00001"
                  value={form.limitPrice || ''}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      limitPrice: parseFloat(e.target.value) || null,
                    }))
                  }
                  disabled={isSubmitting}
                />
              </div>
            )}
          </div>
        )}

        {/* Risk Summary */}
        {calculations && (
          <div className="risk-summary">
            <div className="risk-item">
              <span className="label">Risk:</span>
              <span className="value negative">
                {formatCurrency(calculations.riskAmount)} ({calculations.riskPercent.toFixed(2)}%)
              </span>
            </div>
            <div className="risk-item">
              <span className="label">Reward:</span>
              <span className="value positive">
                {formatCurrency(calculations.rewardAmount)}
              </span>
            </div>
            <div className="risk-item">
              <span className="label">R:R Ratio:</span>
              <span className={`value ${calculations.riskRewardRatio >= 1 ? 'positive' : 'negative'}`}>
                1:{calculations.riskRewardRatio.toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          className={`place-order-btn ${form.side}`}
          disabled={isSubmitting || !price}
        >
          {isSubmitting ? (
            <>
              <InlineSpinner size={16} /> Placing Order...
            </>
          ) : (
            `Place ${form.side.toUpperCase()} Order`
          )}
        </button>

        {/* Feedback */}
        {feedback && (
          <div className={`order-feedback ${feedback.type}`}>{feedback.message}</div>
        )}
      </div>
    </div>
  );
}
