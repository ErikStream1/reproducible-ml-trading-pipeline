from __future__ import annotations

from pathlib import Path
from src.types import ConfigLike
from src.execution import RealtimeSimulationStepResult
from src.pipelines import run_live_broker_pipeline


def _base_cfg(tmp_path: Path) -> ConfigLike:
    return {
        "execution": {
            "qty": 0.001,
            "circuit_breakers": {
                "enabled": True,
                "fail_closed": True,
                "state_path": str(tmp_path / "execution" / "cb.json"),
            },
        },
        "quotes": {"book": "btc_mxn"},
        "paper_trading": {
            "artifacts": {
                "output_dir": str(tmp_path / "paper_trading"),
                "state_filename": "state.json",
            }
        },
        "live_broker": {
            "dry_run": True,
            "client": {
                "base_url": "https://api.bitso.com/v3",
                "timeout_s": 10.0,
            },
        },
        
        "local_live_broker":{
            "api_key": "k",
            "api_secret": "s"
            }
    }


def test_live_broker_pipeline_returns_dry_run_payload(monkeypatch, tmp_path: Path) -> None:
    cfg = _base_cfg(tmp_path)

    monkeypatch.setattr(
        "src.pipelines.live_broker_pipeline.run_realtime_simulation_step",
        lambda _: RealtimeSimulationStepResult(
            timestamp="2024-01-01T00:00:00+00:00",
            bid=100.0,
            ask=101.0,
            mid=100.5,
            predicted_return=0.02,
            target_position=1,
            action="BUY",
        ),
    )

    result = run_live_broker_pipeline(cfg, collect_quotes_first=False)

    assert result.status == "dry_run"
    assert result.order_sent is False
    assert result.side == "buy"
    assert result.major == "0.001"


def test_live_broker_pipeline_submits_order_when_enabled(monkeypatch, tmp_path: Path) -> None:
    cfg = _base_cfg(tmp_path)
    cfg["live_broker"]["dry_run"] = False

    monkeypatch.setattr(
        "src.pipelines.live_broker_pipeline.run_realtime_simulation_step",
        lambda _: RealtimeSimulationStepResult(
            timestamp="2024-01-01T00:00:00+00:00",
            bid=100.0,
            ask=101.0,
            mid=100.5,
            predicted_return=0.02,
            target_position=1,
            action="BUY",
        ),
    )

    class StubClient:
        def __init__(self, _cfg):
            pass

        def place_market_order(self, *, book, side, major):
            assert book == "btc_mxn"
            assert side == "buy"
            assert str(major) == "0.001"
            return type("Order", (), {"oid": "oid-1", "status": "submitted", "raw": {"success": True}})()

    monkeypatch.setattr("src.pipelines.live_broker_pipeline.BitsoBrokerClient", StubClient)

    result = run_live_broker_pipeline(cfg, collect_quotes_first=False)

    assert result.order_sent is True
    assert result.status == "submitted"
    assert result.order_id == "oid-1"

def test_live_broker_pipeline_blocks_order_on_risk_limits(monkeypatch, tmp_path: Path) -> None:
    cfg = _base_cfg(tmp_path)
    cfg["execution"]["risk_limits"] = {"enabled": True, "max_position": 0}

    monkeypatch.setattr(
        "src.pipelines.live_broker_pipeline.run_realtime_simulation_step",
        lambda _: RealtimeSimulationStepResult(
            timestamp="2024-01-01T00:00:00+00:00",
            bid=100.0,
            ask=101.0,
            mid=100.5,
            predicted_return=0.02,
            target_position=1,
            action="BUY",
        ),
    )

    result = run_live_broker_pipeline(cfg, collect_quotes_first=False)

    assert result.order_sent is False
    assert result.status == "risk_blocked"

def test_live_broker_pipeline_fail_closed_on_critical_error(monkeypatch, tmp_path: Path) -> None:
    cfg = _base_cfg(tmp_path)

    def _raise(_: ConfigLike) -> RealtimeSimulationStepResult:
        raise RuntimeError("upstream failure")

    monkeypatch.setattr(
        "src.pipelines.live_broker_pipeline.run_realtime_simulation_step",
        _raise,
    )

    result = run_live_broker_pipeline(cfg, collect_quotes_first=False)

    assert result.order_sent is False
    assert result.status == "fail_closed_hold"
    assert result.action == "HOLD"