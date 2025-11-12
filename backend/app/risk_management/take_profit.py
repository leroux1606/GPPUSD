"""Take profit implementations."""

from typing import Optional, Dict, Any
import pandas as pd


class TakeProfit:
    """Calculate take profit levels."""
    
    @staticmethod
    def fixed_pips(entry_price: float, pips: float, direction: int = 1) -> float:
        """
        Fixed pips take profit.
        
        Args:
            entry_price: Entry price
            pips: Take profit in pips
            direction: 1 for long, -1 for short
        
        Returns:
            Take profit price
        """
        pip_value = pips / 10000
        if direction == 1:  # Long
            return entry_price + pip_value
        else:  # Short
            return entry_price - pip_value
    
    @staticmethod
    def risk_reward_ratio(
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 2.0,
        direction: int = 1
    ) -> float:
        """
        Take profit based on risk/reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_reward_ratio: Risk/reward ratio (e.g., 2.0 for 2:1)
            direction: 1 for long, -1 for short
        
        Returns:
            Take profit price
        """
        risk = abs(entry_price - stop_loss_price)
        reward = risk * risk_reward_ratio
        
        if direction == 1:  # Long
            return entry_price + reward
        else:  # Short
            return entry_price - reward
    
    @staticmethod
    def trailing_take_profit(
        current_price: float,
        highest_price: float,
        trail_pips: float,
        direction: int = 1
    ) -> float:
        """
        Trailing take profit.
        
        Args:
            current_price: Current price
            highest_price: Highest price since entry
            trail_pips: Trailing distance in pips
            direction: 1 for long, -1 for short
        
        Returns:
            Take profit price
        """
        trail_value = trail_pips / 10000
        
        if direction == 1:  # Long
            return highest_price - trail_value
        else:  # Short
            return highest_price + trail_value

