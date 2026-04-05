# Runtime safety controls

This document centralizes the safety controls that protect execution-time behavior.

## Scope

Safety controls span three layers:
1. **Data quality gates** (quote freshness/schema/spread sanity)
2. **Pre-trade risk limits** (position/notional/trade-rate constraints)
3. **Circuit breakers** (global fail-closed state when critical errors occur)

## Pre-trade risk limits

Implemented in `src/execution/risk_limits.py`.

Typical controls:
- max absolute position
- max daily traded notional
- max trades per hour
- optional cooldown overrides

Expected behavior:
- evaluate candidate action before fill simulation or order submission
- reject/convert action to `HOLD` when a hard limit is breached
- provide rejection reason for auditability

## Circuit breakers

Implemented in `src/execution/circuit_breakers.py`.

### Decision state
`evaluate_circuit_breaker(cfg)` reads circuit breaker configuration and persisted state:
- `enabled`
- `fail_closed`
- `is_open`
- `state_path`

If enabled and open, execution pipelines should avoid sending orders and switch to safe behavior.

### Failure recording
`record_circuit_breaker_failure(cfg, pipeline, exc)` writes a state file containing:
- open/closed status
- pipeline name
- exception type and message
- UTC open timestamp

### Clearing state
`clear_circuit_breaker(cfg)` removes persisted open state and re-enables normal flow.

## Fail-closed policy

When `fail_closed: true`:
- any critical runtime error should produce a deterministic hold/no-op behavior,
- live order submission is blocked,
- artifacts should still capture the error context for replay.

## Recommended operational workflow

1. Keep circuit breakers enabled in live environments.
2. Start with strict risk limits and relax only after observing stable behavior.
3. Persist and review artifacts (`paper_trading`, `execution_shadow`, logs) after each run.
4. Clear breaker state only after root-cause verification.

## Minimal config example

```yaml
execution:
  risk_limits:
    max_abs_position: 1
    max_notional_per_day: 2000
    max_trades_per_hour: 10
  circuit_breakers:
    enabled: true
    fail_closed: true
    state_path: artifacts/paper_trading/circuit_breaker_state.json
```

## Shadow-vs-live divergence monitor

Implemented in `src/execution/divergence_monitor.py` and exposed via `run_shadow_live_divergence_monitor_pipeline(...)`.

It compares expected (shadow) vs actual (live) fills and raises an alert when any configured threshold is breached:
- fill-count divergence
- notional divergence (%)
- average fill-price divergence (bps)
- fee divergence (bps)

Recommended usage:
1. Persist shadow fills from end-to-end execution (`artifacts/execution_shadow/fills.csv`).
2. Persist/export live fills to `artifacts/live_broker/fills.csv` with at least `qty` and `price` columns (optional `fee`).
3. Run the divergence monitor after each live execution batch and review alert artifacts.
