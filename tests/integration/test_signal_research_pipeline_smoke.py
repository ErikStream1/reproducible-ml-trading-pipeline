from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.pipelines.signal_research_pipeline import run_signal_research_pipeline


def test_signal_research_pipeline_smoke_writes_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    cfg = {
        "data": {
            "schema": {
                "target_column": "LogReturn",
            },
        },
        "alpha_research": {
            "forward_horizon": 1,
            "signals": {
                "ma_fast_column": "MA_7",
                "ma_slow_column": "MA_30",
                "return_column": "LogReturn",
                "volatility_column": "Volatility_7",
                "close_column": "Close",
            },
            "artifacts": {
                "signal_report_path": str(tmp_path / "artifacts" / "alpha_research" / "signal_report.json"),
                "signal_frame_path": str(tmp_path / "artifacts" / "alpha_research" / "signal_frame.csv"),
            },
        },
    }

    frame = pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0, 103.0, 104.0, 103.0],
            "MA_7": [99.9, 100.7, 101.5, 102.4, 103.5, 103.2],
            "MA_30": [99.0, 99.4, 99.9, 100.4, 100.9, 101.2],
            "LogReturn": [0.0010, 0.0015, -0.0002, 0.0008, 0.0012, -0.0006],
            "Volatility_7": [0.010, 0.011, 0.012, 0.012, 0.011, 0.010],
        }
    )

    monkeypatch.setattr("src.pipelines.signal_research_pipeline.run_data_pipeline", lambda _cfg: frame.copy())
    monkeypatch.setattr("src.pipelines.signal_research_pipeline.run_feature_pipeline", lambda in_df, _cfg: in_df.copy())

    summary = run_signal_research_pipeline(cfg)

    report_path = Path(cfg["alpha_research"]["artifacts"]["signal_report_path"])
    frame_path = Path(cfg["alpha_research"]["artifacts"]["signal_frame_path"])

    assert report_path.exists()
    assert frame_path.exists()
    assert summary["rows_evaluated"] > 0

    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    assert "directional_accuracy" in loaded
    assert "information_coefficient" in loaded