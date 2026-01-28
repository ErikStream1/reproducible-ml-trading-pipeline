from __future__ import annotations

import pandas as pd
import numpy as np
import pytest

from src.backtest import (
    returns_from_equity,
    max_drawdown,
    sharpe_ratio,
    turnover_from_position
)

def test_returns_from_equity():
    data_eq = np.random.rand(10)
    equity = pd.Series(data_eq)
    
    result = returns_from_equity(equity=equity)
    
    assert len(result) > 0
    assert isinstance(result, pd.Series)

def test_max_drawdown():
    data_eq = np.random.rand(10)
    equity = pd.Series(data_eq)
    
    result = max_drawdown(equity=equity)
    
    assert isinstance(result, float)

@pytest.mark.parametrize("data_ret,periods",
                         [([1,1,1,1],60), 
                          (np.random.rand(10),365),
                          (np.random.rand(10),-10)])

def test_sharpe_ratio(data_ret,periods):
    ret = pd.Series(data_ret)
    
    if periods < 0:
        with pytest.raises(ValueError):
            sharpe_ratio(ret = ret, periods_per_year = periods)
    else:
        result = sharpe_ratio(ret = ret, periods_per_year = periods)
        assert isinstance(result, float)

@pytest.mark.parametrize("data_pos",
                         [[0,0,0,0,0],
                          np.random.rand(5)])  
def test_turnover_from_position(data_pos):
    position_qty = pd.Series(data_pos)
    
    result = turnover_from_position(position_qty=position_qty)
    assert isinstance(result, float)

    if position_qty.sum() == 0:
        assert result == 0.0
    else:
        assert result != 0.0

    