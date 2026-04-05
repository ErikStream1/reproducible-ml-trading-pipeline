from __future__ import annotations
from pathlib import Path
from src.utils import read
import json
from dataclasses import asdict
from src.execution import FillAggregate, DivergenceMetrics, DivergenceMonitorResult
from src.types import ConfigLike, FrameLike


def _safe_div(num: float, den: float) -> float:
    return 0.0 if den == 0 else float(num) / float(den)


def _read_fills_csv(path: Path) -> FrameLike:
    if not path.exists():
        raise FileNotFoundError(f"Fills file not found: {path}")

    fills = read(path)
    if fills is None:
        raise ValueError("Fills file is None")
    
    required = {"qty", "price"}
    missing = required.difference(fills.columns)
    if missing:
        raise ValueError(f"Fills file is missing required columns {sorted(missing)}: {path}")

    if "fee" not in fills.columns:
        fills["fee"] = 0.0

    return fills


def _aggregate_fills(fills: FrameLike) -> FillAggregate:
    if fills.empty:
        return FillAggregate(
            fills_count=0,
            notional=0.0,
            avg_fill_price=0.0,
            fee_paid=0.0,
            fee_bps=0.0,
        )

    notional = float((fills["qty"].abs() * fills["price"]).sum())
    qty_total = float(fills["qty"].abs().sum())
    avg_fill_price = _safe_div(notional, qty_total)
    fee_paid = float(fills["fee"].sum())
    fee_bps = 10_000.0 * _safe_div(fee_paid, notional)

    return FillAggregate(
        fills_count=int(len(fills)),
        notional=notional,
        avg_fill_price=avg_fill_price,
        fee_paid=fee_paid,
        fee_bps=fee_bps,
    )


def evaluate_shadow_live_divergence(
    cfg: ConfigLike,
    expected_fills_path: str | Path | None = None,
    actual_fills_path: str | Path | None = None,
) -> DivergenceMonitorResult:
    monitor_cfg = cfg.get("divergence_monitor", {})
    input_cfg = monitor_cfg.get("inputs", {})

    expected_path = Path(expected_fills_path or input_cfg.get("expected_fills_path", "artifacts/execution_shadow/fills.csv"))
    actual_path = Path(actual_fills_path or input_cfg.get("actual_fills_path", "artifacts/live_broker/fills.csv"))

    expected_df = _read_fills_csv(expected_path)
    actual_df = _read_fills_csv(actual_path)

    expected_agg = _aggregate_fills(expected_df)
    actual_agg = _aggregate_fills(actual_df)

    metrics = DivergenceMetrics(
        fill_count_abs_diff=abs(actual_agg.fills_count - expected_agg.fills_count),
        notional_pct_diff=abs(_safe_div(actual_agg.notional - expected_agg.notional, expected_agg.notional)),
        avg_fill_price_bps_diff=10_000.0
        * abs(_safe_div(actual_agg.avg_fill_price - expected_agg.avg_fill_price, expected_agg.avg_fill_price)),
        fee_bps_diff=abs(actual_agg.fee_bps - expected_agg.fee_bps),
    )

    thresholds = monitor_cfg.get("thresholds", {})
    reasons: list[str] = []

    max_fill_count_diff = int(thresholds.get("max_fill_count_diff", 1))
    max_notional_pct_diff = float(thresholds.get("max_notional_pct_diff", 0.20))
    max_avg_fill_price_bps_diff = float(thresholds.get("max_avg_fill_price_bps_diff", 20.0))
    max_fee_bps_diff = float(thresholds.get("max_fee_bps_diff", 10.0))

    if metrics.fill_count_abs_diff > max_fill_count_diff:
        reasons.append(
            f"fill_count_abs_diff={metrics.fill_count_abs_diff} > max_fill_count_diff={max_fill_count_diff}"
        )
    if metrics.notional_pct_diff > max_notional_pct_diff:
        reasons.append(
            f"notional_pct_diff={metrics.notional_pct_diff:.6f} > max_notional_pct_diff={max_notional_pct_diff:.6f}"
        )
    if metrics.avg_fill_price_bps_diff > max_avg_fill_price_bps_diff:
        reasons.append(
            "avg_fill_price_bps_diff="
            f"{metrics.avg_fill_price_bps_diff:.4f} > max_avg_fill_price_bps_diff={max_avg_fill_price_bps_diff:.4f}"
        )
    if metrics.fee_bps_diff > max_fee_bps_diff:
        reasons.append(f"fee_bps_diff={metrics.fee_bps_diff:.4f} > max_fee_bps_diff={max_fee_bps_diff:.4f}")

    result = DivergenceMonitorResult(
        alert_triggered=bool(reasons),
        reasons=tuple(reasons),
        expected=expected_agg,
        actual=actual_agg,
        metrics=metrics,
        expected_path=str(expected_path),
        actual_path=str(actual_path),
        output_path=None,
    )

    artifacts_cfg = monitor_cfg.get("artifacts", {})
    output_dir = artifacts_cfg.get("output_dir")
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        report_filename = artifacts_cfg.get("report_filename", "divergence_report.json")
        alert_filename = artifacts_cfg.get("alert_filename", "divergence_alert.json")

        report_payload = {
            "alert_triggered": result.alert_triggered,
            "reasons": list(result.reasons),
            "expected_path": result.expected_path,
            "actual_path": result.actual_path,
            "expected": asdict(result.expected),
            "actual": asdict(result.actual),
            "metrics": asdict(result.metrics),
        }
        (output_path / report_filename).write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

        alert_payload = {
            "status": "alert" if result.alert_triggered else "ok",
            "reasons": list(result.reasons),
        }
        (output_path / alert_filename).write_text(json.dumps(alert_payload, indent=2), encoding="utf-8")

        result = DivergenceMonitorResult(
            alert_triggered=result.alert_triggered,
            reasons=result.reasons,
            expected=result.expected,
            actual=result.actual,
            metrics=result.metrics,
            expected_path=result.expected_path,
            actual_path=result.actual_path,
            output_path=str(output_path),
        )

    return result