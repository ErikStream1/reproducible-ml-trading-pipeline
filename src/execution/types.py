from __future__ import annotations
from typing import TypeAlias, Sequence, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

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
    
PositionLike: TypeAlias = Sequence[int] | np.ndarray | pd.Series
FillVectorLike: TypeAlias = Sequence[Fill]

