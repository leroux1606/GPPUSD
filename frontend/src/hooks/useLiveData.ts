import { useEffect, useCallback, useState } from 'react';
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
  const { isConnected, lastPriceUpdate, error: wsError } = useWebSocket();
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
    error: error || wsError,
    refetch: fetchPrice,
  };
}

interface UseHistoricalDataReturn {
  data: Candle[];
  isLoading: boolean;
  error: string | null;
  fetchData: (timeframe: string, startDate?: string, endDate?: string) => Promise<void>;
}

export function useHistoricalData(timeframe: string = '1h'): UseHistoricalDataReturn {
  const { historicalData, setHistoricalData } = useDataStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(
    async (tf: string, startDate?: string, endDate?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const params: {
          symbol?: string;
          timeframe?: string;
          start_date?: string;
          end_date?: string;
        } = {
          symbol: 'GBP_USD',
          timeframe: tf,
        };

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
    [setHistoricalData]
  );

  // Fetch data on mount and when timeframe changes
  useEffect(() => {
    if (!historicalData[timeframe] || historicalData[timeframe].length === 0) {
      fetchData(timeframe);
    }
  }, [timeframe, historicalData, fetchData]);

  return {
    data: historicalData[timeframe] || [],
    isLoading,
    error,
    fetchData,
  };
}
