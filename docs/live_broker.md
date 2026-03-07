# Live broker integration (Bitso API)

This milestone adds a **live execution bridge** for Bitso using authenticated private API calls.

The implementation is intentionally conservative:

- uses the existing real-time simulation step for decisioning,
- computes net delta vs current position state,
- supports a safe default `dry_run` mode,
- submits market orders only when explicitly enabled.

---

## Pipeline

**Function:** `run_live_broker_pipeline(cfg, collect_quotes_first=None)`

**File:** `src/pipelines/live_broker_pipeline.py`

### Flow

1. Optionally collect latest quotes (`live_broker.collect_quotes_first`).
2. Compute latest action/target position with `run_realtime_simulation_step`.
3. Read previous position from paper-trading state storage.
4. Compute net order size: `target_position - previous_position`.
5. If no position change is required, return `status="noop"`.
6. If `live_broker.dry_run=true`, return planned order payload without sending.
7. Otherwise submit a Bitso market order via authenticated private endpoint `POST /orders/`.

---

## Configuration

Use `configs/live_broker.yaml`:

```yaml
live_broker:
  collect_quotes_first: true
  dry_run: true
  client:
    base_url: "https://api.bitso.com/v3"
    timeout_s: 10.0
```

```yaml
local_live_broker:
  api_key: "<your-api-key>"
  api_secret: "<your-api-secret>"
```

Notes:

- `dry_run` defaults to safe behavior (no order is sent).
- This project does not auto-resolve env placeholders inside YAML; provide real values at runtime or load from an ignored local config file.
- Order quantity in base units is computed as `abs(net_target) * execution.qty`.

---

## Return value

Pipeline returns `LiveBrokerOrderResult` with:

- simulation metadata (`timestamp`, `action`, `target_position`, `previous_position`),
- order intent (`side`, `major`),
- execution outcome (`order_sent`, `order_id`, `status`),
- raw response payload for traceability.

---

## Safety recommendations

- Keep `dry_run=true` until you validate signals and quantity logic.
- Start with minimal `execution.qty`.
- Restrict API key permissions to trading only what is required.
- Run first against low-risk books/notional and inspect payloads before scaling.