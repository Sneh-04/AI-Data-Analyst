"""Reproducible MCAR/MAR/MNAR imputation benchmark on bundled numeric datasets."""
import argparse
from dataclasses import dataclass
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml-service"))

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import t
from sklearn.datasets import load_breast_cancer, load_diabetes, load_wine
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer
from sklearn.linear_model import BayesianRidge

from app.services.cleaning_service import fill_missing_values


DEFAULT_MASK_RATES = (0.10, 0.20, 0.30, 0.40)
DEFAULT_TRIALS = 10
DEFAULT_SEED = 42
MECHANISMS = ("mar", "mnar")
PROPENSITY_SLOPE = 1.5


@dataclass(frozen=True)
class MissingnessSample:
    masked_data: pd.DataFrame
    ground_truth: pd.Series
    mask: pd.Series
    propensity: pd.Series


def load_benchmark_datasets():
    """Return bundled, numeric datasets without downloading data."""
    datasets = {
        "diabetes": (load_diabetes(as_frame=True).data, "bmi", "bp"),
        "wine": (load_wine(as_frame=True).data, "alcohol", "malic_acid"),
        "breast_cancer": (
            load_breast_cancer(as_frame=True).data,
            "mean radius",
            "mean texture",
        ),
    }
    return datasets


def _standardized_scores(values: pd.Series, name: str) -> np.ndarray:
    if not pd.api.types.is_numeric_dtype(values.dtype) or pd.api.types.is_bool_dtype(values.dtype):
        raise TypeError(f"{name} must be numeric")
    numeric_values = values.to_numpy(dtype=float)
    if not np.isfinite(numeric_values).all():
        raise ValueError(f"{name} must contain only finite observed values")
    scale = numeric_values.std()
    if scale == 0:
        raise ValueError(f"{name} must vary to define feature-dependent missingness")
    return (numeric_values - numeric_values.mean()) / scale


def missingness_probabilities(
    frame: pd.DataFrame,
    target_column: str,
    rate: float,
    mechanism: str,
    mar_column: str | None = None,
) -> pd.Series:
    """Calibrate logistic propensities to the requested expected missing rate.

    MAR propensities depend only on a fully observed numeric predictor;
    MNAR propensities depend on the fully observed target values. The target
    values are used here only to generate MNAR masks, never passed to imputers.
    """
    if not 0 < rate < 1:
        raise ValueError("rate must be greater than 0 and less than 1")
    if target_column not in frame:
        raise KeyError(f"target column {target_column!r} is not present")
    if mechanism not in (*MECHANISMS, "mcar"):
        raise ValueError("mechanism must be 'mcar', 'mar', or 'mnar'")

    target = frame[target_column]
    eligible = target.notna()
    if not eligible.any():
        raise ValueError("target column has no observed values")
    target_scores = _standardized_scores(target.loc[eligible], "target column")

    if mechanism == "mcar":
        probabilities = np.full(len(frame), rate, dtype=float)
    else:
        if mechanism == "mar":
            if mar_column is None:
                raise ValueError("mar_column is required for MAR")
            if mar_column == target_column or mar_column not in frame:
                raise ValueError("MAR predictor must be a different column present in the data")
            predictor = frame[mar_column]
            if predictor.isna().any():
                raise ValueError("MAR predictor must be fully observed")
            scores = _standardized_scores(predictor.loc[eligible], "MAR predictor")
        else:
            scores = target_scores

        low = -40.0 - PROPENSITY_SLOPE * float(scores.max())
        high = 40.0 - PROPENSITY_SLOPE * float(scores.min())
        for _ in range(80):
            intercept = (low + high) / 2
            if expit(intercept + PROPENSITY_SLOPE * scores).mean() < rate:
                low = intercept
            else:
                high = intercept
        eligible_probabilities = expit(
            ((low + high) / 2) + PROPENSITY_SLOPE * scores
        )
        probabilities = np.zeros(len(frame), dtype=float)
        probabilities[np.flatnonzero(eligible.to_numpy())] = eligible_probabilities

    return pd.Series(probabilities, index=frame.index, name="missingness_propensity")


def simulate_missingness(
    frame: pd.DataFrame,
    target_column: str,
    rate: float,
    mechanism: str,
    seed: int,
    mar_column: str | None = None,
) -> MissingnessSample:
    """Create one reproducible mask while retaining truth outside imputer input."""
    if not frame.index.is_unique:
        raise ValueError("frame index must be unique")
    propensity = missingness_probabilities(
        frame, target_column, rate, mechanism, mar_column=mar_column
    )
    eligible = frame[target_column].notna()
    mask_values = np.zeros(len(frame), dtype=bool)
    rng = np.random.RandomState(seed)
    mask_values[eligible.to_numpy()] = (
        rng.random_sample(int(eligible.sum()))
        < propensity.loc[eligible].to_numpy()
    )
    mask = pd.Series(mask_values, index=frame.index, name="artificially_masked")
    ground_truth = frame[target_column].copy(deep=True)
    masked_data = frame.copy(deep=True)
    masked_data.loc[mask, target_column] = np.nan
    return MissingnessSample(masked_data, ground_truth, mask, propensity)


def reconstruction_metrics(
    ground_truth: pd.Series, estimates, evaluation_mask: pd.Series
) -> dict[str, float]:
    """Calculate RMSE/MAE only for artificially hidden, originally observed cells."""
    if not (ground_truth.index.equals(evaluation_mask.index)):
        raise ValueError("ground_truth and evaluation_mask indices must match")
    if evaluation_mask.dtype != bool:
        raise TypeError("evaluation_mask must be boolean")
    if not evaluation_mask.any():
        raise ValueError("evaluation_mask must contain at least one cell")
    truth = ground_truth.loc[evaluation_mask].to_numpy(dtype=float)
    predicted = np.asarray(estimates, dtype=float)
    if predicted.shape == ground_truth.shape:
        predicted = pd.Series(predicted, index=ground_truth.index).loc[evaluation_mask].to_numpy()
    if predicted.shape != truth.shape:
        raise ValueError("estimates must have one value per row or one per evaluated cell")
    if not np.isfinite(truth).all() or not np.isfinite(predicted).all():
        raise ValueError("ground truth and estimates must be finite on evaluation cells")
    errors = predicted - truth
    return {
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mae": float(np.mean(np.abs(errors))),
    }


def _standardize_numeric_input(masked_data: pd.DataFrame, target_column: str):
    numeric_columns = [
        column for column in masked_data.select_dtypes(include=[np.number]).columns
        if not pd.api.types.is_bool_dtype(masked_data[column].dtype)
        and masked_data[column].notna().any()
    ]
    if target_column not in numeric_columns:
        raise TypeError("target column must be numeric with at least one observed value")
    numeric = masked_data[numeric_columns].astype(float)
    if not np.isfinite(numeric.to_numpy()[~numeric.isna().to_numpy()]).all():
        raise ValueError("numeric benchmark features must not contain infinite values")
    means = numeric.mean()
    scales = numeric.std(ddof=0).replace(0, 1.0).fillna(1.0)
    return (numeric - means) / scales, means[target_column], scales[target_column]


def evaluate_methods(
    sample: MissingnessSample,
    target_column: str,
    seed: int,
) -> list[dict]:
    """Evaluate every method on the same masked, scaled input and evaluation cells."""
    if sample.mask.sum() == 0:
        raise ValueError("sample has no artificially masked target values")
    if sample.mask.loc[sample.ground_truth.isna()].any():
        raise ValueError("evaluation mask includes values missing before simulation")

    scaled_data, target_mean, target_scale = _standardize_numeric_input(
        sample.masked_data, target_column
    )
    target_position = list(scaled_data.columns).index(target_column)
    results = []

    def record(method: str, imputed_values, elapsed: float):
        estimates = np.asarray(imputed_values, dtype=float) * target_scale + target_mean
        metrics = reconstruction_metrics(sample.ground_truth, estimates, sample.mask)
        results.append({
            "method": method,
            **metrics,
            "runtime_seconds": elapsed,
        })

    started = time.perf_counter()
    observed_target = scaled_data[target_column].dropna()
    mean_values = scaled_data[target_column].fillna(observed_target.mean()).to_numpy()
    elapsed = time.perf_counter() - started
    record("mean", mean_values, elapsed)

    started = time.perf_counter()
    observed_target = scaled_data[target_column].dropna()
    median_values = scaled_data[target_column].fillna(observed_target.median()).to_numpy()
    elapsed = time.perf_counter() - started
    record("median", median_values, elapsed)

    started = time.perf_counter()
    knn_values = KNNImputer(n_neighbors=5).fit_transform(scaled_data)[:, target_position]
    elapsed = time.perf_counter() - started
    record("knn_k5", knn_values, elapsed)

    started = time.perf_counter()
    iterative_values = IterativeImputer(
        estimator=BayesianRidge(),
        sample_posterior=False,
        max_iter=10,
        random_state=seed,
    ).fit_transform(scaled_data)[:, target_position]
    elapsed = time.perf_counter() - started
    record("iterative_bayesian_ridge", iterative_values, elapsed)

    started = time.perf_counter()
    proposed_data, _ = fill_missing_values(
        scaled_data, strategy="multiple", random_state=seed
    )
    elapsed = time.perf_counter() - started
    proposed_values = proposed_data[target_column].to_numpy(dtype=float)
    record("proposed_iterative_multiple", proposed_values, elapsed)

    return results


def _mean_std_ci(values: pd.Series) -> tuple[float, float, float, float]:
    numeric = values.dropna().to_numpy(dtype=float)
    mean = float(np.mean(numeric))
    std = float(np.std(numeric, ddof=1)) if len(numeric) > 1 else float("nan")
    if len(numeric) > 1:
        half_width = float(t.ppf(0.975, df=len(numeric) - 1) * std / np.sqrt(len(numeric)))
        return mean, std, mean - half_width, mean + half_width
    return mean, std, float("nan"), float("nan")


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    grouping = ["dataset", "mechanism", "mask_rate", "method"]
    rows = []
    for keys, group in results.groupby(grouping, sort=True):
        row = dict(zip(grouping, keys))
        row["n_trials"] = int(group["trial"].nunique())
        row["mean_realized_missing_rate"] = float(group["realized_missing_rate"].mean())
        for metric in ("rmse", "mae", "runtime_seconds"):
            mean, std, low, high = _mean_std_ci(group[metric])
            row[f"mean_{metric}"] = mean
            row[f"std_{metric}"] = std
            if metric != "runtime_seconds":
                row[f"{metric}_ci95_low"] = low
                row[f"{metric}_ci95_high"] = high
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_paired_comparisons(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize per-trial paired method differences on identical masks.

    Negative differences favor the proposed method. The t intervals are
    exploratory, unadjusted intervals over repeated masks on each fixed dataset.
    """
    condition_columns = ["dataset", "mechanism", "mask_rate"]
    methods = [
        "mean",
        "median",
        "knn_k5",
        "iterative_bayesian_ridge",
        "proposed_iterative_multiple",
    ]
    expected_methods = set(methods)
    rows = []
    for condition, group in results.groupby(condition_columns, sort=True):
        pivot = group.pivot(index="trial", columns="method", values=["rmse", "mae"])
        if set(pivot.columns.get_level_values("method")) != expected_methods:
            raise ValueError(f"incomplete method results for condition {condition}")
        if pivot.isna().any().any():
            raise ValueError(f"missing paired trial results for condition {condition}")

        for metric in ("rmse", "mae"):
            metric_values = pivot[metric]
            proposed = metric_values["proposed_iterative_multiple"]
            for baseline in methods:
                if baseline == "proposed_iterative_multiple":
                    continue
                differences = proposed - metric_values[baseline]
                mean, std, low, high = _mean_std_ci(differences)
                rows.append({
                    **dict(zip(condition_columns, condition)),
                    "metric": metric,
                    "baseline": baseline,
                    "n_trials": len(differences),
                    "mean_proposed_minus_baseline": mean,
                    "std_paired_difference": std,
                    "paired_difference_ci95_low": low,
                    "paired_difference_ci95_high": high,
                })
    return pd.DataFrame(rows)


def run_benchmark(
    datasets=None,
    mechanisms=MECHANISMS,
    mask_rates=DEFAULT_MASK_RATES,
    trials=DEFAULT_TRIALS,
    seed=DEFAULT_SEED,
) -> pd.DataFrame:
    all_datasets = load_benchmark_datasets()
    selected = list(all_datasets) if datasets is None else list(datasets)
    if not selected:
        raise ValueError("at least one dataset must be selected")
    if len(selected) != len(set(selected)):
        raise ValueError("datasets must not contain duplicates")
    unknown = sorted(set(selected) - set(all_datasets))
    if unknown:
        raise ValueError(f"unknown dataset(s): {', '.join(unknown)}")
    if trials < 1:
        raise ValueError("trials must be at least 1")
    if not mechanisms or len(mechanisms) != len(set(mechanisms)):
        raise ValueError("select one or more unique missingness mechanisms")
    if not set(mechanisms).issubset(set(MECHANISMS)):
        raise ValueError("mechanisms must be selected from 'mar' and 'mnar'")
    if (
        not mask_rates
        or len(mask_rates) != len(set(mask_rates))
        or any(not np.isfinite(rate) or not 0 < rate < 1 for rate in mask_rates)
    ):
        raise ValueError("mask rates must be between 0 and 1")

    rows = []
    for dataset_name in selected:
        frame, target, mar_column = all_datasets[dataset_name]
        for mechanism in mechanisms:
            for rate in mask_rates:
                for trial in range(trials):
                    trial_seed = seed + trial
                    sample = simulate_missingness(
                        frame,
                        target,
                        rate,
                        mechanism,
                        trial_seed,
                        mar_column=mar_column if mechanism == "mar" else None,
                    )
                    evaluations = evaluate_methods(sample, target, trial_seed)
                    actual_rate = float(sample.mask.sum() / frame[target].notna().sum())
                    for result in evaluations:
                        rows.append({
                            "dataset": dataset_name,
                            "mechanism": mechanism,
                            "mask_rate": rate,
                            "trial": trial,
                            "seed": trial_seed,
                            "n_rows": len(frame),
                            "n_masked": int(sample.mask.sum()),
                            "realized_missing_rate": actual_rate,
                            **result,
                        })
    return pd.DataFrame(rows)


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", choices=load_benchmark_datasets(), default=None)
    parser.add_argument("--mask-rates", nargs="+", type=float, default=DEFAULT_MASK_RATES)
    parser.add_argument("--mechanisms", nargs="+", choices=MECHANISMS, default=MECHANISMS)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "results",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    results = run_benchmark(
        datasets=args.datasets,
        mechanisms=args.mechanisms,
        mask_rates=args.mask_rates,
        trials=args.trials,
        seed=args.seed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.output_dir / "imputation_benchmark_raw.csv"
    summary_path = args.output_dir / "imputation_benchmark_summary.csv"
    comparisons_path = args.output_dir / "imputation_benchmark_comparisons.csv"
    report_path = args.output_dir / "imputation_benchmark_report.md"
    results.to_csv(raw_path, index=False)
    summary = summarize(results)
    summary.to_csv(summary_path, index=False)
    comparisons = summarize_paired_comparisons(results)
    comparisons.to_csv(comparisons_path, index=False)
    all_datasets = load_benchmark_datasets()
    summary_wide = summary.pivot(
        index=["dataset", "mechanism", "mask_rate"],
        columns="method",
        values="mean_rmse",
    )
    proposed = summary_wide["proposed_iterative_multiple"]
    win_rows = []
    for baseline in (
        "mean",
        "median",
        "knn_k5",
        "iterative_bayesian_ridge",
    ):
        win_rows.append({
            "comparison": f"proposed lower mean RMSE than {baseline}",
            "conditions_won": int((proposed < summary_wide[baseline]).sum()),
            "conditions_total": len(summary_wide),
        })
    comparison_counts = []
    for (metric, baseline), group in comparisons.groupby(["metric", "baseline"], sort=True):
        comparison_counts.append({
            "metric": metric,
            "baseline": baseline,
            "paired_95_ci_below_zero": int((group["paired_difference_ci95_high"] < 0).sum()),
            "paired_95_ci_above_zero": int((group["paired_difference_ci95_low"] > 0).sum()),
            "paired_95_ci_includes_zero": int(
                (
                    (group["paired_difference_ci95_low"] <= 0)
                    & (group["paired_difference_ci95_high"] >= 0)
                ).sum()
            ),
            "conditions": len(group),
        })
    dataset_descriptions = [
        f"{name}: target `{all_datasets[name][1]}`, MAR predictor `{all_datasets[name][2]}`"
        for name in sorted(results["dataset"].unique())
    ]
    report = "\n".join([
        "# Missing-data imputation benchmark",
        "",
        f"Datasets: {', '.join(sorted(results['dataset'].unique()))}.",
        "Targets and MAR predictors: " + "; ".join(dataset_descriptions) + ".",
        f"Mechanisms: {', '.join(args.mechanisms)}; seeds start at {args.seed}; "
        f"trials per condition: {args.trials}.",
        f"Configured mask rates: {', '.join(f'{rate:.0%}' for rate in args.mask_rates)}.",
        "",
        "Metrics are computed only on artificially masked, originally observed target values. "
        "Per-method error CIs are t-based 95% intervals over repeated masks on each fixed dataset; "
        "they do not quantify uncertainty across datasets or populations. Runtime is descriptive "
        "and has no confidence interval.",
        "",
        "## Proposed-method comparisons",
        "",
        "Counts below compare condition-level mean RMSEs; they are descriptive, not significance tests.",
        "",
        pd.DataFrame(win_rows).to_markdown(index=False),
        "",
        "## Paired method differences",
        "",
        "Differences are proposed minus baseline (negative favors proposed). These are "
        "exploratory, unadjusted paired t-based 95% intervals over identical trial masks; "
        "they are not confirmatory significance tests.",
        "",
        pd.DataFrame(comparison_counts).to_markdown(index=False),
        "",
        f"Per-condition paired intervals: `{comparisons_path.name}`.",
        "",
        "## Results by condition and method",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
    ])
    report_path.write_text(report, encoding="utf-8")
    print(f"Raw trials: {raw_path} ({len(results)} method-trial rows)")
    print(f"Summary: {summary_path} ({len(summary)} condition-method rows)")
    print(f"Paired comparisons: {comparisons_path} ({len(comparisons)} rows)")
    print(report)
