"""Portfolio manager for multi-strategy risk management."""

from typing import Dict, Any, List, Optional
from app.risk_management.risk_calculator import RiskCalculator


class PortfolioManager:
    """Manages portfolio-level risk across multiple strategies."""
    
    def __init__(self, initial_capital: float = 10000, max_daily_loss: float = 500):
        """
        Initialize portfolio manager.
        
        Args:
            initial_capital: Initial capital
            max_daily_loss: Maximum daily loss limit
        """
        self.initial_capital = initial_capital
        self.max_daily_loss = max_daily_loss
        self.positions = []
        self.daily_pnl = 0
    
    def can_open_position(self, position_size: float, risk_amount: float) -> bool:
        """
        Check if position can be opened.
        
        Args:
            position_size: Position size in lots
            risk_amount: Dollar amount at risk
        
        Returns:
            True if position can be opened
        """
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False
        
        # Check if adding this risk would exceed daily limit
        if (self.daily_pnl - risk_amount) < -self.max_daily_loss:
            return False
        
        return True
    
    def add_position(self, position: Dict[str, Any]) -> bool:
        """
        Add position to portfolio.
        
        Args:
            position: Position dictionary
        
        Returns:
            True if added successfully
        """
        if self.can_open_position(
            position.get("size", 0),
            position.get("risk_amount", 0)
        ):
            self.positions.append(position)
            return True
        return False
    
    def update_daily_pnl(self, pnl: float) -> None:
        """
        Update daily P&L.
        
        Args:
            pnl: Profit/loss for the day
        """
        self.daily_pnl = pnl
    
    def get_portfolio_risk(self) -> Dict[str, Any]:
        """
        Get portfolio risk metrics.
        
        Returns:
            Dictionary with risk metrics
        """
        return RiskCalculator.calculate_portfolio_risk(self.positions)
    
    def reset_daily(self) -> None:
        """Reset daily P&L (call at start of each day)."""
        self.daily_pnl = 0

