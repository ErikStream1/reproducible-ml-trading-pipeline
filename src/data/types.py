from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from src.types import FrameLike
from pathlib import Path

@dataclass(frozen = True)
class BitsoConfig:
    base_url:str = "https://api.bitso.com/v3"
    timeout_s: float = 10.0
    
class BitsoError(RuntimeError):
    pass

@dataclass(frozen = True)
class QuoteSnapshot:
    ts_exchange: datetime
    book: str
    ask: float
    bid: float
    source: str

@dataclass(frozen = True)
class QuoteSeries:
    df: FrameLike
    
@dataclass(frozen = True)
class CollectQuotesConfig:
    book: str
    mode: str
    poll_interval_s: float
    flush_every_n: int
    out_dir: Path
    
@dataclass
class QuotesInfo:
    book : str
    quotes_dir : str