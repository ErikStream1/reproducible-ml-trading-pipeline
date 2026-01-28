from __future__ import annotations

import pandas as pd
import numpy as np

def returns_from_equity(equity: pd.Series)->pd.Series:
    return equity.pct_change().fillna(0.0)

def max_drawdown(equity: pd.Series)->float:
    peak = equity.cummax()
    dd = (equity / peak) - 1
    return float(dd.min())

def sharpe_ratio(ret: pd.Series, periods_per_year: int = 365)->float:
    if periods_per_year < 0:
        raise ValueError("Negative periods per year.")
    
    r = ret.dropna()
    if r.std(ddof = 0) == 0:
        return 0.0
    return float(r.mean() / r.std(ddof = 0)) * np.sqrt(periods_per_year)

def turnover_from_position(position_qty:pd.Series)->float: 
    chg = position_qty.diff().abs().fillna(0.0)
    denom = position_qty.abs().mean()
    return float(chg.sum() / denom) if denom > 0 else 0.0