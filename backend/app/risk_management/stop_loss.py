"""Stop loss implementations."""

from typing import Optional, Dict, Any
import pandas as pd
from app.technical_analysis.indicators import calculate_atr


class StopLoss:
    """Calculate stop loss levels."""
    
    @staticmethod
    def fixed_pips(entry_price: float, pips: float, direction: int = 1) -> float:
        """
        Fixed pips stop loss.
        
        Args:
            entry_price: Entry price
            pips: Stop loss in pips
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        pip_value = pips / 10000
        if direction == 1:  # Long
            return entry_price - pip_value
        else:  # Short
            return entry_price + pip_value
    
    @staticmethod
    def percentage(entry_price: float, percentage: float, direction: int = 1) -> float:
        """
        Percentage stop loss.
        
        Args:
            entry_price: Entry price
            percentage: Stop loss percentage
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        if direction == 1:  # Long
            return entry_price * (1 - percentage / 100)
        else:  # Short
            return entry_price * (1 + percentage / 100)
    
    @staticmethod
    def atr_based(
        df: pd.DataFrame,
        entry_price: float,
        entry_index: int,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        direction: int = 1
    ) -> float:
        """
        ATR-based stop loss.
        
        Args:
            df: Price DataFrame
            entry_price: Entry price
            entry_index: Entry bar index
            atr_period: ATR period
            atr_multiplier: ATR multiplier
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        atr = calculate_atr(df, atr_period)
        current_atr = atr.iloc[entry_index] if entry_index < len(atr) else atr.iloc[-1]
        
        stop_distance = current_atr * atr_multiplier
        
        if direction == 1:  # Long
            return entry_price - stop_distance
        else:  # Short
            return entry_price + stop_distance
    
    @staticmethod
    def trailing_stop(
        current_price: float,
        highest_price: float,
        trail_pips: float,
        direction: int = 1
    ) -> float:
        """
        Trailing stop loss.
        
        Args:
            current_price: Current price
            highest_price: Highest price since entry (for long) or lowest (for short)
            trail_pips: Trailing distance in pips
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        trail_value = trail_pips / 10000
        
        if direction == 1:  # Long
            return highest_price - trail_value
        else:  # Short
            return highest_price + trail_value
    
    @staticmethod
    def break_even(
        entry_price: float,
        current_price: float,
        direction: int = 1,
        buffer_pips: float = 5.0
    ) -> float:
        """
        Move stop to break-even after profit.
        
        Args:
            entry_price: Entry price
            current_price: Current price
            direction: 1 for long, -1 for short
            buffer_pips: Buffer pips above/below entry
        
        Returns:
            Stop loss price (break-even)
        """
        buffer_value = buffer_pips / 10000
        
        if direction == 1:  # Long
            if current_price > entry_price + buffer_value:
                return entry_price + buffer_value
        else:  # Short
            if current_price < entry_price - buffer_value:
                return entry_price - buffer_value
        
        return entry_price
    
    @staticmethod
    def chandelier_exit(
        df: pd.DataFrame,
        entry_index: int,
        atr_period: int = 14,
        atr_multiplier: float = 3.0,
        direction: int = 1
    ) -> float:
        """
        Chandelier Exit (trailing stop based on ATR).
        
        Args:
            df: Price DataFrame
            entry_index: Entry bar index
            atr_period: ATR period
            atr_multiplier: ATR multiplier
            direction: 1 for long, -1 for short
        
        Returns:
            Stop loss price
        """
        atr = calculate_atr(df, atr_period)
        current_atr = atr.iloc[entry_index] if entry_index < len(atr) else atr.iloc[-1]
        
        if direction == 1:  # Long
            highest_high = df.iloc[:entry_index + 1]['high'].max()
            return highest_high - (current_atr * atr_multiplier)
        else:  # Short
            lowest_low = df.iloc[:entry_index + 1]['low'].min()
            return lowest_low + (current_atr * atr_multiplier)

