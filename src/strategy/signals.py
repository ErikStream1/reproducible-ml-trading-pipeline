from __future__ import annotations
from src.types import VectorLike,SeriesLike, ConfigLike, Prediction
import pandas as pd

from src.strategy import (apply_vol_filter, apply_cooldown)

def threshold_signal(
    cfg: ConfigLike,
    pred_return: Prediction,
    volatility: VectorLike | None = None,
)->SeriesLike:
    
    strategy_cfg = cfg["strategy"]
    
    if not isinstance(pred_return, pd.Series):
        pred_return = pd.Series(pred_return)
        
    side_mode = strategy_cfg.get("side_mode", "long_only")
    enter_threshold = strategy_cfg.get("enter_threshold", 0.0)
    exit_threshold = strategy_cfg.get("exit_threshold", 0.0)
    cooldown_bars = strategy_cfg.get("cooldown_bars", 0.0)
    
    volatility_filter_cfg = strategy_cfg["volatility_filter"]
    
    if volatility_filter_cfg.get("enabled", False):
        max_vol = volatility_filter_cfg.get("max_vol", 0.0)
    else:
        max_vol = None
    
    pred_return_index = pred_return.index
    
    if side_mode == "long_only":
        desired = (pred_return > enter_threshold).astype(int)
        
        if exit_threshold != enter_threshold:
            actions = []
            state = 0
            
            for prediction in pred_return.values:
                if state == 0 and prediction > enter_threshold:
                    state = 1
                elif state == 1 and prediction < exit_threshold:
                    state = 0
                
                actions.append(state)
            desired = pd.Series(actions, index = pred_return_index, dtype = int)
                
    else:
        #long short
        desired = pd.Series(0, index = pred_return_index)
        desired.loc[pred_return > enter_threshold] = 1
        desired.loc[pred_return < -enter_threshold] = -1
    
    desired = apply_vol_filter(desired_position=desired, volatility=volatility, vol_max=max_vol)
    desired = apply_cooldown(target_position=desired, cooldown_bars=cooldown_bars)
    
    return desired