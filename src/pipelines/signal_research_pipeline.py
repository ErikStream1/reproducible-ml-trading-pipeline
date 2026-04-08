from __future__ import annotations

import json
from pathlib import Path

from src.evaluation import directional_accuracy
from src.pipelines import run_data_pipeline, run_feature_pipeline
from src.strategy.composite_signals import build_core_signals
from src.types import ConfigLike


def run_signal_research_pipeline(cfg: ConfigLike) -> dict[str, float]:
    
    raw = run_data_pipeline(cfg)
    feat = run_feature_pipeline(raw, cfg)
    signal_frame = build_core_signals(cfg, feat)

    target_col = cfg["data"]["schema"].get("target_column", "LogReturn")
    alpha_cfg = cfg.get("alpha_research", {})
    fwd_horizon = int(alpha_cfg.get("forward_horizon", 1))

    if target_col not in signal_frame.columns:
        raise ValueError(f"Target column '{target_col}' not found for signal research")

    signal_frame["forward_return"] = signal_frame[target_col].shift(-fwd_horizon)
    eval_df = signal_frame[["composite_signal", "forward_return"]].dropna().copy()

    if eval_df.empty:
        raise ValueError("Signal evaluation frame is empty after dropna")

    summary = {
        "rows_evaluated": float(len(eval_df)),
        "composite_mean": float(eval_df["composite_signal"].mean()),
        "composite_std": float(eval_df["composite_signal"].std(ddof=0)),
        "directional_accuracy": float(
            directional_accuracy(eval_df["forward_return"], eval_df["composite_signal"])
        ),
        "information_coefficient": float(
            eval_df["composite_signal"].corr(eval_df["forward_return"], method="spearman")
        ),
    }

    artifacts_cfg = alpha_cfg.get("artifacts", {})
    report_path = Path(artifacts_cfg.get("signal_report_path", "artifacts/alpha_research/signal_report.json"))
    frame_path = Path(artifacts_cfg.get("signal_frame_path", "artifacts/alpha_research/signal_frame.csv"))

    report_path.parent.mkdir(parents=True, exist_ok=True)
    frame_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    signal_frame.to_csv(frame_path, index=False)

    return summary