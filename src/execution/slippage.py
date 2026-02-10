from __future__ import annotations

def slippage_bps(price: float, bps: float)-> float:
    """bps = basis points. 10bps => 0.10%"""
    return price * (bps / 10_000.0)

def slippage_vol(price:float, vol:float | None, k: float = 0.0)->float:
    if vol is None:
        return 0.0
    
    return price * (k*vol)
