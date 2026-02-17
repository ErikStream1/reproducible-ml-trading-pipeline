import pandas as pd

from src.strategy import target_qty_from_fixed_notional


def test_target_qty_applies_cap_and_min_qty() -> None:
    cfg = {
        "strategy": {
            "sizing": {
                "target_notional": 100.0,
                "min_qty": 0.2,
                "max_notional": 50.0,
            }
        }
    }
    idx = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC")
    desired = pd.Series([1, -1, 0], index=idx)
    mid = pd.Series([100.0, 25.0, 10.0], index=idx)

    qty = target_qty_from_fixed_notional(cfg, desired, mid)

    assert qty.tolist() == [0.5, -2.0, 0.0]


def test_target_qty_reindexes_signal_to_mid_index() -> None:
    cfg = {"strategy": {"sizing": {"target_notional": 10.0, "min_qty": 0.0}}}
    mid_idx = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    desired = pd.Series([1], index=[mid_idx[0]])
    mid = pd.Series([5.0, 10.0], index=mid_idx)

    qty = target_qty_from_fixed_notional(cfg, desired, mid)

    assert qty.tolist() == [2.0, 1.0]