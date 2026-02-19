# Configuration

This project is config-drive. Pipelines consume a merged config. Pipelines consume merged  config built from multiple YAML files.

## How configs are loaded
 - Configs are loeaded from `configs/*.yaml` and merged into a single dictionary (`cfg`).
 - Each pipeline reads only the sections it needs.

Notes (applies to all configs):
 - Do not store secrets (API keys/tokens) in `configs/`. Use environment variables or a separate ignored file.
 - Paths are interpreted relative to the repo root unless stated otherwise.
 - Timestamps are handled in UTC end-to-end.

## Overview of YAML files

### `data.yaml`
**Purpose:** sources, schema, paths, updates.

Minimal example:
```yaml
data:
    source: "csv"
    paths:
        raw_path: "data/raw/btc_usd.csv"
        processed_path: "data/processed/processed_btc_usd.csv"
    
    schema:
        target_column: "LogReturn"
        drop_columns:
            - "Date"
            - "Return_1"

    update:
        enabled: true
```
---
### `bitso.yaml`
**Purpose:** Bitso REST client configuration.

Key fields:

* `bitso.base_url`: Bitso API base URL
* `bitso.timeout_s`: HTTP timeout (seconds)
---
### `quotes.yaml`
**Purpose:** Quote collection settings.

Minimal example:
```yaml
quotes:
    provider: "bitso"
    book: "btc_usd"
    mode: "ticker_rest"
    poll_interval_s: 2.0
    out_dir: "data/quotes"
    timezone: "UTC"
```
---
### `features.yaml`
**Purpose:** feature engineering configuration (which features to compute and their parameters)

Minimal example:
```yaml
features:
    base_column: "Close"
    date_column: "Date"

    returns:
        pct_change:
            enabled: true
            periods: [1]
            name_prefix: "Return"
        
        log_diff:
            enabled: true
            name: "LogReturn"
        
        moving_average:
            enabled: true
            windows: [7]
            name_prefix: "MA"
        
        volatility:
            enabled: true
            windows: [7]
            on: "Return_1"
            name_prefix: "Volatility"
        
        momentum:
            enabled: true
            lags: [3]
            name_prefix: "Momentum"
```
---
### `models.yaml`
**Purpose:** model selection and its configuration (parameters and type of model)

Minimal example:
```yaml

models:
    linear:
        type: "linear_regression" #Ridge regression
        params:
            alpha: 1.0
```
---
### `training.yaml`
**Purpose:** training configuration(seed, split method, train and test sizes, step, model_run, models_outputs_paths)

Minimal example
```yaml
training:
    random_seed: 42

    split:
        method: "walk_forward_splits"
        train_size: 250
        test_size: 50
        step: 50
        
    model_run:
        active_model: "xgboost"

    artifacts:
        model_output_dir: "artifacts/models/"
        model_filenames: 
            linear: "linear_model.joblib"
            xgboost: "xgboost_model.joblib"

    experiments:
        enabled: true
        output_dir: "artifacts/experiments"       
         
    evaluation:
        primary_metric: "rmse"

        secondary_metrics:
        - "mae"
        - "directional_accuracy"
```
---
### `inference.yaml`
**Purpose:** inference configuration(model path)

Key fields:

* `inference.artifacts.model_path`: Model path
---
### `realtime_simulation.yaml`
**Purpose:** one-step simulation from collected live-ish quotes.

Minimal example:
```yaml
realtime_simulation:
  min_history_rows: 50
  artifacts:
    output_dir: "artifacts/realtime_simulation"
    step_filename: "last_step.json"
    history_filename: "steps_history.csv"
```
---
### `strategy.yaml`

**Purpose:** signal generation and risk rules (threshold, cooldown, volatility filter and sizing).

Minimal example:
```yaml
strategy:
    type: "threshold"
    side_mode: "long_only"
    enter_threshold: 0.002 # 0.2% in decimal units
    exit_threshold: 0.0
    cooldown_bars: 3
    
    volatility_filter:
        enabled: true
        max_vol: 0.05 # decimal units
    
    sizing:
        target_notional: 1000.0 # quote currency (e.g. USD for btc_usd)
        min_qty: 0.0001
        max_notional: 3000.0

```
---
### `execution.yaml`
**Purpose:** execution assumptions (fill pricing model + transaction cost model).

Minimal example:
```yaml
execution: 
    fill_mode: "next_close"
    qty: 0.001 # BTC units

    fees:
        rate: 0.001 #0.1% in decimal units
    
    slippage:
        bps: 5
        vol_k: 0.0
```
---
### `backtest.yaml`
**Purpose:** backtest settings (initial capital, execution price source, and annualization parameters).

Key fields:
- `backtest.initial_cash`: Initial capital available for trading (quote currency, e.g., USD for `btc_usd`).
- `backtest.execute_on`: Price field used for execution (e.g., `mid`, `bid`, `ask`, `close`, `next_close`).
- `periods_per_year: 15768000`  # 2s bars (experimental). Update if bar frequency changes.

