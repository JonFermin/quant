"""
LightGBM strategy using QLib's Alpha158 feature set on S&P 500 stocks.

This strategy trains a LightGBM model on 158 hand-crafted alpha factors
and backtests a top-k dropout portfolio on the S&P 500 universe.

Usage:
    python -m strategies.lgbm_alpha158 --config configs/lgbm_alpha158.yaml --output-dir results/lgbm_run
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "configs", "lgbm_alpha158.yaml"
)


class ConfigValidationError(ValueError):
    """Raised when strategy config is invalid."""


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load the QLib YAML workflow config."""
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(config: Dict[str, Any]) -> None:
    """Validate required config wiring and basic date/provider sanity."""
    required_top = ["qlib_init", "task", "port_analysis_config"]
    for key in required_top:
        if key not in config:
            raise ConfigValidationError(f"Missing required top-level key: {key}")

    qlib_init = config["qlib_init"]
    provider_uri = qlib_init.get("provider_uri")
    region = qlib_init.get("region")
    if not provider_uri or not isinstance(provider_uri, str):
        raise ConfigValidationError("qlib_init.provider_uri must be a non-empty string")
    if region not in {"us", "cn"}:
        raise ConfigValidationError("qlib_init.region must be one of: us, cn")

    task = config["task"]
    if "model" not in task or "dataset" not in task:
        raise ConfigValidationError("task.model and task.dataset are required")

    dataset_kwargs = task["dataset"].get("kwargs", {})
    segments = dataset_kwargs.get("segments", {})
    for seg in ["train", "valid", "test"]:
        if seg not in segments or len(segments[seg]) != 2:
            raise ConfigValidationError(
                f"task.dataset.kwargs.segments.{seg} must contain [start, end]"
            )

    port_analysis = config["port_analysis_config"]
    if "strategy" not in port_analysis or "backtest" not in port_analysis:
        raise ConfigValidationError(
            "port_analysis_config.strategy and port_analysis_config.backtest are required"
        )


def init_qlib(provider_uri: str = "~/.qlib/qlib_data/us_data", region: str = "us") -> None:
    """Initialize QLib with selected market data."""
    import qlib
    from qlib.constant import REG_CN, REG_US

    reg_map = {"us": REG_US, "cn": REG_CN}
    qlib.init(provider_uri=provider_uri, region=reg_map[region])
    print(f"QLib initialized with region={region}")


def _apply_overrides(
    config: Dict[str, Any],
    provider_uri: Optional[str] = None,
    region: Optional[str] = None,
    test_start: Optional[str] = None,
    test_end: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply runtime overrides to config in-memory."""
    if provider_uri:
        config["qlib_init"]["provider_uri"] = provider_uri
    if region:
        config["qlib_init"]["region"] = region
    if test_start or test_end:
        test_seg = config["task"]["dataset"]["kwargs"]["segments"]["test"]
        bt = config["port_analysis_config"]["backtest"]
        test_seg[0] = test_start or test_seg[0]
        test_seg[1] = test_end or test_seg[1]
        bt["start_time"] = test_start or bt["start_time"]
        bt["end_time"] = test_end or bt["end_time"]
    return config


def _export_artifacts(
    output_dir: Optional[str],
    config: Dict[str, Any],
    ic_analysis,
    portfolio_metrics,
) -> None:
    """Write reproducible run artifacts to disk."""
    if not output_dir:
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    summary = {
        "region": config["qlib_init"]["region"],
        "provider_uri": config["qlib_init"]["provider_uri"],
        "test_segment": config["task"]["dataset"]["kwargs"]["segments"]["test"],
        "ic_mean": float(ic_analysis["IC"].mean()),
        "ic_std": float(ic_analysis["IC"].std()),
        "rank_ic_mean": float(ic_analysis["Rank IC"].mean()),
    }

    with open(out / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    ic_analysis.to_csv(out / "ic_analysis.csv")
    if hasattr(portfolio_metrics, "to_csv"):
        portfolio_metrics.to_csv(out / "portfolio_metrics.csv")

    with open(out / "effective_config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    print(f"Artifacts exported to: {out.resolve()}")


def run_backtest(
    config_path: Optional[str] = None,
    init: bool = True,
    provider_uri: Optional[str] = None,
    region: Optional[str] = None,
    test_start: Optional[str] = None,
    test_end: Optional[str] = None,
    output_dir: Optional[str] = None,
):
    """Run the full LightGBM Alpha158 backtest pipeline."""
    config = load_config(config_path)
    config = _apply_overrides(
        config,
        provider_uri=provider_uri,
        region=region,
        test_start=test_start,
        test_end=test_end,
    )
    validate_config(config)

    if init:
        init_qlib(
            provider_uri=config["qlib_init"]["provider_uri"],
            region=config["qlib_init"]["region"],
        )

    from qlib.utils import init_instance_by_config
    from qlib.workflow import R
    from qlib.workflow.record_temp import PortAnaRecord, SigAnaRecord, SignalRecord

    model = init_instance_by_config(config["task"]["model"])
    dataset = init_instance_by_config(config["task"]["dataset"])

    print("Training LightGBM model...")
    model.fit(dataset)
    print("Training complete.")

    with R.start(experiment_name="lgbm_alpha158"):
        R.log_params(**{"model": "LightGBM", "features": "Alpha158"})

        SignalRecord(model, dataset, R.get_recorder()).generate()
        SigAnaRecord(R.get_recorder()).generate()
        PortAnaRecord(
            R.get_recorder(),
            config={
                "strategy": config["port_analysis_config"]["strategy"],
                "backtest": config["port_analysis_config"]["backtest"],
            },
        ).generate()

        recorder = R.get_recorder()
        ic_analysis = recorder.load_object("sig_analysis/ic.pkl")
        report_normal = recorder.load_object("portfolio_analysis/report_normal_1day.pkl")
        portfolio_metrics = recorder.load_object("portfolio_analysis/port_analysis_1day.pkl")

    print("\n" + "=" * 60)
    print("BACKTEST RESULTS — LightGBM Alpha158 on S&P 500")
    print("=" * 60)
    print("\n--- IC Analysis ---")
    print(f"IC Mean:       {ic_analysis['IC'].mean():.4f}")
    print(f"IC Std:        {ic_analysis['IC'].std():.4f}")
    print(f"Rank IC Mean:  {ic_analysis['Rank IC'].mean():.4f}")
    print(f"ICIR:          {ic_analysis['IC'].mean() / ic_analysis['IC'].std():.4f}")

    _export_artifacts(output_dir, config, ic_analysis, portfolio_metrics)

    return {
        "portfolio_metrics": portfolio_metrics,
        "report_normal": report_normal,
        "ic_analysis": ic_analysis,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run LightGBM Alpha158 QLib backtest")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to config yaml")
    parser.add_argument("--provider-uri", default=None, help="Override qlib provider_uri")
    parser.add_argument("--region", choices=["us", "cn"], default=None, help="Override region")
    parser.add_argument("--test-start", default=None, help="Override test/backtest start date")
    parser.add_argument("--test-end", default=None, help="Override test/backtest end date")
    parser.add_argument("--output-dir", default=None, help="Directory for run artifacts")
    parser.add_argument(
        "--skip-init", action="store_true", help="Skip qlib.init if already initialized"
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    run_backtest(
        config_path=args.config,
        init=not args.skip_init,
        provider_uri=args.provider_uri,
        region=args.region,
        test_start=args.test_start,
        test_end=args.test_end,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
