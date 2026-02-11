from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from src.backtest import (BacktestReport, run_backtest_threshold)
from src.models import (LinearModel, XGBoostModel)
from src.pipelines import (run_data_pipeline, run_feature_pipeline)
from src.types import ConfigLike, PathLike
from src.utils import log_step

logger = logging.getLogger(__name__)


def _load_model(model_path: PathLike) -> LinearModel | XGBoostModel:
    model_path_str = str(model_path)

    if "linear" in model_path_str:
        return LinearModel.load(model_path_str)
    if "xgboost" in model_path_str:
        return XGBoostModel.load(model_path_str)

    raise ValueError(f"Model not found for path: {model_path_str}")


def _save_backtest_artifacts(cfg: ConfigLike, report: BacktestReport) -> None:
    artifacts_cfg = cfg.get("backtest", {}).get("artifacts", {})

    output_dir = artifacts_cfg.get("output_dir")
    if output_dir is None:
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_filename = artifacts_cfg.get("summary_filename", "summary.json")
    equity_filename = artifacts_cfg.get("equity_filename", "equity.csv")
    trades_filename = artifacts_cfg.get("trades_filename", "trades.csv")

    summary_path = output_path / summary_filename
    equity_path = output_path / equity_filename
    trades_path = output_path / trades_filename

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(report.summary, f, indent=2)

    report.ledger.equity.to_csv(equity_path, index=True)
    report.ledger.trades.to_csv(trades_path, index=True)

    logger.info("Backtest artifacts saved at %s", output_path)


def run_backtest_pipeline(
    cfg: ConfigLike,
    model_path: PathLike = None,
) -> BacktestReport:
    
    with log_step(logger, "Data pipeline"):
        df = run_data_pipeline(cfg)

    with log_step(logger, "Features"):    
        df = run_feature_pipeline(df, cfg)
   
    target = cfg["data"]["schema"].get("target_column", "LogReturn")

    if target in df.columns:
        X = df.drop(columns=target, errors="ignore")
    else:
        raise ValueError(f"Target {target} not found in feature frame")

    model_artifact_path = model_path or cfg["inference"]["artifacts"]["model_path"]

    with log_step(logger, "Load model"):
        model = _load_model(model_artifact_path)

    with log_step(logger, "Prediction"):
        y_pred = model.predict(X)
        pred_return = pd.Series(y_pred, index=df.index)

    volatility_column = cfg["strategy"].get("volatility_column", None)
    if volatility_column is not None and volatility_column in df.columns:
        volatility = df[volatility_column]
    else:
        volatility = None

    with log_step(logger, "Backtest"):
        report = run_backtest_threshold(
            cfg=cfg,
            pred_return=pred_return,
            market=df,
            volatility=volatility,
        )

    with log_step(logger, "Save artifacts", level=logging.DEBUG):
        _save_backtest_artifacts(cfg, report)

    return report