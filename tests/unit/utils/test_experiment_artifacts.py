from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.utils import (
    save_experiment_artifacts,
    start_experiment_run,
)


def test_start_experiment_run_disabled_returns_none(tmp_path: Path) -> None:
    cfg = {"training": {"experiments": {"enabled": False}}}

    run = start_experiment_run(cfg, pipeline_name="training", model_name="linear")

    assert run is None


def test_save_experiment_artifacts_creates_bundle(tmp_path: Path) -> None:
    cfg = {
        "training": {
            "random_seed": 42,
            "experiments": {
                "enabled": True,
                "output_dir": str(tmp_path / "experiments"),
            },
        }
    }

    run = start_experiment_run(cfg, pipeline_name="training", model_name="linear")
    assert run is not None

    frame = pd.DataFrame({"f1": [1.0, 2.0], "f2": [3.0, 4.0]})
    save_experiment_artifacts(
        run=run,
        model_path=tmp_path / "models" / "linear.joblib",
        metrics={"rmse": 0.1, "mae": 0.2, "directional_accuracy": 0.5},
        feature_frame=frame,
    )

    assert (run.run_dir / "metadata.json").exists()
    assert (run.run_dir / "config_snapshot.json").exists()
    assert (run.run_dir / "metrics.json").exists()
    assert (run.run_dir / "manifest.json").exists()
    assert (run.run_dir / "feature_sample.csv").exists()

    metrics = json.loads((run.run_dir / "metrics.json").read_text())
    assert metrics["rmse"] == 0.1