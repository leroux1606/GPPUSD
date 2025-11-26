import React, { useState } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { tradingApi } from '../../services/api';
import { useTradingStore } from '../../store/tradingStore';
import { formatPrice } from '../../utils/formatters';
import { InlineSpinner } from '../Common/LoadingSpinner';

export function QuickTrade() {
  const { price, isConnected, error: priceError } = useLiveData();
  const { addPosition, setError } = useTradingStore();
  const [size, setSize] = useState(0.01);
  const [isSubmitting, setIsSubmitting] = useState<'buy' | 'sell' | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleQuickTrade = async (side: 'buy' | 'sell') => {
    if (!price) {
      setFeedback({ type: 'error', message: 'No price data available' });
      return;
    }

    if (size <= 0) {
      setFeedback({ type: 'error', message: 'Invalid lot size' });
      return;
    }

    setIsSubmitting(side);
    setFeedback(null);

    try {
      const entryPrice = side === 'buy' ? price.ask : price.bid;
      const order = {
        symbol: 'GBP_USD',
        side,
        size,
        price: entryPrice,
      };

      const response = await tradingApi.openPosition(order);
      
      addPosition({
        id: response.data.order_id || `trade_${Date.now()}`,
        symbol: 'GBP_USD',
        side,
        size,
        entry_price: entryPrice,
        timestamp: new Date().toISOString(),
        status: 'open',
      });

      setFeedback({ 
        type: 'success', 
        message: `${side.toUpperCase()} order placed at ${formatPrice(entryPrice)}` 
      });

      // Clear feedback after 3 seconds
      setTimeout(() => setFeedback(null), 3000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to place order';
      setFeedback({ type: 'error', message: errorMessage });
      setError(errorMessage);
    } finally {
      setIsSubmitting(null);
    }
  };

  return (
    <div className="quick-trade">
      <h3>Quick Trade</h3>
      
      {/* Price Display */}
      <div className="price-display">
        {price ? (
          <>
            <div className="price-box sell">
              <span className="label">SELL</span>
              <span className="price">{formatPrice(price.bid)}</span>
            </div>
            <div className="spread-indicator">
              <span className="spread-value">
                {formatPrice(price.spread * 10000, 1)} pips
              </span>
            </div>
            <div className="price-box buy">
              <span className="label">BUY</span>
              <span className="price">{formatPrice(price.ask)}</span>
            </div>
          </>
        ) : (
          <div className="price-loading">
            {priceError ? (
              <span className="error">{priceError}</span>
            ) : (
              <span>Loading prices...</span>
            )}
          </div>
        )}
      </div>

      {/* Connection Status */}
      <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? '● Live Prices' : '○ Connecting...'}
      </div>

      {/* Trade Controls */}
      <div className="quick-trade-controls">
        <div className="size-input">
          <label htmlFor="lot-size">Lot Size</label>
          <input
            id="lot-size"
            type="number"
            step="0.01"
            min="0.01"
            max="100"
            value={size}
            onChange={(e) => setSize(Math.max(0.01, parseFloat(e.target.value) || 0.01))}
            disabled={isSubmitting !== null}
          />
        </div>
        
        <div className="trade-buttons">
          <button
            onClick={() => handleQuickTrade('sell')}
            className="sell-btn"
            disabled={!price || isSubmitting !== null}
          >
            {isSubmitting === 'sell' ? (
              <>
                <InlineSpinner size={14} /> Selling...
              </>
            ) : (
              <>SELL</>
            )}
          </button>
          <button
            onClick={() => handleQuickTrade('buy')}
            className="buy-btn"
            disabled={!price || isSubmitting !== null}
          >
            {isSubmitting === 'buy' ? (
              <>
                <InlineSpinner size={14} /> Buying...
              </>
            ) : (
              <>BUY</>
            )}
          </button>
        </div>
      </div>

      {/* Feedback Message */}
      {feedback && (
        <div className={`trade-feedback ${feedback.type}`}>
          {feedback.message}
        </div>
      )}

      {/* Quick Size Buttons */}
      <div className="quick-sizes">
        {[0.01, 0.05, 0.1, 0.5, 1].map((lotSize) => (
          <button
            key={lotSize}
            onClick={() => setSize(lotSize)}
            className={size === lotSize ? 'active' : ''}
            disabled={isSubmitting !== null}
          >
            {lotSize}
          </button>
        ))}
      </div>
    </div>
  );
}
