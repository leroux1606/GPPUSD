import { create } from 'zustand';

export const ALL_PAIRS = [
  { symbol: 'GBP_USD', display: 'GBP/USD' },
  { symbol: 'EUR_USD', display: 'EUR/USD' },
  { symbol: 'USD_JPY', display: 'USD/JPY' },
  { symbol: 'USD_CHF', display: 'USD/CHF' },
  { symbol: 'AUD_USD', display: 'AUD/USD' },
  { symbol: 'USD_CAD', display: 'USD/CAD' },
] as const;

export type PairSymbol = typeof ALL_PAIRS[number]['symbol'];

interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  selectedTimeframe: string;
  selectedPair: PairSymbol;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setTimeframe: (timeframe: string) => void;
  setPair: (pair: PairSymbol) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: 'dark',
  sidebarOpen: true,
  selectedTimeframe: 'M15',
  selectedPair: 'GBP_USD',
  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTimeframe: (timeframe) => set({ selectedTimeframe: timeframe }),
  setPair: (pair) => set({ selectedPair: pair }),
}));

