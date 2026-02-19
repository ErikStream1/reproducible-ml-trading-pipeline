from __future__ import annotations
from src.types import ConfigLike
from src.backtest import RealtimeSimulationStepResult
from dataclasses import asdict
import json
import pandas as pd
from pathlib import Path


def _persist_step_result(cfg: ConfigLike, result: RealtimeSimulationStepResult) -> None:
    artifacts_cfg = cfg.get("realtime_simulation", {}).get("artifacts", {})
    output_dir = artifacts_cfg.get("output_dir")
    if output_dir is None:
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    step_json_path = output_path / artifacts_cfg.get("step_filename", "last_step.json")
    history_csv_path = output_path / artifacts_cfg.get("history_filename", "steps_history.csv")

    row = asdict(result)
    with open(step_json_path, "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2)

    row_df = pd.DataFrame([row])
    if history_csv_path.exists():
        row_df.to_csv(history_csv_path, mode="a", header=False, index=False)
    else:
        row_df.to_csv(history_csv_path, index=False)
