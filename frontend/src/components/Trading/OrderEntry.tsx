import React, { useState } from 'react';
import { tradingApi } from '../../services/api';
import { useTradingStore } from '../../store';
import { formatCurrency } from '../../utils/formatters';

export function OrderEntry() {
  const { addPosition } = useTradingStore();
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [size, setSize] = useState(0.01);
  const [stopLoss, setStopLoss] = useState(0);
  const [takeProfit, setTakeProfit] = useState(0);

  const handlePlaceOrder = async () => {
    try {
      const order = {
        symbol: 'GBP_USD',
        side,
        size,
        stop_loss: stopLoss,
        take_profit: takeProfit,
      };
      const response = await tradingApi.openPosition(order);
      addPosition({
        id: response.data.order_id,
        symbol: 'GBP_USD',
        side,
        size,
        entry_price: response.data.price,
        stop_loss: stopLoss,
        take_profit: takeProfit,
        timestamp: new Date().toISOString(),
        status: 'open',
      });
    } catch (error) {
      console.error('Order error:', error);
    }
  };

  return (
    <div className="order-entry">
      <h3>Place Order</h3>
      <div className="order-form">
        <div className="side-selector">
          <button
            className={side === 'buy' ? 'active' : ''}
            onClick={() => setSide('buy')}
          >
            Buy
          </button>
          <button
            className={side === 'sell' ? 'active' : ''}
            onClick={() => setSide('sell')}
          >
            Sell
          </button>
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
        <div>
          <label>Stop Loss (pips)</label>
          <input
            type="number"
            value={stopLoss}
            onChange={(e) => setStopLoss(parseFloat(e.target.value))}
          />
        </div>
        <div>
          <label>Take Profit (pips)</label>
          <input
            type="number"
            value={takeProfit}
            onChange={(e) => setTakeProfit(parseFloat(e.target.value))}
          />
        </div>
        <button onClick={handlePlaceOrder} className="place-order-btn">
          Place Order
        </button>
      </div>
    </div>
  );
}

