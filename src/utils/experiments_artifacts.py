from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

from src.types import ConfigLike, FrameLike

@dataclass(frozen = True)
class ExperimentRun:
    run_id: str
    run_dir: Path

def _config_hash(cfg: ConfigLike)-> str:
    
    payload = json.dumps(cfg, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
def start_experiment_run(
    cfg:ConfigLike,
    pipeline_name: str,
    model_name: str
)-> ExperimentRun|None:
    
    experiments_cfg = cfg["training"].get("experiments",{})
    if not experiments_cfg.get("enabled", False):
        return None
    
    output_dir = Path(experiments_cfg.get("output_dir", "artifacts/experiments"))
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    config_hash = _config_hash(cfg)
    short_id = config_hash[:8]# short_id: first 8 chars of sha256 hexdigest (vs full 64)
    run_id = f"{ts}_{pipeline_name}_{model_name}_{short_id}"

    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "pipeline": pipeline_name,
        "model_name": model_name,
        "random_seed": cfg.get("training", {}).get("random_seed"),
        "config_hash": _config_hash(cfg),
    }

    with open(run_dir / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    with open(run_dir / "config_snapshot.json", "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)

    return ExperimentRun(run_id=run_id, run_dir=run_dir)


def save_experiment_artifacts(
    run: ExperimentRun | None,
    model_path: Path,
    metrics: dict[str, float],
    feature_frame: FrameLike,
) -> None:
    
    if run is None:
        return

    with open(run.run_dir / "metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    manifest = {
        "model_artifact_path": str(model_path),
        "n_rows": int(len(feature_frame)),
        "n_features": int(feature_frame.shape[1]),
        "columns": feature_frame.columns.tolist(),
    }

    with open(run.run_dir / "manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    feature_frame.head(200).to_csv(run.run_dir / "feature_sample.csv", index=False)