from __future__ import annotations

import numpy as np
import pandas as pd

from src.types import ConfigLike, FrameLike, SeriesLike


def _scaled_tanh(series: SeriesLike, scale: float = 1.0) -> SeriesLike:
    safe_scale = max(float(scale), 1e-12)
    return pd.Series(np.tanh(series.astype(float) / safe_scale), index=series.index)


def build_core_signals(cfg: ConfigLike, feature_frame: FrameLike) -> FrameLike:
    """
    Signals:
      - trend_signal (momentum-style, from moving average crossover)
      - mean_reversion_signal (negative normalized short return)
      - volatility_adjusted_signal (directional return penalized by volatility)
      - ma_spread_signal (normalized MA spread)
      - composite_signal (weighted sum of the four signals)
    """

    frame = feature_frame.copy()
    signal_cfg = cfg["alpha_research"].get("signals", {})

    ma_fast_col = signal_cfg.get("ma_fast_column", "MA_7")
    ma_slow_col = signal_cfg.get("ma_slow_column", "MA_30")
    return_col = signal_cfg.get("return_column", "LogReturn")
    volatility_col = signal_cfg.get("volatility_column", "Volatility_7")
    close_col = signal_cfg.get("close_column", "Close")

    required = [ma_fast_col, ma_slow_col, return_col, volatility_col, close_col]
    missing = [col for col in required if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing feature columns required for composite signals: {missing}")

    trend_scale = float(signal_cfg.get("trend_scale", 0.01))
    mr_scale = float(signal_cfg.get("mean_reversion_scale", 0.01))
    ma_spread_scale = float(signal_cfg.get("ma_spread_scale", trend_scale))
    vol_floor = float(signal_cfg.get("volatility_floor", 1e-6))
    close_floor = float(signal_cfg.get("close_floor", 1e-9))

    ma_fast = frame[ma_fast_col].astype(float)
    ma_slow = frame[ma_slow_col].astype(float)
    ret = frame[return_col].astype(float)
    vol = frame[volatility_col].astype(float).clip(lower=vol_floor)
    close = frame[close_col].astype(float).abs().clip(lower=close_floor)

    trend_raw = (ma_fast / ma_slow) - 1.0
    mean_reversion_raw = -ret
    volatility_adjusted_raw = ret / vol
    ma_spread_raw = (ma_fast - ma_slow) / close

    frame["trend_signal"] = _scaled_tanh(trend_raw, scale=trend_scale)
    frame["mean_reversion_signal"] = _scaled_tanh(mean_reversion_raw, scale=mr_scale)
    frame["volatility_adjusted_signal"] = _scaled_tanh(volatility_adjusted_raw, scale=1.0)
    frame["ma_spread_signal"] = _scaled_tanh(ma_spread_raw, scale=ma_spread_scale)

    weights = signal_cfg.get(
        "weights",
        {
            "trend_signal": 0.35,
            "mean_reversion_signal": 0.20,
            "volatility_adjusted_signal": 0.25,
            "ma_spread_signal": 0.20,
        },
    )

    composite = pd.Series(0.0, index=frame.index)
    for col in ["trend_signal", "mean_reversion_signal", "volatility_adjusted_signal", "ma_spread_signal"]:
        composite = composite + float(weights.get(col, 0.0)) * frame[col].astype(float)

    frame["composite_signal"] = composite
    return frame