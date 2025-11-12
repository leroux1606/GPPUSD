"""Risk calculator for portfolio risk metrics."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd


class RiskCalculator:
    """Calculate risk metrics for trading portfolio."""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0
        
        # Annualize
        sharpe = (mean_return - risk_free_rate / 252) / std_return * np.sqrt(252)
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio."""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        downside_returns = returns_array[returns_array < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if mean_return > risk_free_rate / 252 else 0
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0
        
        sortino = (mean_return - risk_free_rate / 252) / downside_std * np.sqrt(252)
        return sortino
    
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if not returns:
            return 0
        
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        return abs(var)
    
    @staticmethod
    def calculate_cvar(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        if not returns:
            return 0
        
        returns_array = np.array(returns)
        var = RiskCalculator.calculate_var(returns, confidence_level)
        cvar = returns_array[returns_array <= -var].mean()
        return abs(cvar) if not np.isnan(cvar) else 0
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """Calculate maximum drawdown."""
        if not equity_curve:
            return 0
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100
        return abs(min(drawdown))
    
    @staticmethod
    def calculate_portfolio_risk(
        positions: List[Dict[str, Any]],
        correlation_matrix: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Calculate portfolio risk metrics.
        
        Args:
            positions: List of position dictionaries
            correlation_matrix: Optional correlation matrix
        
        Returns:
            Dictionary with risk metrics
        """
        if not positions:
            return {
                "total_exposure": 0,
                "net_exposure": 0,
                "gross_exposure": 0,
                "leverage": 0
            }
        
        total_long = sum([p.get("size", 0) for p in positions if p.get("direction", 1) == 1])
        total_short = sum([p.get("size", 0) for p in positions if p.get("direction", 1) == -1])
        
        return {
            "total_exposure": total_long + total_short,
            "net_exposure": total_long - total_short,
            "gross_exposure": total_long + total_short,
            "leverage": (total_long + total_short) / 10000  # Assuming 10k equity
        }

