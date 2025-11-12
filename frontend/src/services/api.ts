import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Data API
export const dataApi = {
  getLivePrice: () => api.get('/api/data/live'),
  getHistorical: (params: { symbol?: string; timeframe?: string; start_date?: string; end_date?: string }) =>
    api.get('/api/data/historical', { params }),
  downloadHistorical: (params: { symbol?: string; timeframe?: string; start_date?: string; end_date?: string; provider?: string }) =>
    api.post('/api/data/download', null, { params }),
  getTimeframes: () => api.get('/api/data/timeframes'),
};

// Strategy API
export const strategyApi = {
  list: () => api.get('/api/strategies'),
  create: (config: any) => api.post('/api/strategies', config),
  get: (id: string) => api.get(`/api/strategies/${id}`),
  generateSignals: (id: string, data: any) => api.post(`/api/strategies/${id}/signals`, data),
};

// Backtesting API
export const backtestApi = {
  run: (config: any) => api.post('/api/backtest/run', config),
  optimize: (config: any) => api.post('/api/backtest/optimize', config),
  monteCarlo: (config: any) => api.post('/api/backtest/monte-carlo', config),
  walkForward: (config: any) => api.post('/api/backtest/walk-forward', config),
};

// Trading API
export const tradingApi = {
  openPosition: (order: any) => api.post('/api/trading/open', order),
  closePosition: (id: string) => api.post(`/api/trading/close/${id}`),
  getPositions: () => api.get('/api/trading/positions'),
};

// Analytics API
export const analyticsApi = {
  getPerformance: () => api.get('/api/analytics/performance'),
  getEquityCurve: () => api.get('/api/analytics/equity-curve'),
  getDrawdown: () => api.get('/api/analytics/drawdown'),
  getMonthlyReturns: () => api.get('/api/analytics/monthly-returns'),
};

// Indicators API
export const indicatorsApi = {
  list: () => api.get('/api/indicators'),
  calculate: (request: any) => api.post('/api/indicators/calculate', request),
};

