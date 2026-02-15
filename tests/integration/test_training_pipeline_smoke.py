from __future__ import annotations

import pytest

from pathlib import Path
from src.pipelines import run_training_pipeline

from src.utils.fake_data import make_fake_ohlcv

@pytest.mark.parametrize("cur_model",["linear_v1","xgboost_v1"])

def test_training_pipeline_smoke(tmp_path:Path, 
                                 cur_model:str):
    cfg = {
        "data" : {
            "paths":{
               "raw_path": str(tmp_path / "btc_usd.csv"), 
               "processed_path": str(tmp_path / "processed_btc_usd.csv"),
               "joblib_path": str(tmp_path / "artifacts/models/linear_model.joblib"),
            },
            "schema": {
              "datetime_column": "Date",
              "target_column": "Close",  
            },
            "update": {
                "enabled": False
                },
        },
        "features":{
            "base_column": "Close",
            "date_column": "Date",
            "returns":{
                "pct_change":{
                    "enabled": True,
                    "periods": [1],
                    "name_prefix": "Return",
                },
                "log_diff":{
                    "enabled": True,
                    "name": "LogReturn", 
                },
                "moving_average":{
                    "enabled": True,
                    "windows": [7, 30],
                    "name_prefix": "MA",
                },
                "volatility":{
                    "enabled": True,
                    "windows": [7],
                    "on": "Return_1",
                    "name_prefix": "MA",
                },
                "momentum":{
                    "enabled": True,
                    "lags": [7],
                    "on": "Close",
                    "name_prefix": "Momentum",
                },    
            }
        },
        "training":{
            "random_seed": 42,
            "split":{
                "method":"time_series",
                "train_ratio":0.8,
            },
            "model_run":{
                "active_model": cur_model,
            },
            "artifacts":{
                "model_output_dir": str(tmp_path / "artifacts/models/"),
                "model_filenames": {
                    "linear_ridge": "linear_model.joblib", 
                    "xgboost":"xgboost_model.joblib",
                    },
                 
            },
            "experiments": {
                "enabled": True,
                "output_dir": str(tmp_path / "artifacts/experiments"),
            },
            "evaluation":{
                "primary_metric": "rmse",
                "secondary_metrics":{
                    "mae": "mae",
                    "directional_accuracy": "directional_accuracy",
                    }
            },
        },
        "models":{
            "xgboost_v1":{
              "type": "xgboost",
              "params": {
                  "n_estimators": 300,
                  "max_depth": 4,
                  "learning_rate": 0.05,
                  "subsample": 0.9,
                  "colsample_bytree": 0.9,
                  "random_state": 42,
              }  
            },
            "linear_v1":{
                "type": "linear_regression",
                "params":{
                    "alpha": 1,
                }
            },
        }
    }
    
    df = make_fake_ohlcv(50)
    raw_path = cfg["data"]["paths"]["raw_path"]
    
    df.to_csv(raw_path, index = False,)
    result_path, model = run_training_pipeline(cfg)
    
    result_path = Path(str(result_path))
    
    assert model is not None
    assert result_path.exists() == True
    exp_root = tmp_path / "artifacts/experiments"
    run_dirs = [p for p in exp_root.iterdir() if p.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "metadata.json").exists()
    assert (run_dirs[0] / "metrics.json").exists()
