# Pipelines

This document describes the orchestration pipelines in **reproducible-ml-trading-pipeline**: what each pipeline does, which inputs it expects, and which artifacts it produces.

## Summary

Pipelines live under `src/pipelines/` and coordinate data, features, models, validation, and backtest modules.

Implemented pipelines:

-   `run_data_pipeline`
-   `run_feature_pipeline`
-   `run_training_pipeline`
-   `run_inference_pipeline`
-   `run_model_validation_pipeline`
-   `run_collect_quotes_pipeline`
-   `run_backtest_pipeline`

------------------------------------------------------------------------

## 1) Data pipeline

**Function**: `run_data_pipeline(cfg, tmp_output_path=...)`

**File**: `src/pipelines/data_pipeline.py`

### Flow

1.  Reads `cfg["data"]`.
2.  If `raw_path` exists and `update.enabled == False`, loads local CSV.
3.  Otherwise, downloads data with `load_btc_data()`, normalizes column names, and writes `raw_path`.
4.  Validates data using `validate_btc_data(df)`.
5.  Writes processed dataset to `processed_path` (or `tmp_output_path` when provided).
6.  Returns a `DataFrame`.

### Key config inputs

-   `data.paths.raw_path`
-   `data.paths.processed_path`
-   `data.update.enabled`

### Outputs

-   CSV at `raw_path` (when update/download is triggered)
-   CSV at `processed_path`
-   Validated `DataFrame`

------------------------------------------------------------------------

## 2) Feature pipeline

**Function**: `run_feature_pipeline(df, cfg)`

**File**: `src/pipelines/feature_pipeline.py`

### Flow

1.  Builds features via `build_features(df, cfg)`.
2.  Drops columns listed in `features.drop_columns` (default: `Date` and `Return_1`).
3.  If `data.paths.features_path` exists, writes features CSV.
4.  Returns transformed `DataFrame`.

### Key config inputs

-   `features.*`
-   `features.drop_columns`
-   `data.paths.features_path` (optional)

### Outputs

-   Features CSV (optional)
-   Transformed `DataFrame`

------------------------------------------------------------------------

## 3) Training pipeline

**Function**: `run_training_pipeline(cfg)`

**File**: `src/pipelines/training_pipeline.py`

### Flow

1.  Runs `run_data_pipeline(cfg)`.
2.  Runs `run_feature_pipeline(df, cfg)`.
3.  Drops `NaN` values.
4.  Splits `X`/`y` using `data.schema.target_column`.
5.  Builds model with `build_model(cfg)`.
6.  Trains model via `model.fit(X, y)`.
7.  Saves artifact in `training.artifacts.model_output_dir` using `training.artifacts.model_filenames`.
8.  Returns `(model_path, model)`.

### Key config inputs

-   `data.schema.target_column`
-   `training.artifacts.model_output_dir`
-   `training.artifacts.model_filenames`
-   `training.model_run.active_model`
-   `models.*`

### Outputs

-   Serialized model artifact
-   Tuple `(path, model_instance)`

------------------------------------------------------------------------

## 4) Inference pipeline

**Function**: `run_inference_pipeline(cfg, model_path=None)`

**File**: `src/pipelines/inference_pipeline.py`

### Flow

1.  Checks that `data.paths.processed_path` does **not** point into `data/processed` (explicit inference safety restriction).
2.  Runs `run_data_pipeline(cfg)` (or a temporary output path when `processed_path` is `None`).
3.  Loads model from `model_path` or `inference.artifacts.model_path`.
4.  Runs `run_feature_pipeline(df, cfg)`.
5.  Drops `NaN` values.
6.  Builds `X` by removing target column.
7.  If model metadata includes `feature_names`, validates that all required features exist in `X`.
8.  Predicts on the latest row (`X.tail(1)`).
9.  Returns prediction.

### Key config inputs

-   `data.paths.raw_path`
-   `data.paths.processed_path`
-   `data.schema.target_column`
-   `inference.artifacts.model_path` (if `model_path` is not passed)

### Outputs

-   Prediction for the latest sample

------------------------------------------------------------------------

## 5) Validation pipeline

**Function**: `run_model_validation_pipeline(cfg)`

**File**: `src/pipelines/validation_pipeline.py`

### Flow

1.  Runs data + feature pipelines.
2.  Drops `NaN` values.
3.  Runs walk-forward validation with `wfs_cross_validation(df, cfg)`.
4.  Summarizes metrics with `summarize(...)`.
5.  Prints summary.

### Outputs

-   Validation summary printed to stdout

------------------------------------------------------------------------

## 6) Collect quotes pipeline

**Function**: `run_collect_quotes_pipeline(cfg)`

**File**: `src/pipelines/collect_quotes_pipeline.py`

### Flow

1.  Initializes Bitso client with `cfg["client"]`.
2.  Lists available books and validates that `quotes.book` exists.
3.  Runs `collect_quotes(cfg=cfg)` for quote collection/storage.

### Key config inputs

-   `client.*`
-   `quotes.book`
-   Remaining `quotes.*` values used by `collect_quotes`

------------------------------------------------------------------------

## 7) Backtest pipeline

**Function**: `run_backtest_pipeline(cfg, model_path=None)`

**File**: `src/pipelines/backtest_pipeline.py`

### Flow

1.  Runs data + feature pipelines.
2.  Reads `target_column` and builds `X`.
3.  Loads model (`LinearModel` or `XGBoostModel`).
4.  Predicts returns.
5.  Runs `run_backtest_threshold(...)` with predictions + market data + optional volatility series.
6.  Saves backtest artifacts (`summary.json`, `equity.csv`, `trades.csv`) if `backtest.artifacts.output_dir` is set.
7.  Returns `BacktestReport`.

### Key config inputs

-   `data.schema.target_column`
-   `inference.artifacts.model_path` (if `model_path` is not passed)
-   `strategy.*`
-   `execution.*`
-   `backtest.*`

### Outputs

-   `BacktestReport`
-   Backtest artifact files (optional)

------------------------------------------------------------------------

## Execution from `main.py`

`main.py` loads all YAML configs and currently executes `run_collect_quotes_pipeline(cfg=cfg)`; other pipeline calls remain commented for manual activation.

------------------------------------------------------------------------

## Documentation consistency review

Without changing the structure of other docs, these are the key consistency notes:

1.  `docs/pipelines.md` was referenced in `docs/index.md` but previously empty.
2.  In `main.py`, a comment shows `run_model_validation(cfg)`, while the actual exported function is `run_model_validation_pipeline(cfg)`.
3.  Inference docs must include the explicit guard that blocks writing to `data/processed` through `processed_path`.

## 8) Real-time simulation step

**Function**: `run_realtime_simulation_step(cfg, model_path=None)`

**File**: `src/pipelines/realtime_simulation_pipeline.py`

### Flow

1. Loads collected quotes from `quotes.out_dir` for `quotes.book`.
2. Validates minimum history (`realtime_simulation.min_history_rows`).
3. Converts quotes into a market frame (`Date`, `Close`, `bid`, `ask`).
4. Builds features and drops `NaN` rows.
5. Loads model from `model_path` or `inference.artifacts.model_path`.
6. Predicts returns and applies strategy rules (`threshold_signal`) to compute target position.
7. Returns latest step output (`predicted_return`, `target_position`, `action`).
8. Optionally stores artifacts (`last_step.json`, `steps_history.csv`) when configured.

### Key config inputs

- `quotes.out_dir`
- `quotes.book`
- `realtime_simulation.min_history_rows`
- `realtime_simulation.artifacts.*`
- `inference.artifacts.model_path`
- `strategy.*`

### Outputs

- `RealtimeSimulationStepResult` dataclass