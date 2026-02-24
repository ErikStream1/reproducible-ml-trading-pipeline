from __future__ import annotations

import logging
import pandas as pd

from src.execution import (simulate_fills_from_target_position, 
                           ShadowExecutionResult, 
                           _persist_shadow_execution_artifacts)

from src.pipelines import (run_collect_quotes_pipeline, 
                           run_realtime_simulation_step)

from src.types import ConfigLike
from src.utils import log_step

logger = logging.getLogger(__name__)

def run_end_to_end_execution_shadow_pipeline(
    cfg: ConfigLike,
    collect_quotes_first: bool | None = None,
) -> ShadowExecutionResult:
    """
    Run a dry-run end-to-end execution loop in shadow mode.

    This pipeline stitches quote collection (optional), latest-step model inference,
    strategy decisioning, and execution simulation into a single reproducible run.
    No live orders are sent.
    """
    
    if collect_quotes_first is None:
        collect_quotes_first = cfg["execution_shadow"].get("collect_quotes_first", False)
    
    if collect_quotes_first:
        with log_step(logger, "Collect quotes"):
            run_collect_quotes_pipeline(cfg)

    with log_step(logger, "Realtime simulation step"):
        step_result = run_realtime_simulation_step(cfg)

    with log_step(logger, "Shadow execution simulation"):
        prev_position = 0
        target_series = pd.Series([prev_position, step_result.target_position], dtype=int)
        price_frame = pd.DataFrame(
            {
                "Close": [step_result.mid, step_result.mid],
                "mid": [step_result.mid, step_result.mid],
                "bid": [step_result.bid, step_result.bid],
                "ask": [step_result.ask, step_result.ask],
            }
        )

        fills = simulate_fills_from_target_position(
            cfg=cfg,
            target_position=target_series,
            price_frame=price_frame,
            volatility=None,
        )
        
        fills_df = pd.DataFrame(
            [
                {
                    "timestamp": f.timestamp,
                    "side": f.side.value,
                    "qty": f.qty,
                    "price": f.price,
                    "fee": f.fee,
                }
                for f in fills
            ]
        )

    with log_step(logger, "Persist shadow artifacts", level=logging.DEBUG):
        output_path = _persist_shadow_execution_artifacts(
            cfg=cfg,
            step_result=step_result,
            fills_df=fills_df,
        )
        if output_path is None:
            logger.warning(
                "Shadow artifacts were not persisted. "
                "Set execution_shadow.artifacts.output_dir in config."
            )

    return ShadowExecutionResult(
        step=step_result,
        fills_count=len(fills_df),
        has_position_change=step_result.target_position != 0,
        artifact_dir=None if output_path is None else str(output_path),
    )
