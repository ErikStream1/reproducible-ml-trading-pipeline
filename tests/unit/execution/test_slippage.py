from __future__ import annotations

from src.execution import (slippage_bps, 
                           slippage_vol)
import pytest

@pytest.mark.parametrize(
    ("price", "bps", "expected"),
    [
        (100.0, 10.0, 0.1),
        (25_000.0, 5.0, 12.5),
        (0.0, 50.0, 0.0),
    ],
)
def test_slippage_bps(price: float, bps: float, expected: float) -> None:
    assert slippage_bps(price, bps) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("price", "vol", "k", "expected"),
    [
        (100.0, None, 0.2, 0.0),
        (100.0, 0.01, 0.5, 0.5),
        (50.0, 0.02, 1.0, 1.0),
    ],
)
def test_slippage_vol(price: float, vol: float | None, k: float, expected: float) -> None:
    assert slippage_vol(price=price, vol=vol, k=k) == pytest.approx(expected)