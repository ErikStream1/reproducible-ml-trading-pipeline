from __future__ import annotations

import logging

import pandas as pd

from src.execution import (PaperTradingResult, 
                           _append_paper_trading_rows,
                           _load_previous_position,
                           _paper_trading_paths,
                           simulate_fills_from_target_position,
                           evaluate_pre_trade_risk_limits,
                           evaluate_circuit_breaker,
                           record_circuit_breaker_failure,
                           hold_step,
                           persist_incident_replay_bundle,
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

    blotter_path, _, state_path = _paper_trading_paths(cfg)
    previous_position = _load_previous_position(state_path)
    decision = evaluate_circuit_breaker(cfg)

    if decision.enabled and decision.fail_closed and decision.is_open:
        step_result = hold_step(target_position=previous_position)
        return PaperTradingResult(
            step=step_result,
            previous_position=previous_position,
            target_position=previous_position,
            fills_count=0,
            blotter_path=str(blotter_path),
            state_path=str(state_path),
            status="circuit_breaker_open",
            reason=f"fail-closed: open circuit breaker at {decision.state_path}",
        )

    try:
        if collect_quotes_first:
            with log_step(logger, "Collect quotes"):
                run_collect_quotes_pipeline(cfg)

        with log_step(logger, "Realtime simulation step"):
            step_result = run_realtime_simulation_step(cfg)
    except Exception as exc:
        if decision.enabled:
            incident = persist_incident_replay_bundle(
            cfg=cfg,
            pipeline="paper_trading",
            exc=exc,
            context={"previous_position": previous_position},
            )
            state_path = record_circuit_breaker_failure(
            cfg,
            pipeline="paper_trading",
            exc=exc,
            error_code=incident.error_code,
            incident_bundle_path=incident.output_dir,
            )
            logger.exception("Paper trading circuit breaker opened due to critical error")
            step_result = hold_step(target_position=previous_position)
            return PaperTradingResult(
                step=step_result,
                previous_position=previous_position,
                target_position=previous_position,
                fills_count=0,
                blotter_path=str(blotter_path),
                state_path=str(state_path),
                status="fail_closed_hold",
                reason=f"{incident.error_code} | {type(exc).__name__}: {exc}",
            )
        raise

    net_target = int(step_result.target_position) - previous_position
    qty = float(str(abs(net_target))) * float(str(cfg["execution"]["qty"]))
    
    risk = evaluate_pre_trade_risk_limits(
        cfg = cfg,
        blotter_path = blotter_path,
        previous_position = previous_position,
        requested_target_position = int(step_result.target_position),
        order_qty_units = qty,
        reference_price = float(step_result.mid),
        timestamp = step_result.timestamp
    )
    
    blocked_by_risk = (net_target != 0) and (not risk.allowed)
    
    with log_step(logger, "Paper execution simulation"):
        fills_df = pd.DataFrame(columns = ["timestamp", "side", "qty", "price", "fee"])
        
        if blocked_by_risk:
            logger.info("Pre-trade risk blocked paper order",
                        extra = {"reasons": list(risk.reasons), "details": risk.details}
                        )
            executed_target_position = previous_position
        else:
            executed_target_position = int(step_result.target_position)
            
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
            final_position=executed_target_position,
        )

    return PaperTradingResult(
        step=step_result,
        previous_position=previous_position,
        target_position=executed_target_position,
        fills_count=int(len(fills_df)),
        blotter_path=str(blotter_path),
        state_path=str(final_state_path),
        status = "Ok",
        reason = None
    )
