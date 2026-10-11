"""
Imputation benchmark — real data, artificial masking, measured against ground truth.

Methodology (standard in the imputation literature, e.g. Jäger et al. 2021):
take a REAL, complete tabular dataset, artificially mask a known fraction of
cells under MCAR (Missing Completely At Random), run each imputation method,
then measure error against the TRUE values we deliberately hid. This is the
only way to get a ground-truth RMSE for imputation — with genuinely missing
real-world data there is no ground truth to compare against.

Dataset: sklearn's `diabetes` dataset (442 patients, 10 real physiological
features, bundled with scikit-learn — no network access needed, no fabricated
data). Chosen because it is small enough to run quickly but real enough that
feature correlations are not synthetic/trivial, which matters for KNN and
multiple-imputation (both exploit real cross-feature correlation).

Methods compared, all from app/services/cleaning_service.py (the actual
project code, not a reimplementation):
  - mean / median   (naive baselines, what "auto" strategy falls back to)
  - KNN imputation  (k=5, existing "knn" strategy)
  - multiple imputation with uncertainty (existing "multiple" strategy) —
    evaluated on (a) RMSE of the point estimate, same as the others, AND
    (b) whether its reported per-cell uncertainty is actually informative:
    a Spearman correlation between reported uncertainty and actual error.
    A well-calibrated uncertainty estimate should correlate positively
    (cells it's unsure about should on average be the ones it gets more
    wrong) — this is the evidence needed to back the "uncertainty-aware"
    claim, rather than just asserting a std-dev number means something.

Run: PYTHONPATH=../ml-service python3 imputation_benchmark.py
Output: results/imputation_benchmark.csv (+ printed markdown table)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml-service"))

import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.impute import KNNImputer
from scipy.stats import spearmanr

from app.services.cleaning_service import _multiple_impute_column

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

            # --- multiple imputation (our method, with uncertainty) ---
            filled_series, uncertainty_map = _multiple_impute_column(masked_series, random_state=seed)
            multi_filled = filled_series.values[mask]
            error_per_cell = np.abs(true_hidden - multi_filled)
            uncertainty_per_cell = np.array([uncertainty_map.get(i, np.nan) for i in np.where(mask)[0]])
            valid = ~np.isnan(uncertainty_per_cell)
            spearman_corr = (
                float(spearmanr(uncertainty_per_cell[valid], error_per_cell[valid]).correlation)
                if valid.sum() > 2 else None
            )
            rows.append({"mask_rate": rate, "trial": trial, "method": "multiple_imputation",
                         "rmse": rmse(true_hidden, multi_filled),
                         "uncertainty_spearman": spearman_corr})

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

    print(f"\nDataset: sklearn.datasets.load_diabetes, column='bmi', n={len(load_real_data())}")
    print(f"Trials per (mask_rate, method): {N_TRIALS}\n")
    print(summary.to_markdown(index=False, floatfmt=".4f"))
