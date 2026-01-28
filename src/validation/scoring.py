from __future__ import annotations

from typing import  Any, Mapping
from src.evaluation import rmse, mae, directional_accuracy
from src.validation import SummaryLike,FoldMetricLike, FoldLike,GapSummaryLike
import numpy as np
import pandas as pd

def naive_persistence(y_true: pd.Series)->pd.Series:
     return y_true.shift(1).dropna()

def compute_score(
  summary: SummaryLike,
  primary: str,
  stability_lambda: float = 0.5,
)->float:
    
    mu = summary.get(f"{primary}_mean", np.nan)
    sd = summary.get(f"{primary}_std", np.nan)
    
    if np.isnan(mu):
        return float("inf")
    if np.isnan(sd):
        sd = 0
        
    return float(mu + stability_lambda * sd)

def baseline_gap(
    model_summary: SummaryLike,
    baseline_summary: SummaryLike,
    metric:str="rmse"
)->GapSummaryLike:

    m = model_summary.get(f"{metric}_mean", np.nan)
    b = baseline_summary.get(f"{metric}_mean", np.nan)
    
    if np.isnan(m) or np.isnan(b):
        return {"gap_abs": float("nan"), "gap_real": float(np.nan)}
    
    gap_abs = b - m
    gap_rel = (b-m)/b if b!=0 else float("nan")
    
    return {"gap_abs": gap_abs, "gap_real": gap_rel}

def summarize_fold_metrics(fold_metrics: FoldMetricLike) -> SummaryLike:
    
    if not fold_metrics:
        raise ValueError("Fold metrics is empty.")
    
    keys = list({k for fm in fold_metrics for k in fm.keys() if k != "fold"})
    summary: dict[str, float | FoldMetricLike] = {}

    for k in keys:
        
        vals = np.array([fm.get(k, np.nan) for fm in fold_metrics], dtype = float)
        vals = vals[~np.isnan(vals)]
        
        if len(vals) == 0:
            summary[f"{k}_mean"] = float("nan")
            summary[f"{k}_std"] = float("nan")
            continue
            
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        
    summary["n_folds"] = float(len(fold_metrics))
    summary["fold_metrics"] = fold_metrics
    
    return summary

def summarize(
    fold_outputs: FoldLike,
    metrics: Mapping[str, Any] = {"primary": "rmse", "secondary1": "directional_accuracy", "secondary2": "mae"},
    stability_lambda: float = 0.5,
    include_baseline: bool = True,
    )->SummaryLike:
    
    fold_metrics: FoldMetricLike = []
    baseline_fold_metrics: FoldMetricLike = []
   

    for out in fold_outputs:
        
        fold:int = out["fold"]
        y_true:pd.Series = out["y_true"]
        y_pred:pd.Series = out["y_pred"]
    
        fm = {
                "fold": fold,
                "rmse": rmse(y_true, y_pred),
                "mae": mae(y_true, y_pred),
                "directional_accuracy": directional_accuracy(y_true, y_pred),
            }
        
        fold_metrics.append(fm)

        if include_baseline:
            y_base = naive_persistence(y_true)
            s_y_true = y_true[1:]
            bfm = {
                "fold": fold,
                "rmse": rmse(s_y_true, y_base),
                "mae": mae(s_y_true, y_base),
                "directional_accuracy": directional_accuracy(s_y_true, y_base)
            }
            baseline_fold_metrics.append(bfm)
    
    summary = summarize_fold_metrics(list(fold_metrics))
    summary["fold_metrics"] = list(fold_outputs)
    summary["score"] = compute_score(summary = summary, primary = metrics.get("primary", "rmse"), stability_lambda=stability_lambda)
    
    if include_baseline:
        baseline_summary = summarize_fold_metrics(baseline_fold_metrics)
        baseline_summary["baseline_fold_metrics"] = baseline_fold_metrics
        summary["baseline"] = baseline_summary
        tm = {}
        for metric in metrics.values():
           tm[f"{metric}"] = baseline_gap(summary, baseline_summary, metric = metric)

        summary["baseline_gap"] = tm      
                          
    return summary