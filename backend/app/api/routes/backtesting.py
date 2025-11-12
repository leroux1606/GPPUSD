"""Backtesting API routes."""

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from app.strategies.strategy_builder import StrategyBuilder
from app.backtesting.engine import BacktestEngine
from app.backtesting.monte_carlo import MonteCarloSimulation
from app.backtesting.walk_forward import WalkForwardAnalysis
from app.data.data_manager import data_manager
from app.utils.logger import logger

router = APIRouter(prefix="/api/backtest", tags=["backtesting"])


@router.post("/run")
async def run_backtest(config: Dict[str, Any] = Body(...)):
    """Run a backtest."""
    try:
        strategy_type = config.get("strategy_type")
        strategy_params = config.get("params", {})
        symbol = config.get("symbol", "GBP_USD")
        timeframe = config.get("timeframe", "1h")
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        initial_capital = config.get("initial_capital", 10000)
        commission = config.get("commission", 0.0001)
        
        # Get historical data
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await data_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end
        )
        
        if len(df) == 0:
            raise ValueError("No historical data available")
        
        # Create strategy
        strategy = StrategyBuilder.create_strategy(strategy_type, strategy_params)
        
        # Run backtest
        engine = BacktestEngine(strategy, df, initial_capital, commission)
        results = engine.run()
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_strategy(config: Dict[str, Any] = Body(...)):
    """Optimize strategy parameters."""
    try:
        from app.strategies.optimizer import StrategyOptimizer
        from app.strategies.strategy_builder import STRATEGY_REGISTRY
        
        strategy_type = config.get("strategy_type")
        param_grid = config.get("param_grid", {})
        symbol = config.get("symbol", "GBP_USD")
        timeframe = config.get("timeframe", "1h")
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        initial_capital = config.get("initial_capital", 10000)
        commission = config.get("commission", 0.0001)
        
        if strategy_type not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = STRATEGY_REGISTRY[strategy_type]
        
        # Get data
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await data_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end
        )
        
        # Optimize
        optimizer = StrategyOptimizer(strategy_class, df)
        results = optimizer.grid_search(param_grid, initial_capital, commission)
        
        return {
            "status": "success",
            "best_params": results[0]["params"] if results else {},
            "top_results": results[:10]
        }
    except Exception as e:
        logger.error(f"Error optimizing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monte-carlo")
async def run_monte_carlo(config: Dict[str, Any] = Body(...)):
    """Run Monte Carlo simulation."""
    try:
        trades = config.get("trades", [])
        initial_capital = config.get("initial_capital", 10000)
        n_simulations = config.get("n_simulations", 1000)
        
        simulation = MonteCarloSimulation(trades, initial_capital)
        results = simulation.run_simulation(n_simulations)
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error running Monte Carlo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/walk-forward")
async def run_walk_forward(config: Dict[str, Any] = Body(...)):
    """Run walk-forward analysis."""
    try:
        strategy_type = config.get("strategy_type")
        strategy_params = config.get("params", {})
        symbol = config.get("symbol", "GBP_USD")
        timeframe = config.get("timeframe", "1h")
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        initial_capital = config.get("initial_capital", 10000)
        commission = config.get("commission", 0.0001)
        
        # Get data
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await data_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end
        )
        
        # Create strategy
        strategy = StrategyBuilder.create_strategy(strategy_type, strategy_params)
        
        # Run walk-forward
        wf = WalkForwardAnalysis(strategy, df, initial_capital, commission)
        results = wf.run()
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error running walk-forward: {e}")
        raise HTTPException(status_code=500, detail=str(e))

