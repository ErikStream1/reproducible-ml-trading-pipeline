from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.execution import evaluate_pre_trade_risk_limits


def test_risk_limits_blocks_max_position(tmp_path: Path) -> None:
    blotter_path = tmp_path / "blotter.csv"
    cfg = {
        "execution": {
            "risk_limits": {
                "enabled": True,
                "max_position": 1,
            }
        }
    }

    decision = evaluate_pre_trade_risk_limits(
        cfg=cfg,
        blotter_path=blotter_path,
        previous_position=1,
        requested_target_position=2,
        order_qty_units=0.001,
        reference_price=100.0,
        timestamp="2024-01-01T01:00:00+00:00",
    )

    assert decision.allowed is False
    assert "max_position" in decision.reasons


def test_risk_limits_blocks_daily_notional(tmp_path: Path) -> None:
    blotter_path = tmp_path / "blotter.csv"
    pd.DataFrame(
        [
            {"timestamp": "2024-01-01T00:05:00+00:00", "notional_executed": 70.0, "fills_count": 1},
            {"timestamp": "2024-01-01T00:15:00+00:00", "notional_executed": 20.0, "fills_count": 1},
        ]
    ).to_csv(blotter_path, index=False)

    cfg = {
        "execution": {
            "risk_limits": {
                "enabled": True,
                "max_notional_per_day": 100.0,
            }
        }
    }

    decision = evaluate_pre_trade_risk_limits(
        cfg=cfg,
        blotter_path=blotter_path,
        previous_position=0,
        requested_target_position=1,
        order_qty_units=0.2,
        reference_price=100.0,
        timestamp="2024-01-01T01:00:00+00:00",
    )

    assert decision.allowed is False
    assert "max_notional_per_day" in decision.reasons