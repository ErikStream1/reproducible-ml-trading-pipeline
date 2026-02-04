# Bitcoin ML Trading Pipeline

A **Machine Learning + MLOps** project focused on **Bitcoin price prediction** and **trading strategy simulation**, with strong emphasis on clean architecture, static typing in Python, and time-aware validation.

> ⚠️ **Disclaimer**: This project is educational and experimental. It is **not** financial advice.

---

## Project Objective

The goal of this project is to build a **reproducible, extensible, and well-engineered pipeline** that enables:

* Financial data ingestion and preprocessing (BTC)
* Technical feature engineering
* Training predictive models (baseline and advanced)
* Time-series validation using *walk-forward cross-validation*
* Performance comparison against naive baselines
* Trading signal simulation and metric evaluation

All following **software engineering**, **MLOps**, and **static typing** best practices.

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
src/
├── data/           # Data loading and preprocessing
├── features/       # Feature engineering
├── models/         # ML models (BaseModel, LinearModel, etc.)
├── evaluation/     # Metrics (MAE, RMSE, Directional Accuracy)
├── pipelines/      # Pipeline orchestrators
├── validation/     # Walk-forward CV and metrics
├── strategy/       # Trading signal rules (long / flat / short)
├── backtest/       # PnL simulation, equity curve, metrics
├── execution/      # (Future) live / simulated execution
├── utils/          # Shared helpers
└── config/         # YAML configuration files

tests/
├── unit/
│   ├── models/
│   ├── validation/
│   └── features/
├── integration/
└── utils/

requirements.txt
README.md
```

---

## Configuration

The project is **configuration-driven** using YAML files:

```yaml
# training.yaml
model:
  name: linear_ridge
  params:
    alpha: 1.0

validation:
  method: walk_forward
  n_splits: 5
```

This enables:

* Model changes without touching code
* Reproducible experiments
* Controlled and comparable runs

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
* [in progress] Backtest pipeline
* [ ] Reproducible experiments and artifacts
* [ ] Real-time simulation
* [ ] Live broker integration (Bitso / API)
---

## Installation

```bash
git clone https://github.com/your_username/bitcoin-ml-pipeline.git
cd bitcoin-ml-pipeline
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
    "configs/backtest.yaml"
)

run_training_pipeline(cfg)

```

---

## Author

**Erik Ocegueda**
Data Science & ML Engineering
Project oriented toward *ML Engineer / Data Scientist / Quant* roles

---

## Final Notes

This repository is intended for learning and experimentation only. Do not use it to make real financial decisions.
