import { create } from 'zustand';
import { AppNotification, NotificationPriority, LiveSignal, MarketContext } from '../types';

interface NotificationStore {
  notifications: AppNotification[];
  signals: LiveSignal[];
  marketContext: MarketContext | null;
  aiCommentary: string | null;
  aiCommentaryTime: string | null;
  unreadCount: number;

  addNotification: (type: NotificationPriority, message: string, signal?: LiveSignal) => void;
  markAllRead: () => void;
  dismissNotification: (id: string) => void;
  addSignal: (signal: LiveSignal) => void;
  setMarketContext: (ctx: MarketContext) => void;
  setAiCommentary: (text: string) => void;
  clearOldSignals: () => void;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],
  signals: [],
  marketContext: null,
  aiCommentary: null,
  aiCommentaryTime: null,
  unreadCount: 0,

  addNotification: (type, message, signal) => {
    const n: AppNotification = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      type,
      message,
      timestamp: new Date().toISOString(),
      read: false,
      signal,
    };
    set((s) => ({
      notifications: [n, ...s.notifications].slice(0, 100),
      unreadCount: s.unreadCount + 1,
    }));
  },

  markAllRead: () =>
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    })),

  dismissNotification: (id) =>
    set((s) => ({
      notifications: s.notifications.filter((n) => n.id !== id),
      unreadCount: s.notifications.filter((n) => !n.read && n.id !== id).length,
    })),

  addSignal: (signal) =>
    set((s) => ({
      signals: [signal, ...s.signals].slice(0, 20),
    })),

  setMarketContext: (ctx) => set({ marketContext: ctx }),

  setAiCommentary: (text) =>
    set({ aiCommentary: text, aiCommentaryTime: new Date().toISOString() }),

  clearOldSignals: () => {
    const cutoff = Date.now() - 4 * 60 * 60 * 1000; // 4 hours
    set((s) => ({
      signals: s.signals.filter((sig) => new Date(sig.timestamp).getTime() > cutoff),
    }));
  },
}));
