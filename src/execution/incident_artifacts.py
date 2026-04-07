from __future__ import annotations

import hashlib
import json
import traceback
from pathlib import Path
from typing import Any

import pandas as pd
from src.execution import IncidentCode, IncidentArtifactResult

from src.types import ConfigLike

_CODE_REGISTRY: dict[str, IncidentCode] = {
    "paper_trading": IncidentCode(
        code="INC-PAPER-001",
        category="runtime_pipeline_failure",
        description="Paper trading pipeline failed and switched to fail-closed HOLD.",
    ),
    "execution_shadow": IncidentCode(
        code="INC-SHADOW-001",
        category="runtime_pipeline_failure",
        description="Shadow execution pipeline failed and switched to fail-closed HOLD.",
    ),
    "live_broker": IncidentCode(
        code="INC-LIVE-001",
        category="runtime_pipeline_failure",
        description="Live broker pipeline failed and switched to fail-closed HOLD.",
    ),
}


_DEFAULT_INCIDENT_CODE = IncidentCode(
    code="INC-GENERIC-001",
    category="runtime_pipeline_failure",
    description="Unhandled runtime pipeline failure.",
)


def incident_code_for_pipeline(pipeline: str) -> IncidentCode:
    return _CODE_REGISTRY.get(pipeline, _DEFAULT_INCIDENT_CODE)


def _incident_output_root(cfg: ConfigLike) -> Path:
    incident_cfg = cfg.get("incident_artifacts", {})
    output_dir = incident_cfg.get("output_dir", "artifacts/incidents")
    return Path(str(output_dir))


def _stable_config_hash(cfg: ConfigLike) -> str:
    normalized = json.dumps(cfg, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _incident_id(*, pipeline: str, code: str, exc_type: str, config_hash: str) -> str:
    fingerprint = f"{pipeline}|{code}|{exc_type}|{config_hash}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]


def persist_incident_replay_bundle(
    *,
    cfg: ConfigLike,
    pipeline: str,
    exc: Exception,
    context: dict[str, Any] | None = None,
) -> IncidentArtifactResult:
    code = incident_code_for_pipeline(pipeline)
    config_hash = _stable_config_hash(cfg)
    incident_id = _incident_id(
        pipeline=pipeline,
        code=code.code,
        exc_type=type(exc).__name__,
        config_hash=config_hash,
    )

    root = _incident_output_root(cfg)
    output_dir = root / incident_id
    output_dir.mkdir(parents=True, exist_ok=True)

    replay_manifest = {
        "incident_id": incident_id,
        "pipeline": pipeline,
        "error_code": code.code,
        "error_category": code.category,
        "error_description": code.description,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "opened_at": pd.Timestamp.now("UTC").isoformat(),
        "config_hash": config_hash,
        "bundle_version": "v1",
        "files": [
            "manifest.json",
            "config_snapshot.json",
            "context.json",
            "traceback.txt",
            "replay_instructions.md",
        ],
    }

    replay_instructions = (
        "# Replay instructions\n\n"
        "1. Load `config_snapshot.json` as the run configuration.\n"
        "2. Re-run the pipeline stored in `manifest.json` under `pipeline`.\n"
        "3. Use `context.json` and `traceback.txt` to reproduce failure conditions.\n"
        "4. Validate that the same `error_code` is emitted in fail-closed mode.\n"
    )

    (output_dir / "manifest.json").write_text(
        json.dumps(replay_manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "config_snapshot.json").write_text(
        json.dumps(cfg, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    (output_dir / "context.json").write_text(
        json.dumps(context or {}, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    (output_dir / "traceback.txt").write_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        encoding="utf-8",
    )
    (output_dir / "replay_instructions.md").write_text(replay_instructions, encoding="utf-8")

    return IncidentArtifactResult(
        incident_id=incident_id,
        error_code=code.code,
        output_dir=str(output_dir),
    )