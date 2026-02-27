from __future__ import annotations

import logging

import pandas as pd

from src.execution import PaperTradingResult, simulate_fills_from_target_position
from src.execution.reporting.paper_trading_store import (
    _append_paper_trading_rows,
    _load_previous_position,
    _paper_trading_paths,
)
from src.pipelines import run_collect_quotes_pipeline, run_realtime_simulation_step
from src.types import ConfigLike
from src.utils import log_step

logger = logging.getLogger(__name__)


def run_paper_trading_pipeline(
    cfg: ConfigLike,
    collect_quotes_first: bool | None = None,
) -> PaperTradingResult:
    """
    Run one paper-trading step using live market data and simulated fills.

    The pipeline keeps a persistent position state and appends run records to a
    blotter so consecutive calls behave like an execution loop.
    """

    paper_cfg = cfg.get("paper_trading", {})
    if collect_quotes_first is None:
        collect_quotes_first = bool(paper_cfg.get("collect_quotes_first", True))

    if collect_quotes_first:
        with log_step(logger, "Collect quotes"):
            run_collect_quotes_pipeline(cfg)

    with log_step(logger, "Realtime simulation step"):
        step_result = run_realtime_simulation_step(cfg)

    _, _, state_path = _paper_trading_paths(cfg)
    previous_position = _load_previous_position(state_path)

    with log_step(logger, "Paper execution simulation"):
        net_target = int(step_result.target_position) - previous_position
        target_series = pd.Series([0, net_target], dtype=int)
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

    with log_step(logger, "Persist paper-trading artifacts", level=logging.DEBUG):
        blotter_path, final_state_path = _append_paper_trading_rows(
            cfg=cfg,
            step_result=step_result,
            previous_position=previous_position,
            fills_df=fills_df,
        )

    return PaperTradingResult(
        step=step_result,
        previous_position=previous_position,
        target_position=int(step_result.target_position),
        fills_count=int(len(fills_df)),
        blotter_path=str(blotter_path),
        state_path=str(final_state_path),
    )
