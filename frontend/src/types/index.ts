// Type definitions

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

export interface Indicator {
  name: string;
  values: number[] | { [key: string]: number[] };
  type: 'series' | 'dataframe' | 'other';
}

export interface Strategy {
  id?: string;
  name: string;
  type: string;
  params: Record<string, any>;
  description?: string;
}

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
  timestamp: string;
  status: 'open' | 'closed';
}

export interface BacktestResult {
  initial_capital: number;
  final_value: number;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  profit_factor: number;
  avg_win: number;
  avg_loss: number;
  expectancy: number;
  trades: Trade[];
  equity_curve: number[];
}

export interface PerformanceMetrics {
  total_return: number;
  annual_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  avg_win: number;
  avg_loss: number;
  expectancy: number;
  longest_win_streak: number;
  longest_loss_streak: number;
}

