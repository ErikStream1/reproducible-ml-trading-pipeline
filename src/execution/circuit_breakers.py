from __future__ import annotations

import json

from pathlib import Path
import pandas as pd
from src.execution import RealtimeSimulationStepResult, CircuitBreakerDecision
from src.types import ConfigLike


def _state_path(cfg: ConfigLike) -> Path: 
    cb_cfg = cfg["execution"]["circuit_breakers"]
    raw = cb_cfg.get("state_path")
    
    paper_artifacts = cfg.get("paper_trading", {}).get("artifacts", {})
    output_dir = Path(paper_artifacts.get("output_dir", "artifacts/paper_trading"))
    default = output_dir / "circuit_breaker_state.json"
    
    return Path(str(raw)) if raw else default


def evaluate_circuit_breaker(cfg: ConfigLike) -> CircuitBreakerDecision:
    cb_cfg = cfg["execution"]["circuit_breakers"]
    enabled = cb_cfg.get("enabled", False)
    fail_closed = cb_cfg.get("fail_closed", True)
    state_path = _state_path(cfg)

    if not enabled:
        return CircuitBreakerDecision(enabled=False, fail_closed=fail_closed, is_open=False, state_path=state_path)

    is_open = False
    if state_path.exists():
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        is_open = payload.get("is_open", False)

    return CircuitBreakerDecision(enabled=True, fail_closed=fail_closed, is_open=is_open, state_path=state_path)


def record_circuit_breaker_failure(cfg: ConfigLike, *, pipeline: str, exc: Exception) -> Path:
    state_path = _state_path(cfg)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "is_open": True,
        "pipeline": pipeline,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "opened_at": pd.Timestamp.now("UTC").isoformat(),
    }
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return state_path


def clear_circuit_breaker(cfg: ConfigLike) -> None:
    decision = evaluate_circuit_breaker(cfg)
    if decision.state_path.exists():
        decision.state_path.unlink()


def hold_step(*, target_position: int) -> RealtimeSimulationStepResult:
    return RealtimeSimulationStepResult(
        timestamp=pd.Timestamp.now("UTC").isoformat(),
        bid=0.0,
        ask=0.0,
        mid=0.0,
        predicted_return=0.0,
        target_position=int(target_position),
        action="HOLD",
    )