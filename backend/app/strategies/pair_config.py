"""
Per-pair configuration: pip size, sessions, recommended strategies, characteristics.

Each pair has different liquidity windows, volatility profiles, and strategy affinities.
This config drives the signal engine, position sizing, and UI display.
"""

from typing import Dict, Any

# All times are UTC (GMT)
PAIR_CONFIG: Dict[str, Dict[str, Any]] = {

    "GBP_USD": {
        "display":          "GBP/USD",
        "pip_size":         0.0001,   # 1 pip = 0.0001
        "pip_multiplier":   10000,    # close * pip_multiplier → pips
        "pip_value_usd":    10.0,     # $ per pip per standard lot (approx)
        "typical_spread":   1.5,      # pips
        "typical_daily_atr": 80,      # pips
        "yahoo_symbol":     "GBPUSD=X",
        "prime_sessions":   ["London", "London/NY Overlap"],
        "avoid_sessions":   ["Asian"],  # thin liquidity
        "characteristics":  "High volatility, strong trending, very reactive to UK/US data",
        "recommended_strategies": [
            "asian_range_breakout",
            "opening_range_breakout",
            "order_block",
            "liquidity_sweep",
            "squeeze_momentum",
            "keltner_pullback",
            "fair_value_gap",
            "vwap_bounce",
        ],
    },

    "EUR_USD": {
        "display":          "EUR/USD",
        "pip_size":         0.0001,
        "pip_multiplier":   10000,
        "pip_value_usd":    10.0,
        "typical_spread":   0.8,
        "typical_daily_atr": 70,
        "yahoo_symbol":     "EURUSD=X",
        "prime_sessions":   ["London", "London/NY Overlap"],
        "avoid_sessions":   [],
        "characteristics":  "Most liquid pair. Smooth trends. Frankfurt open (07:00) and London (08:00) key.",
        "recommended_strategies": [
            "eur_usd_breakout",
            "opening_range_breakout",
            "order_block",
            "squeeze_momentum",
            "keltner_pullback",
            "liquidity_sweep",
            "macd_signal",
        ],
    },

    "USD_JPY": {
        "display":          "USD/JPY",
        "pip_size":         0.01,     # 1 pip = 0.01 (JPY pairs)
        "pip_multiplier":   100,      # close * 100 → pips
        "pip_value_usd":    9.0,      # approx at 150 rate
        "typical_spread":   0.8,
        "typical_daily_atr": 70,
        "yahoo_symbol":     "USDJPY=X",
        "prime_sessions":   ["Asian", "London/NY Overlap", "NY"],
        "avoid_sessions":   [],
        "characteristics":  "Risk-on/risk-off driven. Very active in Tokyo session. BoJ intervention risk.",
        "recommended_strategies": [
            "tokyo_range_breakout",
            "opening_range_breakout",
            "order_block",
            "squeeze_momentum",
            "keltner_pullback",
            "triple_screen",
            "momentum",
        ],
    },

    "USD_CHF": {
        "display":          "USD/CHF",
        "pip_size":         0.0001,
        "pip_multiplier":   10000,
        "pip_value_usd":    11.0,     # approx, USD quoted, CHF base
        "typical_spread":   1.5,
        "typical_daily_atr": 65,
        "yahoo_symbol":     "USDCHF=X",
        "prime_sessions":   ["London", "London/NY Overlap"],
        "avoid_sessions":   ["Asian"],
        "characteristics":  "Safe-haven. Often mirrors EUR/USD inversely. SNB surprise intervention risk.",
        "recommended_strategies": [
            "mean_reversion",
            "liquidity_sweep",
            "squeeze_momentum",
            "keltner_pullback",
            "bollinger_breakout",
            "triple_screen",
        ],
    },

    "AUD_USD": {
        "display":          "AUD/USD",
        "pip_size":         0.0001,
        "pip_multiplier":   10000,
        "pip_value_usd":    10.0,
        "typical_spread":   1.2,
        "typical_daily_atr": 65,
        "yahoo_symbol":     "AUDUSD=X",
        "prime_sessions":   ["Asian", "London/NY Overlap"],
        "avoid_sessions":   [],
        "characteristics":  "Commodity-linked (gold, iron ore). Active in Sydney/Asian sessions. RBA and China data sensitive.",
        "recommended_strategies": [
            "commodity_momentum",
            "asian_range_breakout",
            "keltner_pullback",
            "squeeze_momentum",
            "liquidity_sweep",
            "breakout",
        ],
    },

    "USD_CAD": {
        "display":          "USD/CAD",
        "pip_size":         0.0001,
        "pip_multiplier":   10000,
        "pip_value_usd":    7.5,      # approx, varies with USDCAD rate
        "typical_spread":   1.5,
        "typical_daily_atr": 65,
        "yahoo_symbol":     "USDCAD=X",
        "prime_sessions":   ["NY", "London/NY Overlap"],
        "avoid_sessions":   ["Asian"],
        "characteristics":  "Oil-correlated (inverse — stronger CAD when oil rises). Most active during NY session.",
        "recommended_strategies": [
            "ny_breakout",
            "opening_range_breakout",
            "commodity_momentum",
            "order_block",
            "keltner_pullback",
            "liquidity_sweep",
        ],
    },
}

# Ordered list for UI display
ALL_PAIRS = ["GBP_USD", "EUR_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD"]


def get_pair(symbol: str) -> Dict[str, Any]:
    """Return config for a pair, defaulting to GBP_USD if unknown."""
    return PAIR_CONFIG.get(symbol, PAIR_CONFIG["GBP_USD"])
