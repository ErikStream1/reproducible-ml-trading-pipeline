# Alpha research and composite signal layer

## Core signal set

`build_core_signals(...)` creates four normalized signals and a weighted composite:

- `trend_signal`: MA crossover strength using `MA_7` and `MA_30`.
- `mean_reversion_signal`: negative short return (`-Return_1`).
- `volatility_adjusted_signal`: return scaled by realized volatility.
- `ma_spread_signal`: MA spread normalized by `Close`.
- `composite_signal`: weighted sum of the four core signals.

## Pipeline

Use `run_signal_research_pipeline(cfg)` to:

1. Run data + feature pipelines.
2. Build core signals and `composite_signal`.
3. Compute forward return labels.
4. Evaluate directional accuracy and information coefficient.
5. Persist artifacts:
   - `artifacts/alpha_research/signal_report.json`
   - `artifacts/alpha_research/signal_frame.csv`

## Configuration

Enable/tune this layer with `configs/alpha_research.yaml`:

- Feature column mapping for MA/return/volatility inputs.
- Normalization parameters (`trend_scale`, `mean_reversion_scale`).
- Signal weights for composite construction.
- Artifact paths for reproducible signal studies.