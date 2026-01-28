from __future__ import annotations
from src.types import Prediction, YLike

import numpy as np

def rmse(y_true: YLike, 
         y_pred: Prediction) -> float:
    """
    Compute Root Mean Squared Error (RMSE).

    Measures the average magnitude of prediction errors.
    Lower values indicate better model performance.
    """
    
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    return float(np.sqrt(np.mean(y_true - y_pred)**2))

def mae(y_true:YLike, 
        y_pred:Prediction) -> float:
    """
    Compute Mean Absolute Error (MAE).

    Measures the average absolute difference between predictions
    and true values.
    """

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    return float(np.mean(np.abs(y_true - y_pred)))

def directional_accuracy(y_true:YLike, 
                         y_pred:Prediction) -> float:
    """
    Compute directional accuracy of predictions.

    Measures the proportion of times the model correctly predicts
    the direction of price movement (up or down).
    """

    dir_true = np.sign(y_true)
    dir_pred = np.sign(y_pred)

    return (dir_true == dir_pred).mean()

