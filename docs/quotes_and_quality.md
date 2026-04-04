# Quotes and data quality gates

This document covers the **real-time quote ingestion path** used by simulation, paper trading, and live broker pipelines.

## Components

### Quote collection
- Pipeline: `run_collect_quotes_pipeline(cfg)` (`src/pipelines/collect_quotes_pipeline.py`)
- Worker: `collect_quotes(cfg)` (`src/data/quotes/collect_quotes.py`)
- Provider client: `BitsoClient` (`src/data/providers/bitso_client.py`)
- Storage: `QuoteStore` (`src/data/quotes/quotes_store.py`)

Current mode:
- `ticker_rest`: polls best bid/ask from Bitso and flushes snapshots in chunks.

### Quote schema
Collected snapshots are persisted with a stable schema:
- `ts_exchange` (UTC timestamp)
- `book` (e.g., `btc_usd`)
- `bid`
- `ask`
- `mid`
- `source`

Downstream consumers (`quotes_resolver`, realtime simulation, quality gates) assume these columns exist.

## Collection behavior

`collect_quotes` reads from `cfg["quotes"]` and `cfg["client"]`:
- `book`
- `mode`
- `poll_interval_s`
- `flush_every_n`
- `out_dir`

Behavior summary:
1. Initialize `CollectQuotesConfig`.
2. Poll quote provider for best bid/ask.
3. Buffer snapshots in memory.
4. Flush chunk to parquet/partitioned storage when buffer reaches `flush_every_n`.

## Quality gates

Quality validation runs through `validate_quote_quality(quotes_df, cfg, now_utc=None)` in `src/data/quotes/quality_gates.py`.

### Checks performed
1. **Schema drift**: required columns must exist.
2. **Minimum rows**: enough history for downstream calculations.
3. **Timestamp validity**: `ts_exchange` must parse to UTC datetimes.
4. **Numeric integrity**: `bid`, `ask`, `mid` must be numeric and non-null.
5. **Market consistency**: `ask > bid`, `mid > 0`.
6. **Staleness guard**: latest quote age must be below `max_staleness_seconds`.
7. **Spread spike guard**: `(ask - bid) / mid` must be below `max_relative_spread`.

These checks fail fast with explicit errors so execution pipelines can fail-closed safely.

## Config example

```yaml
quote_quality:
  min_rows: 30
  max_staleness_seconds: 8
  max_relative_spread: 0.01
```

## Troubleshooting quick guide

- `missing required columns`: inspect collector schema changes and file compatibility.
- `stale latest quote`: collector is not running or polling too slowly.
- `spread spike detected`: temporary market dislocation or provider anomaly; hold trading until normalized.
- `insufficient quote rows`: increase warm-up collection window before inference.