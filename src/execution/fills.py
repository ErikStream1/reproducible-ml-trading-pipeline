from __future__ import annotations
import pandas as pd

def fill_price_next_close(close: pd.Series, t: int)->float:
    
    value = close.loc[t]
    return float(value)

def fill_price_mid(mid: pd.Series, t: int)->float:
    return float(mid.loc[t])

def fill_price_bid_ask(bid: pd.Series, ask: pd.Series, side: str, t:int)->float:      
    if side == "BUY":
        return float(ask.loc[t])
    
    return float(bid.loc[t])
