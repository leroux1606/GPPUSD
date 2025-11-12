"""Performance tracking."""

from typing import List, Dict, Any
from app.money_management.equity_tracker import EquityTracker


class PerformanceTracker:
    """Track trading performance."""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize performance tracker.
        
        Args:
            initial_capital: Initial capital
        """
        self.equity_tracker = EquityTracker(initial_capital)
        self.trades: List[Dict[str, Any]] = []
    
    def add_trade(self, trade: Dict[str, Any]):
        """
        Add a trade.
        
        Args:
            trade: Trade dictionary
        """
        self.trades.append(trade)
    
    def get_win_rate(self) -> float:
        """Calculate win rate."""
        if not self.trades:
            return 0
        
        winning_trades = [t for t in self.trades if t.get("pnl", 0) > 0]
        return len(winning_trades) / len(self.trades) * 100
    
    def get_profit_factor(self) -> float:
        """Calculate profit factor."""
        if not self.trades:
            return 0
        
        gross_profit = sum([t.get("pnl", 0) for t in self.trades if t.get("pnl", 0) > 0])
        gross_loss = abs(sum([t.get("pnl", 0) for t in self.trades if t.get("pnl", 0) < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        
        return gross_profit / gross_loss

