"""Strategies API routes."""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from app.strategies.strategy_builder import StrategyBuilder
from app.strategies.strategy_executor import StrategyExecutor
from app.utils.logger import logger

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("")
async def list_strategies():
    """List all available strategies."""
    try:
        strategies = StrategyBuilder.list_available_strategies()
        return {"strategies": strategies, "count": len(strategies)}
    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_strategy(config: Dict[str, Any] = Body(...)):
    """Create a new strategy."""
    try:
        StrategyBuilder.validate_strategy_config(config)
        strategy = StrategyBuilder.create_from_json(config)
        return {
            "status": "success",
            "strategy": strategy.get_strategy_info()
        }
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get strategy details."""
    try:
        # In a real app, this would load from database
        # For now, create from type
        strategy = StrategyBuilder.create_strategy(strategy_id)
        return strategy.get_strategy_info()
    except Exception as e:
        logger.error(f"Error getting strategy: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{strategy_id}/signals")
async def generate_signals(
    strategy_id: str,
    data: Dict[str, Any] = Body(...)
):
    """Generate signals for a strategy."""
    try:
        import pandas as pd
        
        strategy = StrategyBuilder.create_strategy(strategy_id, data.get("params"))
        executor = StrategyExecutor(strategy)
        
        # Convert data to DataFrame
        df = pd.DataFrame(data.get("price_data", []))
        if len(df) == 0:
            raise ValueError("No price data provided")
        
        signals = executor.execute(df)
        summary = executor.get_signal_summary(df)
        
        return {
            "signals": signals.tolist(),
            "summary": summary,
            "latest_signal": executor.get_latest_signal(df)
        }
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

