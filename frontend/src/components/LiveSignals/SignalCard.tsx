import React from 'react';
import { LiveSignal } from '../../types';

interface Props {
  signal: LiveSignal;
}

function elapsed(ts: string): string {
  const ms = Date.now() - new Date(ts).getTime();
  const m = Math.floor(ms / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  return `${Math.floor(m / 60)}h ${m % 60}m ago`;
}

function ConfidenceBar({ value }: { value: number }) {
  const color =
    value >= 70 ? 'var(--green)' :
    value >= 50 ? 'var(--amber)' :
    'var(--text-muted)';
  return (
    <div className="confidence-bar-wrap" title={`Confidence: ${value}%`}>
      <div className="confidence-bar-track">
        <div
          className="confidence-bar-fill"
          style={{ width: `${value}%`, background: color }}
        />
      </div>
      <span className="confidence-label" style={{ color }}>{value}%</span>
    </div>
  );
}

export function SignalCard({ signal }: Props) {
  const isBuy = signal.direction === 'buy';
  const isConfluence = signal.confluence === true;
  const strategyCount = signal.strategies?.length ?? 1;

  return (
    <div className={`signal-card ${isBuy ? 'signal-buy' : 'signal-sell'} ${isConfluence ? 'signal-confluence' : ''}`}>
      <div className="signal-header">
        <span className={`signal-direction ${isBuy ? 'buy' : 'sell'}`}>
          {isBuy ? '▲ BUY' : '▼ SELL'}
        </span>
        {signal.pair_display && (
          <span className="signal-pair-badge">{signal.pair_display}</span>
        )}
        {isConfluence && (
          <span className="confluence-badge" title={`${strategyCount} strategies agree`}>
            ⚡ {strategyCount}× CONFLUENCE
          </span>
        )}
        <span className="signal-strategy">{signal.strategy}</span>
        <span className="signal-time">{elapsed(signal.timestamp)}</span>
      </div>

      {signal.confidence !== undefined && (
        <ConfidenceBar value={signal.confidence} />
      )}

      <div className="signal-levels">
        <div className="level-row">
          <span className="level-label">Entry</span>
          <span className="level-value entry">{signal.entry.toFixed(5)}</span>
        </div>
        <div className="level-row">
          <span className="level-label">Stop Loss</span>
          <span className="level-value sl">{signal.stop_loss.toFixed(5)}</span>
          <span className="level-pips">−{signal.risk_pips.toFixed(1)} pips</span>
        </div>
        <div className="level-row">
          <span className="level-label">Take Profit</span>
          <span className="level-value tp">{signal.take_profit.toFixed(5)}</span>
          <span className="level-pips">+{signal.reward_pips.toFixed(1)} pips</span>
        </div>
      </div>

      <div className="signal-meta">
        <div className="meta-item">
          <span className="meta-label">R/R</span>
          <span className="meta-value">1:{signal.rr_ratio.toFixed(2)}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Lot</span>
          <span className="meta-value">{signal.suggested_lot.toFixed(2)}</span>
        </div>
        {signal.atr_pips && (
          <div className="meta-item">
            <span className="meta-label">ATR</span>
            <span className="meta-value">{signal.atr_pips}p</span>
          </div>
        )}
      </div>

      {signal.ai_analysis && (
        <div className="signal-ai-note">
          <span className="ai-icon">AI</span>
          <span>{signal.ai_analysis}</span>
        </div>
      )}
    </div>
  );
}
