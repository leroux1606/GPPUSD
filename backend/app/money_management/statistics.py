"""Statistical analysis utilities."""

import numpy as np
from typing import List


def calculate_statistics(data: List[float]) -> dict:
    """
    Calculate basic statistics.
    
    Args:
        data: List of numeric values
    
    Returns:
        Dictionary with statistics
    """
    if not data:
        return {
            "mean": 0,
            "std": 0,
            "min": 0,
            "max": 0,
            "median": 0
        }
    
    arr = np.array(data)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "median": float(np.median(arr))
    }

