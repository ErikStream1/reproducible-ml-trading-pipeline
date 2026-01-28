from __future__ import annotations
from src.types import FrameLike
import pandas as pd

def validate_btc_data(df: FrameLike)->None:
    
    required_cols = {"Date","Open", "High", "Low", "Close", "Volume"}
    
    # Column check
   
    if not required_cols.issubset(df.columns):
        missing_cols = []
        for col in required_cols:
            if col not in df.columns:
                missing_cols.append(col)
    
        if missing_cols:
            raise ValueError(f"Column(s) missing: {missing_cols}.")
    
    # Date checks
    
    df["Date"] = pd.to_datetime(df["Date"])
    if not df["Date"].is_monotonic_increasing:
        raise ValueError("Dates are not in chronological order.")
    
    if df["Date"].duplicated().any():
        raise ValueError("Duplicate timestamps detected.")
    
    # Value checks

    if df.isnull().any(axis = None):
        raise ValueError("Null value detected.")
    
    price_cols = ["Open", "High", "Low", "Close"]
    if (df[price_cols] <= 0).any(axis = None):
        raise ValueError("Non-positive price detected.")
    
    if (df["Volume"] < 0).any():
        raise ValueError("Negative volume detected.")

    
    

    