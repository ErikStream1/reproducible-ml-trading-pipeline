from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
import pandas as pd
import pytest
import joblib

from src.data import QuoteSeries
from src.pipelines import run_realtime_simulation_step

@dataclass
class DummyModel:
    features: list[str]
    def predict(self, X: pd.DataFrame):
        return [0.001] * (len(X) - 1) + [0.01]
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"features": self.features}, path)

    @classmethod
    def load(cls, path: Path) -> "DummyModel":
        payload = joblib.load(path)
        return cls(features=payload["features"])

def _base_cfg(tmp_path: Path) -> dict:
    return {
        "quotes": {
            "out_dir": str(tmp_path / "quotes"),
            "book": "btc_usd",
        },
        "data": {
            "schema": {
                "target_column": "LogReturn"
                },
            "paths": {},
        },
        "features": {
            "base_column": "Close",
            "drop_columns": ["Date", "Return_1"],
            "returns": {
                "pct_change": {
                    "enabled": True, 
                    "periods": [1],
                    "name_prefix": "Return"
                    },
                "log_diff": {
                    "enabled": True,
                    "name": "LogReturn"
                    },
                "moving_average": {
                    "enabled": False
                    },
                "volatility": {
                    "enabled": False
                    },
                "momentum": {
                    "enabled": False
                    },
            },
        },
        "inference": {
            "artifacts": {
                "model_path": str(tmp_path/"models"/"dummy_model.joblib")
                }
            },
        "strategy": {
            "side_mode": "long_only",
            "enter_threshold": 0.002,
            "exit_threshold": 0.0,
            "cooldown_bars": 0,
            "volatility_filter": {"enabled": False, "max_vol": 0.2},
        },
        "realtime_simulation": {
            "min_history_rows": 4,
            "artifacts": {
                "output_dir": str(tmp_path / "artifacts"),
                "step_filename": "last_step.json",
                "history_filename": "steps.csv",
            },
        },
    }


def test_run_realtime_simulation_step_generates_latest_action(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _base_cfg(tmp_path)
    quotes_cfg = cfg["quotes"]
    quotes_out_dir = Path(quotes_cfg["out_dir"])
    model_path_ = Path(cfg["inference"]["artifacts"]["model_path"])
    quotes_df = pd.DataFrame(
        {
            "ts_exchange": pd.date_range("2024-01-01", periods=6, freq="min", tz="UTC"),
            "bid": [100, 101, 102, 103, 104, 105],
            "ask": [101, 102, 103, 104, 105, 106],
            "mid": [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
        }
    )
    
    
    dummy_model = DummyModel(
        features= ["bid","ask","Close"],
    )
    model_path_.parent.mkdir(parents=True, exist_ok=True)

    dummy_model.save(model_path_)
    
    book = quotes_cfg["book"]
    date = "2000-01-01"
    data_now = date + "000000"
    
    part_dir = f"{quotes_out_dir}/book={book}/date={date}"
    part_dir = Path(part_dir)    
    part_dir.mkdir(parents = True, exist_ok = True)
    
    fname = f"quotes_{data_now}.parquet"
    output_path = part_dir / fname
    
    quotes_df = quotes_df.reset_index(drop = True)
        
    pd.DataFrame.to_parquet(quotes_df, path=output_path, index = False)

    monkeypatch.setattr(
        "src.data.quotes.quotes_resolver.load_quotes",
        lambda quotes_out_dir, book: QuoteSeries(df=quotes_df),
    )
    monkeypatch.setattr(
        "src.pipelines.realtime_simulation_pipeline._load_model",
        lambda model_path: DummyModel.load(path = model_path_),
    )

    result = run_realtime_simulation_step(cfg)

    assert result.target_position == 1
    assert result.action == "BUY"
    assert result.predicted_return == pytest.approx(0.01)
    assert (tmp_path / "artifacts" / "last_step.json").exists()
    assert (tmp_path / "artifacts" / "steps.csv").exists()


def test_run_realtime_simulation_step_raises_for_short_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _base_cfg(tmp_path)
    quotes_cfg = cfg["quotes"]
    quotes_out_dir = Path(quotes_cfg["out_dir"])
    cfg["realtime_simulation"]["min_history_rows"] = 10

    quotes_df = pd.DataFrame(
        {
            "ts_exchange": pd.date_range("2024-01-01", periods=3, freq="min", tz="UTC"),
            "bid": [100, 101, 102],
            "ask": [101, 102, 103],
            "mid": [100.5, 101.5, 102.5],
        }
    )
    book = quotes_cfg["book"]
    date = "2000-01-01"
    data_now = date + "000000"
    
    part_dir = f"{quotes_out_dir}/book={book}/date={date}"
    part_dir = Path(part_dir)    
    part_dir.mkdir(parents = True, exist_ok = True)
    
    fname = f"quotes_{data_now}.parquet"
    output_path = part_dir / fname
    
    quotes_df = quotes_df.reset_index(drop = True)
        
    pd.DataFrame.to_parquet(quotes_df, path=output_path, index = False)
    monkeypatch.setattr(
        "src.data.quotes.quotes_resolver.load_quotes",
        lambda out_dir, book: QuoteSeries(df=quotes_df),
    )

    with pytest.raises(ValueError, match="Not enough quotes"):
        run_realtime_simulation_step(cfg)