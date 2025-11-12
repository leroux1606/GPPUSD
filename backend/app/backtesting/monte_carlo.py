"""Monte Carlo simulation for backtesting."""

import random
import numpy as np
from typing import List, Dict, Any
from app.backtesting.metrics import calculate_all_metrics


class MonteCarloSimulation:
    """Monte Carlo simulation for strategy performance."""
    
    def __init__(self, trades: List[Dict[str, Any]], initial_capital: float = 10000):
        """
        Initialize Monte Carlo simulation.
        
        Args:
            trades: List of historical trades
            initial_capital: Initial capital
        """
        self.trades = trades
        self.initial_capital = initial_capital
    
    def run_simulation(
        self,
        n_simulations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation.
        
        Args:
            n_simulations: Number of simulations to run
            confidence_level: Confidence level for results
        
        Returns:
            Dictionary with simulation results
        """
        if not self.trades:
            return {
                "final_values": [],
                "mean_final_value": self.initial_capital,
                "std_final_value": 0,
                "percentile_5": self.initial_capital,
                "percentile_95": self.initial_capital,
                "probability_of_profit": 0,
                "max_drawdown_distribution": []
            }
        
        final_values = []
        max_drawdowns = []
        
        for _ in range(n_simulations):
            # Randomly shuffle trades
            shuffled_trades = random.sample(self.trades, len(self.trades))
            
            # Simulate equity curve
            equity = self.initial_capital
            peak_equity = equity
            max_dd = 0
            
            for trade in shuffled_trades:
                equity += trade.get("pnl", 0)
                if equity > peak_equity:
                    peak_equity = equity
                
                drawdown = (equity - peak_equity) / peak_equity * 100
                if drawdown < max_dd:
                    max_dd = drawdown
            
            final_values.append(equity)
            max_drawdowns.append(abs(max_dd))
        
        # Calculate statistics
        final_values = np.array(final_values)
        max_drawdowns = np.array(max_drawdowns)
        
        percentile_5_idx = int((1 - confidence_level) / 2 * n_simulations)
        percentile_95_idx = int((1 + confidence_level) / 2 * n_simulations)
        
        sorted_values = np.sort(final_values)
        sorted_drawdowns = np.sort(max_drawdowns)
        
        return {
            "final_values": final_values.tolist(),
            "mean_final_value": float(np.mean(final_values)),
            "std_final_value": float(np.std(final_values)),
            "percentile_5": float(sorted_values[percentile_5_idx]),
            "percentile_95": float(sorted_values[percentile_95_idx]),
            "probability_of_profit": float(np.sum(final_values > self.initial_capital) / n_simulations * 100),
            "max_drawdown_distribution": max_drawdowns.tolist(),
            "mean_max_drawdown": float(np.mean(max_drawdowns)),
            "worst_case_drawdown": float(sorted_drawdowns[percentile_95_idx])
        }

