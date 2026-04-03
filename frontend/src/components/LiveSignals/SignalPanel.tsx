import React, { useState } from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import { useUIStore, ALL_PAIRS } from '../../store/uiStore';
import { SignalCard } from './SignalCard';

export function SignalPanel() {
  const { signals, marketContext } = useNotificationStore();
  const { selectedPair } = useUIStore();
  const [filterPair, setFilterPair] = useState<string>('ALL');

  const visible = filterPair === 'ALL'
    ? signals
    : signals.filter((s) => s.pair === filterPair);

  // Show context for the currently filtered/selected pair
  const ctx = filterPair !== 'ALL' && marketContext?.pair === filterPair
    ? marketContext
    : marketContext?.pair === selectedPair
    ? marketContext
    : marketContext;

  return (
    <div className="panel signal-panel">
      <div className="panel-header">
        <span className="panel-title">Live Signals</span>
        {signals.length > 0 && (
          <span className="badge badge-green">{signals.length}</span>
        )}
      </div>

      {/* Pair filter tabs */}
      <div className="signal-pair-filter">
        <button
          className={`pair-filter-btn ${filterPair === 'ALL' ? 'active' : ''}`}
          onClick={() => setFilterPair('ALL')}
        >
          All
        </button>
        {ALL_PAIRS.map((p) => {
          const count = signals.filter((s) => s.pair === p.symbol).length;
          return (
            <button
              key={p.symbol}
              className={`pair-filter-btn ${filterPair === p.symbol ? 'active' : ''}`}
              onClick={() => setFilterPair(p.symbol)}
            >
              {p.display}
              {count > 0 && <span className="pair-count">{count}</span>}
            </button>
          );
        })}
      </div>

      {ctx && (
        <div className="market-summary">
          {ctx.display && (
            <div className="ms-item ms-wide">
              <span className="ms-label">Pair</span>
              <span className="ms-value">{ctx.display}</span>
            </div>
          )}
          <div className="ms-item">
            <span className="ms-label">Session</span>
            <span className="ms-value">{ctx.session}</span>
          </div>
          <div className="ms-item">
            <span className="ms-label">RSI</span>
            <span
              className={`ms-value ${
                ctx.rsi > 70 ? 'text-red' : ctx.rsi < 30 ? 'text-green' : 'text-muted'
              }`}
            >
              {ctx.rsi?.toFixed(1) ?? '—'}
            </span>
          </div>
          <div className="ms-item">
            <span className="ms-label">ATR</span>
            <span className="ms-value">{ctx.atr_pips ?? '—'}p</span>
          </div>
          <div className="ms-item ms-wide">
            <span className="ms-label">Position</span>
            <span className="ms-value">{ctx.range_position}</span>
          </div>
        </div>
      )}

      <div className="signal-list">
        {visible.length === 0 ? (
          <div className="no-signals">
            <div className="no-signals-icon">◎</div>
            <p>Scanning strategies...</p>
            <p className="text-muted">Signals appear here in real-time</p>
          </div>
        ) : (
          visible.map((s) => <SignalCard key={s.id} signal={s} />)
        )}
      </div>
    </div>
  );
}
