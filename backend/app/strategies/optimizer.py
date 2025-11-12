"""Strategy parameter optimization."""

import itertools
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
from app.strategies.base_strategy import BaseStrategy
from app.strategies.strategy_executor import StrategyExecutor
from app.backtesting.engine import BacktestEngine
from app.utils.logger import logger


class StrategyOptimizer:
    """Optimizes strategy parameters using grid search or genetic algorithm."""
    
    def __init__(self, strategy_class: type, data: pd.DataFrame):
        """
        Initialize optimizer.
        
        Args:
            strategy_class: Strategy class to optimize
            data: Historical price data
        """
        self.strategy_class = strategy_class
        self.data = data
    
    def grid_search(
        self,
        param_grid: Dict[str, List[Any]],
        initial_capital: float = 10000,
        commission: float = 0.0001
    ) -> List[Dict[str, Any]]:
        """
        Perform grid search optimization.
        
        Args:
            param_grid: Dictionary of parameter names and value lists
            initial_capital: Initial capital for backtesting
            commission: Commission rate
        
        Returns:
            List of results sorted by performance (best first)
        """
        results = []
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)
        
        logger.info(f"Running grid search with {total_combinations} combinations...")
        
        for i, combination in enumerate(itertools.product(*param_values)):
            params = dict(zip(param_names, combination))
            
            try:
                strategy = self.strategy_class(params)
                executor = StrategyExecutor(strategy)
                engine = BacktestEngine(strategy, self.data, initial_capital, commission)
                
                result = engine.run()
                
                results.append({
                    "params": params,
                    "total_return": result.get("total_return", 0),
                    "sharpe_ratio": result.get("sharpe_ratio", 0),
                    "max_drawdown": result.get("max_drawdown", 0),
                    "win_rate": result.get("win_rate", 0),
                    "profit_factor": result.get("profit_factor", 0),
                    "total_trades": result.get("total_trades", 0)
                })
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Completed {i + 1}/{total_combinations} combinations")
            
            except Exception as e:
                logger.warning(f"Error testing parameters {params}: {e}")
                continue
        
        # Sort by Sharpe ratio (or total return if Sharpe is NaN)
        results.sort(
            key=lambda x: x["sharpe_ratio"] if pd.notna(x["sharpe_ratio"]) else x["total_return"],
            reverse=True
        )
        
        return results
    
    def optimize_by_metric(
        self,
        param_grid: Dict[str, List[Any]],
        metric: str = "sharpe_ratio",
        initial_capital: float = 10000,
        commission: float = 0.0001
    ) -> Dict[str, Any]:
        """
        Find best parameters for a specific metric.
        
        Args:
            param_grid: Parameter grid
            metric: Metric to optimize (sharpe_ratio, total_return, etc.)
            initial_capital: Initial capital
            commission: Commission rate
        
        Returns:
            Best parameter combination and result
        """
        results = self.grid_search(param_grid, initial_capital, commission)
        
        if not results:
            raise ValueError("No valid results from optimization")
        
        best = results[0]
        
        return {
            "best_params": best["params"],
            "best_metric_value": best.get(metric, 0),
            "all_results": results[:10]  # Top 10 results
        }
    
    def random_search(
        self,
        param_ranges: Dict[str, Tuple[Any, Any]],
        n_iterations: int = 50,
        initial_capital: float = 10000,
        commission: float = 0.0001
    ) -> List[Dict[str, Any]]:
        """
        Perform random search optimization.
        
        Args:
            param_ranges: Dictionary of parameter names and (min, max) tuples
            n_iterations: Number of random combinations to test
            initial_capital: Initial capital
            commission: Commission rate
        
        Returns:
            List of results
        """
        import random
        
        results = []
        
        for i in range(n_iterations):
            params = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int):
                    params[param_name] = random.randint(min_val, max_val)
                else:
                    params[param_name] = random.uniform(min_val, max_val)
            
            try:
                strategy = self.strategy_class(params)
                executor = StrategyExecutor(strategy)
                engine = BacktestEngine(strategy, self.data, initial_capital, commission)
                
                result = engine.run()
                
                results.append({
                    "params": params,
                    "total_return": result.get("total_return", 0),
                    "sharpe_ratio": result.get("sharpe_ratio", 0),
                    "max_drawdown": result.get("max_drawdown", 0),
                    "win_rate": result.get("win_rate", 0)
                })
            
            except Exception as e:
                logger.warning(f"Error testing parameters {params}: {e}")
                continue
        
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        return results

