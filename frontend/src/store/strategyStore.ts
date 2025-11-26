import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Strategy, BacktestResult } from '../types';

interface StrategyStore {
  // State
  strategies: Strategy[];
  selectedStrategy: Strategy | null;
  backtestResults: { [strategyId: string]: BacktestResult };
  
  // Loading states
  isLoading: boolean;
  isBacktesting: boolean;
  
  // Error state
  error: string | null;
  
  // Strategy actions
  setStrategies: (strategies: Strategy[]) => void;
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  deleteStrategy: (id: string) => void;
  selectStrategy: (strategy: Strategy | null) => void;
  duplicateStrategy: (id: string) => void;
  
  // Backtest actions
  setBacktestResult: (strategyId: string, result: BacktestResult) => void;
  clearBacktestResult: (strategyId: string) => void;
  
  // State actions
  setLoading: (loading: boolean) => void;
  setBacktesting: (backtesting: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStrategyStore = create<StrategyStore>()(
  persist(
    (set, get) => ({
      // Initial state
      strategies: [],
      selectedStrategy: null,
      backtestResults: {},
      isLoading: false,
      isBacktesting: false,
      error: null,

      // Strategy actions
      setStrategies: (strategies) => set({ strategies, error: null }),

      addStrategy: (strategy) => {
        const newStrategy = {
          ...strategy,
          id: strategy.id || `strategy_${Date.now()}`,
        };
        set((state) => ({
          strategies: [...state.strategies, newStrategy],
          selectedStrategy: newStrategy,
          error: null,
        }));
      },

      updateStrategy: (id, updates) => {
        set((state) => {
          const updatedStrategies = state.strategies.map((s) =>
            s.id === id ? { ...s, ...updates } : s
          );
          const updatedSelected =
            state.selectedStrategy?.id === id
              ? { ...state.selectedStrategy, ...updates }
              : state.selectedStrategy;

          return {
            strategies: updatedStrategies,
            selectedStrategy: updatedSelected,
          };
        });
      },

      deleteStrategy: (id) => {
        set((state) => ({
          strategies: state.strategies.filter((s) => s.id !== id),
          selectedStrategy:
            state.selectedStrategy?.id === id ? null : state.selectedStrategy,
          backtestResults: (() => {
            const newResults = { ...state.backtestResults };
            delete newResults[id];
            return newResults;
          })(),
        }));
      },

      selectStrategy: (strategy) => set({ selectedStrategy: strategy }),

      duplicateStrategy: (id) => {
        const strategy = get().strategies.find((s) => s.id === id);
        if (strategy) {
          const duplicate: Strategy = {
            ...strategy,
            id: `strategy_${Date.now()}`,
            name: `${strategy.name} (Copy)`,
          };
          get().addStrategy(duplicate);
        }
      },

      // Backtest actions
      setBacktestResult: (strategyId, result) => {
        set((state) => ({
          backtestResults: {
            ...state.backtestResults,
            [strategyId]: result,
          },
        }));
      },

      clearBacktestResult: (strategyId) => {
        set((state) => {
          const newResults = { ...state.backtestResults };
          delete newResults[strategyId];
          return { backtestResults: newResults };
        });
      },

      // State actions
      setLoading: (loading) => set({ isLoading: loading }),
      setBacktesting: (backtesting) => set({ isBacktesting: backtesting }),
      setError: (error) => set({ error }),
    }),
    {
      name: 'strategy-store',
      partialize: (state) => ({
        strategies: state.strategies,
      }),
    }
  )
);

// Selectors
export const selectStrategies = (state: StrategyStore) => state.strategies;
export const selectSelectedStrategy = (state: StrategyStore) => state.selectedStrategy;
