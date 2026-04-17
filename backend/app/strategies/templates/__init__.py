"""Strategy templates."""

from app.strategies.templates.ma_crossover import MACrossoverStrategy
from app.strategies.templates.rsi_divergence import RSIDivergenceStrategy
from app.strategies.templates.bollinger_breakout import BollingerBreakoutStrategy
from app.strategies.templates.macd_signal import MACDSignalStrategy
from app.strategies.templates.stochastic import StochasticStrategy
from app.strategies.templates.ichimoku import IchimokuStrategy
from app.strategies.templates.scalping import ScalpingStrategy
from app.strategies.templates.support_resistance import SupportResistanceStrategy
from app.strategies.templates.fibonacci import FibonacciStrategy
from app.strategies.templates.range_trading import RangeTradingStrategy
from app.strategies.templates.breakout import BreakoutStrategy
from app.strategies.templates.mean_reversion import MeanReversionStrategy
from app.strategies.templates.momentum import MomentumStrategy
from app.strategies.templates.grid_trading import GridTradingStrategy
from app.strategies.templates.martingale import MartingaleStrategy
from app.strategies.templates.pivot_points import PivotPointStrategy
from app.strategies.templates.triple_screen import TripleScreenStrategy
from app.strategies.templates.turtle import TurtleStrategy
from app.strategies.templates.session_breakout import SessionBreakoutStrategy
from app.strategies.templates.asian_range_breakout import AsianRangeBreakoutStrategy
from app.strategies.templates.fair_value_gap import FairValueGapStrategy
from app.strategies.templates.vwap_bounce import VWAPBounceStrategy
from app.strategies.templates.eur_usd_breakout import EURUSDBreakoutStrategy
from app.strategies.templates.tokyo_range_breakout import TokyoRangeBreakoutStrategy
from app.strategies.templates.commodity_momentum import CommodityMomentumStrategy
from app.strategies.templates.ny_breakout import NYBreakoutStrategy
from app.strategies.templates.order_block import OrderBlockStrategy
from app.strategies.templates.liquidity_sweep import LiquiditySweepStrategy
from app.strategies.templates.opening_range_breakout import OpeningRangeBreakoutStrategy
from app.strategies.templates.squeeze_momentum import SqueezeMomentumStrategy
from app.strategies.templates.keltner_pullback import KeltnerPullbackStrategy

__all__ = [
    "MACrossoverStrategy",
    "RSIDivergenceStrategy",
    "BollingerBreakoutStrategy",
    "MACDSignalStrategy",
    "StochasticStrategy",
    "IchimokuStrategy",
    "ScalpingStrategy",
    "SupportResistanceStrategy",
    "FibonacciStrategy",
    "RangeTradingStrategy",
    "BreakoutStrategy",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "GridTradingStrategy",
    "MartingaleStrategy",
    "PivotPointStrategy",
    "TripleScreenStrategy",
    "TurtleStrategy",
    "SessionBreakoutStrategy",
    "AsianRangeBreakoutStrategy",
    "FairValueGapStrategy",
    "VWAPBounceStrategy",
    "EURUSDBreakoutStrategy",
    "TokyoRangeBreakoutStrategy",
    "CommodityMomentumStrategy",
    "NYBreakoutStrategy",
    "OrderBlockStrategy",
    "LiquiditySweepStrategy",
    "OpeningRangeBreakoutStrategy",
    "SqueezeMomentumStrategy",
    "KeltnerPullbackStrategy",
]
