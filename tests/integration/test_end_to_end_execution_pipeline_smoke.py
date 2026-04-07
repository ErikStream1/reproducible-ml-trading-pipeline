from __future__ import annotations

from pathlib import Path
import json

from src.execution import RealtimeSimulationStepResult
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
            "circuit_breakers": {
                "enabled": True,
                "fail_closed": True,
                "state_path": str(tmp_path / "execution" / "cb.json"),
            },
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


def test_run_end_to_end_execution_shadow_pipeline_without_shadow_config(
    monkeypatch,
) -> None:
    cfg = {
        "execution": {
            "fill_mode": "next_close",
            "qty": 0.001,
            "fees": {"rate": 0.001},
            "slippage": {"bps": 5, "vol_k": 0.0},
            "circuit_breakers": {
                "enabled": True,
                "fail_closed": True,
            },
        }
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

    result = run_end_to_end_execution_shadow_pipeline(cfg)

    assert result.fills_count == 1
    assert result.has_position_change is True
    assert result.artifact_dir is None

def test_run_end_to_end_execution_shadow_pipeline_fail_closed_on_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cfg = {
        "execution": {
            "fill_mode": "next_close",
            "qty": 0.001,
            "fees": {"rate": 0.001},
            "slippage": {"bps": 5, "vol_k": 0.0},
            "circuit_breakers": {
                "enabled": True,
                "fail_closed": True,
                "state_path": str(tmp_path / "execution" / "cb.json"),
            },
        }
    }

    def _raise(_: dict) -> RealtimeSimulationStepResult:
        raise RuntimeError("inference crash")

    monkeypatch.setattr(
        "src.pipelines.end_to_end_execution_pipeline.run_realtime_simulation_step",
        _raise,
    )

    result = run_end_to_end_execution_shadow_pipeline(cfg, collect_quotes_first=False)

    assert result.status == "fail_closed_hold"
    assert result.step.action == "HOLD"
    assert result.fills_count == 0
    cb_state = json.loads((tmp_path / "execution" / "cb.json").read_text(encoding="utf-8"))
    assert cb_state["error_code"] == "INC-SHADOW-001"
    assert Path(cb_state["incident_bundle_path"]).exists()