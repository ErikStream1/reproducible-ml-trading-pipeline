from __future__ import annotations

import json
from pathlib import Path

from src.execution.incident_artifacts import persist_incident_replay_bundle


def test_persist_incident_replay_bundle_is_deterministic(tmp_path: Path) -> None:
    cfg = {
        "execution": {"circuit_breakers": {"enabled": True, "fail_closed": True}},
        "incident_artifacts": {"output_dir": str(tmp_path / "incidents")},
    }

    exc = RuntimeError("boom")
    first = persist_incident_replay_bundle(
        cfg=cfg,
        pipeline="paper_trading",
        exc=exc,
        context={"previous_position": 0},
    )
    second = persist_incident_replay_bundle(
        cfg=cfg,
        pipeline="paper_trading",
        exc=exc,
        context={"previous_position": 1},
    )

    assert first.incident_id == second.incident_id
    assert first.error_code == "INC-PAPER-001"

    bundle = Path(first.output_dir)
    assert (bundle / "manifest.json").exists()
    assert (bundle / "config_snapshot.json").exists()
    assert (bundle / "context.json").exists()
    assert (bundle / "traceback.txt").exists()
    assert (bundle / "replay_instructions.md").exists()

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pipeline"] == "paper_trading"
    assert manifest["error_code"] == "INC-PAPER-001"