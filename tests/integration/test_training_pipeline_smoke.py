from __future__ import annotations

import pytest

from pathlib import Path
from src.pipelines import run_training_pipeline

from src.utils.fake_data import make_fake_ohlcv

@pytest.mark.parametrize("cur_model",["linear_v1","xgboost_v1"])

def test_training_pipeline_smoke(tmp_path:Path, 
                                 cur_model:str,
                                 monkeypatch)->None:
    cfg = {
        "data" : {
            "paths":{
               "raw_dir": str(tmp_path / "data" / "raw"),
               "raw_path": str(tmp_path/"data"/"raw"), 
               "processed_path": str(tmp_path / "processed_btc_usd.csv"),
               "joblib_path": str(tmp_path / "artifacts/models/linear_model.joblib"),
            },
            "schema": {
              "datetime_column": "Date",
              "target_column": "Close",  
            },
           "market_data": {
                "Symbol": {
                    "BTC": "BTC-USD"
                },
                "interval": "1d"
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
                "method": "walk_forward_splits",
                "train_size": 10,
                "test_size": 2,
                "step": 2,
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
    
    df = make_fake_ohlcv(51)
    df_old = df.iloc[:50]
    daily_candle = df.iloc[50:51]

    raw_dir = Path(cfg["data"]["paths"]["raw_dir"])
    raw_path_ = raw_dir / "candles_1d" / "symbol=BTC-USD"
    raw_path_.mkdir(parents=True, exist_ok=True)
    file_dir = raw_path_ / "historic_candles.csv"
    df_old.to_csv(file_dir, index=False)

    def fake_daily(*args, **kwargs):
        return daily_candle
    monkeypatch.setattr(
        "src.pipelines.data_pipeline.load_btc_data_daily_candles",
        fake_daily,
    )
    monkeypatch.setattr("src.pipelines.data_pipeline.load_btc_data_daily_candles",
                         fake_daily)
    
    result_path, model = run_training_pipeline(cfg)
    result_path = Path(str(result_path))

    assert model is not None
    assert result_path.exists() == True
    exp_root = tmp_path / "artifacts/experiments"
    run_dirs = [p for p in exp_root.iterdir() if p.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "metadata.json").exists()
    assert (run_dirs[0] / "metrics.json").exists()
