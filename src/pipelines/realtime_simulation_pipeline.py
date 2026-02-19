from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.data import load_quotes
from src.pipelines import run_feature_pipeline
from src.strategy import threshold_signal
from src.backtest import RealtimeSimulationStepResult, _persist_step_result
from src.models import _load_model
from src.types import ConfigLike
from src.utils import log_step

logger = logging.getLogger(__name__)

def run_realtime_simulation_step(
    cfg: ConfigLike,
    model_path: Path | None = None,
) -> RealtimeSimulationStepResult:
    """
    Simulate a single real-time decision step from collected quotes.

    The function:
      1) Loads quote snapshots from parquet storage.
      2) Builds features over the available quote history.
      3) Predicts returns with the trained model.
      4) Applies strategy rules and returns the latest target/action.
    """

    rt_cfg = cfg.get("realtime_simulation", {})
    min_history_rows = int(rt_cfg.get("min_history_rows", 50))

    quotes_cfg = cfg["quotes"]
    out_dir = Path(quotes_cfg.get("out_dir", "data/quotes"))
    book = quotes_cfg["book"]

    with log_step(logger, "Load quotes"):
        quote_series = load_quotes(out_dir=out_dir, book=book)
        quotes_df = quote_series.df.copy()

    if len(quotes_df) < min_history_rows:
        raise ValueError(
            f"Not enough quotes for simulation step. "
            f"required={min_history_rows} got={len(quotes_df)}"
        )

    with log_step(logger, "Prepare market frame"):
        
        market = quotes_df.rename(columns={"ts_exchange": "Date", "mid": "Close"})
    
    with log_step(logger, "Features"):
        feat = run_feature_pipeline(market, cfg)
        feat = feat.dropna().reset_index(drop=True)
    
    if feat.empty:
        raise ValueError("Feature frame is empty after dropna; increase quote history.")

    target = cfg["data"]["schema"].get("target_column", "LogReturn")
    if target not in feat.columns:
        raise ValueError(f"Target {target} not found in feature frame")

    X = feat.drop(columns=target, errors="ignore")

    model_artifact_path = model_path or Path(cfg["inference"]["artifacts"]["model_path"])

    with log_step(logger, "Load model"):
        model = _load_model(model_artifact_path)
    
    with log_step(logger, "Predict"):
        y_pred = model.predict(X)
        pred_series = pd.Series(y_pred, index=feat.index, dtype=float)

    volatility_column = cfg.get("strategy", {}).get("volatility_column", None)
    if volatility_column is not None and volatility_column in feat.columns:
        volatility = feat[volatility_column]
    else:
        volatility = None

    with log_step(logger, "Generate target position"):
        desired = threshold_signal(cfg=cfg, pred_return=pred_series, volatility=volatility)

    last_quote = quotes_df.iloc[-1]
    latest_target = int(desired.iloc[-1])
    prev_target = int(desired.iloc[-2]) if len(desired) > 1 else 0

    if latest_target > prev_target:
        action = "BUY"
    elif latest_target < prev_target:
        action = "SELL"
    else:
        action = "HOLD"

    result = RealtimeSimulationStepResult(
        timestamp=pd.to_datetime(last_quote["ts_exchange"], utc=True).isoformat(),
        bid=float(last_quote["bid"]),
        ask=float(last_quote["ask"]),
        mid=float(last_quote["mid"]),
        predicted_return=float(pred_series.iloc[-1]),
        target_position=latest_target,
        action=action,
    )

    with log_step(logger, "Save step artifacts", level=logging.DEBUG):
        _persist_step_result(cfg, result)

    return result