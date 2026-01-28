from __future__ import annotations
from src.types import VectorLike
import pandas as pd

def apply_vol_filter(
    vol_max: float | None,
    desired_position: pd.Series, 
    volatility: VectorLike | None = None,
)-> pd.Series:
    
    if not isinstance(volatility, pd.Series):
        volatility = pd.Series(volatility)
        
    if volatility.empty or vol_max is None:
        return desired_position
    
    mask_ok = volatility <= vol_max
    
    out = desired_position.copy()
    out.loc[~mask_ok] = 0
    
    return out

def apply_cooldown(
    target_position: pd.Series,
    cooldown_bars: int
)->pd.Series:
    
    if cooldown_bars <= 0:
        return target_position
    
    out = target_position.copy()
    
    changes = out.diff().fillna(0).ne(0)
    
    last_trade_idx = None
    
    for i, (idx, changed) in enumerate(changes.items()):
        if not changed:
            continue
        
        if last_trade_idx is not None and (i - last_trade_idx) <= cooldown_bars:
            out.iloc[i] = out.iloc[i-1]
            continue 
            
        last_trade_idx = i
    
    return out