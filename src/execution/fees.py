from __future__ import annotations

def fee_proportional(notional: float, fee_rate: float)->float:
    """fee_rate ej. 0.001 => 0.1%"""
    return abs(notional)*fee_rate

