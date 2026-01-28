from __future__ import annotations
from typing import TypeAlias, Sequence
from dataclasses import dataclass
from enum import Enum
from src.types import SeriesLike, IntArray

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

