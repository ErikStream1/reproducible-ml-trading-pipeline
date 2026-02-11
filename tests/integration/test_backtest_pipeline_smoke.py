from __future__ import annotations

from pathlib import Path

from src.models import LinearModel
from src.pipelines.backtest_pipeline import run_backtest_pipeline
from src.types import ConfigLike
from src.utils import make_fake_ohlcv

def test_backtest_pipeline_smoke_with_artifacts(tmp_path: Path, monkeypatch) -> None:
    cfg: ConfigLike = {
        "data": {
            "schema": {
                "target_column": "LogReturn"
                }
            },
        "inference": {
            "artifacts": {
                "model_path": tmp_path / "linear_model.joblib"
                }
            },
        "strategy": {
            "side_mode": "long_only",
            "enter_threshold": 95.0,
            "exit_threshold": 96.0,
            "cooldown_bars": 2,
            "volatility_filter": {"enabled": False},
        },
        "execution": {
            "fill_mode": "next_close",
            "qty": 1.0,
            "fees": {
                "rate": 0.001
                },
            "slippage": {
                "bps": 0.0, 
                "vol_k": 0.0
                },
        },
        "backtest": {
            "initial_cash": 100_000,
            "periods_per_year": 365,
            "artifacts": {
                "output_dir": tmp_path / "artifacts/backtest",
                "summary_filename": "summary.json",
                "equity_filename": "equity.csv",
                "trades_filename": "trades.csv",
            },
        },
    }

    df = make_fake_ohlcv(with_features=True)
    df = df.drop(columns = "Date")

    monkeypatch.setattr("src.pipelines.backtest_pipeline.run_data_pipeline", lambda _cfg: df.copy())
    monkeypatch.setattr("src.pipelines.backtest_pipeline.run_feature_pipeline", lambda in_df, _cfg: in_df.copy())

    model = LinearModel(alpha=1.0)
    
    target = cfg["data"]["schema"]["target_column"]    
    columns = [col for col in df.columns if col != target ]
    
    X = df[columns]
    y = df[target]
    
    model.fit(X, y)
    model.save(cfg["inference"]["artifacts"]["model_path"])

    report = run_backtest_pipeline(cfg=cfg)

    assert "final_equity" in report.summary
    assert len(report.ledger.equity) == len(df)

    output_dir = cfg["backtest"]["artifacts"]["output_dir"]
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "equity.csv").exists()
    assert (output_dir / "trades.csv").exists()