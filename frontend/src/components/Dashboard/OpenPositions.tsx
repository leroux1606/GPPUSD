import React from 'react';
import { useTradingStore } from '../../store';
import { formatCurrency, formatDate } from '../../utils/formatters';

export function OpenPositions() {
  const { positions } = useTradingStore();

  return (
    <div className="open-positions">
      <h3>Open Positions</h3>
      {positions.length === 0 ? (
        <p>No open positions</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Side</th>
              <th>Size</th>
              <th>Entry Price</th>
              <th>Stop Loss</th>
              <th>Take Profit</th>
              <th>P&L</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => (
              <tr key={position.id}>
                <td>{position.symbol}</td>
                <td className={position.side === 'buy' ? 'buy' : 'sell'}>
                  {position.side.toUpperCase()}
                </td>
                <td>{position.size}</td>
                <td>{position.entry_price.toFixed(5)}</td>
                <td>{position.stop_loss?.toFixed(5) || '-'}</td>
                <td>{position.take_profit?.toFixed(5) || '-'}</td>
                <td className={position.pnl && position.pnl >= 0 ? 'positive' : 'negative'}>
                  {position.pnl ? formatCurrency(position.pnl) : '-'}
                </td>
                <td>{formatDate(position.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

