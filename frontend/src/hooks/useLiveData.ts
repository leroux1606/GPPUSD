import { useEffect, useCallback, useState, useRef } from 'react';
import { dataApi } from '../services/api';
import { useDataStore } from '../store/dataStore';
import { useWebSocket } from './useWebSocket';
import { PriceData, Candle } from '../types';

interface UseLiveDataReturn {
  price: PriceData | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useLiveData(): UseLiveDataReturn {
  const { connected: isConnected } = useWebSocket();
  const { livePrice, setLivePrice } = useDataStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial price data
  const fetchPrice = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await dataApi.getLivePrice();
      if (response.data) {
        setLivePrice(response.data);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch price';
      setError(errorMessage);
      console.error('Error fetching live price:', err);
    } finally {
      setIsLoading(false);
    }
  }, [setLivePrice]);

  // Fetch initial price on mount
  useEffect(() => {
    if (!livePrice) {
      fetchPrice();
    }
  }, [fetchPrice, livePrice]);

  // Fallback polling when WebSocket is disconnected
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    if (!isConnected) {
      // Poll every 2 seconds when WebSocket is down
      intervalId = setInterval(fetchPrice, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isConnected, fetchPrice]);

  return {
    price: livePrice,
    isConnected,
    isLoading,
    error: error,
    refetch: fetchPrice,
  };
}

interface UseHistoricalDataReturn {
  data: Candle[];
  isLoading: boolean;
  error: string | null;
  fetchData: (timeframe: string, startDate?: string, endDate?: string) => Promise<void>;
}

export function useHistoricalData(timeframe: string = 'M15', pair: string = 'GBP_USD'): UseHistoricalDataReturn {
  const { historicalData, setHistoricalData } = useDataStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const prevPairRef = useRef(pair);

  const fetchData = useCallback(
    async (tf: string, startDate?: string, endDate?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = { symbol: pair, timeframe: tf };
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        const response = await dataApi.getHistorical(params);
        if (response.data?.data) {
          setHistoricalData(tf, response.data.data);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch historical data';
        setError(errorMessage);
        console.error('Error fetching historical data:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [setHistoricalData, pair]
  );

  // Re-fetch whenever pair changes (ignore cache) or when timeframe has no data
  useEffect(() => {
    const pairChanged = prevPairRef.current !== pair;
    prevPairRef.current = pair;
    if (pairChanged || !historicalData[timeframe] || historicalData[timeframe].length === 0) {
      fetchData(timeframe);
    }
  }, [timeframe, pair, historicalData, fetchData]);

  return {
    data: historicalData[timeframe] || [],
    isLoading,
    error,
    fetchData,
  };
}
