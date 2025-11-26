// Price and Market Data Types
export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceData {
  symbol: string;
  timestamp: string;
  bid: number;
  ask: number;
  mid: number;
  spread: number;
}

export interface MarketData {
  symbol: string;
  candles: Candle[];
  lastUpdate: string;
}

// Indicator Types
export interface Indicator {
  name: string;
  values: number[] | { [key: string]: number[] };
  type: 'series' | 'dataframe' | 'other';
  params?: Record<string, number | string>;
}

export interface IndicatorConfig {
  name: string;
  enabled: boolean;
  params: Record<string, number | string>;
  color?: string;
  lineWidth?: number;
}

// Strategy Types
export interface Strategy {
  id?: string;
  name: string;
  type: string;
  params: Record<string, number | string | boolean>;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface StrategySignal {
  timestamp: string;
  type: 'buy' | 'sell' | 'close';
  price: number;
  confidence?: number;
  reason?: string;
}

// Trade Types
export interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  size: number;
  entry_price: number;
  exit_price?: number;
  stop_loss?: number;
  take_profit?: number;
  pnl?: number;
  pnl_pips?: number;
  timestamp: string;
  close_timestamp?: string;
  status: 'open' | 'closed' | 'pending' | 'cancelled';
  commission?: number;
  swap?: number;
}

export interface Order {
  id?: string;
  symbol: string;
  side: 'buy' | 'sell';
  size: number;
  type: 'market' | 'limit' | 'stop';
  price?: number;
  stop_loss?: number;
  take_profit?: number;
}

// Backtest Types
export interface BacktestConfig {
  strategy_type: string;
  params: Record<string, number | string | boolean>;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission: number;
  slippage?: number;
}

export interface BacktestResult {
  initial_capital: number;
  final_value: number;
  total_return: number;
  annual_return?: number;
  sharpe_ratio: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  max_drawdown: number;
  avg_drawdown?: number;
  win_rate: number;
  total_trades: number;
  winning_trades?: number;
  losing_trades?: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
  expectancy: number;
  longest_win_streak?: number;
  longest_loss_streak?: number;
  trades: Trade[];
  equity_curve: number[];
  drawdown_curve?: number[];
  timestamps?: string[];
}

// Performance Metrics Types
export interface PerformanceMetrics {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  avg_drawdown?: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  avg_win: number;
  avg_loss: number;
  expectancy: number;
  longest_win_streak: number;
  longest_loss_streak: number;
  avg_trade_duration?: number;
  risk_reward_ratio?: number;
}

// Account Types
export interface AccountInfo {
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  margin_level: number;
  unrealized_pnl: number;
  realized_pnl: number;
}

// Economic Calendar Types
export interface EconomicEvent {
  id?: string;
  date: string;
  time: string;
  currency: string;
  event: string;
  impact: 'high' | 'medium' | 'low';
  actual?: string;
  forecast?: string;
  previous?: string;
}

// Optimization Types
export interface OptimizationConfig {
  strategy_type: string;
  param_grid: Record<string, number[]>;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission: number;
  metric: 'sharpe_ratio' | 'total_return' | 'profit_factor';
}

export interface OptimizationResult {
  params: Record<string, number | string>;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Chart Types
export interface ChartConfig {
  timeframe: string;
  indicators: IndicatorConfig[];
  showVolume: boolean;
  showGrid: boolean;
  theme: 'dark' | 'light';
}

// Monthly Returns Type
export interface MonthlyReturn {
  year: number;
  month: number;
  return_pct: number;
  trades: number;
}
