"""Helper utility functions."""

from typing import Any, Optional
from datetime import datetime, timedelta


def format_price(price: float, decimals: int = 5) -> str:
    """Format price with specified decimals."""
    return f"{price:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage."""
    return f"{value:.{decimals}f}%"


def calculate_pips(price1: float, price2: float) -> float:
    """Calculate pips between two prices."""
    return abs(price1 - price2) * 10000

