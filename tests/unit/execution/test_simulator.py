from __future__ import annotations

import pandas as pd
import pytest
import numpy as np
from typing import Any
from src.execution import simulate_fills_from_target_position, Fill

@pytest.mark.parametrize("fill_mode",
                         ["next_close", "mid", "bid_ask", "fill"])
def test_simulator(fill_mode: str):
    cfg: dict[str, Any] = {
        "execution":{
            "fill_mode": fill_mode,
            "qty": 1.0,
            
            "fees":{
                "rate": 0.01
                },
            
            "slippage":{
                "bps": 5,
                "vol_k": 0.0
            }
        }
    }
    
    fill_modes = ["next_close", "mid", "bid_ask"]
    
    data_tp = np.random.randint(0,2,10)
    data_pf = np.random.rand(10,4)
    data_v = np.random.rand(10)
    
    target_position = pd.Series(data_tp)
    price_frame = pd.DataFrame(data_pf, columns = ["Close","mid", "ask", "bid"])
    volatility = pd.Series(data_v)
    
  
    
    if fill_mode not in fill_modes:
        with pytest.raises(ValueError):
            simulate_fills_from_target_position(cfg = cfg, 
                                        target_position= target_position,
                                        price_frame=price_frame,
                                        volatility=volatility)
    else:
        result = simulate_fills_from_target_position(cfg = cfg, 
                                        target_position= target_position,
                                        price_frame=price_frame,
                                        volatility=volatility
                        )
        assert len(result) > 0
        assert isinstance(result, list)
        for element in result:
            assert isinstance(element, Fill)
        