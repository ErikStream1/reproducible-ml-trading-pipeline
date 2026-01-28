from __future__ import annotations
import pandas as pd
import pytest
from src.strategy import apply_vol_filter, apply_cooldown

@pytest.mark.parametrize("case_volatility, case_vol_max, result",
                         [
                             (None, 0.5, True),
                             ([],0.5, True),
                             ([0.03,0.6,0.4,1.1,0.1,0.9], 0.5, False),
                             ([0.03,0.6,0.4,1.1,0.1,0.9], None, True)
                         ])

def test_vol_filter(case_volatility:list|None, 
                    case_vol_max:float|None, 
                    result: bool):
    
    desired_position = pd.Series([1,1,0,1,0,-1])
    volatility =pd.Series(case_volatility) 
            
    vol_filter = apply_vol_filter(desired_position = desired_position,
                     volatility=volatility,
                     vol_max=case_vol_max)
    
    assert desired_position.equals(vol_filter) == result
        
        
@pytest.mark.parametrize("target_position_case,cooldown_bars_case, result",
                         [([0, 0, 0, 0], 2, True),
                          ([0,1,0,1,0], 2, False),
                          ([0,1,1,1,0], 2, True), 
                          ([1,1,0,0,1], 0, True)])

def test_apply_cooldown(target_position_case: list,
                        cooldown_bars_case:int, 
                        result:bool):

    target_position = pd.Series(target_position_case)
    cooldown = apply_cooldown(target_position=target_position,
                                  cooldown_bars=cooldown_bars_case) 
    
    assert target_position.equals(cooldown) == result
