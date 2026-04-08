from __future__ import annotations

import pandas as pd

from src.strategy import build_core_signals


def _feature_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": [100.0, 101.0, 100.5, 102.0, 103.0],
            "MA_7": [99.8, 100.4, 100.2, 101.1, 102.0],
            "MA_30": [99.0, 99.2, 99.4, 99.7, 100.0],
            "Return_1": [0.002, -0.001, 0.0005, 0.003, -0.0007],
            "Volatility_7": [0.01, 0.011, 0.0105, 0.012, 0.012],
            "LogReturn": [0.0019, -0.0011, 0.0004, 0.0029, -0.0008],
        }
    )


def test_build_core_signals_adds_expected_columns() -> None:
    cfg = {"alpha_research": {"signals": {}}}

    out = build_core_signals(cfg, _feature_frame())

    expected = {
        "trend_signal",
        "mean_reversion_signal",
        "volatility_adjusted_signal",
        "ma_spread_signal",
        "composite_signal",
    }
    assert expected.issubset(set(out.columns))
    assert out["composite_signal"].notna().all()