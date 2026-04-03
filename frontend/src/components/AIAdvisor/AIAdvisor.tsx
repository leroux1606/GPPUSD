import React, { useState, useCallback } from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { signalsApi } from '../../services/api';

function formatTime(iso: string | null): string {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function AIAdvisor() {
  const { aiCommentary, aiCommentaryTime, marketContext } = useNotificationStore();
  const { requestAiCommentary } = useWebSocket();
  const [loading, setLoading] = useState(false);
  const [autoMode, setAutoMode] = useState(false);

  const handleRequest = useCallback(async () => {
    setLoading(true);
    try {
      if (marketContext) {
        // Try via REST first (more reliable than WS for on-demand requests)
        const resp = await signalsApi.getAiCommentary(marketContext as unknown as Record<string, unknown>);
        if (resp.data?.commentary) {
          useNotificationStore.getState().setAiCommentary(resp.data.commentary);
        }
      } else {
        requestAiCommentary({});
      }
    } catch {
      // Fallback to WS if REST fails
      requestAiCommentary(marketContext || {});
    } finally {
      setLoading(false);
    }
  }, [marketContext, requestAiCommentary]);

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
              Click <strong>Analyse</strong> to get real-time GBP/USD commentary.
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
