# Reproducible ML Trading Pipeline

An end-to-end **Machine Learning + MLOps-style** project for **trading research and strategy simulation**, with strong emphasis on clean architecture, static typing in Python, and time-aware validation.

> ⚠️ **Disclaimer**: This project is educational and experimental. It is **not** financial advice.

---

## Project Objective

The goal is to build a **reproducible, extensible, and well-engineered pipeline** that enables:

- Market data ingestion and preprocessing *(initial implementation uses a single asset as an example)*
- Technical feature engineering
- Training predictive models (baseline and advanced)
- Time-series validation using **walk-forward cross-validation**
- Performance comparison against naive baselines
- Trading signal simulation and metric evaluation

All while following strong **software engineering**, **testing/CI**, **experiment reproducibility**, and **static typing** practices.

---

## Approach

* **Prediction**: supervised learning models (e.g. Ridge, XGBoost)
* **Target**: price direction / log-returns
* **Baseline**: naive persistence (yₜ = yₜ₋₁)
* **Validation**: Walk-Forward Split (no data leakage)
* **Evaluation metrics**:

  * RMSE / MAE
  * Directional Accuracy
  * Gap vs Baseline

---

## Project Architecture

```text
    configs/            # YAML configuration files
    docs/               # Project documentation
    src/
    ├── data/           # Data loading and preprocessing
    ├── features/       # Feature engineering
    ├── models/         # ML models (Ridge, XGBoost, etc.)
    ├── evaluation/     # Metrics (MAE, RMSE, Directional Accuracy)
    ├── pipelines/      # Pipeline orchestrators
    ├── validation/     # Walk-forward CV and reporting
    ├── strategy/       # Trading signal rules
    ├── execution/      # Fees, slippage and fill simulation
    ├── backtest/       # Ledger + PnL simulation + reports
    └── utils/          # Shared helpers
    tests/
    ├── unit/
    └── integration/

requirements.txt
README.md
```

---

## Configuration

The project is **configuration-driven** using YAML files:

```yaml
# models.yaml
model:
  name: linear_ridge
  params:
    alpha: 1.0
```
```yaml
# training.yaml
training:
  random_seed: 42
  split:
    method: "walk_forward"
    train_size: 250
    test_size: 50
    step_size: 50
```

This enables:

* Model changes without touching code
* Reproducible experiments
* Controlled and comparable runs

Logging is also configurable in `configs/logging.yaml` and can be persisted to `logs/pipeline.log`.

---

## Typing & Code Quality

* Extensive use of `typing` and `TypeAlias`
* Clear separation between:

  * `VectorLike`
  * `TargetLike`
* Metadata handled with `dataclasses` (`ModelInfo`, `LedgerResult`)
* Unit and integration testing with `pytest`
* Smoke tests to validate the full pipeline

---

## Core Metrics

* **RMSE / MAE** → magnitude error
* **Directional Accuracy** → trend correctness
* **Gap vs Baseline** → real improvement over naive models

Example:

```text
baseline_gap:
  rmse: -0.0037
  directional_accuracy: +0.18
```

---

## Roadmap

This is an **ongoing project**, actively being extended and refined. Planned and in-progress work includes:

### Core ML & Strategy
* [x] Data ingestion and feature pipelines
* [x] Naive baseline and linear models (Ridge)
* [x] Walk-forward cross-validation (time-aware)
* [x] Baseline comparison and gap analysis
* [x] Non-linear models (XGBoost)
* [x] Advanced backtesting (transaction fees, slippage, position sizing)
* [x] Strategy layer refinement (risk filters, cooldowns, volatility rules)

### Engineering & MLOps
* [x] Config-driven execution (YAML-based configs)
* [x] Reproducible pipelines
* [x] Step-level logging for training and inference pipelines
* [x] Centralized logging infrastructure and error-handling policy
* [x] Bitso market data (bid/ask): client + quote collector + storage
* [x] Backtest pipeline
* [x] Reproducible experiments and artifacts
* [x] Real-time simulation
* [in progress] End-to-end execution (shadow mode)
* [ ] Paper trading (market data live + simulated fills + blotter)
* [ ] Live broker integration (Bitso / API)
---
### Real-time simulation step

A new pipeline step can now simulate the latest trading decision from collected quote snapshots:

* Loads quote history from `data/quotes` partitions
* Rebuilds features and runs model inference
* Applies strategy thresholds/cooldown filters
* Produces latest action (`BUY`/`SELL`/`HOLD`) and target position
* Optionally stores step artifacts under `artifacts/realtime_simulation/`

Configure this behavior in `configs/realtime_simulation.yaml`.
### Reproducible experiments and artifacts

Training runs now persist experiment bundles under `artifacts/experiments/<run_id>/` containing:

* `metadata.json` (run id, UTC timestamp, model, seed, config hash)
* `config_snapshot.json` (normalized config used in the run)
* `metrics.json` (RMSE, MAE, directional accuracy on the training frame)
* `manifest.json` (model artifact path + feature schema)
* `feature_sample.csv` (first 200 rows of features for quick debugging)

Enable/disable from `training.experiments.enabled` in `configs/training.yaml`.
## Installation

```bash
git clone https://github.com/ErikStream1/reproducible-ml-trading-pipeline.git
cd reproducible-ml-trading-pipeline
pip install -r requirements.txt
```

---

## Basic Usage

```python
from src.pipelines import run_training_pipeline

setup_logging()
    
cfg = load_config(
    "configs/data.yaml",
    "configs/features.yaml",
    "configs/training.yaml",
    "configs/models.yaml",
    "configs/inference.yaml",
    "configs/strategy.yaml",
    "configs/execution.yaml",
    "configs/backtest.yaml",
    "configs/bitso.yaml",
    "configs/quotes.yaml",
    "configs/logging.yaml"
)

run_training_pipeline(cfg)

```
## CI

This repository now includes **GitHub Actions** workflows for continuous integration and delivery:

- **CI** (`.github/workflows/ci.yml`)
  - Runs on every push and pull request
  - Tests against Python **3.11** and **3.12**
  - Executes unit tests and integration smoke tests

---

## Author

**Erik Ocegueda**
Data Science & ML Engineering
Project oriented toward *ML Engineer / Data Scientist / Quant* roles

---

## Final Notes

This repository is intended for learning and experimentation only. Do not use it to make real financial decisions.
