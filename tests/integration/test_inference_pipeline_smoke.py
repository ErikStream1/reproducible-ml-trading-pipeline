import pytest
from typing import Any

import numpy as np
from pathlib import Path
from src.types import PathLike
from src.pipelines import run_inference_pipeline
from src.models import LinearModel, XGBoostModel

from tests.utils.fake_data import make_fake_ohlcv

@pytest.mark.parametrize("cur_model",["linear_v1","xgboost_v1"])

def test_inference_pipeline_smoke(cur_model:str,
                                  tmp_path:PathLike,
                                  ):
    tmp_path = Path(str(tmp_path))
    cfg: dict[str, Any] = {
        "data" : {
            "paths":{
               "raw_path": tmp_path / "btc_usd.csv",
               "processed_path": tmp_path / Path("processed_btc_usd.csv"),
               "predictions_path": tmp_path / "artifacts/predictions/btc_predictions.csv"
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
                "model_output_dir": tmp_path / Path("artifacts/models/"),
                "model_filenames": {
                    "linear_v1": "linear_model.joblib", 
                    "xgboost_v1":"xgboost_model.joblib",
                    }, 
            },
            "evaluation":{
                "primary_metric": "rmse",
                "secondary_metrics":{
                    "mae": "mae",
                    "directional_accuracy": "directional_accuracy",
                    }
                    
            },
            "direction": {
                "rmse": "min",
                "mae": "min",
                "directional_accuracy": "max",
            }
        },
        "models":{
            "xgboost_v1":{
              "type": "xgboost_v1",
              "params": {
                    "n_estimators" : 300,
                    "learning_rate" : 0.05,
                    "max_depth" : 4,
                    "subsample" : 0.9,
                    "colsample_bytree" : 0.9,
                    "random_state" : 42,
              }  
            },
            "linear_v1":{
                "type": "linear_regression",
                "params":{
                    "alpha": 1,
                }
            },
        },
        "inference":{
            "artifacts":{               
                "linear_path": tmp_path / Path("artifacts/models/linear_model.joblib"),
                "xgboost_path": tmp_path / Path("artifacts/models/xgboost_model.joblib")
            },
            "run_time":{
                "fail_on_missing_columns":True
            }
        },
    }
    df = make_fake_ohlcv(n = 50, with_features=True)
    df.to_csv(cfg["data"]["paths"]["raw_path"],index = False)
    params = cfg["models"]["xgboost_v1"]["params"]
    X = df[['Open', 'High', 'Low', 'Volume', 'LogReturn', 'MA_7', 'MA_30', 'Momentum_7']]
    y = df["Close"]
    
    if cur_model == "linear_v1":
        model_path = cfg["inference"]["artifacts"]["linear_path"]
        model = LinearModel()
    
    elif cur_model == "xgboost_v1":
        model_path=cfg["inference"]["artifacts"]["xgboost_path"]
        model = XGBoostModel(params = params)

    model.fit(X, y)
        
    if hasattr(model, "save"):
        model.save(model_path)
    else:
        import joblib
        joblib.dump(model, model_path)

    out = run_inference_pipeline(cfg, model_path)
    
    assert out[0] is not None
    assert len(out) > 0
    assert np.isfinite(out).all()
