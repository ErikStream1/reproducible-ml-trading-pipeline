from __future__ import annotations
import yfinance as yf
import pandas as pd
from src.types import FrameLike

def load_btc_data(
    ticker: str = "BTC-USD",
    start: str = "2015-01-01",
    end: str|None = None,
    )->FrameLike:

    df = yf.download(ticker, start=start, end=end, progress=False)
    
    if df is None:
        return pd.DataFrame()
    
    df = df.reset_index()
    return df