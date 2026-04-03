from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.execution import RealtimeSimulationStepResult
from src.pipelines import run_paper_trading_pipeline


def test_run_paper_trading_pipeline_persists_blotter_and_state(
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
        "paper_trading": {
            "artifacts": {
                "output_dir": str(tmp_path / "paper_trading"),
                "blotter_filename": "blotter.csv",
                "fills_filename": "fills.csv",
                "state_filename": "state.json",
            }
        },
    }

    steps = iter(
        [
            RealtimeSimulationStepResult(
                timestamp="2024-01-01T00:00:00+00:00",
                bid=100.0,
                ask=101.0,
                mid=100.5,
                predicted_return=0.01,
                target_position=1,
                action="BUY",
            ),
            RealtimeSimulationStepResult(
                timestamp="2024-01-01T00:01:00+00:00",
                bid=101.0,
                ask=102.0,
                mid=101.5,
                predicted_return=-0.01,
                target_position=0,
                action="SELL",
            ),
        ]
    )

    monkeypatch.setattr(
        "src.pipelines.paper_trading_pipeline.run_realtime_simulation_step",
        lambda _: next(steps),
    )

    first = run_paper_trading_pipeline(cfg, collect_quotes_first=False)
    second = run_paper_trading_pipeline(cfg, collect_quotes_first=False)

    assert first.previous_position == 0
    assert first.target_position == 1
    assert first.fills_count == 1

    assert second.previous_position == 1
    assert second.target_position == 0
    assert second.fills_count == 1

    blotter_path = tmp_path / "paper_trading" / "blotter.csv"
    fills_path = tmp_path / "paper_trading" / "fills.csv"
    state_path = tmp_path / "paper_trading" / "state.json"

    assert blotter_path.exists()
    assert fills_path.exists()
    assert state_path.exists()

    blotter = pd.read_csv(blotter_path)
    assert len(blotter) == 2
    assert blotter["previous_position"].tolist() == [0, 1]
    assert blotter["target_position"].tolist() == [1, 0]

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["last_position"] == 0
    
    
def test_paper_trading_pipeline_applies_cooldown_risk_limit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cfg = {
        "execution": {
            "fill_mode": "next_close",
            "qty": 0.001,
            "fees": {"rate": 0.001},
            "slippage": {"bps": 5, "vol_k": 0.0},
            "risk_limits": {
                "enabled": True,
                "cooldown_minutes": 5,
                "cooldown_override": False,
            },
            "circuit_breakers": {
                "enabled": True,
                "fail_closed": True,
                "state_path": str(tmp_path / "execution" / "cb.json"),
            },
        },
        "paper_trading": {
            "artifacts": {
                "output_dir": str(tmp_path / "paper_trading"),
                "blotter_filename": "blotter.csv",
                "fills_filename": "fills.csv",
                "state_filename": "state.json",
            }
        },
    }

    steps = iter(
        [
            RealtimeSimulationStepResult(
                timestamp="2024-01-01T00:00:00+00:00",
                bid=100.0,
                ask=101.0,
                mid=100.5,
                predicted_return=0.01,
                target_position=1,
                action="BUY",
            ),
            RealtimeSimulationStepResult(
                timestamp="2024-01-01T00:01:00+00:00",
                bid=100.0,
                ask=101.0,
                mid=100.5,
                predicted_return=-0.01,
                target_position=0,
                action="SELL",
            ),
        ]
    )

    monkeypatch.setattr(
        "src.pipelines.paper_trading_pipeline.run_realtime_simulation_step",
        lambda _: next(steps),
    )

    first = run_paper_trading_pipeline(cfg, collect_quotes_first=False)
    second = run_paper_trading_pipeline(cfg, collect_quotes_first=False)

    assert first.fills_count == 1
    assert second.fills_count == 0
    assert second.previous_position == 1
    assert second.target_position == 1
    
def test_paper_trading_pipeline_fail_closed_on_critical_error(
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
        "paper_trading": {
            "artifacts": {
                "output_dir": str(tmp_path / "paper_trading"),
                "blotter_filename": "blotter.csv",
                "fills_filename": "fills.csv",
                "state_filename": "state.json",
            }
        },
    }

    def _raise(_: dict) -> RealtimeSimulationStepResult:
        raise ValueError("quotes missing")

    monkeypatch.setattr(
        "src.pipelines.paper_trading_pipeline.run_realtime_simulation_step",
        _raise,
    )

    result = run_paper_trading_pipeline(cfg, collect_quotes_first=False)
    assert result.status == "fail_closed_hold"
    assert result.step.action == "HOLD"
    assert result.target_position == 0
    assert result.fills_count == 0