from __future__ import annotations

from src.execution import (fill_price_next_close,
                           fill_price_mid,
                           fill_price_bid_ask)

import pandas as pd
import numpy as np
import pytest

def test_fill_price_next_close():
    data_close = np.random.rand(6)
    t = np.random.randint(6)
    close = pd.Series(data_close)
    
    result = fill_price_next_close(close = close, t = t)
    
    assert isinstance(result, float)
    
    
def test_fill_price_mid():
    data_mid = np.random.rand(6)
    t = np.random.randint(6)
    mid = pd.Series(data_mid)
    
    result = fill_price_mid(mid = mid, t = t)
    
    assert isinstance(result, float)
    

@pytest.mark.parametrize("side",
                         ["BUY",
                          "CLOSE"])

def test_fill_price_bid_ask(side:str):
    data_bid = np.random.rand(6)
    data_ask = np.random.rand(6)
    t = np.random.randint(6)
    bid = pd.Series(data_bid)
    ask = pd.Series(data_ask)
    
    result = fill_price_bid_ask(bid = bid, ask = ask, side = side, t = t)
    
    assert isinstance(result, float)
    