from __future__ import annotations

from src.execution import (slippage_bps, 
                           slippage_vol)
import pytest
import numpy as np

def test_slippage_bps():
    price = 100 * np.random.rand()
    bps = np.random.rand()
    result = slippage_bps(price, bps)
    
    assert isinstance(result,float)

@pytest.mark.parametrize("vol",
                         [None, 2.0])

def test_slippage_vol(vol: float|None):
    price = 100 * np.random.rand()
    k = np.random.rand()
    result = slippage_vol(price = price, vol = vol, k = k)
    
    assert isinstance(result, float)
    