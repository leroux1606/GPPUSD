"""Base Strategy class for all trading strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import pandas as pd
from app.utils.logger import logger


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Strategy parameters dictionary
        """
        self.params = params or self.get_default_params()
        self.name = self.__class__.__name__
        self.validate_params()
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, Any]:
        """
        Get default strategy parameters.
        
        Returns:
            Dictionary with default parameters
        """
        pass
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals from price data.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass
    
    def validate_params(self) -> None:
        """Validate strategy parameters."""
        default_params = self.get_default_params()
        for key, default_value in default_params.items():
            if key not in self.params:
                self.params[key] = default_value
                logger.warning(f"Missing parameter {key}, using default: {default_value}")
    
    def get_entry_conditions(self, df: pd.DataFrame) -> pd.Series:
        """
        Get entry conditions (buy signals).
        
        Args:
            df: Price DataFrame
        
        Returns:
            Boolean Series indicating entry points
        """
        signals = self.generate_signals(df)
        return signals == 1
    
    def get_exit_conditions(self, df: pd.DataFrame) -> pd.Series:
        """
        Get exit conditions (sell signals).
        
        Args:
            df: Price DataFrame
        
        Returns:
            Boolean Series indicating exit points
        """
        signals = self.generate_signals(df)
        return signals == -1
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get strategy information.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": self.name,
            "params": self.params,
            "description": self.__doc__ or "No description available"
        }
    
    def backtest_prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for backtesting (calculate indicators, etc.).
        
        Args:
            df: Price DataFrame
        
        Returns:
            Prepared DataFrame
        """
        return df.copy()
    
    def on_bar(self, df: pd.DataFrame, index: int) -> int:
        """
        Called on each bar during backtesting.
        
        Args:
            df: Price DataFrame
            index: Current bar index
        
        Returns:
            Signal: 1 (buy), -1 (sell), 0 (hold)
        """
        if index < len(df):
            current_df = df.iloc[:index + 1]
            signals = self.generate_signals(current_df)
            return int(signals.iloc[-1]) if len(signals) > 0 else 0
        return 0

