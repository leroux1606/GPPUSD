"""Indicators API routes."""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import pandas as pd
from app.technical_analysis.indicators import INDICATORS
from app.utils.logger import logger

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("")
async def list_indicators():
    """List all available indicators."""
    return {
        "indicators": list(INDICATORS.keys()),
        "count": len(INDICATORS)
    }


@router.post("/calculate")
async def calculate_indicator(request: Dict[str, Any] = Body(...)):
    """Calculate an indicator."""
    try:
        indicator_name = request.get("indicator")
        price_data = request.get("price_data", [])
        params = request.get("params", {})
        
        if indicator_name not in INDICATORS:
            raise ValueError(f"Unknown indicator: {indicator_name}")
        
        # Convert to DataFrame
        df = pd.DataFrame(price_data)
        if len(df) == 0:
            raise ValueError("No price data provided")
        
        # Calculate indicator
        indicator_func = INDICATORS[indicator_name]
        result = indicator_func(df, **params)
        
        # Convert to list format
        if isinstance(result, pd.Series):
            return {
                "indicator": indicator_name,
                "values": result.tolist(),
                "type": "series"
            }
        elif isinstance(result, pd.DataFrame):
            return {
                "indicator": indicator_name,
                "values": result.to_dict('list'),
                "type": "dataframe"
            }
        else:
            return {
                "indicator": indicator_name,
                "values": result,
                "type": "other"
            }
    except Exception as e:
        logger.error(f"Error calculating indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e))

