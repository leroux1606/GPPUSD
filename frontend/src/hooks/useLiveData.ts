import { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { useWebSocket } from './useWebSocket';

export function useLiveData() {
  const { lastMessage } = useWebSocket();
  const [price, setPrice] = useState<any>(null);

  useEffect(() => {
    if (lastMessage?.data) {
      setPrice(lastMessage.data);
    }
  }, [lastMessage]);

  useEffect(() => {
    // Fetch initial price
    dataApi.getLivePrice().then(res => setPrice(res.data)).catch(console.error);
  }, []);

  return { price };
}

