from __future__ import annotations
import json
from pathlib import Path

from src.types import ConfigLike
from src.backtest import BacktestReport

def _save_backtest_artifacts(cfg: ConfigLike, report: BacktestReport) -> Path|None:
    artifacts_cfg = cfg.get("backtest", {}).get("artifacts", {})

    output_dir = artifacts_cfg.get("output_dir")
    if output_dir is None:
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_filename = artifacts_cfg.get("summary_filename", "summary.json")
    equity_filename = artifacts_cfg.get("equity_filename", "equity.csv")
    trades_filename = artifacts_cfg.get("trades_filename", "trades.csv")

    summary_path = output_path / summary_filename
    equity_path = output_path / equity_filename
    trades_path = output_path / trades_filename

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(report.summary, f, indent=2)

    report.ledger.equity.to_csv(equity_path, index=True)
    report.ledger.trades.to_csv(trades_path, index=True)

    return output_path