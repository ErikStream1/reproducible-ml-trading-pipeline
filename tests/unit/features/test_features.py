import pytest
import numpy as np
import pandas as pd

from src.features import build_features

def test_build_features():
    n = 200
    df = pd.DataFrame({
        "Date": pd.date_range("2023-01-01", periods=n, freq="D"),
        "Open": np.linspace(100, 200, n),
        "High": np.linspace(101, 201, n),
        "Low": np.linspace(99, 199, n),
        "Close": np.linspace(100, 200, n),
        "Volume": np.random.randint(1000, 2000, n),
    })
    
    cfg = {
        "features": {
            "base_column": "Close",
        
        "returns": {
                "pct_change": {
                    "enabled": True, 
                    "periods": [1], 
                    "name_prefix": "Return"
                    },
                "log_diff": {
                    "enabled": True, 
                    "name": "LogReturn"
                    },           
                "moving_average": {
                    "enabled": True,
                    "windows": [7, 30],
                    "name_prefix": "MA",
                    },
                "volatility": {
                    "enabled": True, 
                    "windows": [7], 
                    "on": "Return_1", 
                    "name_prefix": "Volatility"
                    },
                "momentum": {
                    "enabled": True,
                    "lags": [7],
                    "on": "Close",
                    "name_prefix": "Momentum"
                    },
            }
        }
    }
    
    
    df_with_features = build_features(df, cfg)
    
    expected_cols = {"Return_1", "LogReturn", "MA_7", "MA_30", "Volatility_7", "Momentum_7"}
    assert expected_cols.issubset(df_with_features.columns)
    assert len(df) == len(df_with_features)
     