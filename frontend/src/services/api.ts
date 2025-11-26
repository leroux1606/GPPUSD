import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const errorMessage = getErrorMessage(error);
    console.error('API Error:', errorMessage);
    
    // Handle specific error codes
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect
      localStorage.removeItem('auth_token');
    }
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Helper to extract error message
function getErrorMessage(error: AxiosError): string {
  if (error.response?.data) {
    const data = error.response.data as Record<string, unknown>;
    if (typeof data.detail === 'string') return data.detail;
    if (typeof data.message === 'string') return data.message;
    if (typeof data.error === 'string') return data.error;
  }
  
  if (error.code === 'ECONNABORTED') {
    return 'Request timeout - please try again';
  }
  
  if (error.code === 'ERR_NETWORK') {
    return 'Network error - please check your connection';
  }
  
  return error.message || 'An unexpected error occurred';
}

// Type definitions for API parameters
interface HistoricalParams {
  symbol?: string;
  timeframe?: string;
  start_date?: string;
  end_date?: string;
}

interface DownloadParams extends HistoricalParams {
  provider?: string;
}

interface StrategyConfig {
  type: string;
  params?: Record<string, unknown>;
  name?: string;
}

interface BacktestConfig {
  strategy_type: string;
  params?: Record<string, unknown>;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission?: number;
  slippage?: number;
}

interface OptimizeConfig {
  strategy_type: string;
  param_grid: Record<string, number[]>;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission?: number;
  metric?: string;
}

interface OrderParams {
  symbol: string;
  side: 'buy' | 'sell';
  size: number;
  price?: number;
  stop_loss?: number;
  take_profit?: number;
  type?: 'market' | 'limit' | 'stop';
}

interface IndicatorRequest {
  indicator: string;
  price_data: unknown[];
  params?: Record<string, unknown>;
}

// Data API
export const dataApi = {
  getLivePrice: () => 
    api.get('/api/data/live'),
  
  getHistorical: (params: HistoricalParams) =>
    api.get('/api/data/historical', { params }),
  
  downloadHistorical: (params: DownloadParams) =>
    api.post('/api/data/download', null, { params }),
  
  getTimeframes: () => 
    api.get('/api/data/timeframes'),
    
  getSymbols: () =>
    api.get('/api/data/symbols'),
};

// Strategy API
export const strategyApi = {
  list: () => 
    api.get('/api/strategies'),
  
  create: (config: StrategyConfig) => 
    api.post('/api/strategies', config),
  
  get: (id: string) => 
    api.get(`/api/strategies/${id}`),
  
  update: (id: string, config: Partial<StrategyConfig>) =>
    api.put(`/api/strategies/${id}`, config),
  
  delete: (id: string) =>
    api.delete(`/api/strategies/${id}`),
  
  generateSignals: (id: string, data: unknown) => 
    api.post(`/api/strategies/${id}/signals`, data),
  
  getParameters: (strategyType: string) =>
    api.get(`/api/strategies/parameters/${strategyType}`),
};

// Backtesting API
export const backtestApi = {
  run: (config: BacktestConfig) => 
    api.post('/api/backtest/run', config),
  
  optimize: (config: OptimizeConfig) => 
    api.post('/api/backtest/optimize', config),
  
  monteCarlo: (config: BacktestConfig & { simulations?: number }) => 
    api.post('/api/backtest/monte-carlo', config),
  
  walkForward: (config: BacktestConfig & { window_size?: number; step_size?: number }) => 
    api.post('/api/backtest/walk-forward', config),
  
  getHistory: () =>
    api.get('/api/backtest/history'),
};

// Trading API
export const tradingApi = {
  openPosition: (order: OrderParams) => 
    api.post('/api/trading/open', order),
  
  closePosition: (id: string) => 
    api.post(`/api/trading/close/${id}`),
  
  modifyPosition: (id: string, updates: { stop_loss?: number; take_profit?: number }) =>
    api.put(`/api/trading/modify/${id}`, updates),
  
  getPositions: () => 
    api.get('/api/trading/positions'),
  
  getOrders: () =>
    api.get('/api/trading/orders'),
  
  cancelOrder: (id: string) =>
    api.delete(`/api/trading/orders/${id}`),
  
  getAccountInfo: () =>
    api.get('/api/trading/account'),
};

// Analytics API
export const analyticsApi = {
  getPerformance: () => 
    api.get('/api/analytics/performance'),
  
  getEquityCurve: () => 
    api.get('/api/analytics/equity-curve'),
  
  getDrawdown: () => 
    api.get('/api/analytics/drawdown'),
  
  getMonthlyReturns: () => 
    api.get('/api/analytics/monthly-returns'),
  
  getTradeStats: () =>
    api.get('/api/analytics/trade-stats'),
  
  getRiskMetrics: () =>
    api.get('/api/analytics/risk-metrics'),
};

// Indicators API
export const indicatorsApi = {
  list: () => 
    api.get('/api/indicators'),
  
  calculate: (request: IndicatorRequest) => 
    api.post('/api/indicators/calculate', request),
  
  getInfo: (indicatorName: string) =>
    api.get(`/api/indicators/${indicatorName}`),
};

// Health check
export const healthApi = {
  check: () => 
    api.get('/health'),
  
  status: () =>
    api.get('/api/status'),
};

export default api;
