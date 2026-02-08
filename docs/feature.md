# Features

This document describes the **feature engineering layer**: how the project transforms market data
(raw/processed) into a feature table ready for training, inference, and backtesting.

## Purpose
- Compute reproducible, config-driven features from a base price series (e.g., `Close`, `mid`).
- Keep feature definitions centralized in `configs/features.yaml`.
- Produce a dataset with predictable column names for downstream pipelines.

## Scope

### In scope
- Feature computation (returns, moving averages, volatility, momentum, etc.)
- Feature naming conventions (prefixes / stable names)

### Out of scope
- Data ingestion/storage (see `docs/data.md`)
- Modeling and validation (see `docs/training.md` / `docs/pipelines.md`)
- Strategy rules and sizing (see `docs/strategy.md` / `docs/backtest.md`)

## Inputs and outputs

### Input (minimum requirements)
A `pandas.DataFrame` with:
- A datetime representation (column or index; whatever your project standard is)
- A base price column (configured via `features.base_column`, e.g., `Close` or `mid`)

Optional but common:
- Volume column
- Pre-existing return columns (if you sometimes load precomputed datasets)

### Output
A `pandas.DataFrame` containing:
- Original columns (unless dropped later by config/pipeline)
- Feature columns computed according to `features.yaml`
- (Optional) target column if it already exists in the dataset (e.g., `LogReturn`)

## Missing values (NaNs)

Some feature builders (e.g., moving averages, volatility, momentum) produce `NaN` values in the first
N rows where the calculation is not defined (e.g., rolling windows / lags).

**Policy:** feature builders do **not** drop NaNs. NaN handling is performed downstream by the consumer
pipeline (typically the training pipeline), depending on the use case and configuration.


> Note: Feature generation commonly introduces NaNs at the beginning of the series (expected behavior).
