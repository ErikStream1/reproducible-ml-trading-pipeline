from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.data import QuoteSeries
from src.types import PathLike

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
 