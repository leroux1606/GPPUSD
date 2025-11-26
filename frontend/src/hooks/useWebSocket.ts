import { useState, useEffect, useCallback } from 'react';
import { wsService, PriceUpdate, PositionUpdate } from '../services/websocket';
import { useDataStore } from '../store/dataStore';
import { useTradingStore } from '../store/tradingStore';

interface WebSocketState {
  isConnected: boolean;
  connectionState: 'connected' | 'disconnected' | 'reconnecting';
  lastPriceUpdate: PriceUpdate | null;
  error: string | null;
}

export function useWebSocket() {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    connectionState: 'disconnected',
    lastPriceUpdate: null,
    error: null,
  });

  const setLivePrice = useDataStore((s) => s.setLivePrice);
  const updatePosition = useTradingStore((s) => s.updatePosition);

  useEffect(() => {
    // Connect to WebSocket
    wsService.connect();

    // Handle connection state changes
    const unsubConnection = wsService.on<{ connected: boolean }>('connection', (data) => {
      setState((prev) => ({
        ...prev,
        isConnected: data.connected,
        connectionState: data.connected ? 'connected' : 'disconnected',
      }));
    });

    // Handle price updates
    const unsubPrice = wsService.on<PriceUpdate>('price_update', (data) => {
      setState((prev) => ({ ...prev, lastPriceUpdate: data }));
      // Update the global data store
      setLivePrice({
        symbol: data.symbol,
        timestamp: data.timestamp,
        bid: data.bid,
        ask: data.ask,
        mid: data.mid,
        spread: data.spread,
      });
    });

    // Handle position updates
    const unsubPosition = wsService.on<PositionUpdate>('position_update', (data) => {
      updatePosition(data.id, { pnl: data.pnl });
    });

    // Handle errors
    const unsubError = wsService.on<Error>('error', (error) => {
      setState((prev) => ({ ...prev, error: error.message }));
    });

    // Set initial connection state
    setState((prev) => ({
      ...prev,
      isConnected: wsService.isConnected(),
      connectionState: wsService.getConnectionState(),
    }));

    return () => {
      unsubConnection();
      unsubPrice();
      unsubPosition();
      unsubError();
    };
  }, [setLivePrice, updatePosition]);

  const reconnect = useCallback(() => {
    wsService.disconnect();
    wsService.connect();
  }, []);

  return {
    ...state,
    reconnect,
  };
}
