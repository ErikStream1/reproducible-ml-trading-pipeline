from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Any

from src.strategy import threshold_signal
from src.execution import simulate_fills_from_target_position
from src.backtest import run_ledger, LedgerResult, metrics

@dataclass
class BacktestReport:
    ledger: LedgerResult
    ret: pd.Series
    summary: dict
    
def run_backtest_threshold(
    pred_return: pd.Series,
    market: pd.DataFrame, #at least close and bid/ask or mid.
    cfg: dict[str, Any],
    volatility: pd.Series|None = None,
)->BacktestReport:
    
    target_pos = threshold_signal(pred_return=pred_return, cfg=cfg,volatility=volatility)
    
    fills = simulate_fills_from_target_position(cfg = cfg, 
                                                target_position=target_pos,
                                                price_frame=market,
                                                volatility=volatility
                                                )
    
    ledger = run_ledger(cfg, index = market.index, close=market["Close"], fills=fills,)
    ret = metrics.returns_from_equity(ledger.equity)
    
    summary = {
        "final_equity": ledger.equity.iloc[-1],
        "total_return": ledger.equity.iloc[-1] / ledger.equity.iloc[0] - 1.0,
        "max_drawdown": metrics.max_drawdown(ledger.equity),
        "sharpe": metrics.sharpe_ratio(ledger.equity),
        "turnover": metrics.turnover_from_position(ledger.position_qty),
        "n_trades": int(len(ledger.trades)) if hasattr(ledger, "trades") else 0,
    }
    
    return BacktestReport(ledger=ledger, ret = ret,summary = summary)

