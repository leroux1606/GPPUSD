import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { PriceData, Candle } from '../types';

interface IndicatorData {
  name: string;
  values: number[];
  color?: string;
  type: 'overlay' | 'separate';
}

interface DataStore {
  // Price data
  livePrice: PriceData | null;
  priceHistory: PriceData[];
  
  // Historical candle data
  historicalData: { [timeframe: string]: Candle[] };
  
  // Indicators
  indicators: { [key: string]: IndicatorData };
  
  // Loading states
  isLoadingPrice: boolean;
  isLoadingHistorical: boolean;
  
  // Errors
  priceError: string | null;
  historicalError: string | null;
  
  // Actions
  setLivePrice: (price: PriceData) => void;
  addToPriceHistory: (price: PriceData) => void;
  setHistoricalData: (timeframe: string, data: Candle[]) => void;
  appendCandle: (timeframe: string, candle: Candle) => void;
  updateLastCandle: (timeframe: string, candle: Partial<Candle>) => void;
  addIndicator: (name: string, data: IndicatorData) => void;
  removeIndicator: (name: string) => void;
  clearIndicators: () => void;
  setLoadingPrice: (loading: boolean) => void;
  setLoadingHistorical: (loading: boolean) => void;
  setPriceError: (error: string | null) => void;
  setHistoricalError: (error: string | null) => void;
}

const MAX_PRICE_HISTORY = 1000;

export const useDataStore = create<DataStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    livePrice: null,
    priceHistory: [],
    historicalData: {},
    indicators: {},
    isLoadingPrice: false,
    isLoadingHistorical: false,
    priceError: null,
    historicalError: null,

    // Price actions
    setLivePrice: (price) => {
      set({ livePrice: price, priceError: null });
      // Also add to price history
      get().addToPriceHistory(price);
    },

    addToPriceHistory: (price) => {
      set((state) => {
        const history = [...state.priceHistory, price];
        // Keep only the last MAX_PRICE_HISTORY entries
        if (history.length > MAX_PRICE_HISTORY) {
          history.shift();
        }
        return { priceHistory: history };
      });
    },

    // Historical data actions
    setHistoricalData: (timeframe, data) => {
      set((state) => ({
        historicalData: { ...state.historicalData, [timeframe]: data },
        historicalError: null,
      }));
    },

    appendCandle: (timeframe, candle) => {
      set((state) => {
        const existing = state.historicalData[timeframe] || [];
        return {
          historicalData: {
            ...state.historicalData,
            [timeframe]: [...existing, candle],
          },
        };
      });
    },

    updateLastCandle: (timeframe, updates) => {
      set((state) => {
        const existing = state.historicalData[timeframe] || [];
        if (existing.length === 0) return state;

        const updated = [...existing];
        const lastIndex = updated.length - 1;
        updated[lastIndex] = { ...updated[lastIndex], ...updates };

        return {
          historicalData: {
            ...state.historicalData,
            [timeframe]: updated,
          },
        };
      });
    },

    // Indicator actions
    addIndicator: (name, data) => {
      set((state) => ({
        indicators: { ...state.indicators, [name]: data },
      }));
    },

    removeIndicator: (name) => {
      set((state) => {
        const newIndicators = { ...state.indicators };
        delete newIndicators[name];
        return { indicators: newIndicators };
      });
    },

    clearIndicators: () => {
      set({ indicators: {} });
    },

    // Loading state actions
    setLoadingPrice: (loading) => set({ isLoadingPrice: loading }),
    setLoadingHistorical: (loading) => set({ isLoadingHistorical: loading }),

    // Error actions
    setPriceError: (error) => set({ priceError: error }),
    setHistoricalError: (error) => set({ historicalError: error }),
  }))
);

// Selectors for optimized re-renders
export const selectLivePrice = (state: DataStore) => state.livePrice;
export const selectHistoricalData = (timeframe: string) => (state: DataStore) =>
  state.historicalData[timeframe] || [];
export const selectIndicators = (state: DataStore) => state.indicators;
