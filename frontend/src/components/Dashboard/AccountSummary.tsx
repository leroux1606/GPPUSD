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
          <value>{formatCurrency(balance)}</value>
        </div>
        <div className="metric">
          <label>Equity</label>
          <value className={pnl >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(equity)}
          </value>
        </div>
        <div className="metric">
          <label>Margin</label>
          <value>{formatCurrency(margin)}</value>
        </div>
        <div className="metric">
          <label>Free Margin</label>
          <value>{formatCurrency(freeMargin)}</value>
        </div>
        <div className="metric">
          <label>Margin Level</label>
          <value>{formatPercentage(marginLevel)}</value>
        </div>
        <div className="metric">
          <label>P&L</label>
          <value className={pnl >= 0 ? 'positive' : 'negative'}>
            {formatCurrency(pnl)}
          </value>
        </div>
      </div>
    </div>
  );
}

