"""
Imputation benchmark v2 -- real datasets, MCAR / MAR / MNAR masking, ground-truth error AND
uncertainty calibration, with paired significance tests.

Protocol (the standard one in the imputation literature, e.g. Jäger et al. 2021): take a REAL
complete table, standardise it, hide a known fraction of cells under a known missingness
mechanism, impute, and score against the hidden truth.

Datasets (real, bundled with scikit-learn, no network): diabetes (10 feats, n=442), wine
(13, n=178), breast_cancer (first 10 "mean" feats, n=569), iris (4, n=150).
Mechanisms: MCAR (independent of everything), MAR (missingness depends on an always-observed
driver column), MNAR (missingness depends on the cell's own value; strong self-censoring).
Rates: 10% and 30% of cells. Trials: N_TRIALS random masks per configuration.

Methods -- project code unless noted:
  mean, median                 baselines
  knn5                         sklearn KNNImputer(k=5)
  iterative_single             sklearn IterativeImputer, ONE deterministic regression pass
  marginal_bootstrap (OLD)     the project's previous "multiple imputation" (_multiple_impute_column)
  mice_multiple (NEW)          the project's feature-aware multiple imputation (_multiple_impute_dataframe)

Metrics: RMSE in standardised units over the hidden cells (lower = better); for the two multiple-
imputation methods also (a) Spearman(uncertainty, |error|) and (b) empirical coverage of a nominal
90% interval (mean +/- t_{0.95,m-1} * sd * sqrt(1+1/m)); well-calibrated => coverage ~0.90.

Run:  python3 imputation_benchmark.py          (from experiments/, with ml-service deps installed)
"""
import itertools
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_wine
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer

from common import RESULTS_DIR, holm_adjust, save_environment
from app.services.cleaning_service import _multiple_impute_column, _multiple_impute_dataframe

warnings.filterwarnings("ignore")  # IterativeImputer ConvergenceWarnings are expected at max_iter=10

SEED = 42
N_TRIALS = 12
RATES = [0.10, 0.30]
MECHANISMS = ["MCAR", "MAR", "MNAR"]
N_IMPUTATIONS = 5  # the production default


def load_datasets() -> dict[str, pd.DataFrame]:
    out = {
        "diabetes": load_diabetes(as_frame=True).frame.drop(columns="target"),
        "wine": load_wine(as_frame=True).frame.drop(columns="target"),
        "breast_cancer": load_breast_cancer(as_frame=True).frame.drop(columns="target").iloc[:, :10],
        "iris": load_iris(as_frame=True).frame.drop(columns="target"),
    }
    # z-score so every column has unit variance: KNN is scale-sensitive and RMSE is comparable
    return {k: (v - v.mean()) / v.std(ddof=0) for k, v in out.items()}


def _calibrate_bias(base_logit: np.ndarray, rate: float) -> np.ndarray:
    """Per-column intercepts so the mean missingness probability equals `rate` (bisection)."""
    n_cols = base_logit.shape[1]
    bias = np.zeros(n_cols)
    for j in range(n_cols):
        lo, hi = -20.0, 20.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if (1 / (1 + np.exp(-(base_logit[:, j] + mid)))).mean() > rate:
                hi = mid
            else:
                lo = mid
        bias[j] = (lo + hi) / 2
    return bias


def make_mask(df: pd.DataFrame, mechanism: str, rate: float, rng: np.random.RandomState) -> np.ndarray:
    x = df.values
    n, d = x.shape
    if mechanism == "MCAR":
        prob = np.full((n, d), rate)
    elif mechanism == "MAR":
        base = np.tile(2.0 * x[:, [0]], (1, d))            # depends on the observed driver (column 0)
        prob = 1 / (1 + np.exp(-(base + _calibrate_bias(base, rate))))
        prob[:, 0] = 0.0                                   # the driver itself is always observed
    elif mechanism == "MNAR":
        base = 2.0 * x                                     # depends on the cell's own (hidden) value
        prob = 1 / (1 + np.exp(-(base + _calibrate_bias(base, rate))))
    else:
        raise ValueError(mechanism)
    mask = rng.rand(n, d) < prob
    for j in range(d):                                     # keep at least a few observed cells per column
        if mask[:, j].sum() > n - 5:
            mask[rng.choice(n, 5, replace=False), j] = False
    for i in np.where(mask.all(axis=1))[0]:                # no completely empty rows
        mask[i, rng.randint(d)] = False
    return mask


def _interval_stats(true, pred, sd, m):
    sd_total = sd * np.sqrt(1 + 1 / m)
    half = stats.t.ppf(0.95, m - 1) * sd_total
    covered = float(np.mean(np.abs(true - pred) <= half))
    spearman = float(stats.spearmanr(sd, np.abs(true - pred)).correlation) if np.std(sd) > 0 else np.nan
    return covered, float(np.mean(2 * half)), spearman


def run_one(name, df, mechanism, rate, trial) -> list[dict]:
    rng = np.random.RandomState(SEED + 1000 * trial + int(rate * 100) + MECHANISMS.index(mechanism))
    mask = make_mask(df, mechanism, rate, rng)
    truth = df.values[mask]
    masked_df = df.mask(mask)
    rows = []

    def record(method, filled, **extra):
        rmse = float(np.sqrt(np.mean((np.asarray(filled)[mask] - truth) ** 2)))
        rows.append({"dataset": name, "mechanism": mechanism, "rate": rate, "trial": trial,
                     "method": method, "rmse": rmse, "n_masked": int(mask.sum()), **extra})

    record("mean", masked_df.fillna(masked_df.mean()).values)
    record("median", masked_df.fillna(masked_df.median()).values)
    record("knn5", KNNImputer(n_neighbors=5).fit_transform(masked_df))
    record("iterative_single", IterativeImputer(sample_posterior=False, max_iter=10, random_state=SEED,
                                                skip_complete=True).fit_transform(masked_df))

    # OLD project method: independent per-column marginal bootstrap
    filled_old = masked_df.copy()
    sd_old = np.full(masked_df.shape, np.nan)
    for j, col in enumerate(masked_df.columns):
        filled_col, unc = _multiple_impute_column(masked_df[col], n_imputations=N_IMPUTATIONS, random_state=SEED + trial)
        filled_old[col] = filled_col
        for idx, u in unc.items():
            sd_old[masked_df.index.get_loc(idx), j] = u
    cov, width, rho = _interval_stats(truth, filled_old.values[mask], sd_old[mask], N_IMPUTATIONS)
    record("marginal_bootstrap_OLD", filled_old.values, coverage90=cov, interval_width=width, uncertainty_spearman=rho)

    # NEW project method: feature-aware MICE
    filled_new, unc_new = _multiple_impute_dataframe(masked_df, n_imputations=N_IMPUTATIONS, random_state=SEED + trial)
    sd_new = np.full(masked_df.shape, np.nan)
    for j, col in enumerate(masked_df.columns):
        for idx, uncertainty in unc_new.get(col, {}).items():
            sd_new[masked_df.index.get_loc(idx), j] = uncertainty
    cov, width, rho = _interval_stats(truth, filled_new.values[mask], sd_new[mask], N_IMPUTATIONS)
    record("mice_multiple_NEW", filled_new.values, coverage90=cov, interval_width=width, uncertainty_spearman=rho)
    return rows


def main():
    data = load_datasets()
    started = time.time()
    rows = []
    configs = list(itertools.product(data.items(), MECHANISMS, RATES, range(N_TRIALS)))
    for k, ((name, df), mech, rate, trial) in enumerate(configs):
        rows.extend(run_one(name, df, mech, rate, trial))
        if k % 24 == 0:
            print(f"  {k}/{len(configs)} configs, {time.time() - started:.0f}s", flush=True)
    raw = pd.DataFrame(rows)
    raw.to_csv(f"{RESULTS_DIR}/imputation_raw.csv", index=False)

    summary = raw.groupby(["dataset", "mechanism", "method"]).agg(
        rmse=("rmse", "mean"), rmse_sd=("rmse", "std"),
        coverage90=("coverage90", "mean"), interval_width=("interval_width", "mean"),
        uncertainty_spearman=("uncertainty_spearman", "mean")).reset_index()
    summary.to_csv(f"{RESULTS_DIR}/imputation_summary.csv", index=False)

    # paired Wilcoxon signed-rank: NEW method vs every other method, per dataset x mechanism
    pivot = raw.pivot_table(index=["dataset", "mechanism", "rate", "trial"], columns="method", values="rmse")
    sig = []
    for (dataset, mech), block in pivot.groupby(level=["dataset", "mechanism"]):
        for other in ["mean", "median", "knn5", "iterative_single", "marginal_bootstrap_OLD"]:
            diff = block["mice_multiple_NEW"] - block[other]
            p = stats.wilcoxon(diff).pvalue if (diff != 0).any() else 1.0
            sig.append({"dataset": dataset, "mechanism": mech, "vs": other, "mean_rmse_diff": diff.mean(),
                        "new_wins": int((diff < 0).sum()), "pairs": int(len(diff)), "p_value": p})
    sig = pd.DataFrame(sig)
    sig["p_holm"] = holm_adjust(sig["p_value"].values)
    sig.to_csv(f"{RESULTS_DIR}/imputation_significance.csv", index=False)
    save_environment({"imputation": {"seed": SEED, "n_trials": N_TRIALS, "rates": RATES,
                                     "mechanisms": MECHANISMS, "n_imputations": N_IMPUTATIONS}},
                     "environment_imputation.json")

    overall = raw.groupby(["mechanism", "method"]).rmse.mean().unstack("method").round(4)
    print("\nMean RMSE (standardised units) by mechanism, averaged over datasets/rates/trials:")
    print(overall.to_markdown())
    cal = raw[raw.method.isin(["marginal_bootstrap_OLD", "mice_multiple_NEW"])].groupby(["mechanism", "method"]).agg(
        coverage90=("coverage90", "mean"), spearman=("uncertainty_spearman", "mean")).round(3)
    print("\nUncertainty calibration (nominal coverage 0.90):")
    print(cal.to_markdown())
    print(f"\nTotal runtime {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
