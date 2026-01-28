from __future__ import annotations

from src.execution import fee_proportional
import numpy as np

def test_fee_proportional():
    notional = 100*np.random.random()  
    fee = np.random.random()  
    
    result = fee_proportional(notional = notional, fee_rate = fee)
    
    assert isinstance(result, float)
    assert result > 0
    
    
    