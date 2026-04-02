from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.execution import RealtimeSimulationStepResult
from src.types import ConfigLike, FrameLike

def _paper_trading_paths(cfg: ConfigLike) -> tuple[Path, Path, Path]:
    paper_cfg = cfg.get("paper_trading", {})
    artifacts_cfg = paper_cfg.get("artifacts", {})

    output_dir = Path(artifacts_cfg.get("output_dir", "artifacts/paper_trading"))
    output_dir.mkdir(parents=True, exist_ok=True)

    blotter_path = output_dir / artifacts_cfg.get("blotter_filename", "blotter.csv")
    fills_path = output_dir / artifacts_cfg.get("fills_filename", "fills.csv")
    state_path = output_dir / artifacts_cfg.get("state_filename", "state.json")
    return blotter_path, fills_path, state_path


def _load_previous_position(state_path: Path) -> int:
    if not state_path.exists():
        return 0

    payload = json.loads(state_path.read_text(encoding="utf-8"))
    return int(payload.get("last_position", 0))


def _append_paper_trading_rows(
    cfg: ConfigLike,
    step_result: RealtimeSimulationStepResult,
    previous_position: int,
    fills_df: FrameLike,
    final_position: int | None = None
) -> tuple[Path, Path]:
    blotter_path, fills_path, state_path = _paper_trading_paths(cfg)

    fills_count = int(len(fills_df))
    notional = 0.0
    fees_paid = 0.0
    if not fills_df.empty and {"qty", "price"}.issubset(fills_df.columns):
        notional = float((fills_df["qty"].abs() * fills_df["price"]).sum())
    if not fills_df.empty and "fee" in fills_df.columns:
        fees_paid = float(fills_df["fee"].sum())

    executed_position = int(step_result.target_position) if final_position is None else int(final_position)
    
    blotter_row = pd.DataFrame(
        [
            {
                "timestamp": step_result.timestamp,
                "action": step_result.action,
                "predicted_return": step_result.predicted_return,
                "mid": step_result.mid,
                "bid": step_result.bid,
                "ask": step_result.ask,
                "previous_position": previous_position,
                "target_position": executed_position,
                "fills_count": fills_count,
                "notional_executed": notional,
                "fees_paid": fees_paid,
            }
        ]
    )

    if blotter_path.exists():
        blotter_row.to_csv(blotter_path, mode="a", header=False, index=False)
    else:
        blotter_row.to_csv(blotter_path, index=False)

    if not fills_df.empty:
        if fills_path.exists():
            fills_df.to_csv(fills_path, mode="a", header=False, index=False)
        else:
            fills_df.to_csv(fills_path, index=False)

    state_payload = {
        "last_timestamp": step_result.timestamp,
        "last_position": executed_position,
    }
    state_path.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")

    return blotter_path, state_path