from __future__ import annotations
from src.strategy import threshold_signal

import pytest
import pandas as pd


@pytest.mark.parametrize("mode",
                         ["long_only",
                          "long_short"])
def test_signals(mode:str):
    cfg = {
        "strategy":{
            "type": "threshold",
            "side_mode": mode,
            "enter_threshold": 0.002,
            "exit_threshold": 0.0,
            "cooldown_bars": 1,
            "volatility_filter":{
                "enabled": True,
                "max_vol": 0.0,
            },
        }
    }
    
    pred_return = pd.Series([1,0,1,1,1,0,0])
    volatility = pd.Series([0.1,0.2,0.3,0.6,0.9,0.4,0.6])
    
    result = threshold_signal(cfg, pred_return, volatility)
    assert isinstance(result, pd.Series)
    