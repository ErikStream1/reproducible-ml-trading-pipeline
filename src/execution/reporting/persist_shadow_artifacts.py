from __future__ import annotations
from dataclasses import asdict
from src.types import ConfigLike
from src.backtest import RealtimeSimulationStepResult
from pathlib import Path

import pandas as pd
import json

def _persist_shadow_execution_artifacts(
    cfg: ConfigLike,
    step_result: RealtimeSimulationStepResult,
    fills_df: pd.DataFrame,
) -> Path | None:
    artifacts_cfg = cfg.get("execution_shadow", {}).get("artifacts", {})
    output_dir = artifacts_cfg.get("output_dir")
    if not output_dir:
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    step_filename = artifacts_cfg.get("step_filename", "last_step_with_execution.json")
    fills_filename = artifacts_cfg.get("fills_filename", "fills.csv")
    result_filename = artifacts_cfg.get("result_filename", "shadow_execution_result.json")

    notional = 0.0
    fees_paid = 0.0
    if not fills_df.empty and {"qty", "price"}.issubset(fills_df.columns):
        notional = float((fills_df["qty"].abs() * fills_df["price"]).sum())
    if not fills_df.empty and "fee" in fills_df.columns:
        fees_paid = float(fills_df["fee"].sum())

    payload = {
        **asdict(step_result),
        "execution": {
            "fills_count": int(len(fills_df)),
            "has_position_change": bool(step_result.target_position != 0),
            "notional_executed": notional,
            "fees_paid": fees_paid,
            "fills_filename": fills_filename,
        },
    }

    with (output_path / step_filename).open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    fills_df.to_csv(output_path / fills_filename, index=False)

    result_payload = {
        "step": asdict(step_result),
        "fills_count": int(len(fills_df)),
        "has_position_change": bool(step_result.target_position != 0),
        "artifact_dir": str(output_path),
        "step_filename": step_filename,
        "fills_filename": fills_filename,
    }
    with (output_path / result_filename).open("w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    return output_path
