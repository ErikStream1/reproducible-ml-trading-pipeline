from __future__ import annotations

from src.backtest.metrics import turnover_from_position
from src.types import ConfigLike, SeriesLike, FrameLike, Prediction

from src.strategy import threshold_signal
from src.execution import simulate_fills_from_target_position
from src.backtest import (run_ledger, 
                          BacktestReport,
                          returns_from_equity,
                          max_drawdown,
                          sharpe_ratio,
                          turnover_from_position
                          )

def run_backtest_threshold(
    cfg: ConfigLike,
    pred_return: Prediction,
    market: FrameLike, #at least close and bid/ask or mid.
    volatility: SeriesLike|None = None,
)->BacktestReport:
    
    target_pos = threshold_signal(pred_return=pred_return, cfg=cfg,volatility=volatility)
    
    fills = simulate_fills_from_target_position(cfg = cfg, 
                                                target_position=target_pos,
                                                price_frame=market,
                                                volatility=volatility
                                                )
    
    ledger = run_ledger(cfg, index = market.index, close=market["Close"], fills=fills,)
    ret = returns_from_equity(ledger.equity)
    
    summary = {
        "final_equity": ledger.equity.iloc[-1],
        "total_return": ledger.equity.iloc[-1] / ledger.equity.iloc[0] - 1.0,
        "max_drawdown": max_drawdown(ledger.equity),
        "sharpe": sharpe_ratio(ledger.equity),
        "turnover": turnover_from_position(ledger.position_qty),
        "n_trades": int(len(ledger.trades)) if hasattr(ledger, "trades") else 0,
    }
    
    return BacktestReport(ledger=ledger, ret = ret,summary = summary)

