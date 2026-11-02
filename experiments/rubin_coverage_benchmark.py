"""Run the pre-registered v4 Rubin coverage study or its sanity-only gate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import time
import traceback
from typing import Any

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from common import save_environment
from datasets.registry import CACHE_DIR, DATASETS, MANIFEST_PATH, fetch_dataset
from run_real_datasets import (
    MECHANISMS,
    ObservedScaler,
    _calibrate_intercept,
)
from rubin_study.imputers import (
    analyze_column_mean,
    analyze_ols_coefficient,
    impute_m_datasets,
    naive_single_imputation_interval,
)
from app.services.imputation_uncertainty import (  # type: ignore[reportMissingImports]
    pool_rubins_rules,
)


EXPERIMENTS_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = EXPERIMENTS_DIR.parent
PROTOCOL_PATH = EXPERIMENTS_DIR / "RUBIN_COVERAGE_PROTOCOL.md"
RESULTS_ROOT = EXPERIMENTS_DIR / "results"
ELIGIBLE_DATASETS = (
    "adult",
    "bank-marketing",
    "breast-w",
    "credit-approval",
    "credit-g",
    "diabetes",
    "heart-statlog",
    "pc1",
    "telco-customer-churn",
    "wine-quality-red",
)
MASK_RATES = (0.10, 0.30, 0.50)
DELTA_GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)
METHODS = ("median", "knn", "mice_improper", "mice_proper")
ESTIMANDS = ("mean", "ols_slope")
MASTER_SEED = 42
SAMPLE_SIZE = 500
SANITY_TRIALS = tuple(range(100))
RAW_COLUMNS = (
    "run_key",
    "dataset",
    "estimand",
    "mechanism",
    "mask_rate",
    "delta_sd",
    "delta_raw",
    "method",
    "m",
    "trial",
    "master_seed",
    "trial_seed",
    "mask_seed",
    "imputation_seeds",
    "bootstrap_seeds",
    "n_rows",
    "population_n",
    "sample_n",
    "n_columns",
    "x1",
    "x2",
    "observed_x2_sd",
    "realized_mask_rate",
    "truth",
    "estimate",
    "within_variances",
    "pooled_estimate",
    "within_imputation_variance",
    "between_imputation_variance",
    "total_variance",
    "standard_error",
    "degrees_of_freedom",
    "ci_lower",
    "ci_upper",
    "ci_width",
    "ci_covers_truth",
    "bias",
    "interval_type",
    "interval_reason",
    "status",
    "failure_stage",
    "attempt",
    "error_type",
    "error_message",
    "traceback",
    "elapsed_seconds",
)
FAILURE_COLUMNS = (
    "run_key",
    "dataset",
    "mechanism",
    "mask_rate",
    "delta_sd",
    "method",
    "m",
    "trial",
    "estimand",
    "stage",
    "attempt",
    "error_type",
    "error_message",
    "traceback",
    "mask_seed",
    "trial_seed",
    "imputation_seeds",
    "bootstrap_seeds",
    "elapsed_seconds",
)


def _git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _protocol_hash() -> str:
    return hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest()


def _feature_cohort(
    name: str
) -> dict[str, Any]:
    spec = DATASETS[name]
    features, target, fetched = fetch_dataset(spec, CACHE_DIR)
    target_observed = target.notna()
    features = features.loc[target_observed].reset_index(drop=True)
    target = target.loc[target_observed].reset_index(drop=True)
    numeric_features = [
        column
        for column in features.columns
        if fetched["feature_types"].get(column, "").lower() == "numeric"
        and features[column].notna().all()
        and features[column].nunique(dropna=True) > 1
    ]
    if len(numeric_features) < 2:
        raise ValueError(
            f"{name} has fewer than two naturally complete nonconstant numeric features"
        )
    qualifying_features = [
        column for column in numeric_features
        if features[column].nunique(dropna=True) >= 10
    ]
    if len(qualifying_features) < 2:
        raise ValueError(
            f"{name} has fewer than two naturally complete numeric features "
            "with at least 10 distinct values"
        )
    features = features.loc[:, numeric_features]
    features = features.reset_index(drop=True).astype(float)
    if len(features) < 100:
        raise ValueError(f"{name} has fewer than 100 complete-target rows")
    if not np.isfinite(features.to_numpy()).all():
        raise ValueError(f"{name} eligible numeric cohort is not fully finite")
    x1, x2 = qualifying_features[:2]
    scaler = ObservedScaler.fit(features.to_numpy(dtype=float))
    mean_truth = analyze_column_mean(features, x2)[0]
    slope_truth = analyze_ols_coefficient(features, x2, x1)[0]
    if not np.isfinite([mean_truth, slope_truth]).all():
        raise ValueError(f"{name} has a non-finite pre-mask estimand")
    return {
        "name": name,
        "features": features,
        "numeric_columns": numeric_features,
        "x1": x1,
        "x2": x2,
        "x1_nunique": int(features[x1].nunique(dropna=True)),
        "x2_nunique": int(features[x2].nunique(dropna=True)),
        "scaler": scaler,
        "scaled": scaler.transform(features.to_numpy(dtype=float)),
        "truths": {"mean": mean_truth, "ols_slope": slope_truth},
        "n_rows": len(features),
        "population_n": len(features),
        "n_columns": len(numeric_features),
        "source": fetched["source"],
        "data_id": fetched["data_id"],
        "version": fetched["version"],
    }


def _seed_schedule(
    dataset_index: int, trial: int, mechanism: str
) -> tuple[int, int]:
    trial_seed = MASTER_SEED + 100_000 * dataset_index + 1_000 * trial
    mask_seed = trial_seed + MECHANISMS.index(mechanism)
    return trial_seed, mask_seed


def _sample_population(dataset: dict[str, Any], trial_seed: int) -> pd.DataFrame:
    """Draw the replicate bootstrap sample from the full eligible population."""
    population = dataset["features"]
    sample_n = min(SAMPLE_SIZE, len(population))
    rng = np.random.RandomState(trial_seed)
    indices = rng.choice(len(population), size=sample_n, replace=True)
    return population.iloc[indices].reset_index(drop=True)


def _x2_mask(
    sample: pd.DataFrame,
    dataset: dict[str, Any],
    mechanism: str,
    rate: float,
    seed: int,
) -> np.ndarray:
    """Generate an x2-only mask with x1 as the MAR driver."""
    if mechanism not in MECHANISMS:
        raise ValueError(f"Unsupported missingness mechanism: {mechanism}")
    if not 0 < rate < 1:
        raise ValueError("Mask rate must be strictly between zero and one")
    scaled = dataset["scaler"].transform(sample.to_numpy(dtype=float))
    x1_position = dataset["numeric_columns"].index(dataset["x1"])
    x2_position = dataset["numeric_columns"].index(dataset["x2"])
    x1 = scaled[:, x1_position]
    x2 = scaled[:, x2_position]
    if mechanism == "MCAR":
        probabilities = np.full(len(sample), rate, dtype=float)
    else:
        driver = x1 if mechanism == "MAR" else x2
        intercept = _calibrate_intercept(2.0 * driver, rate)
        probabilities = 1.0 / (
            1.0 + np.exp(-np.clip(2.0 * driver + intercept, -35, 35))
        )
    rng = np.random.RandomState(seed)
    x2_mask = rng.random_sample(len(sample)) < probabilities
    if int(x2_mask.sum()) > len(sample) - 5:
        observed_positions = np.flatnonzero(x2_mask)
        restore_count = int(x2_mask.sum()) - (len(sample) - 5)
        x2_mask[rng.choice(observed_positions, size=restore_count, replace=False)] = False
    if not x2_mask.any():
        x2_mask[rng.randint(len(sample))] = True
    mask = np.zeros(sample.shape, dtype=bool)
    mask[:, x2_position] = x2_mask
    return mask


def _key(
    dataset: str,
    mechanism: str,
    rate: float,
    delta_sd: float,
    method: str,
    m: int,
    trial: int,
    estimand: str,
) -> str:
    return json.dumps(
        [dataset, mechanism, rate, delta_sd, method, m, trial, estimand],
        separators=(",", ":"),
    )


def _analysis(frame: pd.DataFrame, estimand: str, x1: str, x2: str):
    if estimand == "mean":
        return analyze_column_mean(frame, x2)
    return analyze_ols_coefficient(frame, x2, x1)


def _make_record(
    *,
    task: dict[str, Any],
    dataset: dict[str, Any],
    mechanism: str,
    rate: float,
    delta_sd: float,
    delta_raw: float,
    method: str,
    m: int,
    trial: int,
    trial_seed: int,
    mask_seed: int,
    imputation_seeds: list[int],
    bootstrap_seeds: list[int],
    observed_x2_sd: float,
    estimand: str,
    completed: list[pd.DataFrame],
    started: float,
) -> dict[str, Any]:
    truth = float(dataset["truths"][estimand])
    shifted: list[pd.DataFrame] = []
    for frame in completed:
        adjusted = frame.copy(deep=True)
        if delta_raw:
            missing_outcome = task["mask"][:, task["x2_position"]]
            values = adjusted[dataset["x2"]].to_numpy(copy=True)
            values[missing_outcome] += delta_raw
            adjusted[dataset["x2"]] = values
        shifted.append(adjusted)

    analyses = [
        _analysis(frame, estimand, dataset["x1"], dataset["x2"])
        for frame in shifted
    ]
    estimates = [float(item[0]) for item in analyses]
    variances = [float(item[1]) for item in analyses]
    if method in {"median", "knn"}:
        estimate, variance, complete_df = analyses[0]
        from rubin_study.imputers import naive_single_imputation_interval

        interval = naive_single_imputation_interval(
            estimate, variance, complete_df, confidence_level=0.95
        )
        lower, upper = interval["confidence_interval"]
        pooled = None
        interval_type = "naive single imputation"
    else:
        complete_df_values = [float(item[2]) for item in analyses]
        if not np.allclose(complete_df_values, complete_df_values[0]):
            raise ValueError("complete-data degrees of freedom differ across imputations")
        pooled = pool_rubins_rules(
            estimates,
            variances,
            complete_data_df=complete_df_values[0],
        )
        estimate = pooled.estimate
        lower, upper = pooled.confidence_interval or (np.nan, np.nan)
        interval_type = "Rubin pooled Barnard-Rubin"
    finite_ci = np.isfinite([lower, upper]).all()
    return {
        "run_key": _key(
            dataset["name"], mechanism, rate, delta_sd, method, m, trial, estimand
        ),
        "dataset": dataset["name"],
        "estimand": estimand,
        "mechanism": mechanism,
        "mask_rate": rate,
        "delta_sd": delta_sd,
        "delta_raw": delta_raw,
        "method": method,
        "m": m,
        "trial": trial,
        "master_seed": MASTER_SEED,
        "trial_seed": trial_seed,
        "mask_seed": mask_seed,
        "imputation_seeds": json.dumps(imputation_seeds),
        "bootstrap_seeds": json.dumps(bootstrap_seeds),
        "n_rows": dataset["n_rows"],
        "population_n": dataset["population_n"],
        "sample_n": len(task["mask"]),
        "n_columns": dataset["n_columns"],
        "x1": dataset["x1"],
        "x2": dataset["x2"],
        "observed_x2_sd": observed_x2_sd,
        "realized_mask_rate": float(
            task["mask"][:, task["x2_position"]].mean()
        ),
        "truth": truth,
        "estimate": float(estimate),
        "within_variances": json.dumps(variances),
        "pooled_estimate": pooled.estimate if pooled else np.nan,
        "within_imputation_variance": (
            pooled.within_imputation_variance if pooled else np.nan
        ),
        "between_imputation_variance": (
            pooled.between_imputation_variance if pooled else np.nan
        ),
        "total_variance": pooled.total_variance if pooled else np.nan,
        "standard_error": pooled.standard_error if pooled else np.sqrt(variance),
        "degrees_of_freedom": (
            pooled.degrees_of_freedom if pooled else float(complete_df)
        ),
        "ci_lower": float(lower) if finite_ci else np.nan,
        "ci_upper": float(upper) if finite_ci else np.nan,
        "ci_width": float(upper - lower) if finite_ci else np.nan,
        "ci_covers_truth": bool(finite_ci and lower <= truth <= upper),
        "bias": float(estimate - truth),
        "interval_type": interval_type,
        "interval_reason": (
            "Barnard-Rubin degrees of freedom are zero"
            if pooled is not None and pooled.confidence_interval is None
            else ""
        ),
        "status": "success",
        "elapsed_seconds": time.perf_counter() - started,
    }


def _run_seed_task(
    dataset: dict[str, Any],
    mechanism: str,
    rate: float,
    trial: int,
    m_values: tuple[int, ...],
    include_deltas: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trial_seed, mask_seed = _seed_schedule(
        list(DATASETS).index(dataset["name"]), trial, mechanism
    )
    task_started = time.perf_counter()
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    try:
        sample = _sample_population(dataset, trial_seed)
        mask = _x2_mask(
            sample,
            dataset,
            mechanism,
            rate,
            mask_seed,
        )
        masked = sample.mask(mask)
    except Exception as error:
        delta_values = DELTA_GRID if include_deltas else (0.0,)
        for method in METHODS:
            method_m_values = (1,) if method in {"median", "knn"} else m_values
            for m, delta_sd, estimand in itertools.product(
                method_m_values, delta_values, ESTIMANDS
            ):
                failures.append({
                    "run_key": _key(
                        dataset["name"], mechanism, rate, delta_sd,
                        method, m, trial, estimand,
                    ),
                    "dataset": dataset["name"],
                    "mechanism": mechanism,
                    "mask_rate": rate,
                    "delta_sd": delta_sd,
                    "method": method,
                    "m": m,
                    "trial": trial,
                    "estimand": estimand,
                    "stage": "masking",
                    "attempt": 1,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "traceback": traceback.format_exc(),
                    "mask_seed": mask_seed,
                    "trial_seed": trial_seed,
                    "elapsed_seconds": time.perf_counter() - task_started,
                })
        return records, failures

    replicate_dataset = {
        **dataset,
        "features": sample,
        "n_rows": len(sample),
        "sample_n": len(sample),
    }
    task = {
        "mask": mask,
        "x2_position": dataset["numeric_columns"].index(dataset["x2"]),
    }
    observed_x2 = masked[dataset["x2"]].dropna().to_numpy(dtype=float)
    observed_x2_sd = (
        float(np.std(observed_x2, ddof=1)) if len(observed_x2) > 1 else np.nan
    )
    delta_values = DELTA_GRID if include_deltas else (0.0,)
    for method in METHODS:
        method_m_values = (1,) if method in {"median", "knn"} else m_values
        for m in method_m_values:
            method_started = time.perf_counter()
            try:
                completed = impute_m_datasets(
                    masked,
                    m=m,
                    seed=trial_seed,
                    method=method,
                )
                imputation_seeds = (
                    [trial_seed + 100 + draw for draw in range(m)]
                    if method == "mice_improper"
                    else (
                        [trial_seed + 200 + draw for draw in range(m)]
                        if method == "mice_proper"
                        else []
                    )
                )
                bootstrap_seeds = (
                    [trial_seed + 100 + draw for draw in range(m)]
                    if method == "mice_proper"
                    else []
                )
            except Exception as error:
                for delta_sd in delta_values:
                    for estimand in ESTIMANDS:
                        failures.append({
                            "run_key": _key(
                                dataset["name"], mechanism, rate, delta_sd,
                                method, m, trial, estimand,
                            ),
                            "dataset": dataset["name"],
                            "mechanism": mechanism,
                            "mask_rate": rate,
                            "delta_sd": delta_sd,
                            "method": method,
                            "m": m,
                            "trial": trial,
                            "estimand": estimand,
                            "stage": "imputation",
                            "attempt": 1,
                            "error_type": type(error).__name__,
                            "error_message": str(error),
                            "traceback": traceback.format_exc(),
                            "mask_seed": mask_seed,
                            "trial_seed": trial_seed,
                            "elapsed_seconds": time.perf_counter() - method_started,
                        })
                continue

            for delta_sd in delta_values:
                if mechanism == "MNAR":
                    if not np.isfinite(observed_x2_sd) or observed_x2_sd <= 0:
                        for estimand in ESTIMANDS:
                            failures.append({
                                "run_key": _key(
                                    dataset["name"], mechanism, rate, delta_sd,
                                    method, m, trial, estimand,
                                ),
                                "dataset": dataset["name"],
                                "mechanism": mechanism,
                                "mask_rate": rate,
                                "delta_sd": delta_sd,
                                "method": method,
                                "m": m,
                                "trial": trial,
                                "estimand": estimand,
                                "stage": "mnar_delta",
                                "attempt": 1,
                                "error_type": "ValueError",
                                "error_message": "observed x2 standard deviation must be finite and positive",
                                "traceback": "",
                                "mask_seed": mask_seed,
                                "trial_seed": trial_seed,
                                "elapsed_seconds": time.perf_counter() - method_started,
                            })
                        continue
                    delta_raw = delta_sd * observed_x2_sd
                else:
                    delta_raw = 0.0
                for estimand in ESTIMANDS:
                    try:
                        records.append(_make_record(
                            task=task,
                            dataset=replicate_dataset,
                            mechanism=mechanism,
                            rate=rate,
                            delta_sd=delta_sd if mechanism == "MNAR" else 0.0,
                            delta_raw=delta_raw,
                            method=method,
                            m=m,
                            trial=trial,
                            trial_seed=trial_seed,
                            mask_seed=mask_seed,
                            imputation_seeds=imputation_seeds,
                            bootstrap_seeds=bootstrap_seeds,
                            observed_x2_sd=observed_x2_sd,
                            estimand=estimand,
                            completed=completed,
                            started=method_started,
                        ))
                    except Exception as error:
                        failures.append({
                            "run_key": _key(
                                dataset["name"], mechanism, rate,
                                delta_sd if mechanism == "MNAR" else 0.0,
                                method, m, trial, estimand,
                            ),
                            "dataset": dataset["name"],
                            "mechanism": mechanism,
                            "mask_rate": rate,
                            "delta_sd": delta_sd if mechanism == "MNAR" else 0.0,
                            "method": method,
                            "m": m,
                            "trial": trial,
                            "estimand": estimand,
                            "stage": "analysis_or_pooling",
                            "attempt": 1,
                            "error_type": type(error).__name__,
                            "error_message": str(error),
                            "traceback": traceback.format_exc(),
                            "mask_seed": mask_seed,
                            "trial_seed": trial_seed,
                            "elapsed_seconds": time.perf_counter() - method_started,
                        })
    return records, failures


def _run_sanity_task(
    dataset: dict[str, Any], trial: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run the pre-specified complete-data interval sanity replicate."""
    trial_seed, _ = _seed_schedule(
        list(DATASETS).index(dataset["name"]), trial, "MCAR"
    )
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    try:
        sample = _sample_population(dataset, trial_seed)
    except Exception as error:
        for estimand in ESTIMANDS:
            failures.append({
                "run_key": _key(
                    dataset["name"], "NONE", 0.0, 0.0,
                    "no_missing_sanity", 1, trial, estimand,
                ),
                "dataset": dataset["name"],
                "mechanism": "NONE",
                "mask_rate": 0.0,
                "delta_sd": 0.0,
                "method": "no_missing_sanity",
                "m": 1,
                "trial": trial,
                "estimand": estimand,
                "stage": "no_missing_sanity_sampling",
                "attempt": 1,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "mask_seed": np.nan,
                "trial_seed": trial_seed,
                "elapsed_seconds": time.perf_counter() - started,
            })
        return records, failures

    for estimand in ESTIMANDS:
        try:
            estimate, variance, complete_df = _analysis(
                sample, estimand, dataset["x1"], dataset["x2"]
            )
            interval = naive_single_imputation_interval(
                estimate, variance, complete_df, confidence_level=0.95
            )
            lower, upper = interval["confidence_interval"]
            records.append({
                "run_key": _key(
                    dataset["name"], "NONE", 0.0, 0.0,
                    "no_missing_sanity", 1, trial, estimand,
                ),
                "dataset": dataset["name"],
                "estimand": estimand,
                "mechanism": "NONE",
                "mask_rate": 0.0,
                "delta_sd": 0.0,
                "delta_raw": 0.0,
                "method": "no_missing_sanity",
                "m": 1,
                "trial": trial,
                "master_seed": MASTER_SEED,
                "trial_seed": trial_seed,
                "mask_seed": np.nan,
                "imputation_seeds": "[]",
                "bootstrap_seeds": "[]",
                "n_rows": len(sample),
                "population_n": dataset["population_n"],
                "sample_n": len(sample),
                "n_columns": dataset["n_columns"],
                "x1": dataset["x1"],
                "x2": dataset["x2"],
                "observed_x2_sd": float(np.std(sample[dataset["x2"]], ddof=1)),
                "realized_mask_rate": 0.0,
                "truth": float(dataset["truths"][estimand]),
                "estimate": float(estimate),
                "within_variances": json.dumps([float(variance)]),
                "pooled_estimate": np.nan,
                "within_imputation_variance": np.nan,
                "between_imputation_variance": np.nan,
                "total_variance": np.nan,
                "standard_error": float(interval["standard_error"]),
                "degrees_of_freedom": float(complete_df),
                "ci_lower": float(lower),
                "ci_upper": float(upper),
                "ci_width": float(upper - lower),
                "ci_covers_truth": bool(
                    lower <= dataset["truths"][estimand] <= upper
                ),
                "bias": float(estimate - dataset["truths"][estimand]),
                "interval_type": "complete-data t interval (no missing; m=1)",
                "interval_reason": "",
                "status": "success",
                "failure_stage": "",
                "attempt": 1,
                "error_type": "",
                "error_message": "",
                "traceback": "",
                "elapsed_seconds": time.perf_counter() - started,
            })
        except Exception as error:
            failures.append({
                "run_key": _key(
                    dataset["name"], "NONE", 0.0, 0.0,
                    "no_missing_sanity", 1, trial, estimand,
                ),
                "dataset": dataset["name"],
                "mechanism": "NONE",
                "mask_rate": 0.0,
                "delta_sd": 0.0,
                "method": "no_missing_sanity",
                "m": 1,
                "trial": trial,
                "estimand": estimand,
                "stage": "no_missing_sanity",
                "attempt": 1,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "mask_seed": np.nan,
                "trial_seed": trial_seed,
                "elapsed_seconds": time.perf_counter() - started,
            })
    return records, failures


def _append_rows(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    if not rows:
        return
    frame = pd.DataFrame(rows).reindex(columns=columns)
    frame.to_csv(path, mode="a", index=False, header=not path.exists())
    with path.open("a", encoding="utf-8") as stream:
        stream.flush()
        os.fsync(stream.fileno())


def _read_completed_keys(raw_path: Path) -> set[str]:
    if not raw_path.exists() or raw_path.stat().st_size == 0:
        return set()
    frame = pd.read_csv(raw_path, usecols=["run_key", "status"])
    return set(frame.loc[frame["status"].eq("success"), "run_key"].astype(str))


def _failure_as_raw_row(failure: dict[str, Any]) -> dict[str, Any]:
    """Keep failed attempts in raw.csv while retaining their detailed log."""
    row = {column: np.nan for column in RAW_COLUMNS}
    for column in (
        "run_key", "dataset", "mechanism", "mask_rate", "delta_sd",
        "method", "m",         "trial", "estimand", "trial_seed", "mask_seed",
        "imputation_seeds", "bootstrap_seeds", "elapsed_seconds", "attempt",
        "error_type", "error_message", "traceback",
    ):
        if column in failure:
            row[column] = failure[column]
    row.update({
        "master_seed": MASTER_SEED,
        "status": "failed",
        "failure_stage": failure.get("stage", ""),
        "interval_reason": failure.get("error_message", ""),
    })
    return row


def _write_sanity_summary(
    raw_path: Path,
    failures_path: Path,
    output_path: Path,
    datasets: list[dict[str, Any]],
) -> None:
    """Write a separate per-dataset/estimand sanity gate status report."""
    raw = pd.read_csv(raw_path)
    sanity = raw.loc[
        raw["method"].eq("no_missing_sanity") & raw["status"].eq("success")
    ]
    failures = pd.read_csv(failures_path)
    if not failures.empty:
        failures = failures.loc[failures["method"].eq("no_missing_sanity")]

    rows = []
    for dataset in datasets:
        for estimand in ESTIMANDS:
            successful_group = sanity.loc[
                sanity["dataset"].eq(dataset["name"])
                & sanity["estimand"].eq(estimand)
                & sanity["trial"].isin(SANITY_TRIALS)
            ]
            failed_group = (
                failures.loc[
                    failures["dataset"].eq(dataset["name"])
                    & failures["estimand"].eq(estimand)
                    & failures["trial"].isin(SANITY_TRIALS)
                ]
                if not failures.empty
                else pd.DataFrame()
            )
            successful_runs = len(successful_group)
            failed_runs = len(failed_group)
            coverage = (
                float(successful_group["ci_covers_truth"].astype(bool).mean())
                if successful_runs
                else np.nan
            )
            completed_trials = set(successful_group["trial"].astype(int))
            if not set(SANITY_TRIALS).issubset(completed_trials):
                status = "incomplete"
            elif coverage < 0.91 or coverage > 0.99:
                status = "sanity-failed"
            else:
                status = "sanity-passed"
            rows.append({
                "dataset": dataset["name"],
                "estimand": estimand,
                "expected_trials": len(SANITY_TRIALS),
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "attempted_runs": successful_runs + failed_runs,
                "coverage": coverage,
                "sanity_status": status,
            })
    pd.DataFrame(rows).to_csv(output_path, index=False)


def _read_failure_attempts(failures_path: Path) -> dict[str, int]:
    if not failures_path.exists() or failures_path.stat().st_size == 0:
        return {}
    frame = pd.read_csv(failures_path, usecols=["run_key"])
    return frame.groupby("run_key").size().astype(int).to_dict()


def _run_configuration(args: argparse.Namespace, datasets: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "protocol": PROTOCOL_PATH.name,
        "protocol_sha256": _protocol_hash(),
        "dataset_manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
        "git_commit": _git_commit(),
        "master_seed": MASTER_SEED,
        "datasets": [
            {
                "name": item["name"],
                "data_id": item["data_id"],
                "version": item["version"],
                "source": item["source"],
                "dataset_sha256": manifest[item["name"]]["sha256"],
                "n_rows": item["n_rows"],
                "population_n": item["population_n"],
                "replicate_sample_n": min(SAMPLE_SIZE, item["population_n"]),
                "n_columns": item["n_columns"],
                "columns": item["numeric_columns"],
                "x1": item["x1"],
                "x2": item["x2"],
                "x1_nunique": item["x1_nunique"],
                "x2_nunique": item["x2_nunique"],
                "truths": item["truths"],
            }
            for item in datasets
        ],
        "mechanisms": [] if args.sanity_only else list(MECHANISMS),
        "mask_rates": [] if args.sanity_only else list(MASK_RATES),
        "methods": ["no_missing_sanity"] if args.sanity_only else list(METHODS),
        "m_values": list(args.m_values),
        "trials": list(args.trials),
        "deltas_sd": [] if args.sanity_only else list(DELTA_GRID),
        "row_sampling_rule": (
            "For every trial, sample min(500, full eligible population N) rows "
            "with replacement using trial_seed before any mask."
        ),
        "no_missing_sanity": {
            "trials": list(args.trials),
            "sanity_only": args.sanity_only,
            "m": 1,
            "mask": "none",
            "interval": "complete-data two-sided Student-t 95% interval",
            "flag_outside_coverage_range": [0.91, 0.99],
        },
        "seed_schedule": {
            "trial_seed": "42 + 100000 * dataset_registry_index + 1000 * trial",
            "mask_seed": "trial_seed + mechanism_index (MCAR=0, MAR=1, MNAR=2)",
            "mice_improper": "trial_seed + 100 + draw",
            "mice_proper_bootstrap": "trial_seed + 100 + draw",
            "mice_proper_imputer": "trial_seed + 200 + draw",
        },
        "n_jobs": args.n_jobs,
        "pilot": args.pilot,
        "quick": args.quick,
        "sanity_only": args.sanity_only,
    }


def _prepare_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=None, help="Output tag under experiments/results.")
    parser.add_argument("--datasets", nargs="+", choices=ELIGIBLE_DATASETS)
    parser.add_argument(
        "--seeds",
        type=int,
        default=100,
        help="Number of pre-specified trial indices, starting at zero (default: 100).",
    )
    parser.add_argument("--quick", action="store_true", help="Run 2 small datasets and 2 seeds (smoke run).")
    parser.add_argument("--pilot", action="store_true", help="Run 2 smallest eligible datasets, 20 seeds, and m=5.")
    parser.add_argument(
        "--sanity-only",
        action="store_true",
        help="Run only the no-mask m=1 sanity gate for all selected datasets and 100 trials.",
    )
    parser.add_argument("--n-jobs", type=int, default=1, help="Joblib worker count (default: 1; -1 uses all CPUs).")
    return parser


def run(args: argparse.Namespace) -> Path:
    if sum((args.quick, args.pilot, args.sanity_only)) > 1:
        raise ValueError("--quick, --pilot, and --sanity-only are mutually exclusive")
    if args.seeds < 1:
        raise ValueError("--seeds must be positive")
    if args.sanity_only:
        if args.datasets is not None:
            raise ValueError("--sanity-only always runs all selected datasets; omit --datasets")
        if args.seeds != 100:
            raise ValueError("--sanity-only uses exactly 100 trials; omit --seeds or set it to 100")
        chosen = list(ELIGIBLE_DATASETS)
        trials = tuple(range(100))
        m_values = (1,)
    elif args.pilot:
        if args.datasets is not None and len(args.datasets) != 2:
            raise ValueError("--pilot requires exactly two datasets if --datasets is supplied")
        chosen = args.datasets or sorted(
            ELIGIBLE_DATASETS, key=lambda name: (DATASETS[name].n_rows, name)
        )[:2]
        trials = tuple(range(20))
        m_values = (5,)
    elif args.quick:
        chosen = args.datasets or sorted(
            ELIGIBLE_DATASETS, key=lambda name: (DATASETS[name].n_rows, name)
        )[:2]
        trials = tuple(range(2))
        m_values = (5,)
    else:
        chosen = args.datasets or list(ELIGIBLE_DATASETS)
        trials = tuple(range(args.seeds))
        m_values = (5, 20)
    tag = args.tag or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = RESULTS_ROOT / f"rubin_coverage_{tag}"
    output_dir.mkdir(parents=True, exist_ok=True)

    prepared = []
    for name in chosen:
        dataset_index = list(DATASETS).index(name)
        prepared.append(_feature_cohort(name))

    config = _run_configuration(
        argparse.Namespace(**vars(args), trials=trials, m_values=m_values),
        prepared,
    )
    config_path = output_dir / "run_config.json"
    if config_path.exists():
        existing = json.loads(config_path.read_text(encoding="utf-8"))
        comparable = dict(existing)
        comparable.pop("n_jobs", None)
        proposed = dict(config)
        proposed.pop("n_jobs", None)
        if comparable != proposed:
            raise ValueError(f"Existing output directory has a different run configuration: {output_dir}")
    else:
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    import common

    common.RESULTS_DIR = str(output_dir)
    save_environment(
        extra={
            "git_commit": config["git_commit"],
            "protocol_sha256": config["protocol_sha256"],
            "run_tag": tag,
        },
        name="environment.json",
    )

    raw_path = output_dir / "raw.csv"
    failures_path = output_dir / "failures.csv"
    if not raw_path.exists():
        pd.DataFrame(columns=RAW_COLUMNS).to_csv(raw_path, index=False)
    if not failures_path.exists():
        pd.DataFrame(columns=FAILURE_COLUMNS).to_csv(failures_path, index=False)
    completed_keys = _read_completed_keys(raw_path)
    failure_attempts = _read_failure_attempts(failures_path)
    jobs = []
    for dataset in prepared:
        for trial in trials:
            sanity_keys = [
                _key(
                    dataset["name"], "NONE", 0.0, 0.0,
                    "no_missing_sanity", 1, trial, estimand,
                )
                for estimand in ESTIMANDS
            ]
            if not all(key in completed_keys for key in sanity_keys):
                jobs.append((dataset, "NONE", 0.0, trial))
        if args.sanity_only:
            continue
        for mechanism, rate, trial in itertools.product(
            MECHANISMS, MASK_RATES, trials
        ):
            expected_deltas = DELTA_GRID if mechanism == "MNAR" else (0.0,)
            expected_methods = [
                (method, 1 if method in {"median", "knn"} else m)
                for method in METHODS
                for m in ((1,) if method in {"median", "knn"} else m_values)
            ]
            expected_keys = [
                _key(dataset["name"], mechanism, rate, delta, method, m, trial, estimand)
                for delta, (method, m), estimand in itertools.product(
                    expected_deltas, expected_methods, ESTIMANDS
                )
            ]
            if all(key in completed_keys for key in expected_keys):
                continue
            jobs.append((dataset, mechanism, rate, trial))

    print(f"Output directory: {output_dir}", flush=True)
    print(f"Scheduled seed-condition tasks: {len(jobs)}", flush=True)
    parallel = Parallel(
        n_jobs=args.n_jobs,
        return_as="generator_unordered",
        batch_size=1,
    )
    for records, failures in parallel(
        (
            delayed(_run_sanity_task)(dataset, trial)
            if mechanism == "NONE"
            else delayed(_run_seed_task)(
                dataset,
                mechanism,
                rate,
                trial,
                m_values,
                mechanism == "MNAR",
            )
        )
        for dataset, mechanism, rate, trial in jobs
    ):
        new_records = [row for row in records if row["run_key"] not in completed_keys]
        _append_rows(raw_path, new_records, RAW_COLUMNS)
        completed_keys.update(row["run_key"] for row in new_records)
        for failure in failures:
            failure["attempt"] = failure_attempts.get(failure["run_key"], 0) + 1
            failure_attempts[failure["run_key"]] = failure["attempt"]
            m = int(failure.get("m", 0))
            trial_seed = int(failure.get("trial_seed", 0))
            method = failure.get("method")
            failure["imputation_seeds"] = json.dumps(
                [trial_seed + (200 if method == "mice_proper" else 100) + draw
                 for draw in range(m)]
                if method in {"mice_improper", "mice_proper"} else []
            )
            failure["bootstrap_seeds"] = json.dumps(
                [trial_seed + 100 + draw for draw in range(m)]
                if method == "mice_proper" else []
            )
        _append_rows(failures_path, failures, FAILURE_COLUMNS)
        _append_rows(
            raw_path,
            [_failure_as_raw_row(failure) for failure in failures],
            RAW_COLUMNS,
        )
        if new_records or failures:
            print(
                f"appended raw={len(new_records)} failures={len(failures)}",
                flush=True,
            )
    _write_sanity_summary(
        raw_path,
        failures_path,
        output_dir / "sanity_summary.csv",
        prepared,
    )
    return output_dir


def main() -> None:
    parser = _prepare_args()
    args = parser.parse_args()
    try:
        output_dir = run(args)
    except Exception as error:
        parser.exit(2, f"ERROR: {type(error).__name__}: {error}\n")
    print(f"Completed/resumable output: {output_dir}")


if __name__ == "__main__":
    main()
