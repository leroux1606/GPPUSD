import { create } from 'zustand';
import { Strategy } from '../types';

interface StrategyStore {
  strategies: Strategy[];
  selectedStrategy: Strategy | null;
  setStrategies: (strategies: Strategy[]) => void;
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, strategy: Strategy) => void;
  deleteStrategy: (id: string) => void;
  selectStrategy: (strategy: Strategy | null) => void;
}

export const useStrategyStore = create<StrategyStore>((set) => ({
  strategies: [],
  selectedStrategy: null,
  setStrategies: (strategies) => set({ strategies }),
  addStrategy: (strategy) =>
    set((state) => ({ strategies: [...state.strategies, strategy] })),
  updateStrategy: (id, strategy) =>
    set((state) => ({
      strategies: state.strategies.map((s) => (s.id === id ? strategy : s)),
    })),
  deleteStrategy: (id) =>
    set((state) => ({
      strategies: state.strategies.filter((s) => s.id !== id),
    })),
  selectStrategy: (strategy) => set({ selectedStrategy: strategy }),
}));

