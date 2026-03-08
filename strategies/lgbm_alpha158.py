"""
LightGBM strategy using QLib's Alpha158 feature set on S&P 500 stocks.

This strategy trains a LightGBM model on 158 hand-crafted alpha factors
and backtests a top-k dropout portfolio on the S&P 500 universe.

Usage:
    from strategies.lgbm_alpha158 import run_backtest
    portfolio_metrics, analysis = run_backtest()
"""

import qlib
from qlib.constant import REG_US
from qlib.utils import init_instance_by_config
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, SigAnaRecord, PortAnaRecord
from qlib.data import D
import pandas as pd
import yaml
import os


DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "configs", "lgbm_alpha158.yaml"
)


def load_config(config_path=None):
    """Load the QLib YAML workflow config."""
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r") as f:
        return yaml.safe_load(f)


def init_qlib(provider_uri="~/.qlib/qlib_data/us_data", region=REG_US):
    """Initialize QLib with US market data."""
    qlib.init(provider_uri=provider_uri, region=region)
    print(f"QLib initialized with region={region}")


def run_backtest(config_path=None, init=True):
    """
    Run the full LightGBM Alpha158 backtest pipeline.

    Args:
        config_path: Path to YAML config. Uses default if None.
        init: Whether to initialize QLib. Set False if already initialized.

    Returns:
        dict with keys:
            - portfolio_metrics: DataFrame of portfolio analysis results
            - report_normal: backtest report dict
            - ic_analysis: IC (information coefficient) analysis
    """
    if init:
        init_qlib()

    config = load_config(config_path)

    # --- Build model and dataset from config ---
    model = init_instance_by_config(config["task"]["model"])
    dataset = init_instance_by_config(config["task"]["dataset"])

    # --- Train ---
    print("Training LightGBM model...")
    model.fit(dataset)
    print("Training complete.")

    # --- Record experiment ---
    with R.start(experiment_name="lgbm_alpha158"):
        R.log_params(**{"model": "LightGBM", "features": "Alpha158"})

        # Signal (prediction) recording
        sr = SignalRecord(model, dataset, R.get_recorder())
        sr.generate()

        # Signal analysis (IC, rank IC)
        sar = SigAnaRecord(R.get_recorder())
        sar.generate()

        # Portfolio analysis (backtest with top-k dropout strategy)
        par = PortAnaRecord(
            R.get_recorder(),
            config={
                "strategy": config["port_analysis_config"]["strategy"],
                "backtest": config["port_analysis_config"]["backtest"],
            },
        )
        par.generate()

        # --- Extract results ---
        recorder = R.get_recorder()

        ic_analysis = recorder.load_object("sig_analysis/ic.pkl")
        report_normal = recorder.load_object("portfolio_analysis/report_normal_1day.pkl")
        portfolio_metrics = recorder.load_object(
            "portfolio_analysis/port_analysis_1day.pkl"
        )

    # --- Print summary ---
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS — LightGBM Alpha158 on S&P 500")
    print("=" * 60)

    print("\n--- IC Analysis ---")
    print(f"IC Mean:       {ic_analysis['IC'].mean():.4f}")
    print(f"IC Std:        {ic_analysis['IC'].std():.4f}")
    print(f"Rank IC Mean:  {ic_analysis['Rank IC'].mean():.4f}")
    print(f"ICIR:          {ic_analysis['IC'].mean() / ic_analysis['IC'].std():.4f}")

    if isinstance(portfolio_metrics, dict):
        for k, v in portfolio_metrics.items():
            print(f"\n--- {k} ---")
            if isinstance(v, pd.DataFrame):
                print(v.to_string())
            else:
                print(v)
    else:
        print("\n--- Portfolio Metrics ---")
        print(portfolio_metrics)

    return {
        "portfolio_metrics": portfolio_metrics,
        "report_normal": report_normal,
        "ic_analysis": ic_analysis,
    }


if __name__ == "__main__":
    run_backtest()
