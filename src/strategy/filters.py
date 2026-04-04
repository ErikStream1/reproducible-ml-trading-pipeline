from __future__ import annotations
from src.types import VectorLike, SeriesLike
import pandas as pd

def apply_confidence_gate(
    desired_position: SeriesLike,
    confidence: VectorLike | None,
    threshold: float | None,
)-> SeriesLike:

    if threshold is None or confidence is None:
        return desired_position

    if not isinstance(confidence, pd.Series):
        confidence = pd.Series(confidence, index=desired_position.index)
    else:
        confidence = confidence.reindex(desired_position.index)

    mask_ok = confidence.fillna(0.0) >= float(threshold)
    out = desired_position.copy()
    out.loc[~mask_ok] = 0
    return out

def apply_vol_filter(
    vol_max: float | None,
    desired_position: SeriesLike, 
    volatility: VectorLike | None = None,
)-> SeriesLike:
    
    if not isinstance(volatility, SeriesLike):
        volatility = pd.Series(volatility)
        
    if volatility.empty or vol_max is None:
        return desired_position
    
    mask_ok = volatility <= vol_max
    
    out = desired_position.copy()
    out.loc[~mask_ok] = 0
    
    return out

def apply_cooldown(
    target_position: SeriesLike,
    cooldown_bars: int
)->SeriesLike:
    
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