"""Post-hoc point-estimate ablation for the real-dataset MICE benchmark."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

from datasets.registry import CACHE_DIR, DATASETS, fetch_dataset
from run_real_datasets import (
    MECHANISMS,
    ObservedScaler,
    _fit_transform_method,
    _metric_rows,
    _project_mice_complete,
    _project_mice_train_test,
    _stratified_row_cap,
    _uncertainty_metrics,
    make_mask,
    EncodedFrame,
)


RATE = 0.20
VARIANTS = (
    "project_m5",
    "project_m20",
    "project_m50",
    "project_deterministic",
    "project_deterministic_no_bounds",
    "project_m50_no_bounds",
    "project_hybrid_m20",
    "iterative_single_as_is",
    "iterative_single_posterior_true",
    "iterative_single_posterior_false",
)
DRAW_COUNTS = {
    "project_m5": 5,
    "project_m20": 20,
    "project_m50": 50,
    "project_m50_no_bounds": 50,
    "project_hybrid_m20": 20,
}
DRAW_VARIANTS = set(DRAW_COUNTS)
REPRO_VARIANTS = ("project_m5", "project_m20", "project_m50")
OUTPUT_COLUMNS = (
    "dataset",
    "mechanism",
    "mask_rate",
    "trial",
    "variant",
    "numeric_rmse",
    "rmse_ratio_vs_mean",
    "uncertainty_spearman_numeric",
    "uncertainty_coverage90_numeric",
    "elapsed_seconds",
)
REPRO_METHODS = {
    "project_m5": "mice_multiple_NEW",
    "iterative_single_as_is": "iterative_single",
}


def _dataset_protocol_frame(
    name: str, max_rows: int, seed: int
) -> tuple[pd.DataFrame, EncodedFrame, np.ndarray, ObservedScaler, np.ndarray]:
    features, target, _ = fetch_dataset(DATASETS[name], CACHE_DIR)
    features, target = _stratified_row_cap(features, target, max_rows, seed)
    complete = target.notna()
    features = features.loc[complete].reset_index(drop=True)
    target = target.loc[complete].reset_index(drop=True)
    complete_columns = [
        column
        for column in features
        if features[column].notna().all() and features[column].nunique(dropna=True) > 1
    ]
    features = features.loc[:, complete_columns]
    if len(features) < 100:
        raise ValueError(f"{name}: Protocol A requires at least 100 complete-target rows.")
    encoded = EncodedFrame.fit_transformer(features)
    raw = encoded.values.copy()
    scaler = ObservedScaler.fit(raw)
    numeric_scoring = encoded.numeric_columns & (raw.std(axis=0) >= 1e-8)
    return features, encoded, raw, scaler, numeric_scoring


def _seed_for(name: str, trial: int, seed: int) -> int:
    return seed + 100_000 * list(DATASETS).index(name) + 1_000 * trial + int(RATE * 100)


def _iterative_single(
    masked: np.ndarray, seed: int, sample_posterior: bool
) -> tuple[np.ndarray, None]:
    imputer = IterativeImputer(
        estimator=BayesianRidge(),
        sample_posterior=sample_posterior,
        max_iter=10,
        random_state=seed,
        skip_complete=True,
        keep_empty_features=True,
    )
    return imputer.fit_transform(masked), None


def _variant_estimate(
    variant: str, masked: np.ndarray, seed: int
) -> tuple[np.ndarray, np.ndarray | None]:
    if variant == "project_m5":
        estimate, uncertainty = _project_mice_complete(masked, seed)
        return estimate, uncertainty
    if variant in {"project_m20", "project_m50"}:
        count = int(variant.removeprefix("project_m"))
        _, estimate, uncertainty = _project_mice_train_test(
            masked, masked, seed, n_imputations=count
        )
        observed = np.isfinite(masked)
        estimate[observed] = masked[observed]
        uncertainty[observed] = np.nan
        return estimate, uncertainty
    if variant == "project_m50_no_bounds":
        estimate, uncertainty = _project_multiple_no_bounds(masked, seed, 50)
        return estimate, uncertainty
    if variant == "project_hybrid_m20":
        _, _, uncertainty = _project_mice_train_test(
            masked, masked, seed, n_imputations=20
        )
        estimate = _project_deterministic(masked, seed)
        observed = np.isfinite(masked)
        estimate[observed] = masked[observed]
        uncertainty[observed] = np.nan
        return estimate, uncertainty
    if variant == "project_deterministic":
        return _project_deterministic(masked, seed), None
    if variant == "project_deterministic_no_bounds":
        return _project_deterministic_no_bounds(masked, seed), None
    if variant == "iterative_single_as_is":
        # Keep this path identical to the existing harness dispatch.
        estimate, _, _ = _fit_transform_method(
            "iterative_single", masked, masked, seed
        )
        return estimate, None
    if variant == "iterative_single_posterior_true":
        estimate, _ = _iterative_single(masked, seed, sample_posterior=True)
        return estimate, None
    if variant == "iterative_single_posterior_false":
        estimate, _ = _iterative_single(masked, seed, sample_posterior=False)
        return estimate, None
    raise ValueError(f"Unknown ablation variant {variant!r}.")


def _project_deterministic(masked: np.ndarray, seed: int) -> np.ndarray:
    return _iterative_estimate(masked, seed, sample_posterior=False, bounded=True)


def _project_deterministic_no_bounds(masked: np.ndarray, seed: int) -> np.ndarray:
    return _iterative_estimate(masked, seed, sample_posterior=False, bounded=False)


def _project_multiple_no_bounds(
    masked: np.ndarray, seed: int, n_imputations: int
) -> tuple[np.ndarray, np.ndarray]:
    draws = []
    for draw in range(n_imputations):
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            sample_posterior=True,
            max_iter=10,
            random_state=seed + draw,
            skip_complete=True,
            keep_empty_features=True,
        )
        draws.append(imputer.fit_transform(masked))
    stack = np.stack(draws)
    estimate = stack.mean(axis=0)
    uncertainty = stack.std(axis=0, ddof=1)
    observed = np.isfinite(masked)
    estimate[observed] = masked[observed]
    uncertainty[observed] = np.nan
    return estimate, uncertainty


def _iterative_estimate(
    masked: np.ndarray, seed: int, sample_posterior: bool, bounded: bool
) -> np.ndarray:
    finite = np.isfinite(masked)
    options: dict[str, Any] = {}
    if bounded:
        mins = np.array([
            np.min(masked[finite[:, column], column])
            if finite[:, column].any() else -np.inf
            for column in range(masked.shape[1])
        ])
        maxs = np.array([
            np.max(masked[finite[:, column], column])
            if finite[:, column].any() else np.inf
            for column in range(masked.shape[1])
        ])
        constant = np.isfinite(mins) & np.isfinite(maxs) & (mins >= maxs)
        mins[constant] -= 1e-8
        maxs[constant] += 1e-8
        options = {"min_value": mins, "max_value": maxs}
    imputer = IterativeImputer(
        estimator=BayesianRidge(),
        sample_posterior=sample_posterior,
        max_iter=10,
        random_state=seed,
        skip_complete=True,
        keep_empty_features=True,
        **options,
    )
    return imputer.fit_transform(masked)


def _run_cell(
    name: str,
    raw: np.ndarray,
    encoded: EncodedFrame,
    scaler: ObservedScaler,
    numeric_scoring: np.ndarray,
    mechanism: str,
    trial: int,
    seed: int,
    variants: tuple[str, ...] = VARIANTS,
) -> list[dict[str, Any]]:
    trial_seed = _seed_for(name, trial, seed)
    scaled = scaler.transform(raw)
    mask = make_mask(
        scaled,
        mechanism,
        RATE,
        np.random.RandomState(trial_seed + MECHANISMS.index(mechanism)),
    )
    masked = np.where(mask, np.nan, scaled)
    mean_estimate, _, _ = _fit_transform_method("mean", masked, masked, trial_seed)
    mean_rmse = _metric_rows(
        raw, mean_estimate, mask, encoded, scaler,
        numeric_metric_columns=numeric_scoring,
    )["numeric_rmse"]
    rows = []
    for variant in variants:
        started = time.perf_counter()
        estimate, uncertainty = _variant_estimate(variant, masked, trial_seed)
        metrics = _metric_rows(
            raw, estimate, mask, encoded, scaler,
            numeric_metric_columns=numeric_scoring,
        )
        if uncertainty is not None and variant in DRAW_VARIANTS:
            coverage, spearman = _uncertainty_metrics(
                raw, estimate, uncertainty, mask, encoded, scaler,
                numeric_scoring, n_imputations=DRAW_COUNTS[variant],
            )
        else:
            coverage, spearman = np.nan, np.nan
        numeric_rmse = float(metrics["numeric_rmse"])
        rows.append({
            "dataset": name,
            "mechanism": mechanism,
            "mask_rate": RATE,
            "trial": trial,
            "variant": variant,
            "numeric_rmse": numeric_rmse,
            "rmse_ratio_vs_mean": (
                numeric_rmse / float(mean_rmse)
                if np.isfinite(mean_rmse) and mean_rmse != 0
                else np.nan
            ),
            "uncertainty_spearman_numeric": spearman,
            "uncertainty_coverage90_numeric": coverage,
            "elapsed_seconds": time.perf_counter() - started,
        })
    return rows


def run_dataset(
    name: str,
    repeats: int,
    seed: int,
    max_rows: int,
    mechanisms: tuple[str, ...] = MECHANISMS,
    variants: tuple[str, ...] = VARIANTS,
) -> pd.DataFrame:
    _, encoded, raw, scaler, numeric_scoring = _dataset_protocol_frame(
        name, max_rows, seed
    )
    rows = []
    for mechanism in mechanisms:
        for trial in range(repeats):
            rows.extend(
                _run_cell(
                    name, raw, encoded, scaler, numeric_scoring,
                    mechanism, trial, seed, variants,
                )
            )
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def run_pc1_diagnostic(repeats: int, seed: int, max_rows: int) -> pd.DataFrame:
    _, encoded, raw, scaler, numeric_scoring = _dataset_protocol_frame(
        "pc1", max_rows, seed
    )
    variants = (
        "project_deterministic",
        "project_deterministic_no_bounds",
        "iterative_single_as_is",
    )
    scaled_truth = scaler.transform(raw)
    records = []
    for mechanism in MECHANISMS:
        for trial in range(repeats):
            trial_seed = _seed_for("pc1", trial, seed)
            mask = make_mask(
                scaled_truth,
                mechanism,
                RATE,
                np.random.RandomState(trial_seed + MECHANISMS.index(mechanism)),
            )
            masked = np.where(mask, np.nan, scaled_truth)
            for variant in variants:
                estimate, _ = _variant_estimate(variant, masked, trial_seed)
                for column_index, column in enumerate(encoded.columns):
                    if not numeric_scoring[column_index]:
                        continue
                    selected = mask[:, column_index]
                    n_masked = int(selected.sum())
                    if n_masked == 0:
                        continue
                    observed = ~mask[:, column_index]
                    observed_values = scaled_truth[observed, column_index]
                    true_values = scaled_truth[selected, column_index]
                    low, high = float(observed_values.min()), float(observed_values.max())
                    outside = (true_values < low) | (true_values > high)
                    records.append({
                        "dataset": "pc1",
                        "mechanism": mechanism,
                        "trial": trial,
                        "variant": variant,
                        "column": column,
                        "per_column_rmse": float(np.sqrt(np.mean(
                            (estimate[selected, column_index] - true_values) ** 2
                        ))),
                        "masked_values_outside_observed_range_fraction": float(outside.mean()),
                        "n_masked": n_masked,
                        "n_outside": int(outside.sum()),
                    })
    return pd.DataFrame(records)


def compare_reproduction(
    ablation: pd.DataFrame,
    saved: pd.DataFrame,
    atol: float = 1e-9,
) -> tuple[pd.DataFrame, float]:
    expected_keys = ["dataset", "mechanism", "mask_rate", "trial", "method"]
    ablation_saved = ablation.loc[
        ablation["variant"].isin(REPRO_METHODS)
    ].copy()
    ablation_saved["method"] = ablation_saved["variant"].map(REPRO_METHODS)
    left = ablation_saved.rename(columns={"numeric_rmse": "ablation_numeric_rmse"})
    right = saved[expected_keys + ["numeric_rmse"]].rename(
        columns={"numeric_rmse": "saved_numeric_rmse"}
    )
    joined = left.merge(
        right,
        on=expected_keys,
        how="outer",
        indicator=True,
        validate="one_to_one",
    )
    if not joined["_merge"].eq("both").all():
        counts = joined["_merge"].value_counts().to_dict()
        raise ValueError(f"Reproduction keys do not match exactly: {counts}")
    joined["absolute_difference"] = (
        joined["ablation_numeric_rmse"] - joined["saved_numeric_rmse"]
    ).abs()
    maximum = float(joined["absolute_difference"].max()) if not joined.empty else 0.0
    if maximum > atol:
        raise AssertionError(
            f"Reproduction max absolute difference {maximum:.12g} exceeds {atol}."
        )
    return joined, maximum


def _expected_rows(repeats: int, mechanisms: tuple[str, ...]) -> int:
    return repeats * len(mechanisms) * len(VARIANTS)


def _is_complete_dataset(
    directory: Path,
    dataset: str,
    repeats: int,
    mechanisms: tuple[str, ...],
    seed: int,
    max_rows: int,
) -> bool:
    config_path = directory / "run_config.json"
    csv_path = directory / "ablation.csv"
    if not config_path.is_file() or not csv_path.is_file():
        return False
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if (
        config.get("dataset") != dataset
        or config.get("repeats") != repeats
        or config.get("seed") != seed
        or config.get("max_rows") != max_rows
        or tuple(config.get("mechanisms", ())) != mechanisms
        or tuple(config.get("variants", ())) != VARIANTS
    ):
        return False
    frame = pd.read_csv(csv_path)
    complete = (
        len(frame) == _expected_rows(repeats, mechanisms)
        and set(frame["variant"]) == set(VARIANTS)
    )
    return complete and (dataset != "pc1" or (directory / "pc1_diagnostic.csv").is_file())


def _default_output() -> Path:
    root = Path(__file__).resolve().parent / "results"
    candidate = root / f"mice_ablation_{date.today().isoformat()}"
    suffix = 1
    while candidate.exists():
        candidate = root / f"mice_ablation_{date.today().isoformat()}_{suffix}"
        suffix += 1
    return candidate


def run(args: argparse.Namespace) -> Path:
    datasets = args.datasets or [
        name
        for name in DATASETS
        if name in {
            "adult", "bank-marketing", "breast-w", "credit-approval",
            "credit-g", "cylinder-bands", "heart-statlog", "pc1",
            "telco-customer-churn", "wine-quality-red",
        }
    ]
    unknown = sorted(set(datasets).difference(DATASETS))
    if unknown:
        raise ValueError(f"Unknown datasets: {unknown}")
    mechanisms = tuple(args.mechanisms or MECHANISMS)
    if set(mechanisms).difference(MECHANISMS):
        raise ValueError(f"Unknown mechanisms: {mechanisms}")
    output = Path(args.out).expanduser() if args.out else _default_output()
    output.mkdir(parents=True, exist_ok=True)
    expected_config = {
        "repeats": args.repeats,
        "seed": args.seed,
        "max_rows": args.max_rows,
        "rate": RATE,
        "mechanisms": list(mechanisms),
        "variants": list(VARIANTS),
    }
    for name in datasets:
        destination = output / name
        if _is_complete_dataset(
            destination, name, args.repeats, mechanisms, args.seed, args.max_rows
        ):
            print(f"SKIP COMPLETE {name}", flush=True)
            continue
        destination.mkdir(parents=True, exist_ok=True)
        config_path = destination / "run_config.json"
        if config_path.is_file():
            previous = json.loads(config_path.read_text(encoding="utf-8"))
            if previous.get("dataset") != name or any(
                previous.get(key) != value for key, value in expected_config.items()
            ):
                raise FileExistsError(
                    f"Incomplete output config differs; refusing to overwrite {destination}."
                )
        config = {
            "dataset": name,
            **expected_config,
            "label": "post-hoc exploratory",
        }
        config_path.write_text(
            json.dumps(config, indent=2) + "\n", encoding="utf-8"
        )
        started = time.perf_counter()
        frame = run_dataset(
            name, args.repeats, args.seed, args.max_rows, mechanisms
        )
        frame.to_csv(destination / "ablation.csv", index=False)
        if name == "pc1":
            diagnostic = run_pc1_diagnostic(args.repeats, args.seed, args.max_rows)
            diagnostic.to_csv(destination / "pc1_diagnostic.csv", index=False)
        print(
            f"COMPLETE {name}: rows={len(frame)} "
            f"elapsed_seconds={time.perf_counter() - started:.3f}",
            flush=True,
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", choices=tuple(DATASETS))
    parser.add_argument("--mechanisms", nargs="+", choices=MECHANISMS)
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-rows", type=int, default=5000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    print(run(args), flush=True)


if __name__ == "__main__":
    main()
