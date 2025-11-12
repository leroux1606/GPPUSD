import React from 'react';
import { useLiveData } from '../hooks/useLiveData';
import { formatPrice, formatPercentage } from '../utils/formatters';

export function PriceTicker() {
  const { price } = useLiveData();

  if (!price) {
    return <div>Loading...</div>;
  }

  const change = price.mid - (price.mid * 0.999); // Mock change
  const changePercent = (change / price.mid) * 100;

  return (
    <div className="price-ticker">
      <div className="symbol">GBP/USD</div>
      <div className={`price ${change >= 0 ? 'up' : 'down'}`}>
        {formatPrice(price.mid)}
      </div>
      <div className={`change ${change >= 0 ? 'up' : 'down'}`}>
        {change >= 0 ? '+' : ''}{formatPrice(change, 5)} ({formatPercentage(changePercent)})
      </div>
      <div className="spread">Spread: {formatPrice(price.spread, 5)}</div>
    </div>
  );
}

