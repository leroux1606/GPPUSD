import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { Trade } from '../types';

interface TradingStore {
  // Account state
  positions: Trade[];
  closedTrades: Trade[];
  balance: number;
  equity: number;
  margin: number;
  freeMargin: number;
  marginLevel: number;
  
  // Loading states
  isLoading: boolean;
  isPlacingOrder: boolean;
  
  // Error state
  error: string | null;
  
  // Position actions
  addPosition: (trade: Trade) => void;
  updatePosition: (id: string, updates: Partial<Trade>) => void;
  closePosition: (id: string, exitPrice?: number, pnl?: number) => void;
  removePosition: (id: string) => void;
  setPositions: (positions: Trade[]) => void;
  
  // Account actions
  setBalance: (balance: number) => void;
  setEquity: (equity: number) => void;
  setMargin: (margin: number) => void;
  updateAccountFromPositions: () => void;
  
  // State actions
  setLoading: (loading: boolean) => void;
  setPlacingOrder: (placing: boolean) => void;
  setError: (error: string | null) => void;
  
  // Computed getters
  getOpenPositions: () => Trade[];
  getClosedTrades: () => Trade[];
  getTotalPnL: () => number;
}

export const useTradingStore = create<TradingStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    positions: [],
    closedTrades: [],
    balance: 10000,
    equity: 10000,
    margin: 0,
    freeMargin: 10000,
    marginLevel: 0,
    isLoading: false,
    isPlacingOrder: false,
    error: null,

    // Position actions
    addPosition: (trade) => {
      set((state) => ({
        positions: [...state.positions, { ...trade, status: 'open' }],
        error: null,
      }));
      get().updateAccountFromPositions();
    },

    updatePosition: (id, updates) => {
      set((state) => ({
        positions: state.positions.map((p) =>
          p.id === id ? { ...p, ...updates } : p
        ),
      }));
      get().updateAccountFromPositions();
    },

    closePosition: (id, exitPrice, pnl) => {
      set((state) => {
        const position = state.positions.find((p) => p.id === id);
        if (!position) return state;

        const closedTrade: Trade = {
          ...position,
          status: 'closed',
          exit_price: exitPrice,
          pnl: pnl ?? position.pnl ?? 0,
        };

        return {
          positions: state.positions.filter((p) => p.id !== id),
          closedTrades: [...state.closedTrades, closedTrade],
          balance: state.balance + (closedTrade.pnl || 0),
        };
      });
      get().updateAccountFromPositions();
    },

    removePosition: (id) => {
      set((state) => ({
        positions: state.positions.filter((p) => p.id !== id),
      }));
      get().updateAccountFromPositions();
    },

    setPositions: (positions) => {
      set({ positions });
      get().updateAccountFromPositions();
    },

    // Account actions
    setBalance: (balance) => {
      set({ balance });
      get().updateAccountFromPositions();
    },

    setEquity: (equity) => set({ equity }),
    setMargin: (margin) => set({ margin }),

    updateAccountFromPositions: () => {
      set((state) => {
        const totalPnL = state.positions.reduce((sum, p) => sum + (p.pnl || 0), 0);
        const equity = state.balance + totalPnL;
        const margin = state.positions.reduce(
          (sum, p) => sum + p.size * 100000 * 0.01, // 1% margin for forex
          0
        );
        const freeMargin = equity - margin;
        const marginLevel = margin > 0 ? (equity / margin) * 100 : 0;

        return { equity, margin, freeMargin, marginLevel };
      });
    },

    // State actions
    setLoading: (loading) => set({ isLoading: loading }),
    setPlacingOrder: (placing) => set({ isPlacingOrder: placing }),
    setError: (error) => set({ error }),

    // Computed getters
    getOpenPositions: () => get().positions.filter((p) => p.status === 'open'),
    getClosedTrades: () => get().closedTrades,
    getTotalPnL: () =>
      get().positions.reduce((sum, p) => sum + (p.pnl || 0), 0) +
      get().closedTrades.reduce((sum, t) => sum + (t.pnl || 0), 0),
  }))
);

// Selectors
export const selectOpenPositions = (state: TradingStore) =>
  state.positions.filter((p) => p.status === 'open');
export const selectBalance = (state: TradingStore) => state.balance;
export const selectEquity = (state: TradingStore) => state.equity;
