"""Fair Value Gap (FVG) Strategy — ICT / Smart Money Concept."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_ema, calculate_atr


class FairValueGapStrategy(BaseStrategy):
    """
    Fair Value Gap (FVG) Strategy.

    Based on the ICT (Inner Circle Trader) / Smart Money Concept framework.

    A Fair Value Gap is a 3-candle pattern where price moves so quickly that
    it leaves an 'imbalance' — a gap between candle[i-2].high and candle[i].low
    (bullish FVG) or candle[i-2].low and candle[i].high (bearish FVG).

    Logic:
    - Detect FVGs on each bar.
    - Enter when price retraces into the FVG (50% fill) — this is the edge.
    - Trend filter: only take FVGs that align with the short-term EMA direction.
    - Session filter: only trade during London and NY sessions (07:00–20:00 GMT).

    Edge rationale:
    - Institutions leave these imbalances intentionally; price often returns to
      'fill' them before continuing in the original direction.
    - High R:R setups: stop below/above the full FVG, target previous swing high/low.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "min_gap_pips": 0.0003,      # Minimum FVG size (~3 pips) — ignore noise
            "fvg_fill_pct": 0.5,         # Enter when price fills 50% into the gap
            "trend_ema_period": 50,      # EMA for trend direction filter
            "atr_period": 14,
            "session_filter": True,      # Only trade London/NY (07:00–20:00 GMT)
            "session_start_hour": 7,
            "session_end_hour": 20,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)

        if len(df) < 3:
            return signals

        min_gap = self.params["min_gap_pips"]
        fill_pct = self.params["fvg_fill_pct"]
        trend_ema = calculate_ema(df, self.params["trend_ema_period"])
        session_filter = self.params["session_filter"]
        session_start = self.params["session_start_hour"]
        session_end = self.params["session_end_hour"]

        df = df.copy()
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

        # Build FVG table: for each bar i, record any FVG defined by bars i-2, i-1, i
        bullish_fvgs = []   # (gap_low, gap_high, created_at_i) — price left a gap upward
        bearish_fvgs = []   # (gap_low, gap_high, created_at_i)

        for i in range(2, len(df)):
            # Session filter
            if session_filter and 'hour' in df.columns:
                h = df.iloc[i]['hour']
                if not (session_start <= h < session_end):
                    continue

            candle_a = df.iloc[i - 2]  # 2 bars ago
            candle_b = df.iloc[i - 1]  # middle candle (the impulse)
            candle_c = df.iloc[i]      # current bar

            close = candle_c['close']
            ema_val = trend_ema.iloc[i]

            # Bullish FVG: candle_c.low > candle_a.high (gap up — bullish impulse)
            gap_low = candle_a['high']
            gap_high = candle_c['low']
            if gap_high > gap_low and (gap_high - gap_low) >= min_gap:
                # Trend must be bullish (price above EMA)
                if not pd.isna(ema_val) and close > ema_val:
                    bullish_fvgs.append({
                        'gap_low': gap_low,
                        'gap_high': gap_high,
                        'mid': gap_low + (gap_high - gap_low) * fill_pct,
                        'created': i,
                    })

            # Bearish FVG: candle_c.high < candle_a.low (gap down — bearish impulse)
            gap_high_b = candle_a['low']
            gap_low_b = candle_c['high']
            if gap_high_b > gap_low_b and (gap_high_b - gap_low_b) >= min_gap:
                if not pd.isna(ema_val) and close < ema_val:
                    bearish_fvgs.append({
                        'gap_low': gap_low_b,
                        'gap_high': gap_high_b,
                        'mid': gap_high_b - (gap_high_b - gap_low_b) * fill_pct,
                        'created': i,
                    })

            # Check if current price retraces into a recent bullish FVG
            # Keep only FVGs from the last 20 bars
            bullish_fvgs = [g for g in bullish_fvgs if i - g['created'] <= 20]
            bearish_fvgs = [g for g in bearish_fvgs if i - g['created'] <= 20]

            for fvg in bullish_fvgs:
                # Price dips into the gap (retest) — buy at the 50% level
                if candle_c['low'] <= fvg['mid'] and close > fvg['gap_low']:
                    signals.iloc[i] = 1
                    break

            for fvg in bearish_fvgs:
                # Price rallies into the gap (retest) — sell at the 50% level
                if candle_c['high'] >= fvg['mid'] and close < fvg['gap_high']:
                    signals.iloc[i] = -1
                    break

        return signals
