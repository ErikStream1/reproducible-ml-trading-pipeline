from __future__ import annotations

import numpy as np
import pandas as pd

from src.validation import wfs_cross_validation

class DummyModel:
    def fit(self, X, y):
        self.mean_ = float(np.mean(y))
        return self
    
    def predict(self, X):
        return np.full(shape=(len(X),), fill_value= self.mean_, dtype = float)
    
def dummy_build_model(dummy):
    return DummyModel()

def test_wfs_cross_validation():
    n = 500
    df = pd.DataFrame({
        "base":np.random.RandomState(0).randn(n),
        "f1": np.random.RandomState(0).randn(n),
        "f2": np.random.RandomState(1).randn(n),
        "Close": np.linspace(100, 200, n),
    })
       
    cfg = {
        "data" : {
            "schema": {
              "datetime_column": "Date",
              "target_column": "Close",  
            },   
        },
        "training":{
            "random_seed": 42,
            "split":{
                "train_size": 200,
                "test_size": 50,
                "step": 50
            },
            "model_run":{
                "active_model": "anything",
            },
        },
        "models":{},
        "features":{
            "base_column" : "base"
        }
    }
    folds = list(wfs_cross_validation(df, cfg, dummy_build_model))

    for out in folds:
        y_true = out["y_true"]
        y_pred = out["y_pred"]
        
        assert len(y_true) == 50
        assert len(y_pred) == 50
        

        