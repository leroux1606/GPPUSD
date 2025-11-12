import { create } from 'zustand';
import { PriceData, Candle } from '../types';

interface DataStore {
  livePrice: PriceData | null;
  historicalData: { [timeframe: string]: Candle[] };
  indicators: { [key: string]: number[] };
  setLivePrice: (price: PriceData) => void;
  setHistoricalData: (timeframe: string, data: Candle[]) => void;
  addIndicator: (name: string, values: number[]) => void;
  removeIndicator: (name: string) => void;
}

export const useDataStore = create<DataStore>((set) => ({
  livePrice: null,
  historicalData: {},
  indicators: {},
  setLivePrice: (price) => set({ livePrice: price }),
  setHistoricalData: (timeframe, data) =>
    set((state) => ({
      historicalData: { ...state.historicalData, [timeframe]: data },
    })),
  addIndicator: (name, values) =>
    set((state) => ({
      indicators: { ...state.indicators, [name]: values },
    })),
  removeIndicator: (name) =>
    set((state) => {
      const newIndicators = { ...state.indicators };
      delete newIndicators[name];
      return { indicators: newIndicators };
    }),
}));

