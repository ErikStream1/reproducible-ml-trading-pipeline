import pytest
import numpy as np
import pandas as pd

from src.features import build_features
from src.pipelines import run_feature_pipeline
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

def test_feature_pipeline_aligns_target_to_next_step():
    n = 20
    df = pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "Open": np.linspace(100, 120, n),
        "High": np.linspace(101, 121, n),
        "Low": np.linspace(99, 119, n),
        "Close": np.linspace(100, 120, n),
        "Volume": np.random.randint(1000, 2000, n),
    })

    cfg = {
        "data": {
            "schema": {"target_column": "LogReturn"},
            "paths": {"features_path": None},
        },
        "features": {
            "base_column": "Close",
            "drop_columns": [],
            "returns": {
                "pct_change": {"enabled": False},
                "log_diff": {"enabled": True, "name": "LogReturn"},
                "moving_average": {"enabled": False},
                "volatility": {"enabled": False},
                "momentum": {"enabled": False},
            },
        },
    }

    out = run_feature_pipeline(df, cfg)
    raw_log_return = np.log(df["Close"]).diff()
    expected = raw_log_return.shift(-1)

    pd.testing.assert_series_equal(out["LogReturn"], expected, check_names=False)