from __future__ import annotations

from datetime import timedelta

import pandas as pd
import pytest

from src.data import validate_quote_quality
from src.types import FrameLike, ConfigLike

def _quotes_frame() -> FrameLike:
    return pd.DataFrame(
        {
            "ts_exchange": pd.date_range("2024-01-01", periods=3, freq="min", tz="UTC"),
            "bid": [100.0, 100.1, 100.2],
            "ask": [100.2, 100.3, 100.4],
            "mid": [100.1, 100.2, 100.3],
        }
    )

def _cfg()->ConfigLike:
    return {
        "quote_quality":{
            "enabled": True,
            "max_staleness_seconds": 180,
            "max_relative_spread": 0.01,
            "min_rows": 2
        }
    }

def test_validate_quote_quality_passes_for_valid_quotes() -> None:
    df = _quotes_frame()
    now = df["ts_exchange"].iloc[-1] + timedelta(seconds=30)
    cfg = _cfg()
    cfg["quote_quality"]["max_staleness_seconds"] = 60
    
    validate_quote_quality(df, cfg, now_utc=now)


def test_validate_quote_quality_detects_schema_drift() -> None:
    cfg = _cfg()
    df = _quotes_frame().drop(columns=["mid"])

    with pytest.raises(ValueError, match="schema drift"):
        validate_quote_quality(df, cfg)


def test_validate_quote_quality_detects_missing_quotes() -> None:
    cfg = _cfg()
    df = _quotes_frame()
    df.loc[1, "bid"] = None

    with pytest.raises(ValueError, match="missing or non-numeric"):
            validate_quote_quality(df, cfg)


def test_validate_quote_quality_detects_stale_quotes() -> None:
    df = _quotes_frame()
    cfg = _cfg()
    cfg["quote_quality"]["max_staleness_seconds"] = 60
    now = df["ts_exchange"].iloc[-1] + timedelta(seconds=600)

    with pytest.raises(ValueError, match="stale latest quote"):
        validate_quote_quality(df, cfg, now_utc=now)


def test_validate_quote_quality_detects_spread_spike() -> None:
    df = _quotes_frame()
    df.loc[2, "ask"] = 110.0
    cfg = _cfg()
    cfg["quote_quality"]["max_relative_spread"] = 0.02
    now = df["ts_exchange"].iloc[-1] + timedelta(seconds=10)

    with pytest.raises(ValueError, match="spread spike"):
        validate_quote_quality(df, cfg, now_utc=now)