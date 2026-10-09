"""
Imputation benchmark — real data, artificial masking, measured against ground truth.

Methodology: take a complete tabular dataset, artificially mask a known
fraction of one column under MCAR, and measure reconstruction error against the
hidden values. This supplies ground truth for this controlled experiment, but
does not establish performance under naturally occurring missingness.

Dataset: sklearn's `diabetes` dataset (442 patients, 10 real physiological
features, bundled with scikit-learn — no network access needed). Only `bmi` is
masked; the other nine features remain observed.

Methods compared, all from app/services/cleaning_service.py (the actual
project code, not a reimplementation):
  - mean / median: univariate baselines
  - KNN (k=5): feature-aware baseline
  - multiple_imputation_marginal: previous bootstrap baseline
  - multiple_imputation_iterative: current production strategy

For the stochastic methods, the benchmark also reports the per-trial Spearman
rank association between reported between-imputation spread and absolute error.
This is a diagnostic, not a calibration metric.

Run from `experiments/`:
  PYTHONPATH=../ml-service python imputation_benchmark.py
Output: raw/summary CSVs and a Markdown table in results/.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml-service"))

import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.impute import KNNImputer
from scipy.stats import spearmanr

from app.services.cleaning_service import _multiple_impute_column, fill_missing_values

RANDOM_STATE = 42
MASK_RATES = [0.10, 0.20, 0.30]
N_TRIALS = 10  # repeat each masking with a different random mask to reduce variance


def load_real_data() -> pd.DataFrame:
    data = load_diabetes(as_frame=True)
    return data.frame.drop(columns=["target"])  # 10 real physiological features, 442 rows


def mask_mcar(df: pd.DataFrame, col: str, rate: float, seed: int) -> tuple[pd.Series, np.ndarray]:
    """Returns (series_with_holes, mask) where mask[i]=True means we hid the true value at i."""
    rng = np.random.RandomState(seed)
    series = df[col].copy()
    mask = rng.rand(len(series)) < rate
    masked_series = series.copy()
    masked_series[mask] = np.nan
    return masked_series, mask


def rmse(a, b) -> float:
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def uncertainty_spearman(true_values, estimates, uncertainties) -> float | None:
    errors = np.abs(np.asarray(true_values) - np.asarray(estimates))
    uncertainty_values = np.asarray(uncertainties, dtype=float)
    valid = np.isfinite(uncertainty_values)
    if valid.sum() <= 2:
        return None
    return float(spearmanr(uncertainty_values[valid], errors[valid]).correlation)


def run_benchmark() -> pd.DataFrame:
    df = load_real_data()
    target_col = "bmi"  # a continuous, real, non-trivial feature to mask
    true_values_full = df[target_col].values.copy()

    rows = []
    for rate in MASK_RATES:
        for trial in range(N_TRIALS):
            seed = RANDOM_STATE + trial
            masked_series, mask = mask_mcar(df, target_col, rate, seed)
            true_hidden = true_values_full[mask]
            if mask.sum() == 0:
                continue
            masked_frame = df.copy()
            masked_frame[target_col] = masked_series

            # --- mean ---
            mean_filled = masked_series.fillna(masked_series.mean())
            rows.append({"mask_rate": rate, "trial": trial, "method": "mean",
                         "rmse": rmse(true_hidden, mean_filled.values[mask]),
                         "uncertainty_spearman": None})

            # --- median ---
            median_filled = masked_series.fillna(masked_series.median())
            rows.append({"mask_rate": rate, "trial": trial, "method": "median",
                         "rmse": rmse(true_hidden, median_filled.values[mask]),
                         "uncertainty_spearman": None})

            # --- KNN (k=5), using the other 9 real features as neighbors ---
            knn_frame = df.copy()
            knn_frame[target_col] = masked_series
            imputer = KNNImputer(n_neighbors=5)
            knn_result = imputer.fit_transform(knn_frame)
            knn_col_idx = list(knn_frame.columns).index(target_col)
            knn_filled = knn_result[:, knn_col_idx]
            rows.append({"mask_rate": rate, "trial": trial, "method": "knn_k5",
                         "rmse": rmse(true_hidden, knn_filled[mask]),
                         "uncertainty_spearman": None})

            # --- previous marginal-bootstrap implementation as a fixed baseline ---
            marginal_filled, marginal_uncertainty = _multiple_impute_column(
                masked_series, random_state=seed
            )
            marginal_values = marginal_filled.values[mask]
            marginal_uncertainty_values = [
                marginal_uncertainty.get(i, np.nan) for i in np.where(mask)[0]
            ]
            rows.append({
                "mask_rate": rate, "trial": trial, "method": "multiple_imputation_marginal",
                "rmse": rmse(true_hidden, marginal_values),
                "uncertainty_spearman": uncertainty_spearman(
                    true_hidden, marginal_values, marginal_uncertainty_values
                ),
            })

            # --- production multiple strategy using the other columns as predictors ---
            iterative_frame, repair_log = fill_missing_values(
                masked_frame, strategy="multiple", random_state=seed
            )
            iterative_values = iterative_frame[target_col].values[mask]
            iterative_uncertainty = {
                repair["row_index"]: repair["imputation_uncertainty"]
                for repair in repair_log
                if repair["column"] == target_col and "imputation_uncertainty" in repair
            }
            iterative_uncertainty_values = [
                iterative_uncertainty.get(i, np.nan) for i in np.where(mask)[0]
            ]
            rows.append({
                "mask_rate": rate, "trial": trial, "method": "multiple_imputation_iterative",
                "rmse": rmse(true_hidden, iterative_values),
                "uncertainty_spearman": uncertainty_spearman(
                    true_hidden, iterative_values, iterative_uncertainty_values
                ),
            })

    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    summary = results.groupby(["mask_rate", "method"]).agg(
        mean_rmse=("rmse", "mean"),
        std_rmse=("rmse", "std"),
        mean_uncertainty_spearman=("uncertainty_spearman", "mean"),
    ).reset_index()
    return summary


if __name__ == "__main__":
    results = run_benchmark()
    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)
    results.to_csv(os.path.join(out_dir, "imputation_benchmark_raw.csv"), index=False)

    summary = summarize(results)
    summary.to_csv(os.path.join(out_dir, "imputation_benchmark_summary.csv"), index=False)

    report = "\n".join([
        "# Imputation benchmark results",
        "",
        f"Dataset: scikit-learn diabetes, target `bmi`, n={len(load_real_data())}.",
        f"Trials per mask rate: {N_TRIALS}; rates: {', '.join(f'{rate:.0%}' for rate in MASK_RATES)}.",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
    ])
    with open(os.path.join(out_dir, "imputation_benchmark_report.md"), "w", encoding="utf-8") as report_file:
        report_file.write(report)

    print(f"\nDataset: sklearn.datasets.load_diabetes, column='bmi', n={len(load_real_data())}")
    print(f"Trials per (mask_rate, method): {N_TRIALS}\n")
    print(summary.to_markdown(index=False, floatfmt=".4f"))
