from __future__ import annotations
from typing import TypeAlias, Sequence
from dataclasses import dataclass
from enum import Enum
from src.types import SeriesLike, IntArray
from src.backtest import RealtimeSimulationStepResult

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
