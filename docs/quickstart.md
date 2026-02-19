# Quickstart
## Requirements
 - Python >= 3.11 (recommended)
 - (Optional) venv/conda

## Install
```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configure
Configs live in configs/

Typical files:

* Data & providers:
    * `data.yaml`
    * `bitso.yaml`
    * `quotes.yaml`
* ML / features:
    * `features.yaml`
    * `models.yaml`    
    * `training.yaml`
    * `inference.yaml`
    * `realtime_simulation.yaml`
* Strategy & backtest:
    * `strategy.yaml`
    * `execution.yaml`
    * `backtest.yaml`

## Run
Run commands from the repo root.

This project uses `main.py` as an entry point. By default, the pipeline executed is controlled
by the code inside `main.py` (you can enable/disable pipeline calls there).


```bash
python main.py
```

## Outputs
Typical artifacts locations:
* Data outputs:
    * `data/raw`
    * `data/processed`
    * `data/quotes`
* Artifacts:
    * `artifacts/` (models, predictions, experiments)
* Logs:
    * `logs printed to stdout`
    * `logs/pipeline.log` (persisted file)

