import React from 'react';
import { Trade } from '../../types';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface TradeListProps {
  trades: Trade[];
}

export function TradeList({ trades }: TradeListProps) {
  return (
    <div className="trade-list">
      <h3>Trade History</h3>
      {trades.length === 0 ? (
        <p>No trades</p>
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
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
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
                <td>{trade.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

