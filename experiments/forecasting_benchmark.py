"""
Forecasting benchmark — real data, walk-forward evaluation, using the
project's ACTUAL run_forecast() / CANDIDATES code (not a reimplementation).

Dataset: statsmodels' built-in Mauna Loa weekly CO2 dataset (real atmospheric
measurements, 1958-2001, bundled with statsmodels — no network access
needed). Resampled to monthly means (2284 weekly points -> ~526 months) to
match typical business time-series granularity the platform targets.

Why this dataset: it has genuine trend (rising CO2) AND genuine seasonality
(annual cycle) AND real-world noise — exactly the three meta-features
_compute_meta_features() in forecasting_service.py tries to detect, so it is
a fair test of whether meta-feature-based shortlisting picks sensible models
instead of always defaulting to the most complex one.

Evaluation: walk-forward (expanding window), not a single train/test split —
N_WINDOWS independent forecast origins, each one calling the project's own
run_forecast() in two modes:
  (a) model="auto"  -> exercises meta-feature shortlisting + rolling-origin
      backtest + MASE-based selection, all together, as a real user would
      experience it
  (b) each individual model explicitly (naive, seasonal_naive, holt, arima,
      sarima) -> gives the actual per-model MASE/RMSE so "auto"'s choice can
      be checked against what the best possible single choice would have been

Run: PYTHONPATH=../ml-service python3 forecasting_benchmark.py
Output: results/forecasting_benchmark.csv (+ printed markdown table)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml-service"))

import numpy as np
import pandas as pd
from statsmodels.datasets import co2

from app.services.forecasting_service import run_forecast, CANDIDATES, _mase, _mape, _rmse

HORIZON = 12  # forecast 12 months ahead, a realistic business planning horizon
N_WINDOWS = 6  # independent walk-forward origins
MIN_TRAIN_SIZE = 60  # at least 5 years of monthly history before the first forecast


def load_real_series() -> pd.DataFrame:
    raw = co2.load().data["co2"]
    monthly = raw.resample("MS").mean().interpolate()  # a handful of weeks have gaps; linear-fill them
    df = monthly.reset_index()
    df.columns = ["date", "value"]
    return df


def walk_forward_windows(df: pd.DataFrame, min_train: int, horizon: int, n_windows: int):
    """Yields (train_df, test_df) pairs, each with a later origin than the last."""
    max_start = len(df) - min_train - horizon
    if max_start <= 0:
        raise ValueError("Series too short for the requested min_train/horizon/n_windows.")
    step = max(1, max_start // n_windows)
    for i in range(n_windows):
        train_end = min_train + i * step
        if train_end + horizon > len(df):
            break
        yield df.iloc[:train_end].copy(), df.iloc[train_end:train_end + horizon].copy()


def run_benchmark() -> pd.DataFrame:
    df = load_real_series()
    rows = []

    for window_idx, (train_df, test_df) in enumerate(walk_forward_windows(df, MIN_TRAIN_SIZE, HORIZON, N_WINDOWS)):
        actual = test_df["value"].values

        # (a) the project's actual "auto" mode end-to-end
        auto_result = run_forecast(train_df, "date", "value", periods=HORIZON, model="auto")
        auto_forecast = np.array([p["value"] for p in auto_result["forecast"]])
        rows.append({
            "window": window_idx, "method": f"auto (picked: {auto_result['model_used']})",
            "mape": _mape(actual, auto_forecast), "rmse": _rmse(actual, auto_forecast),
            "mase": _mase(actual, auto_forecast, train_df.set_index("date")["value"]),
            "candidates_evaluated": ",".join(auto_result.get("candidates_evaluated", [])),
        })

        # (b) every individual candidate explicitly, for comparison
        train_series = train_df.set_index("date")["value"]
        for name, fit_fn in CANDIDATES.items():
            try:
                forecast = fit_fn(train_series, HORIZON).values
                rows.append({
                    "window": window_idx, "method": name,
                    "mape": _mape(actual, forecast), "rmse": _rmse(actual, forecast),
                    "mase": _mase(actual, forecast, train_series),
                    "candidates_evaluated": "",
                })
            except Exception as exc:
                rows.append({"window": window_idx, "method": name,
                             "mape": None, "rmse": None, "mase": None,
                             "candidates_evaluated": f"FAILED: {exc}"})

    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    is_auto = results["method"].str.startswith("auto")
    results = results.copy()
    results.loc[is_auto, "method_group"] = "auto"
    results.loc[~is_auto, "method_group"] = results.loc[~is_auto, "method"]
    summary = results.groupby("method_group").agg(
        mean_mase=("mase", "mean"), std_mase=("mase", "std"),
        mean_mape=("mape", "mean"), windows=("mase", "count"),
    ).reset_index().sort_values("mean_mase")
    return summary


if __name__ == "__main__":
    results = run_benchmark()
    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    results.to_csv(os.path.join(out_dir, "forecasting_benchmark_raw.csv"), index=False)

    summary = summarize(results)
    summary.to_csv(os.path.join(out_dir, "forecasting_benchmark_summary.csv"), index=False)

    df = load_real_series()
    print(f"\nDataset: statsmodels Mauna Loa CO2, monthly-resampled, n={len(df)} months")
    print(f"Walk-forward windows: {N_WINDOWS}, horizon: {HORIZON} months each\n")
    print(summary.to_markdown(index=False, floatfmt=".4f"))
    print("\nPer-window detail (which model 'auto' actually picked each time):")
    print(results[results["method"].str.startswith("auto")][["window", "method", "mase"]].to_markdown(index=False, floatfmt=".4f"))
