from __future__ import annotations
from src.execution import (fill_price_next_close,
                           fill_price_mid,
                           fill_price_bid_ask)

from src.types import SeriesLike
import pandas as pd
import pytest

@pytest.fixture
def price_series()-> tuple[SeriesLike, ...]:
    close = pd.Series([100.0, 101.5, 102.0])
    mid = pd.Series([99.5, 100.5, 101.0])
    bid = pd.Series([99.0, 100.0, 100.5])
    ask = pd.Series([100.0, 101.0, 101.5])
    
    return close, mid, bid, ask


def test_fill_price_next_close_returns_selected_bar(price_series: tuple[SeriesLike, ...]) -> None:
    close, *_ = price_series
 
    assert fill_price_next_close(close=close, t=1) == pytest.approx(101.5)


def test_fill_price_mid_returns_selected_bar(price_series: tuple[SeriesLike, ...]) -> None:
    _, mid, *_ = price_series

    assert fill_price_mid(mid=mid, t=2) == pytest.approx(101.0)

@pytest.mark.parametrize(
    ("side", "expected"),
    [
        ("BUY", 101.0),
        ("buy", 101.0),
        ("SELL", 100.0),
        ("sell", 100.0),
        ("unknown", 100.0),
    ],
)
def test_fill_price_bid_ask_selects_quote_by_side(
    side: str,
    expected: float,
    price_series: tuple[SeriesLike, ...],
) -> None:
    *_, bid, ask = price_series
    if side == "unknown":
        with pytest.raises(ValueError):
            fill_price_bid_ask(bid=bid, ask=ask, side=side, t=1) 
    else:       
        assert fill_price_bid_ask(bid=bid, ask=ask, side=side, t=1) == pytest.approx(expected)