import { useState, useEffect } from 'react';
import { wsService } from '../services/websocket';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    wsService.connect();
    setIsConnected(wsService.isConnected());

    const handleMessage = (data: any) => {
      setLastMessage(data);
    };

    wsService.on('price_update', handleMessage);

    return () => {
      wsService.off('price_update', handleMessage);
    };
  }, []);

  return { isConnected, lastMessage };
}

