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
    
def test_threshold_signal_applies_confidence_gate_from_abs_prediction() -> None:
    cfg = {
        "strategy": {
            "type": "threshold",
            "side_mode": "long_only",
            "enter_threshold": 0.002,
            "exit_threshold": 0.0,
            "cooldown_bars": 0,
            "volatility_filter": {"enabled": False},
            "confidence_gate": {"enabled": True, "threshold": 0.005},
        }
    }
    pred_return = pd.Series([0.001, 0.006, 0.008])

    result = threshold_signal(cfg, pred_return)

    assert result.tolist() == [0, 1, 1]