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

    with (output_path / step_filename).open("w", encoding="utf-8") as f:
        json.dump(asdict(step_result), f, ensure_ascii=False, indent=2)

    fills_df.to_csv(output_path / fills_filename, index=False)

    return output_path