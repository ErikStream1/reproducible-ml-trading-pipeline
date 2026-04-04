# Strategy

This document describes the **strategy layer**: how trading signals are produced from model
predictions (and optional filters), and how desired exposure/size intent is defined.

## Purpose
- Convert model predictions into trade decisions (signals).
- Apply optional risk filters (e.g., volatility filter, cooldown).
- Produce sizing intent (qty/notional constraints) consumed by execution/backtest.

## Signal generation (conceptual)

### Threshold signal
Common rule:

- Enter long if pred_return > enter_threshold

- Exit/flat if pred_return < exit_threshold

## Filters

### Model confidence gate
If enabled, entries are blocked unless confidence is above `threshold`.

- Default confidence source is `abs(pred_return)` when no explicit confidence score is provided.
- Failing the gate forces target position to `0` (`HOLD`).

### Cooldown
After an action (enter/exit), strategy may enforce `cooldown_bars` where new entries are blocked.

### Volatility filter
If enabled:

- Entries are blocked when volatility exceeds `max_vol`.

### Sizing intent
The strategy defines “how big” positions should be:

- typically via `target_notional` (quote currency) and constraints (`min_qty`, `max_notional`).

<strong>Strategy does not execute trades</strong>; it only emits intent consumed by the execution/backtest layer.

### Common pitfalls
- Unit ambiguity: thresholds and volatility are decimals, not percentages.

- `cooldown_bars` is measured in bars/rows, so changing bar frequency changes behavior.

- Ensure sizing currency matches the book quote currency.