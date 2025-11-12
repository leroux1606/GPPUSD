"""Walk-forward analysis for strategy optimization."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from app.strategies.base_strategy import BaseStrategy
from app.backtesting.engine import BacktestEngine
from app.utils.logger import logger


class WalkForwardAnalysis:
    """Walk-forward analysis for strategy validation."""
    
    def __init__(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        initial_capital: float = 10000,
        commission: float = 0.0001
    ):
        """
        Initialize walk-forward analysis.
        
        Args:
            strategy: Strategy instance
            data: Historical price data
            initial_capital: Initial capital
            commission: Commission rate
        """
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
    
    def run(
        self,
        optimization_period: int = 252,  # Days
        test_period: int = 63,  # Days
        step_size: int = 21  # Days
    ) -> Dict[str, Any]:
        """
        Run walk-forward analysis.
        
        Args:
            optimization_period: Period for optimization (in bars)
            test_period: Period for testing (in bars)
            step_size: Step size for rolling window (in bars)
        
        Returns:
            Dictionary with walk-forward results
        """
        results = []
        
        total_bars = len(self.data)
        current_start = 0
        
        while current_start + optimization_period + test_period <= total_bars:
            # Optimization period
            opt_start = current_start
            opt_end = current_start + optimization_period
            opt_data = self.data.iloc[opt_start:opt_end]
            
            # Test period
            test_start = opt_end
            test_end = min(test_start + test_period, total_bars)
            test_data = self.data.iloc[test_start:test_end]
            
            if len(test_data) == 0:
                break
            
            try:
                # Run backtest on test period
                engine = BacktestEngine(
                    self.strategy,
                    test_data,
                    self.initial_capital,
                    self.commission
                )
                
                result = engine.run()
                
                results.append({
                    "optimization_start": opt_start,
                    "optimization_end": opt_end,
                    "test_start": test_start,
                    "test_end": test_end,
                    "total_return": result.get("total_return", 0),
                    "sharpe_ratio": result.get("sharpe_ratio", 0),
                    "max_drawdown": result.get("max_drawdown", 0),
                    "win_rate": result.get("win_rate", 0),
                    "total_trades": result.get("total_trades", 0)
                })
                
                logger.info(f"Walk-forward period {len(results)}: Return={result.get('total_return', 0):.2f}%")
            
            except Exception as e:
                logger.warning(f"Error in walk-forward period: {e}")
            
            # Move to next period
            current_start += step_size
        
        # Calculate aggregate statistics
        if results:
            returns = [r["total_return"] for r in results]
            sharpe_ratios = [r["sharpe_ratio"] for r in results if pd.notna(r["sharpe_ratio"])]
            
            return {
                "periods": results,
                "avg_return": float(np.mean(returns)),
                "std_return": float(np.std(returns)),
                "avg_sharpe": float(np.mean(sharpe_ratios)) if sharpe_ratios else 0,
                "consistency": float(np.sum([r > 0 for r in returns]) / len(returns) * 100),
                "total_periods": len(results)
            }
        else:
            return {
                "periods": [],
                "avg_return": 0,
                "std_return": 0,
                "avg_sharpe": 0,
                "consistency": 0,
                "total_periods": 0
            }

