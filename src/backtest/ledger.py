from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from src.types import ConfigLike, IndexLike, VectorLike
from src.execution import OrderSide, FillVectorLike

@dataclass
class LedgerResult:
    equity: pd.Series
    cash: pd.Series
    position_qty: pd.Series
    trades: pd.DataFrame #fills as dataframe
    
def run_ledger(
    cfg: ConfigLike,
    close: VectorLike,
    index: IndexLike,
    fills: FillVectorLike,
)->LedgerResult:
    
    if not isinstance(close, pd.Series):
        close = pd.Series(close)
    
    initial_cash: float = cfg["backtest"].get("initial_cash",100_000)
    
    cash = pd.Series(initial_cash, index = index, dtype = float)
    pos = pd.Series(0.0, index = index, dtype=float)
    
    rows = []
    if not fills: 
        fills_df = pd.DataFrame(columns=["side","qty","price","fee"])

    else:
        for f in fills:
            rows.append({
                "timestamp": f.timestamp,
                "side": f.side.value,
                "qty": f.qty,
                "price": f.price,
                "fee": f.fee
                })
        
        fills_df = pd.DataFrame(rows).set_index("timestamp").sort_index()        
    
    for t in range(1, len(index)):
        idx = index[t]
        if t != index[0]:
            
            
            prev_idx = index[t - 1]
            
            cash.loc[idx] = cash.loc[prev_idx]
            pos.loc[prev_idx] = pos.loc[prev_idx]
            
        if not fills_df.empty and t in fills_df.index:
            if isinstance(fills_df.loc[t], pd.Series):
                rows = fills_df.loc[[t]]
            else:
                rows = fills_df.loc[t]
                
            if isinstance(rows, pd.Series):

                rows = rows.to_frame().T
                
            for _, r in rows.iterrows():
                side = r["side"]
                qty = r["qty"]
                price = r["price"]
                fee = r["fee"]
                notional = qty * price
                
                if side == OrderSide.BUY.value:
                    pos.loc[idx] += qty
                    cash.loc[idx] -= (notional + fee)
                else:
                    pos.loc[idx] -= qty
                    cash.loc[idx] += (notional - fee)
                    
    equitiy = cash + pos * close.reindex(index).astype(float)
    return LedgerResult(equity=equitiy, cash=cash, position_qty= pos, trades=fills_df)