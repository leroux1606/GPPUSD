"""Order Block Retest Strategy — ICT / Smart Money Concept."""

import pandas as pd
from typing import Dict, Any, List
from app.strategies.base_strategy import BaseStrategy
from app.technical_analysis.indicators import calculate_ema, calculate_atr


class OrderBlockStrategy(BaseStrategy):
    """
    Order Block Retest.

    An Order Block (OB) is the last opposite-coloured candle before a strong
    impulsive move that breaks structure. Institutions leave these behind as
    footprints; price frequently returns to them before continuing.

    Detection:
      Bullish OB: last bearish candle before a run of `impulse_bars` bullish
      bars whose aggregate move ≥ `impulse_atr_mult` × ATR.
      Bearish OB: mirror image.

    Entry:
      - BUY  when a later bar's low dips into a fresh bullish OB AND closes back
        above its high (reclaim); trend filter: price above EMA200.
      - SELL mirror.

    Edge rationale:
      - Institutional order flow leaves imbalances; retests offer tight stops
        and high R:R (stop below the OB, target previous swing).
      - Restricted to London/NY hours for clean liquidity.

    Works across all FX majors — particularly strong on GBP/USD and EUR/USD
    during the London open.
    """

    def get_default_params(self) -> Dict[str, Any]:
        return {
            "impulse_bars": 3,
            "impulse_atr_mult": 1.5,
            "max_age_bars": 40,           # OB is "stale" after this many bars
            "ema_trend_period": 200,
            "atr_period": 14,
            "session_start_hour": 7,      # London open (GMT)
            "session_end_hour": 20,       # NY close (GMT)
            "require_session": True,
        }

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        n = len(df)
        if n < 60:
            return signals

        imp_bars = self.params["impulse_bars"]
        imp_mult = self.params["impulse_atr_mult"]
        max_age = self.params["max_age_bars"]
        require_session = self.params["require_session"]
        s_start = self.params["session_start_hour"]
        s_end = self.params["session_end_hour"]

        atr = calculate_atr(df, self.params["atr_period"]).values
        ema = calculate_ema(df, self.params["ema_trend_period"]).values

        op = df["open"].values
        hi = df["high"].values
        lo = df["low"].values
        cl = df["close"].values

        hours = None
        if "timestamp" in df.columns:
            hours = pd.to_datetime(df["timestamp"]).dt.hour.values

        bullish_obs: List[Dict[str, float]] = []  # {low, high, created}
        bearish_obs: List[Dict[str, float]] = []

        for i in range(imp_bars + 1, n):
            # --- detect new OBs at bar i-1 (previous completed bar) ---
            # Look at the candle that preceded the most recent impulse
            base_idx = i - 1 - imp_bars
            if base_idx > 0 and not pd.isna(atr[i]):
                base_move = cl[i - 1] - cl[base_idx]
                needed = imp_mult * atr[i]
                # Bullish impulse → store the last bearish candle before it
                if base_move >= needed:
                    # find last bearish candle within the last `imp_bars+2` bars
                    for j in range(base_idx, max(base_idx - 3, -1), -1):
                        if j >= 0 and cl[j] < op[j]:
                            bullish_obs.append({"low": lo[j], "high": hi[j], "created": j})
                            break
                # Bearish impulse → store last bullish candle
                elif base_move <= -needed:
                    for j in range(base_idx, max(base_idx - 3, -1), -1):
                        if j >= 0 and cl[j] > op[j]:
                            bearish_obs.append({"low": lo[j], "high": hi[j], "created": j})
                            break

            # --- prune stale OBs ---
            bullish_obs = [ob for ob in bullish_obs if i - ob["created"] <= max_age]
            bearish_obs = [ob for ob in bearish_obs if i - ob["created"] <= max_age]

            # --- session filter ---
            if require_session and hours is not None:
                h = hours[i]
                if not (s_start <= h < s_end):
                    continue

            trend_ok_long = (not pd.isna(ema[i])) and cl[i] > ema[i]
            trend_ok_short = (not pd.isna(ema[i])) and cl[i] < ema[i]

            # --- bullish OB retest: price dips into OB then reclaims ---
            if trend_ok_long:
                for ob in list(bullish_obs):
                    if lo[i] <= ob["high"] and cl[i] > ob["high"]:
                        signals.iloc[i] = 1
                        bullish_obs.remove(ob)  # consume the OB
                        break

            # --- bearish OB retest ---
            if signals.iloc[i] == 0 and trend_ok_short:
                for ob in list(bearish_obs):
                    if hi[i] >= ob["low"] and cl[i] < ob["low"]:
                        signals.iloc[i] = -1
                        bearish_obs.remove(ob)
                        break

        return signals
