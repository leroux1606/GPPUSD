"""Equity tracker for account equity over time."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class EquityTracker:
    """Track equity over time."""
    
    def __init__(self, initial_equity: float = 10000):
        """
        Initialize equity tracker.
        
        Args:
            initial_equity: Initial account equity
        """
        self.initial_equity = initial_equity
        self.equity_history: List[Dict[str, Any]] = []
    
    def update(self, equity: float, timestamp: Optional[datetime] = None):
        """
        Update equity.
        
        Args:
            equity: Current equity value
            timestamp: Timestamp (defaults to now)
        """
        self.equity_history.append({
            "timestamp": timestamp or datetime.utcnow(),
            "equity": equity
        })
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Get equity curve as DataFrame.
        
        Returns:
            DataFrame with timestamp and equity columns
        """
        if not self.equity_history:
            return pd.DataFrame(columns=["timestamp", "equity"])
        
        return pd.DataFrame(self.equity_history)
    
    def get_current_equity(self) -> float:
        """
        Get current equity.
        
        Returns:
            Current equity value
        """
        if not self.equity_history:
            return self.initial_equity
        return self.equity_history[-1]["equity"]

