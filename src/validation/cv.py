from __future__ import annotations
from src.types import FrameLike, ConfigLike
from typing import Callable
import pandas as pd

from src.validation import walk_forward_splits
from src.models import build_model

def wfs_cross_validation(df: FrameLike, cfg: ConfigLike, build_model_fn: Callable|None = None):
    
    n = len(df)
    target =  cfg["data"]["schema"].get("target_column", "LogReturn")
    base = cfg["features"]["base_column"]


    if build_model_fn is None:
        build_model_fn = build_model
    
    X = df.drop(columns=[base,target])
    y = df[target]
    
    for fold, (tr_idx, te_idx) in enumerate(walk_forward_splits(n, cfg)):
            X_train, y_train = X.iloc[tr_idx], y.iloc[tr_idx]
            X_test, y_test = X.iloc[te_idx], y.iloc[te_idx]
            
            model = build_model_fn(cfg)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            y_pred = pd.Series(y_pred, index = y_test.index, dtype=float)
            
            yield {"fold": fold, "y_true": y_test, "y_pred": y_pred}
            