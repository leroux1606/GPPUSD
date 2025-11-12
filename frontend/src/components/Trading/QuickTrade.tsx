import React from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { tradingApi } from '../../services/api';
import { useTradingStore } from '../../store';

export function QuickTrade() {
  const { price } = useLiveData();
  const { addPosition } = useTradingStore();
  const [size, setSize] = React.useState(0.01);

  const handleQuickBuy = async () => {
    if (!price) return;
    try {
      const order = {
        symbol: 'GBP_USD',
        side: 'buy',
        size,
        price: price.ask,
      };
      const response = await tradingApi.openPosition(order);
      addPosition({
        id: response.data.order_id,
        symbol: 'GBP_USD',
        side: 'buy',
        size,
        entry_price: price.ask,
        timestamp: new Date().toISOString(),
        status: 'open',
      });
    } catch (error) {
      console.error('Quick buy error:', error);
    }
  };

  const handleQuickSell = async () => {
    if (!price) return;
    try {
      const order = {
        symbol: 'GBP_USD',
        side: 'sell',
        size,
        price: price.bid,
      };
      const response = await tradingApi.openPosition(order);
      addPosition({
        id: response.data.order_id,
        symbol: 'GBP_USD',
        side: 'sell',
        size,
        entry_price: price.bid,
        timestamp: new Date().toISOString(),
        status: 'open',
      });
    } catch (error) {
      console.error('Quick sell error:', error);
    }
  };

  return (
    <div className="quick-trade">
      <h3>Quick Trade</h3>
      {price && (
        <div className="current-price">
          <div>Bid: {price.bid.toFixed(5)}</div>
          <div>Ask: {price.ask.toFixed(5)}</div>
        </div>
      )}
      <div className="quick-trade-controls">
        <input
          type="number"
          step="0.01"
          value={size}
          onChange={(e) => setSize(parseFloat(e.target.value))}
          placeholder="Lot size"
        />
        <button onClick={handleQuickBuy} className="buy-btn">
          Quick Buy
        </button>
        <button onClick={handleQuickSell} className="sell-btn">
          Quick Sell
        </button>
      </div>
    </div>
  );
}

