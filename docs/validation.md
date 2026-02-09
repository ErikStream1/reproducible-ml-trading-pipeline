# Validation

This document describes the **validation layer** used to evaluate models under **time-aware**
splits (e.g., walk-forward). The goal is to estimate out-of-sample performance while respecting
temporal ordering and preventing data leakage.

## Purpose
- Generate time-aware train/test splits (walk-forward).
- Run evaluation consistently across splits using metrics from `src/evaluation`.
- Produce structured summaries (per split + aggregate) used by training/experimentation.

## Scope

### In scope
- Split generation (walk-forward / expanding window, depending on implementation)
- Split-level evaluation (MAE, RMSE, Directional Accuracy)
- Aggregation of split metrics into a report

### Out of scope
- Feature engineering (`src/features`)
- Model training logic (model fitting/prediction lives in `src/models` and is orchestrated by `src/pipelines`)
- Strategy/backtest performance (`src/backtest`)

## Core concept: time-aware splitting

### Why random splits are invalid here
For time series, random shuffling leaks future information into training. Validation must preserve
chronological order.

### Walk-forward validation (typical)
Walk-forward iterates through time using sequential windows:

- Train on `[t0, t1]`
- Test on `(t1, t2]`
- Move forward by `step_size` and repeat

This produces multiple out-of-sample test windows, which is useful to measure stability across regimes.


## Baseline comparison

`src/validation` provides utilities for time-aware splitting and metric computation. The end-to-end validation process is orchestrated by the validation pipeline.


Validation workflow (pipeline-level):
1) Fit the model on the train window and predict on the test window.
2) Compute baseline predictions on the same test window.
3) Evaluate both using the same metrics (MAE, RMSE, DA).
4) Report per-fold metrics for both the baseline and the model, and compute the gap between them.

### Gap convention
- For error metrics (MAE, RMSE): lower is better  
  `gap = baseline_metric - model_metric`  
  Positive gap ⇒ model improves over baseline.
- For Directional Accuracy (DA): higher is better  
  `gap = model_DA - baseline_DA`  
  Positive gap ⇒ model improves over baseline.

Note: Baseline and model must be evaluated on the **same aligned timestamps** to avoid misleading gaps.


