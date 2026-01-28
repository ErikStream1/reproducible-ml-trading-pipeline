from __future__ import annotations

import pandas as pd
import numpy as np
from src.types import ConfigLike
from src.backtest import run_ledger, LedgerResult
from src.execution import Fill, OrderSide

def test_run_ledger():
    cfg: ConfigLike = {
        "backtest":{
            "initial_cash": 100_000,
            "execute_on": "next_bar",
            "periods_per_year": 365
        }
    }

    data_close = np.random.rand(10)
    
    
    timestamps = pd.date_range(start = "2024-01-01", periods = 10)
    close = pd.Series(data_close, index = timestamps)
    index = close.index
    
    fills = []
    
    for i in range(10):
        fills.append(
            Fill(
                timestamp=timestamps[i],
                side = OrderSide.BUY if np.random.randint(0,2) == 1 else OrderSide.SELL,
                qty = np.random.rand()*100,
                price = np.random.rand()*100,
                fee = np.random.rand()
            )
        )
        
    output = run_ledger(cfg = cfg,
                        close = close,
                        index = index,
                        fills = fills)
    
    assert isinstance(output, LedgerResult)
    