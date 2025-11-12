"""Performance metrics calculation."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta


def calculate_all_metrics(
    initial_capital: float,
    final_value: float,
    trades: List[Dict[str, Any]],
    equity_curve: List[float],
    returns_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate all performance metrics.
    
    Args:
        initial_capital: Starting capital
        final_value: Final portfolio value
        trades: List of trade dictionaries
        equity_curve: Equity curve over time
        returns_data: Returns analyzer data
    
    Returns:
        Dictionary with all metrics
    """
    metrics = {}
    
    # Returns
    metrics["total_return"] = (final_value - initial_capital) / initial_capital * 100
    metrics["annual_return"] = calculate_annual_return(initial_capital, final_value, len(equity_curve))
    metrics["monthly_returns"] = calculate_monthly_returns(trades, equity_curve)
    
    # Risk metrics
    if equity_curve:
        metrics["max_drawdown"] = calculate_max_drawdown(equity_curve)
        metrics["avg_drawdown"] = calculate_avg_drawdown(equity_curve)
    else:
        metrics["max_drawdown"] = 0
        metrics["avg_drawdown"] = 0
    
    metrics["sharpe_ratio"] = calculate_sharpe_ratio(trades, equity_curve)
    metrics["sortino_ratio"] = calculate_sortino_ratio(trades, equity_curve)
    metrics["calmar_ratio"] = calculate_calmar_ratio(metrics["annual_return"], metrics["max_drawdown"])
    
    # Trade statistics
    if trades:
        metrics["total_trades"] = len(trades)
        metrics["win_rate"] = calculate_win_rate(trades)
        metrics["profit_factor"] = calculate_profit_factor(trades)
        metrics["avg_win"] = calculate_avg_win(trades)
        metrics["avg_loss"] = calculate_avg_loss(trades)
        metrics["expectancy"] = calculate_expectancy(trades)
        metrics["largest_win"] = max([t.get("pnl", 0) for t in trades], default=0)
        metrics["largest_loss"] = min([t.get("pnl", 0) for t in trades], default=0)
    else:
        metrics["total_trades"] = 0
        metrics["win_rate"] = 0
        metrics["profit_factor"] = 0
        metrics["avg_win"] = 0
        metrics["avg_loss"] = 0
        metrics["expectancy"] = 0
        metrics["largest_win"] = 0
        metrics["largest_loss"] = 0
    
    # Streaks
    if trades:
        metrics["longest_win_streak"] = calculate_longest_win_streak(trades)
        metrics["longest_loss_streak"] = calculate_longest_loss_streak(trades)
        metrics["max_consecutive_losses"] = metrics["longest_loss_streak"]
    else:
        metrics["longest_win_streak"] = 0
        metrics["longest_loss_streak"] = 0
        metrics["max_consecutive_losses"] = 0
    
    # Additional metrics
    metrics["recovery_factor"] = calculate_recovery_factor(metrics["total_return"], metrics["max_drawdown"])
    metrics["profit_to_max_drawdown"] = metrics["total_return"] / abs(metrics["max_drawdown"]) if metrics["max_drawdown"] != 0 else 0
    
    return metrics


def calculate_annual_return(initial_capital: float, final_value: float, num_bars: int) -> float:
    """Calculate annualized return."""
    if num_bars == 0:
        return 0
    
    # Assume daily bars (252 trading days per year)
    years = num_bars / 252
    if years == 0:
        return 0
    
    total_return = (final_value - initial_capital) / initial_capital
    annual_return = ((1 + total_return) ** (1 / years) - 1) * 100
    return annual_return


def calculate_monthly_returns(trades: List[Dict], equity_curve: List[float]) -> Dict[str, float]:
    """Calculate monthly returns."""
    # Simplified - would need date information
    return {}


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """Calculate maximum drawdown percentage."""
    if not equity_curve:
        return 0
    
    equity = np.array(equity_curve)
    running_max = np.maximum.accumulate(equity)
    drawdown = (equity - running_max) / running_max * 100
    return abs(min(drawdown))


def calculate_avg_drawdown(equity_curve: List[float]) -> float:
    """Calculate average drawdown."""
    if not equity_curve:
        return 0
    
    equity = np.array(equity_curve)
    running_max = np.maximum.accumulate(equity)
    drawdown = (equity - running_max) / running_max * 100
    drawdown = drawdown[drawdown < 0]
    return abs(np.mean(drawdown)) if len(drawdown) > 0 else 0


def calculate_sharpe_ratio(trades: List[Dict], equity_curve: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio."""
    if not trades or len(trades) < 2:
        return 0
    
    returns = [t.get("pnl", 0) / 10000 for t in trades]  # Normalize
    
    if len(returns) < 2:
        return 0
    
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    # Annualize
    sharpe = (mean_return - risk_free_rate / 252) / std_return * np.sqrt(252)
    return sharpe


def calculate_sortino_ratio(trades: List[Dict], equity_curve: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino ratio."""
    if not trades or len(trades) < 2:
        return 0
    
    returns = [t.get("pnl", 0) / 10000 for t in trades]
    
    if len(returns) < 2:
        return 0
    
    mean_return = np.mean(returns)
    downside_returns = [r for r in returns if r < 0]
    
    if len(downside_returns) == 0:
        return float('inf') if mean_return > risk_free_rate / 252 else 0
    
    downside_std = np.std(downside_returns)
    
    if downside_std == 0:
        return 0
    
    sortino = (mean_return - risk_free_rate / 252) / downside_std * np.sqrt(252)
    return sortino


def calculate_calmar_ratio(annual_return: float, max_drawdown: float) -> float:
    """Calculate Calmar ratio."""
    if max_drawdown == 0:
        return 0
    return annual_return / abs(max_drawdown)


def calculate_win_rate(trades: List[Dict]) -> float:
    """Calculate win rate percentage."""
    if not trades:
        return 0
    
    winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
    return len(winning_trades) / len(trades) * 100


def calculate_profit_factor(trades: List[Dict]) -> float:
    """Calculate profit factor."""
    if not trades:
        return 0
    
    gross_profit = sum([t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0])
    gross_loss = abs(sum([t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0]))
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0
    
    return gross_profit / gross_loss


def calculate_avg_win(trades: List[Dict]) -> float:
    """Calculate average winning trade."""
    winning_trades = [t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0]
    return np.mean(winning_trades) if winning_trades else 0


def calculate_avg_loss(trades: List[Dict]) -> float:
    """Calculate average losing trade."""
    losing_trades = [t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0]
    return np.mean(losing_trades) if losing_trades else 0


def calculate_expectancy(trades: List[Dict]) -> float:
    """Calculate trade expectancy."""
    if not trades:
        return 0
    
    win_rate = calculate_win_rate(trades) / 100
    avg_win = calculate_avg_win(trades)
    avg_loss = abs(calculate_avg_loss(trades))
    
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    return expectancy


def calculate_longest_win_streak(trades: List[Dict]) -> int:
    """Calculate longest winning streak."""
    if not trades:
        return 0
    
    max_streak = 0
    current_streak = 0
    
    for trade in trades:
        if trade.get("pnl", 0) > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def calculate_longest_loss_streak(trades: List[Dict]) -> int:
    """Calculate longest losing streak."""
    if not trades:
        return 0
    
    max_streak = 0
    current_streak = 0
    
    for trade in trades:
        if trade.get("pnl", 0) < 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def calculate_recovery_factor(total_return: float, max_drawdown: float) -> float:
    """Calculate recovery factor."""
    if max_drawdown == 0:
        return 0
    return total_return / abs(max_drawdown)

