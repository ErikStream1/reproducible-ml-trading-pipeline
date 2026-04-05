from __future__ import annotations

import json

import pytest

from src.execution import evaluate_shadow_live_divergence


def _write_fills(path, rows):
    import pandas as pd

    pd.DataFrame(rows).to_csv(path, index=False)


def test_evaluate_shadow_live_divergence_no_alert(tmp_path):
    expected_path = tmp_path / "expected.csv"
    actual_path = tmp_path / "actual.csv"

    _write_fills(
        expected_path,
        [
            {"qty": 0.001, "price": 100_000.0, "fee": 0.1},
            {"qty": 0.001, "price": 100_010.0, "fee": 0.1},
        ],
    )
    _write_fills(
        actual_path,
        [
            {"qty": 0.001, "price": 100_005.0, "fee": 0.1},
            {"qty": 0.001, "price": 100_008.0, "fee": 0.1},
        ],
    )

    cfg = {
        "divergence_monitor": {
            "thresholds": {
                "max_fill_count_diff": 1,
                "max_notional_pct_diff": 0.20,
                "max_avg_fill_price_bps_diff": 20.0,
                "max_fee_bps_diff": 10.0,
            },
            "artifacts": {"output_dir": str(tmp_path / "monitor")},
        }
    }

    result = evaluate_shadow_live_divergence(cfg, expected_path, actual_path)

    assert result.alert_triggered is False
    assert result.metrics.fill_count_abs_diff == 0
    assert result.output_path is not None

    report = json.loads((tmp_path / "monitor" / "divergence_report.json").read_text(encoding="utf-8"))
    assert report["alert_triggered"] is False


def test_evaluate_shadow_live_divergence_triggers_alert(tmp_path):
    expected_path = tmp_path / "expected.csv"
    actual_path = tmp_path / "actual.csv"

    _write_fills(expected_path, [{"qty": 0.001, "price": 100_000.0, "fee": 0.1}])
    _write_fills(actual_path, [{"qty": 0.004, "price": 102_000.0, "fee": 2.0}])

    cfg = {"divergence_monitor": {"thresholds": {"max_fill_count_diff": 0, "max_notional_pct_diff": 0.05,
                                                     "max_avg_fill_price_bps_diff": 5.0, "max_fee_bps_diff": 1.0}}}

    result = evaluate_shadow_live_divergence(cfg, expected_path, actual_path)

    assert result.alert_triggered is True
    assert result.reasons


def test_evaluate_shadow_live_divergence_requires_columns(tmp_path):
    expected_path = tmp_path / "expected.csv"
    actual_path = tmp_path / "actual.csv"

    expected_path.write_text("qty\n1\n", encoding="utf-8")
    actual_path.write_text("qty,price\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError):
        evaluate_shadow_live_divergence({}, expected_path, actual_path)