from __future__ import annotations

import numpy as np
import pandas as pd

def make_fake_ohlcv(n:int = 31, seed:int = 42, with_features:bool=False)->pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods = n, freq = "D")
    
    close = 100 + rng.normal(0, 1, size = n).cumsum()
    open_ = close + rng.normal(0, 0.5, size = n)
    high = np.maximum(open_, close) + rng.random(n)
    low = np.minimum(open_, close) + rng.random(n)
    volume = rng.integers(900, 1100, size = n)
    
    data = {
        "Date": dates.astype(str),
        "Open": open_,   
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    }
    
    if with_features:
        LogReturn = 100 + rng.normal(0, 1, size = n).cumsum()
        MA_7 = close + rng.normal(0, 0.5, size = n)
        MA_30 = np.maximum(open_, close) + rng.random(n)
        Momentum_7 = volume = rng.integers(900, 1100, size = n)
        
        data["LogReturn"] = LogReturn
        data["MA_7"] = MA_7
        data["MA_30"] = MA_30
        data["Momentum_7"] = Momentum_7
    
    df = pd.DataFrame(data)
    return df

