from __future__ import annotations

from src.backtest import run_ledger

from typing import Any
import pandas as pd

def test_runner():
    cfg: dict[str, Any] = {
        "execution":{
            "fill_mode": "next_close",
            "qty": 1.0,
            "fees":{
                "rate": 0.01
                },
            
            "slippage":{
                "bps": 5,
                "vol_k": 0.0
            }           
        },
        "backtest":{
            "initial_cash": 100_000,
            "execute_on": "next_bar",
            "periods_per_year": 365
        },
    }