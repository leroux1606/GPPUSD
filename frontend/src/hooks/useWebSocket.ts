import { useEffect, useRef, useCallback, useState } from 'react';
import { useDataStore } from '../store/dataStore';
import { useNotificationStore } from '../store/notificationStore';
import { LiveSignal } from '../types';

const WS_URL = (import.meta.env.VITE_WS_URL || 'ws://localhost:8002') + '/ws';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [connected, setConnected] = useState(false);

  const setLivePrice = useDataStore((s) => s.setLivePrice);
  const { addNotification, addSignal, setMarketContext, setAiCommentary } = useNotificationStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data as string);

        switch (msg.type) {
          case 'price_update':
            setLivePrice(msg.data);
            break;

          case 'signal': {
            const signal = msg.data as LiveSignal;
            addSignal(signal);
            addNotification(
              'opportunity',
              `${signal.direction.toUpperCase()} — ${signal.strategy} | Entry ${signal.entry.toFixed(5)} | SL ${signal.stop_loss.toFixed(5)} | TP ${signal.take_profit.toFixed(5)}`,
              signal
            );
            break;
          }

          case 'warning':
            addNotification(msg.data.type || 'warning', msg.data.message);
            break;

          case 'market_context':
            setMarketContext(msg.data);
            break;

          case 'ai_commentary':
            if (msg.data?.text) setAiCommentary(msg.data.text);
            break;

          default:
            break;
        }
      } catch {
        // ignore malformed messages
      }
    };

    ws.onerror = () => {
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
      reconnectTimer.current = setTimeout(connect, 5000);
    };
  }, [setLivePrice, addNotification, addSignal, setMarketContext, setAiCommentary]);

  const sendCommand = useCallback((cmd: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(cmd));
    }
  }, []);

  const requestAiCommentary = useCallback(
    (context: object) => sendCommand({ cmd: 'get_ai_commentary', context }),
    [sendCommand]
  );

  const updateAccount = useCallback(
    (balance: number, equity: number, positions: unknown[]) =>
      sendCommand({ cmd: 'update_account', balance, equity, positions }),
    [sendCommand]
  );

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected, sendCommand, requestAiCommentary, updateAccount };
}
