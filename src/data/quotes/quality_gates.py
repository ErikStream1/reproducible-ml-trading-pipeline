from __future__ import annotations

import pandas as pd

from src.types import FrameLike, ConfigLike

def validate_quote_quality(
    quotes_df: FrameLike,
    cfg: ConfigLike,
    now_utc: pd.Timestamp | None = None
    )->None:
    
    quote_quality_cfg = cfg["quote_quality"]
    required_cols = ["ts_exchange", "bid", "ask", "mid"]
    
    missing_cols = [col for col in required_cols if col not in quotes_df.columns]
    if missing_cols:
        raise ValueError(f"Quote schema drift: missing required columns: {missing_cols}")
    
    ts = pd.to_datetime(quotes_df["ts_exchange"], utc=True, errors="coerce")
    if ts.isna().any():
        raise ValueError("Quote schema drift: ts_exchange contains invalid timestamps")

    numeric = quotes_df[["bid", "ask", "mid"]].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise ValueError("Quote quality gate failed: missing or non-numeric bid/ask/mid values")

    if (numeric["ask"] <= numeric["bid"]).any():
        raise ValueError("Quote quality gate failed: ask must be strictly greater than bid")

    if (numeric["mid"] <= 0).any():
        raise ValueError("Quote quality gate failed: mid must be positive")

    reference_now = now_utc if now_utc is not None else pd.Timestamp.now(tz="UTC")
    staleness_seconds = (reference_now - ts.iloc[-1]).total_seconds()
    
    max_staleness_seconds = quote_quality_cfg["max_staleness_seconds"]
    max_relative_spread = quote_quality_cfg["max_relative_spread"]
    
    if staleness_seconds > max_staleness_seconds:
        raise ValueError(
            "Quote quality gate failed: stale latest quote. "
            f"staleness_s={staleness_seconds:.2f} limit={max_staleness_seconds}"
        )

    relative_spread = (numeric["ask"] - numeric["bid"]) / numeric["mid"]
    max_observed = float(relative_spread.max())
    if max_observed > max_relative_spread:
        raise ValueError(
            "Quote quality gate failed: spread spike detected. "
            f"max_relative_spread={max_observed:.6f} limit={max_relative_spread:.6f}"
        )
    