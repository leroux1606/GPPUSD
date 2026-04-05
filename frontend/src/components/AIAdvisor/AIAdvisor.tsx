import React, { useState, useCallback } from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import { useUIStore, ALL_PAIRS } from '../../store/uiStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { signalsApi } from '../../services/api';

function formatTime(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function AIAdvisor() {
  const { aiCommentary, aiCommentaryTime, marketContext } = useNotificationStore();
  const { selectedPair } = useUIStore();
  const { requestAiCommentary } = useWebSocket();
  const [loading, setLoading] = useState(false);
  const [autoMode, setAutoMode] = useState(false);

  // Only use market context if it matches the currently selected pair
  const activeContext = marketContext?.pair === selectedPair ? marketContext : null;
  const pairDisplay = ALL_PAIRS.find((p) => p.symbol === selectedPair)?.display ?? selectedPair;

  const handleRequest = useCallback(async () => {
    setLoading(true);
    try {
      // Build context: use matching market context or fall back to just the pair
      const ctx = activeContext
        ? (activeContext as unknown as Record<string, unknown>)
        : { pair: selectedPair, symbol: selectedPair };
      const resp = await signalsApi.getAiCommentary(ctx);
      if (resp.data?.commentary) {
        useNotificationStore.getState().setAiCommentary(resp.data.commentary);
      }
    } catch {
      // Fallback to WS
      requestAiCommentary(activeContext || { pair: selectedPair });
    } finally {
      setLoading(false);
    }
  }, [activeContext, selectedPair, requestAiCommentary]);

  return (
    <div className="panel ai-panel">
      <div className="panel-header">
        <span className="panel-title">AI Advisor</span>
        <div className="ai-controls">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={autoMode}
              onChange={(e) => setAutoMode(e.target.checked)}
            />
            Auto
          </label>
          <button
            className={`btn-sm ${loading ? 'btn-loading' : 'btn-primary'}`}
            onClick={handleRequest}
            disabled={loading}
          >
            {loading ? '...' : 'Analyse'}
          </button>
        </div>
      </div>

      <div className="ai-content">
        {aiCommentary ? (
          <>
            <p className="ai-text">{aiCommentary}</p>
            {aiCommentaryTime && (
              <span className="ai-timestamp">Updated {formatTime(aiCommentaryTime)}</span>
            )}
          </>
        ) : (
          <div className="ai-placeholder">
            <p className="text-muted">
              Click <strong>Analyse</strong> to get real-time {pairDisplay} commentary.
            </p>
            <p className="text-muted small">
              Requires OpenRouter API key in Settings.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
