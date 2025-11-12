import { create } from 'zustand';
import { Trade } from '../types';

interface TradingStore {
  positions: Trade[];
  balance: number;
  equity: number;
  margin: number;
  addPosition: (trade: Trade) => void;
  updatePosition: (id: string, trade: Partial<Trade>) => void;
  closePosition: (id: string) => void;
  setBalance: (balance: number) => void;
  setEquity: (equity: number) => void;
  setMargin: (margin: number) => void;
}

export const useTradingStore = create<TradingStore>((set) => ({
  positions: [],
  balance: 10000,
  equity: 10000,
  margin: 0,
  addPosition: (trade) =>
    set((state) => ({ positions: [...state.positions, trade] })),
  updatePosition: (id, updates) =>
    set((state) => ({
      positions: state.positions.map((p) =>
        p.id === id ? { ...p, ...updates } : p
      ),
    })),
  closePosition: (id) =>
    set((state) => ({
      positions: state.positions.filter((p) => p.id !== id),
    })),
  setBalance: (balance) => set({ balance }),
  setEquity: (equity) => set({ equity }),
  setMargin: (margin) => set({ margin }),
}));

