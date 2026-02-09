# Evaluation

This document describes the evaluation utilities used to assess prediction quality in
**bitcoin_ml_pipeline**. The evaluation module currently provides:

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- Directional Accuracy (DA)

## Purpose
- Provide a small, consistent set of metrics for regression-style return prediction.
- Ensure metrics are computed in a reproducible way across training/validation runs.

## Inputs and assumptions

### Inputs
- `y_true`: realized target values (e.g., returns/log-returns)
- `y_pred`: model predictions

Typical types:
- `pandas.Series` (preferred) or array-like vectors

### Assumptions
- `y_true` and `y_pred` are **aligned** (same ordering, same timestamps/index).
- NaNs are handled upstream (e.g., the training/validation pipeline drops NaNs before evaluation).

## Metrics

### MAE (Mean Absolute Error)
Average absolute error between prediction and truth.

- Lower is better.

### RMSE (Root Mean Squared Error)
Square root of mean squared error; penalizes large errors more than MAE.

- Lower is better.

### Directional Accuracy (DA)
Fraction of times the prediction gets the **sign** of the target correct.

Typical definition:
- `DA = mean(sign(y_pred) == sign(y_true))`

Notes:
- DA ignores magnitude and only checks direction (up vs down).
- If `y_true` contains values extremely close to zero, sign-based metrics may be noisy.

#### Sanity check (potential leakage)
For return prediction tasks, consistently high DA values can be a red flag. As a rough heuristic,
if DA is persistently very high (e.g., > 0.7) on out-of-sample windows, investigate:
- target/feature alignment (off-by-one / accidental look-ahead)
- leakage via rolling computations using future data
- data splitting mistakes (train/test contamination)
- evaluation performed on training data by accident

This is a heuristic, not a proof of leakage.

## Common pitfalls
- **Misalignment:** If `y_true` and `y_pred` are shifted relative to each other (horizon mismatch),
  metrics will be invalid.
- **NaNs:** Do not evaluate with NaNs present; handle them upstream.
- **Scale:** Keep `y_true` and `y_pred` in the same units (e.g., decimal returns).

## Example (conceptual)
```python
from src.evaluation import mae, rmse, directional_accuracy

m1 = mae(y_true, y_pred)
m2 = rmse(y_true, y_pred)
da = directional_accuracy(y_true, y_pred)
```
