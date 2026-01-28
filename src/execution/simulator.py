from __future__ import annotations
from typing import cast
from src.types import ConfigLike, VectorLike, FrameLike
import pandas as pd

from src.execution import (
                           #Types
                           Fill, 
                           OrderSide,
                           PositionLike,
                           FillVectorLike,
                           #Fills
                           fill_price_next_close, 
                           fill_price_mid, 
                           fill_price_bid_ask,
                           #Slippage
                           slippage_bps,
                           slippage_vol,
                           #Fees
                           fee_proportional,
                           )

def simulate_fills_from_target_position(
    cfg: ConfigLike, 
    target_position: PositionLike, 
    price_frame: FrameLike, 
    volatility: VectorLike | None = None
)->FillVectorLike:
    
    if not isinstance(target_position,pd.Series):
        target_position = pd.Series(target_position, dtype = int)
    
    if not isinstance(volatility,pd.Series):
        volatility = pd.Series(volatility, dtype = float)
    
    exe_cfg = cfg["execution"]
    
    qty: float = exe_cfg.get("qty", 1.0)
    fee_rate: float = exe_cfg["fees"].get("rate", 0.001)
    fill_mode: str = exe_cfg.get("fill_mode", "next_close")
    slippage_bps_value: float = exe_cfg["slippage"].get("bps", 5)
    slippage_vol_k: float = exe_cfg["slippage"].get("vol_k", 0.0)

    tp = target_position.astype(int)
    changes = tp.diff().fillna(tp.iloc[0]).astype(int)
    fills: FillVectorLike = []
    
    for t, delta in changes.items():
        if delta == 0:
            continue
        
        t_int = cast(int, t)
        
        side = OrderSide.BUY if delta > 0 else OrderSide.SELL
        base_price: float 
        
        if fill_mode == "next_close":
            base_price = fill_price_next_close(close = price_frame["Close"],t = t_int)
        elif fill_mode == "mid":
            base_price = fill_price_mid(mid = price_frame["mid"],t = t_int)
        elif fill_mode == "bid_ask":
            base_price = fill_price_bid_ask(bid = price_frame["bid"], ask=price_frame["ask"], side= side.value, t = t_int)
        else:
            raise ValueError(f"Unknown fill_mode {fill_mode}")


        slip = slippage_bps(price = base_price, bps = slippage_bps_value) + \
            slippage_vol(price = base_price, vol = None if volatility is None else volatility.loc[t_int], k = slippage_vol_k)
        
        if side == OrderSide.BUY:
            price = base_price + slip
        else:
            price = base_price - slip

        notional = qty * price
        fee = fee_proportional(notional, fee_rate)
              
        fills.append(Fill(timestamp=t, side = side,qty = qty, price = price, fee = fee))
        
    return fills

