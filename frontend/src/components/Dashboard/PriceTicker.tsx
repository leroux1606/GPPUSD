import React, { useState, useEffect } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { formatPrice, formatPercentage } from '../../utils/formatters';

export function PriceTicker() {
  const { price, isConnected, isLoading, error } = useLiveData();
  const [previousPrice, setPreviousPrice] = useState<number | null>(null);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [priceChangePercent, setPriceChangePercent] = useState<number>(0);

  // Track price changes
  useEffect(() => {
    if (price?.mid && previousPrice !== null) {
      const change = price.mid - previousPrice;
      const changePercent = (change / previousPrice) * 100;
      setPriceChange(change);
      setPriceChangePercent(changePercent);
    }
    if (price?.mid) {
      setPreviousPrice(price.mid);
    }
  }, [price?.mid, previousPrice]);

  if (isLoading && !price) {
    return (
      <div className="price-ticker">
        <div className="symbol">GBP/USD</div>
        <div className="price">Loading...</div>
      </div>
    );
  }

  if (error && !price) {
    return (
      <div className="price-ticker">
        <div className="symbol">GBP/USD</div>
        <div className="price error">Error: {error}</div>
      </div>
    );
  }

  if (!price) {
    return (
      <div className="price-ticker">
        <div className="symbol">GBP/USD</div>
        <div className="price">--</div>
      </div>
    );
  }

  const direction = priceChange >= 0 ? 'up' : 'down';

  return (
    <div className="price-ticker">
      <div className="ticker-main">
        <div className="symbol">GBP/USD</div>
        <div className={`price ${direction}`}>
          {formatPrice(price.mid)}
        </div>
        <div className={`change ${direction}`}>
          {priceChange >= 0 ? '+' : ''}
          {formatPrice(priceChange, 5)} ({formatPercentage(priceChangePercent)})
        </div>
      </div>
      <div className="ticker-details">
        <div className="bid-ask">
          <span className="label">Bid:</span>
          <span className="value sell">{formatPrice(price.bid)}</span>
        </div>
        <div className="bid-ask">
          <span className="label">Ask:</span>
          <span className="value buy">{formatPrice(price.ask)}</span>
        </div>
        <div className="spread">
          <span className="label">Spread:</span>
          <span className="value">{formatPrice(price.spread * 10000, 1)} pips</span>
        </div>
      </div>
      <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? '● Live' : '○ Offline'}
      </div>
    </div>
  );
}
