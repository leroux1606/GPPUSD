import React from 'react';
import { useTradingStore } from '../../store';
import { formatCurrency, formatDate } from '../../utils/formatters';

export function TradeHistory() {
  const { positions } = useTradingStore();
  const closedTrades = positions.filter((p) => p.status === 'closed');

  return (
    <div className="trade-history">
      <h3>Trade History</h3>
      {closedTrades.length === 0 ? (
        <p>No closed trades</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Size</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            {closedTrades.map((trade) => (
              <tr key={trade.id}>
                <td>{formatDate(trade.timestamp)}</td>
                <td>{trade.symbol}</td>
                <td className={trade.side === 'buy' ? 'buy' : 'sell'}>
                  {trade.side.toUpperCase()}
                </td>
                <td>{trade.size}</td>
                <td>{trade.entry_price.toFixed(5)}</td>
                <td>{trade.exit_price?.toFixed(5) || '-'}</td>
                <td className={trade.pnl && trade.pnl >= 0 ? 'positive' : 'negative'}>
                  {trade.pnl ? formatCurrency(trade.pnl) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

