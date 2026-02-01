from __future__ import annotations

import logging
import pandas as pd

from src.backtest import LedgerResult
from src.types import ConfigLike, IndexLike, VectorLike, SeriesLike
from src.execution import OrderSide, FillVectorLike

logger = logging.getLogger(__name__)

def run_ledger(
    cfg: ConfigLike,
    close: VectorLike,
    index: IndexLike,
    fills: FillVectorLike,
)->LedgerResult:
    
    if not isinstance(close, SeriesLike):
        close = pd.Series(close)
    
    initial_cash: float = cfg["backtest"].get("initial_cash",100_000)
    
    cash = pd.Series(0.0, index = index, dtype = float)
    pos = pd.Series(0.0, index = index, dtype=float)
    
    rows = []
    if not fills: 
        fills_df = pd.DataFrame(columns=["side","qty","price","fee"])

    else:
        for f in fills:
            if f.timestamp != index[0]:
                rows.append({
                    "timestamp": f.timestamp,
                    "side": f.side.value,
                    "qty": f.qty,
                    "price": f.price,
                    "fee": f.fee
                    })
            
        fills_df = pd.DataFrame(rows).set_index("timestamp").sort_index()        
        
    for t in range(len(index)):
        idx = index[t]
        prev_idx = index[t - 1]
        
        if idx == index[0]:
            cash.loc[idx] = initial_cash
            continue
            
        else:            
            cash.loc[idx] = cash.loc[prev_idx]
            pos.loc[idx] = pos.loc[prev_idx]

        if not fills_df.empty and idx in fills_df.index:
            if isinstance(fills_df.loc[idx], SeriesLike):
                rows = fills_df.loc[[idx]]
            else:
                rows = fills_df.loc[idx]
                
            if isinstance(rows, SeriesLike):
                rows = rows.to_frame().T
            
            for _, r in rows.iterrows():
                side:OrderSide = r["side"]
                qty:float = r["qty"]
                price:float = r["price"]
                fee_rate:float = r["fee"]

                if side == OrderSide.SELL.value:
                    position_qty = pos.loc[idx]
                    sell_qty = min(qty, position_qty)
                    if sell_qty <= 0:
                        logger.debug(
                            "Reject SELL (no inventory). ts=%s requested_qty=%.6f position_qty=%.6f",
                            idx, qty, position_qty
                            )
                        continue
                    
                    notional = sell_qty * price
                    fee = fee_rate * notional
                    
                    pos.loc[idx] -= sell_qty
                    cash.loc[idx] += (notional - fee)
                
                elif side == OrderSide.BUY.value:
                    max_affordable = cash.loc[idx] / price
                    buy_qty = min(qty, max_affordable)
                    notional = buy_qty * price
                    fee = fee_rate * notional
                    
                    pos.loc[idx] += buy_qty
                    cash.loc[idx] -= (notional + fee)
                else:
                    pos.loc[idx] = pos.loc[prev_idx]
                    cash.loc[idx] = cash.loc[prev_idx]
    
    mask = pos.eq(0)
    trades = fills_df.loc[~mask]
            
    equitiy = cash + pos * close.reindex(index).astype(float)
    return LedgerResult(equity=equitiy, cash=cash, position_qty= pos, trades=trades)