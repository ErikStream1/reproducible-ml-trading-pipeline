from __future__ import annotations

import logging

from src.execution import (LiveBrokerOrderResult,
                           BitsoBrokerClient,
                           _load_previous_position,
                           _paper_trading_paths,
                           evaluate_pre_trade_risk_limits)
from src.pipelines import (run_collect_quotes_pipeline,
                           run_realtime_simulation_step)

from src.types import ConfigLike
from src.utils import log_step

logger = logging.getLogger(__name__)

def run_live_broker_pipeline(
    cfg: ConfigLike,
    collect_quotes_first: bool | None = None,
) -> LiveBrokerOrderResult:
    """Run one live broker execution step against Bitso private API."""

    live_cfg = cfg.get("live_broker", {})
    if collect_quotes_first is None:
        collect_quotes_first = bool(live_cfg.get("collect_quotes_first", True))

    if collect_quotes_first:
        with log_step(logger, "Collect quotes"):
            run_collect_quotes_pipeline(cfg)

    with log_step(logger, "Realtime simulation step"):
        step_result = run_realtime_simulation_step(cfg)

    blotter_path, _, state_path = _paper_trading_paths(cfg)
    previous_position = _load_previous_position(state_path)

    net_target = int(step_result.target_position) - previous_position
    if net_target == 0:
        return LiveBrokerOrderResult(
            timestamp=step_result.timestamp,
            action=step_result.action,
            target_position=int(step_result.target_position),
            previous_position=previous_position,
            order_sent=False,
            side=None,
            major=None,
            order_id=None,
            status="noop",
            payload={"reason": "target position unchanged"},
        )

    side = "buy" if net_target > 0 else "sell"
    qty = float(str(abs(net_target))) * float(str(cfg["execution"]["qty"]))
    if qty <= 0:
        return LiveBrokerOrderResult(
            timestamp=step_result.timestamp,
            action=step_result.action,
            target_position=int(step_result.target_position),
            previous_position=previous_position,
            order_sent=False,
            side=side,
            major=str(qty),
            order_id=None,
            status="noop",
            payload={"reason": "computed order quantity is zero"},
        )
    risk = evaluate_pre_trade_risk_limits(
        cfg = cfg,
        blotter_path = blotter_path,
        previous_position = previous_position,
        requested_target_position = int(step_result.target_position),
        order_qty_units = qty,
        reference_price = float(step_result.mid),
        timestamp = step_result.timestamp
    )
    
    if not risk.allowed:
        return LiveBrokerOrderResult(
            timestamp=step_result.timestamp,
            action=step_result.action,
            target_position=previous_position,
            previous_position=previous_position,
            order_sent=False,
            side=side,
            major=str(qty),
            order_id=None,
            status="risk_blocked",
            payload={
                "book": cfg["quotes"]["book"],
                "side": side,
                "major": str(qty),
            },
        )
    
    if bool(live_cfg.get("dry_run", True)):
        return LiveBrokerOrderResult(
            timestamp=step_result.timestamp,
            action=step_result.action,
            target_position=int(step_result.target_position),
            previous_position=previous_position,
            order_sent=False,
            side=side,
            major=str(qty),
            order_id=None,
            status="dry_run",
            payload={
                "book": cfg["quotes"]["book"],
                "side": side,
                "major": str(qty),
            },
        )

    with log_step(logger, "Submit live Bitso market order"):
        client = BitsoBrokerClient(cfg)
        order = client.place_market_order(book=cfg["quotes"]["book"], side=side, major=qty)

    return LiveBrokerOrderResult(
        timestamp=step_result.timestamp,
        action=step_result.action,
        target_position=int(step_result.target_position),
        previous_position=previous_position,
        order_sent=True,
        side=side,
        major=str(qty),
        order_id=order.oid,
        status=order.status,
        payload=order.raw,
    )