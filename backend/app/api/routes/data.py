"""Data API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import pandas as pd
from app.data.data_manager import data_manager
from app.data.live_feed import stream_gbpusd_live
from app.utils.logger import logger

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/live")
async def get_live_price():
    """Get current GBP/USD price."""
    try:
        price = data_manager.get_latest_price()
        if price:
            return price
        
        # Fallback: get from provider
        from app.data.providers.yahoo_finance import yahoo_finance_provider
        price_data = yahoo_finance_provider.get_current_price()
        data_manager.cache_latest_price("GBP_USD", price_data)
        return price_data
    except Exception as e:
        logger.error(f"Error getting live price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    symbol: str = Query(default="GBP_USD"),
    timeframe: str = Query(default="1h"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None)
):
    """Get historical OHLCV data."""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await data_manager.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": df.to_dict('records'),
            "count": len(df)
        }
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_historical_data(
    symbol: str = Query(default="GBP_USD"),
    timeframe: str = Query(default="1h"),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    provider: str = Query(default="oanda")
):
    """Download and cache historical data."""
    try:
        from app.data.historical import download_historical, save_historical_data
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        df = await download_historical(symbol, timeframe, start, end, provider)
        filepath = save_historical_data(df, symbol, timeframe)
        
        return {
            "status": "success",
            "filepath": filepath,
            "records": len(df),
            "start_date": df['timestamp'].min().isoformat() if len(df) > 0 else None,
            "end_date": df['timestamp'].max().isoformat() if len(df) > 0 else None
        }
    except Exception as e:
        logger.error(f"Error downloading historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeframes")
async def get_timeframes():
    """Get available timeframes."""
    return {
        "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
        "default": "1h"
    }

