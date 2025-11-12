import { create } from 'zustand';

interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  selectedTimeframe: string;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setTimeframe: (timeframe: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: 'dark',
  sidebarOpen: true,
  selectedTimeframe: '1h',
  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTimeframe: (timeframe) => set({ selectedTimeframe: timeframe }),
}));

