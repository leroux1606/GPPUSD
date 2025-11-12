"""Backtesting engine using Backtrader."""

import backtrader as bt
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from app.strategies.base_strategy import BaseStrategy
from app.utils.logger import logger


class StrategyWrapper(bt.Strategy):
    """Wrapper to convert BaseStrategy to Backtrader strategy."""
    
    params = (
        ('strategy', None),
        ('stop_loss_pips', None),
        ('take_profit_pips', None),
    )
    
    def __init__(self):
        """Initialize strategy wrapper."""
        self.strategy = self.params.strategy
        self.signals = []
        self.orders = []
        self.trades = []
    
    def next(self):
        """Called on each bar."""
        if len(self.data) < 2:
            return
        
        # Get current data as DataFrame
        df = self._get_dataframe()
        
        if len(df) < 2:
            return
        
        # Generate signal
        signal = self.strategy.on_bar(df, len(df) - 1)
        
        # Execute signal
        if signal == 1 and not self.position:
            # Buy signal
            size = self._calculate_position_size()
            self.buy(size=size)
        elif signal == -1 and self.position:
            # Sell signal
            self.sell(size=abs(self.position.size))
    
    def _get_dataframe(self) -> pd.DataFrame:
        """Convert Backtrader data to DataFrame."""
        data_list = []
        for i in range(len(self.data)):
            data_list.append({
                'timestamp': self.data.datetime.datetime(i),
                'open': self.data.open[i],
                'high': self.data.high[i],
                'low': self.data.low[i],
                'close': self.data.close[i],
                'volume': self.data.volume[i] if hasattr(self.data, 'volume') else 0
            })
        return pd.DataFrame(data_list)
    
    def _calculate_position_size(self) -> float:
        """Calculate position size."""
        # Simple fixed size for now
        return 0.01
    
    def notify_order(self, order):
        """Notify order status."""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.orders.append({
                    'type': 'buy',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'bar': len(self.data) - 1
                })
            else:
                self.orders.append({
                    'type': 'sell',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'bar': len(self.data) - 1
                })
    
    def notify_trade(self, trade):
        """Notify trade status."""
        if trade.isclosed:
            self.trades.append({
                'entry_price': trade.price,
                'exit_price': trade.pnlcomm / trade.size + trade.price if trade.size > 0 else trade.price,
                'size': trade.size,
                'pnl': trade.pnlcomm,
                'entry_bar': trade.baropen,
                'exit_bar': trade.barclose
            })


class BacktestEngine:
    """Backtesting engine using Backtrader."""
    
    def __init__(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        initial_capital: float = 10000,
        commission: float = 0.0001,
        slippage: float = 0.0001
    ):
        """
        Initialize backtest engine.
        
        Args:
            strategy: Strategy instance
            data: Historical price DataFrame
            initial_capital: Starting capital
            commission: Commission rate
            slippage: Slippage rate
        """
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Prepare data
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data = self.data.set_index('timestamp')
    
    def run(self) -> Dict[str, Any]:
        """
        Run backtest.
        
        Returns:
            Dictionary with backtest results
        """
        try:
            # Create cerebro
            cerebro = bt.Cerebro()
            
            # Add data
            data_feed = bt.feeds.PandasData(
                dataname=self.data,
                datetime=None,
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=None
            )
            cerebro.adddata(data_feed)
            
            # Add strategy
            cerebro.addstrategy(
                StrategyWrapper,
                strategy=self.strategy,
                stop_loss_pips=None,
                take_profit_pips=None
            )
            
            # Set initial capital
            cerebro.broker.setcash(self.initial_capital)
            
            # Set commission
            cerebro.broker.setcommission(commission=self.commission)
            
            # Add slippage
            cerebro.broker.set_slippage_perc(perc=self.slippage * 100)
            
            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            
            # Run backtest
            logger.info(f"Running backtest with {len(self.data)} bars...")
            results = cerebro.run()
            result = results[0]
            
            # Extract results
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - self.initial_capital) / self.initial_capital * 100
            
            # Get analyzer results
            sharpe = result.analyzers.sharpe.get_analysis()
            drawdown = result.analyzers.drawdown.get_analysis()
            trades = result.analyzers.trades.get_analysis()
            returns = result.analyzers.returns.get_analysis()
            
            # Get strategy wrapper results
            strategy_wrapper = result.strategies[0]
            orders = strategy_wrapper.orders
            trades_list = strategy_wrapper.trades
            
            # Calculate metrics
            from app.backtesting.metrics import calculate_all_metrics
            
            metrics = calculate_all_metrics(
                initial_capital=self.initial_capital,
                final_value=final_value,
                trades=trades_list,
                equity_curve=self._get_equity_curve(cerebro),
                returns_data=returns
            )
            
            return {
                "initial_capital": self.initial_capital,
                "final_value": final_value,
                "total_return": total_return,
                "total_trades": len(trades_list),
                "orders": orders,
                "trades": trades_list,
                "equity_curve": self._get_equity_curve(cerebro),
                **metrics
            }
        
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            raise
    
    def _get_equity_curve(self, cerebro) -> list:
        """Extract equity curve from cerebro."""
        # This would need to be implemented by tracking equity over time
        # For now, return empty list
        return []

