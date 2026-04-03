import React from 'react';
import { useTradingStore } from '../../store';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

export function AccountSummary() {
  const { balance, equity, margin } = useTradingStore();

  const freeMargin = equity - margin;
  const marginLevel = margin > 0 ? (equity / margin) * 100 : 0;
  const pnl = equity - balance;

  return (
    <div className="account-summary">
      <h3>Account Summary</h3>
      <div className="metrics">
        <div className="metric">
          <label>Balance</label>
          <span>{formatCurrency(balance)}</span>
        </div>
        <div className="metric">
          <label>Equity</label>
          <span className={pnl >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(equity)}
          </span>
        </div>
        <div className="metric">
          <label>Margin</label>
          <span>{formatCurrency(margin)}</span>
        </div>
        <div className="metric">
          <label>Free Margin</label>
          <span>{formatCurrency(freeMargin)}</span>
        </div>
        <div className="metric">
          <label>Margin Level</label>
          <span>{formatPercentage(marginLevel)}</span>
        </div>
        <div className="metric">
          <label>P&L</label>
          <span className={pnl >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(pnl)}
          </span>
        </div>
      </div>
    </div>
  );
}

