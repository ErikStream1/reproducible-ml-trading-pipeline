# Incident runbook artifacts

This milestone adds **runbook-style incident artifacts** for fail-closed runtime errors.

## Structured error codes

Every fail-closed runtime pipeline now emits a deterministic error code family:

- `INC-PAPER-001` for `paper_trading`
- `INC-SHADOW-001` for `execution_shadow`
- `INC-LIVE-001` for `live_broker`
- `INC-GENERIC-001` fallback for unknown pipelines

The codes are persisted in circuit-breaker state and returned in pipeline error payloads.

## Deterministic replay bundle

When a runtime exception opens the circuit breaker, the pipeline writes a replay bundle under:

`artifacts/incidents/<incident_id>/`

Where `incident_id` is deterministic from:
- pipeline id
- structured error code
- exception type
- normalized config hash

Bundle contents:
- `manifest.json` (error code, category, bundle version, config hash)
- `config_snapshot.json` (exact config used)
- `context.json` (runtime context such as previous position)
- `traceback.txt` (captured stack trace)
- `replay_instructions.md` (step-by-step reproduction guide)

## Manual bundle generation (Python API)

Use `persist_incident_replay_bundle(...)` directly when you need to create a bundle outside the runtime loop.

Example:

```python
from src.execution import persist_incident_replay_bundle

cfg = {
    "execution": {"circuit_breakers": {"enabled": True, "fail_closed": True}},
    "incident_artifacts": {"output_dir": "artifacts/incidents"},
}

try:
    raise ValueError("quotes missing")
except Exception as exc:
    result = persist_incident_replay_bundle(
        cfg=cfg,
        pipeline="paper_trading",
        exc=exc,
        context={"previous_position": 0},
    )
    print(result.output_dir)
```

## Operational workflow

1. Detect fail-closed result in pipeline response/logs.
2. Read circuit breaker state (`execution.circuit_breakers.state_path`) for `error_code` and `incident_bundle_path`.
3. Open the replay bundle directory and inspect `manifest.json` + `traceback.txt`.
4. Replay with `config_snapshot.json` and validate the same error code is emitted.
5. Clear breaker state only after mitigation is verified.