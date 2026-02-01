from __future__ import annotations
from dataclasses import dataclass

from src.validation.types import SummaryLike
from src.types import SeriesLike, FrameLike

@dataclass(frozen = True)
class LedgerResult:
    equity: SeriesLike
    cash: SeriesLike
    position_qty: SeriesLike
    trades: FrameLike #fills as dataframe

@dataclass(frozen = True)
class BacktestReport:
    ledger: LedgerResult
    ret: SeriesLike
    summary: SummaryLike
    