from __future__ import annotations

from src.execution import PreTradeRiskDecision
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from src.types import ConfigLike, FrameLike


def _parse_ts(ts: str) -> datetime:
    normalized = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _load_blotter(path: Path) -> FrameLike:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def evaluate_pre_trade_risk_limits(
    *,
    cfg: ConfigLike,
    blotter_path: Path,
    previous_position: int,
    requested_target_position: int,
    order_qty_units: float,
    reference_price: float,
    timestamp: str,
) -> PreTradeRiskDecision:
    limits = cfg.get("execution", {}).get("risk_limits", {})
    enabled = bool(limits.get("enabled", True))

    if not enabled or requested_target_position == previous_position:
        return PreTradeRiskDecision(True, tuple(), {"enabled": enabled})

    reasons: list[str] = []
    now = _parse_ts(timestamp)
    blotter = _load_blotter(blotter_path)

    max_position = limits.get("max_position")
    if max_position is not None and abs(int(requested_target_position)) > int(max_position):
        reasons.append("max_position")

    proposed_notional = abs(float(order_qty_units) * float(reference_price))
    max_notional_per_day = limits.get("max_notional_per_day")
    day_notional = 0.0
    if max_notional_per_day is not None and not blotter.empty and {"timestamp", "notional_executed"}.issubset(blotter.columns):
        ts = pd.to_datetime(blotter["timestamp"], utc=True, errors="coerce")
        same_day = ts.dt.date == now.date()
        day_notional = float(blotter.loc[same_day, "notional_executed"].fillna(0.0).sum())
    if max_notional_per_day is not None and (day_notional + proposed_notional) > float(max_notional_per_day):
        reasons.append("max_notional_per_day")

    max_trades_per_hour = limits.get("max_trades_per_hour")
    trades_last_hour = 0
    if max_trades_per_hour is not None and not blotter.empty and {"timestamp", "fills_count"}.issubset(blotter.columns):
        ts = pd.to_datetime(blotter["timestamp"], utc=True, errors="coerce")
        lower = now - timedelta(hours=1)
        in_window = (ts > lower) & (ts <= now)
        traded = blotter["fills_count"].fillna(0).astype(int) > 0
        trades_last_hour = int((in_window & traded).sum())
    if max_trades_per_hour is not None and trades_last_hour >= int(max_trades_per_hour):
        reasons.append("max_trades_per_hour")

    cooldown_minutes = limits.get("cooldown_minutes")
    cooldown_override = bool(limits.get("cooldown_override", False))
    seconds_since_last_trade: float | None = None
    if cooldown_minutes is not None and not cooldown_override and not blotter.empty and {"timestamp", "fills_count"}.issubset(blotter.columns):
        ts = pd.to_datetime(blotter["timestamp"], utc=True, errors="coerce")
        traded = blotter["fills_count"].fillna(0).astype(int) > 0
        trade_ts = ts[traded].dropna()
        if not trade_ts.empty:
            last_trade = trade_ts.max().to_pydatetime()
            seconds_since_last_trade = (now - last_trade).total_seconds()
            if seconds_since_last_trade < float(cooldown_minutes) * 60.0:
                reasons.append("cooldown")

    details = {
        "enabled": enabled,
        "max_position": None if max_position is None else int(max_position),
        "max_notional_per_day": None if max_notional_per_day is None else float(max_notional_per_day),
        "max_trades_per_hour": None if max_trades_per_hour is None else int(max_trades_per_hour),
        "cooldown_minutes": None if cooldown_minutes is None else float(cooldown_minutes),
        "cooldown_override": cooldown_override,
        "proposed_notional": proposed_notional,
        "day_notional": day_notional,
        "trades_last_hour": trades_last_hour,
        "seconds_since_last_trade": seconds_since_last_trade,
    }
    return PreTradeRiskDecision(len(reasons) == 0, tuple(reasons), details)