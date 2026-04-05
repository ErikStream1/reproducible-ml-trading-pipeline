from __future__ import annotations

from src.execution import DivergenceMonitorResult, evaluate_shadow_live_divergence
from src.types import ConfigLike


def run_shadow_live_divergence_monitor_pipeline(
    cfg: ConfigLike,
    expected_fills_path: str | None = None,
    actual_fills_path: str | None = None,
) -> DivergenceMonitorResult:
    """Compare shadow expected fills vs live fills and return divergence alert decision."""

    return evaluate_shadow_live_divergence(
        cfg=cfg,
        expected_fills_path=expected_fills_path,
        actual_fills_path=actual_fills_path,
    )