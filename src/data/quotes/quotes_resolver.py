from __future__ import annotations

from pathlib import Path
import pandas as pd

from typing import Sequence
from src.data import QuoteSeries
from src.types import PathLike, FrameLike

def load_quotes(out_dir:PathLike, book:str)->QuoteSeries:
    base = Path(str(out_dir)) / f"book={book}"
    if not base.exists():
        raise FileNotFoundError(f"No quotes found for book={book} at {base}")
    
    files = sorted(base.rglob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files found under {base}")
    
    df = pd.concat([
        pd.read_parquet(p) 
        for p in files], ignore_index= True)
    
    df["ts_exchange"] = pd.to_datetime(df["ts_exchange"], utc = True)
    df = df.sort_values("ts_exchange").reset_index(drop = True)
    
    return QuoteSeries(df = df[["ts_exchange", "bid", "ask"]])
    
def resolve_quotes_asof(
    quote_series: QuoteSeries,
    timestamps: Sequence[pd.Timestamp],
)->FrameLike:
    
    quotes = quote_series.df.copy()
    tdf = pd.DataFrame({"ts": pd.to_datetime(list(timestamps), utc = True)})
    tdf = tdf.sort_values("ts").reset_index(drop = True)
    
    out = pd.merge_asof(
        tdf,
        quotes,
        left_on="ts",
        right_on="ts_exchange",
        direction="backward",
        allow_exact_matches=True
    )
    
    out = out.drop(columns = ["ts_exchange"])
    return out