from __future__ import annotations

from pathlib import Path
import json

from src.backtest import RealtimeSimulationStepResult
from src.pipelines import run_end_to_end_execution_shadow_pipeline


def test_run_end_to_end_execution_shadow_pipeline_persists_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cfg = {
        "execution": {
            "fill_mode": "next_close",
            "qty": 0.001,
            "fees": {"rate": 0.001},
            "slippage": {"bps": 5, "vol_k": 0.0},
        },
        "execution_shadow": {
            "artifacts": {
                "output_dir": str(tmp_path / "execution_shadow"),
                "step_filename": "last_step_with_execution.json",
                "fills_filename": "fills.csv",
                "result_filename": "shadow_execution_result.json",
            }
        },
    }

    monkeypatch.setattr(
        "src.pipelines.end_to_end_execution_pipeline.run_realtime_simulation_step",
        lambda _: RealtimeSimulationStepResult(
            timestamp="2024-01-01T00:00:00+00:00",
            bid=100.0,
            ask=101.0,
            mid=100.5,
            predicted_return=0.01,
            target_position=1,
            action="BUY",
        ),
    )

    result = run_end_to_end_execution_shadow_pipeline(cfg, collect_quotes_first=False)

    assert result.fills_count == 1
    assert result.has_position_change is True
    step_path = tmp_path / "execution_shadow" / "last_step_with_execution.json"
    result_path = tmp_path / "execution_shadow" / "shadow_execution_result.json"
    assert step_path.exists()
    assert (tmp_path / "execution_shadow" / "fills.csv").exists()
    assert result_path.exists()

    payload = json.loads(step_path.read_text(encoding="utf-8"))
    assert "execution" in payload
    assert payload["execution"]["fills_count"] == 1
    assert payload["execution"]["has_position_change"] is True

    result_payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert result_payload["fills_count"] == 1
    assert result_payload["has_position_change"] is True
