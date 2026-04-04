from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import pandas as pd
import pytest
import joblib
from src.types import FrameLike
from src.data import QuoteSeries
from src.pipelines import run_realtime_simulation_step

@dataclass
class DummyModel:
    features: list[str]
    def predict(self, X: FrameLike):
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
        "quote_quality":{
            "enabled": True,
            "max_staleness_seconds": 60,
            "max_relative_spread": 0.05,
            "min_rows": 2
        }
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
    historic_df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "Open": [90, 91, 92, 93, 94, 95],
            "High": [91, 92, 93, 94, 95, 96],
            "Low": [89, 90, 91, 92, 93, 94],
            "Close": [90.5, 91.5, 92.5, 93.5, 94.5, 95.5],
            "Volume": [1000, 1005, 1010, 1015, 1020, 1025],
        }
    )
    
    
    dummy_model = DummyModel(
        features= ["bid","ask","Close"],
    )
    model_path_.parent.mkdir(parents=True, exist_ok=True)

    dummy_model.save(model_path_)
    
    book = quotes_cfg["book"]
    date = "2024-01-01"
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
        "src.pipelines.realtime_simulation_pipeline.run_data_pipeline",
        lambda cfg: historic_df,
    )
    
    monkeypatch.setattr(
        "src.data.quotes.quality_gates.pd.Timestamp.now",
        lambda tz: pd.Timestamp(2024,1,1, tz = "UTC")
    )
    
    monkeypatch.setattr(
        "src.pipelines.realtime_simulation_pipeline._load_model",
        lambda model_path: DummyModel.load(path = model_path_),
    )

    result = run_realtime_simulation_step(cfg)
    result_2 = run_realtime_simulation_step(cfg)

    assert result.target_position == 1
    assert result_2.target_position == 1
    assert result.action == "BUY"
    assert result.predicted_return == pytest.approx(0.01)
    assert (tmp_path / "artifacts" / "last_step.json").exists()
    assert (tmp_path / "artifacts" / "steps.csv").exists()

    history_df = pd.read_csv(tmp_path / "artifacts" / "steps.csv")
    assert len(history_df) == 1


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
    historic_df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Open": [90, 91, 92],
            "High": [91, 92, 93],
            "Low": [89, 90, 91],
            "Close": [90.5, 91.5, 92.5],
            "Volume": [1000, 1005, 1010],
        }
    )
    book = quotes_cfg["book"]
    date = "2024-01-01"
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
    monkeypatch.setattr(
        "src.pipelines.realtime_simulation_pipeline.run_data_pipeline",
        lambda cfg: historic_df,
    )
    monkeypatch.setattr(
        "src.data.quotes.quality_gates.pd.Timestamp.now",
        lambda tz: pd.Timestamp(2024,1,1, tz = "UTC")
    )
    with pytest.raises(ValueError, match="Not enough historical rows"):
        run_realtime_simulation_step(cfg)
        
def test_run_realtime_simulation_step_raises_on_stale_quotes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _base_cfg(tmp_path)
    quotes_cfg = cfg["quotes"]
    quotes_out_dir = Path(quotes_cfg["out_dir"])    
    quotes_df = pd.DataFrame(
        {
            "ts_exchange": pd.to_datetime(["2024-01-01T00:00:00Z", "2024-01-01T00:01:00Z"]),
            "bid": [100, 101],
            "ask": [101, 102],
            "mid": [100.5, 101.5],
        }
    )
    historic_df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "Open": [90, 91, 92, 93, 94, 95],
            "High": [91, 92, 93, 94, 95, 96],
            "Low": [89, 90, 91, 92, 93, 94],
            "Close": [90.5, 91.5, 92.5, 93.5, 94.5, 95.5],
            "Volume": [1000, 1005, 1010, 1015, 1020, 1025],
        }
    )
    #parcha pero no guarda
    book = quotes_cfg["book"]
    date = "2024-01-01"
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
        "src.pipelines.realtime_simulation_pipeline.run_data_pipeline",
        lambda cfg: historic_df,
    )

    with pytest.raises(ValueError, match="stale latest quote"):
        run_realtime_simulation_step(cfg)
        
def test_run_realtime_simulation_step_holds_when_confidence_gate_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg = _base_cfg(tmp_path)
    cfg["strategy"]["confidence_gate"] = {"enabled": True, "threshold": 0.02}
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
    historic_df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "Open": [90, 91, 92, 93, 94, 95],
            "High": [91, 92, 93, 94, 95, 96],
            "Low": [89, 90, 91, 92, 93, 94],
            "Close": [90.5, 91.5, 92.5, 93.5, 94.5, 95.5],
            "Volume": [1000, 1005, 1010, 1015, 1020, 1025],
        }
    )
    dummy_model = DummyModel(features=["bid", "ask", "Close"])
    model_path_.parent.mkdir(parents=True, exist_ok=True)
    dummy_model.save(model_path_)

    book = quotes_cfg["book"]
    date = "2024-01-01"
    data_now = date + "000000"
    part_dir = Path(f"{quotes_out_dir}/book={book}/date={date}")
    part_dir.mkdir(parents=True, exist_ok=True)
    output_path = part_dir / f"quotes_{data_now}.parquet"
    pd.DataFrame.to_parquet(quotes_df.reset_index(drop=True), path=output_path, index=False)

    monkeypatch.setattr(
        "src.data.quotes.quotes_resolver.load_quotes",
        lambda quotes_out_dir, book: QuoteSeries(df=quotes_df),
    )
    monkeypatch.setattr(
        "src.pipelines.realtime_simulation_pipeline.run_data_pipeline",
        lambda cfg: historic_df,
    )
    monkeypatch.setattr(
        "src.data.quotes.quality_gates.pd.Timestamp.now",
        lambda tz: pd.Timestamp(2024, 1, 1, tz="UTC"),
    )
    monkeypatch.setattr(
        "src.pipelines.realtime_simulation_pipeline._load_model",
        lambda model_path: DummyModel.load(path=model_path_),
    )

    result = run_realtime_simulation_step(cfg)

    assert result.target_position == 0
    assert result.action == "HOLD"