from __future__ import annotations
from typing import Any, TypeAlias, Sequence
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from src.types import SeriesLike, IntArray, payloadLike


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass(frozen=True)
class Fill:
    timestamp: object
    side: OrderSide
    qty: float
    price: float
    fee: float
    
PositionLike: TypeAlias = IntArray | SeriesLike
FillVectorLike: TypeAlias = Sequence[Fill]

@dataclass(frozen=True)
class ShadowExecutionResult:
    step: RealtimeSimulationStepResult
    fills_count: int
    has_position_change: bool
    artifact_dir: str | None
    status: str = "Ok"
    reason: str | None = None

@dataclass(frozen=True)
class RealtimeSimulationStepResult:
    timestamp: str
    bid: float
    ask: float
    mid: float
    predicted_return: float
    target_position: int
    action: str

@dataclass(frozen=True)
class PaperTradingResult:
    step: RealtimeSimulationStepResult
    previous_position: int
    target_position: int
    fills_count: int
    blotter_path: str
    state_path: str
    status: str = "Ok"
    reason: str | None = None
    
class BitsoBrokerError(RuntimeError):
    """Raised when an authenticated bitso broker request fails."""

@dataclass(frozen = True)
class BitsoOrderResponse:
    oid: str | None
    status: str
    raw: dict[str, Any]
    
@dataclass(frozen = True)
class LiveBrokerOrderResult:
    timestamp: str
    action: str
    target_position: int
    previous_position: int
    order_sent: bool
    side: str | None
    major: str | None
    order_id: str | None
    status: str
    payload: payloadLike

@dataclass(frozen=True)
class PreTradeRiskDecision:
    allowed: bool
    reasons: tuple[str, ...]
    details: dict[str, float | int | str | bool | None]
    
@dataclass(frozen=True)
class CircuitBreakerDecision:
    enabled: bool
    fail_closed: bool
    is_open: bool
    state_path: Path
