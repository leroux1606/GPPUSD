"""Position sizing methods."""

from typing import Dict, Any, Optional
import numpy as np
from app.technical_analysis.indicators import calculate_atr
import pandas as pd


class PositionSizer:
    """Calculate position sizes using various methods."""
    
    def __init__(self, equity: float = 10000):
        """
        Initialize position sizer.
        
        Args:
            equity: Current account equity
        """
        self.equity = equity
    
    def fixed_lot_size(self, lot_size: float = 0.01) -> float:
        """
        Fixed lot size position sizing.
        
        Args:
            lot_size: Fixed lot size
        
        Returns:
            Position size
        """
        return lot_size
    
    def percentage_of_equity(self, percentage: float = 2.0) -> float:
        """
        Position size as percentage of equity.
        
        Args:
            percentage: Percentage of equity to risk
        
        Returns:
            Position size in lots
        """
        risk_amount = self.equity * (percentage / 100)
        # Assuming 1 lot = $100,000 notional for GBP/USD
        lot_value = 100000
        return risk_amount / lot_value
    
    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Kelly Criterion position sizing.
        
        Args:
            win_rate: Win rate (0-1)
            avg_win: Average winning trade
            avg_loss: Average losing trade (positive value)
        
        Returns:
            Kelly percentage
        """
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Cap at 25% to avoid over-leverage
        return min(kelly, 0.25)
    
    def optimal_f(
        self,
        trades: list,
        initial_capital: float
    ) -> float:
        """
        Ralph Vince's Optimal F position sizing.
        
        Args:
            trades: List of trade P&L values
            initial_capital: Initial capital
        
        Returns:
            Optimal F value
        """
        if not trades:
            return 0
        
        returns = [t / initial_capital for t in trades]
        
        best_f = 0
        best_twr = 0
        
        for f in np.arange(0.01, 1.0, 0.01):
            twr = 1.0
            for ret in returns:
                twr *= (1 + f * ret)
            
            if twr > best_twr:
                best_twr = twr
                best_f = f
        
        return best_f
    
    def volatility_based(
        self,
        df: pd.DataFrame,
        risk_per_trade: float,
        atr_period: int = 14,
        atr_multiplier: float = 2.0
    ) -> float:
        """
        Position size based on volatility (ATR).
        
        Args:
            df: Price DataFrame
            risk_per_trade: Dollar amount to risk per trade
            atr_period: ATR period
            atr_multiplier: ATR multiplier for stop loss
        
        Returns:
            Position size in lots
        """
        atr = calculate_atr(df, atr_period)
        current_atr = atr.iloc[-1] if len(atr) > 0 else 0.001
        
        stop_distance = current_atr * atr_multiplier
        
        # Position size = risk / stop distance
        # For GBP/USD, 1 pip = $10 per lot
        pip_value = 10
        stop_in_pips = stop_distance * 10000  # Convert to pips
        
        if stop_in_pips == 0:
            return 0
        
        position_size = risk_per_trade / (stop_in_pips * pip_value)
        return max(0.01, min(position_size, 1.0))  # Clamp between 0.01 and 1.0 lots
    
    def risk_per_trade(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_amount: float
    ) -> float:
        """
        Calculate position size to risk specific dollar amount.
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_amount: Dollar amount to risk
        
        Returns:
            Position size in lots
        """
        stop_distance = abs(entry_price - stop_loss_price)
        
        if stop_distance == 0:
            return 0
        
        # For GBP/USD, 1 pip = $10 per lot
        pip_value = 10
        stop_in_pips = stop_distance * 10000
        
        position_size = risk_amount / (stop_in_pips * pip_value)
        return max(0.01, min(position_size, 1.0))

