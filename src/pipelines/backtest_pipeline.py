from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.backtest import (BacktestReport, run_backtest_threshold, _save_backtest_artifacts)
from src.pipelines import (run_data_pipeline, run_feature_pipeline)
from src.models import _load_model
from src.types import ConfigLike
from src.utils import log_step

logger = logging.getLogger(__name__)


def run_backtest_pipeline(
    cfg: ConfigLike,
    model_path: Path | None = None,
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

    valid_idx = X.dropna().index
    X = X.loc[valid_idx]
    df = df.loc[valid_idx]
    
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
        output_path = _save_backtest_artifacts(cfg, report)
        
    logger.info("Backtest artifacts saved at %s", output_path)
    
    return report