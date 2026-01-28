import pytest

import numpy as np
import pandas as pd
from src.validation import summarize

def fake_data(n_folds:int = 100, fold_len:int = 50, seed: int = 42, mode:str = "random"):    
    rng = np.random.default_rng(seed)
    folds = []
    
    for i in range(n_folds):
        if mode == "random":
            y_prev = rng.normal(size = fold_len)
            y_true = rng.normal(size = fold_len)
            y_pred = rng.normal(size = fold_len)
           
            
        elif mode == "perfect":
            y_prev = rng.normal(size = fold_len)
            y_true = rng.normal(size = fold_len)
            y_pred = y_true.copy()

        elif mode == "perfect_direction":
            y_prev = rng.normal(size = fold_len)
            delta = np.abs(rng.normal(size = fold_len))
            y_true = y_prev + delta
            y_pred = y_prev + 2*delta
        
        else:
            raise ValueError("Mode must be on of: random, perfect, perfect_direction")
            
        fold = {
            "fold": i+1,
            "y_prev": pd.Series(y_prev),
            "y_true": pd.Series(y_true),
            "y_pred": pd.Series(y_pred),
        }
        folds.append(fold)

    return folds


@pytest.mark.parametrize("mode",
                         ["random", "perfect", "perfect_direction"])
def test_scoring(mode:str):
    folds_output = fake_data(mode = mode)
    summary = summarize(folds_output)
    assert isinstance(summary, dict)
    assert isinstance(summary["fold_metrics"], list)
    assert isinstance(summary["score"], float)

    if mode == "perfect":
        assert summary["score"] == float(0)
    
    if mode == "perfect_direction":
        assert summary["directional_accuracy_mean"] >= float(0.70)