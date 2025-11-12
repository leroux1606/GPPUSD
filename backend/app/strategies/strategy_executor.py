"""Strategy executor for running strategies."""

import pandas as pd
from typing import Dict, Any, Optional, List
from app.strategies.base_strategy import BaseStrategy
from app.utils.logger import logger


class StrategyExecutor:
    """Executes strategies on price data."""
    
    def __init__(self, strategy: BaseStrategy):
        """
        Initialize executor with strategy.
        
        Args:
            strategy: Strategy instance
        """
        self.strategy = strategy
    
    def execute(self, df: pd.DataFrame) -> pd.Series:
        """
        Execute strategy and generate signals.
        
        Args:
            df: Price DataFrame
        
        Returns:
            Signal series
        """
        try:
            prepared_df = self.strategy.backtest_prepare(df)
            signals = self.strategy.generate_signals(prepared_df)
            return signals
        except Exception as e:
            logger.error(f"Error executing strategy {self.strategy.name}: {e}")
            return pd.Series(0, index=df.index)
    
    def get_entry_points(self, df: pd.DataFrame) -> pd.Series:
        """
        Get entry signal points.
        
        Args:
            df: Price DataFrame
        
        Returns:
            Boolean series indicating entry points
        """
        signals = self.execute(df)
        return signals == 1
    
    def get_exit_points(self, df: pd.DataFrame) -> pd.Series:
        """
        Get exit signal points.
        
        Args:
            df: Price DataFrame
        
        Returns:
            Boolean series indicating exit points
        """
        signals = self.execute(df)
        return signals == -1
    
    def get_signal_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary of signals generated.
        
        Args:
            df: Price DataFrame
        
        Returns:
            Dictionary with signal statistics
        """
        signals = self.execute(df)
        
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        hold_signals = (signals == 0).sum()
        
        return {
            "total_bars": len(df),
            "buy_signals": int(buy_signals),
            "sell_signals": int(sell_signals),
            "hold_signals": int(hold_signals),
            "signal_rate": (buy_signals + sell_signals) / len(df) if len(df) > 0 else 0
        }
    
    def get_latest_signal(self, df: pd.DataFrame) -> int:
        """
        Get latest signal from strategy.
        
        Args:
            df: Price DataFrame
        
        Returns:
            Latest signal: 1 (buy), -1 (sell), 0 (hold)
        """
        signals = self.execute(df)
        if len(signals) > 0:
            return int(signals.iloc[-1])
        return 0

