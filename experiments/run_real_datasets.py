"""Evaluate the project imputation methods on verified OpenML tabular datasets."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date
import itertools
import json
import warnings
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer
from sklearn.linear_model import BayesianRidge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from common import holm_adjust
from datasets.registry import (
    CACHE_DIR,
    DATASETS,
    EXPERIMENTS_DIR,
    MANIFEST_PATH,
    DatasetLoadError,
    DatasetSpec,
    fetch_dataset,
    validate_registry,
    write_manifest_record,
)

sys.path.insert(0, str(EXPERIMENTS_DIR.parent / "ml-service"))


METHODS = ("mean", "median", "knn5", "iterative_single", "mice_multiple_NEW")
MECHANISMS = ("MCAR", "MAR", "MNAR")
MASK_RATES = (0.10, 0.20, 0.30)
N_IMPUTATIONS = 5
QUICK_DATASETS = ("breast-w", "hepatitis", "credit-approval")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


@dataclass
class EncodedFrame:
    values: np.ndarray
    numeric_columns: np.ndarray
    categorical_columns: np.ndarray
    categories: dict[str, list[str]]
    columns: list[str]

    @classmethod
    def fit_transformer(cls, frame: pd.DataFrame) -> "EncodedFrame":
        categories: dict[str, list[str]] = {}
        numeric: list[bool] = []
        for column in frame.columns:
            series = frame[column]
            is_categorical = (
                pd.api.types.is_object_dtype(series.dtype)
                or isinstance(series.dtype, pd.CategoricalDtype)
                or pd.api.types.is_string_dtype(series.dtype)
                or pd.api.types.is_bool_dtype(series.dtype)
            )
            numeric.append(not is_categorical)
            if is_categorical:
                categories[column] = sorted(series.dropna().astype(str).unique().tolist())
        encoded = cls(
            values=np.empty((len(frame), len(frame.columns)), dtype=float),
            numeric_columns=np.asarray(numeric, dtype=bool),
            categorical_columns=~np.asarray(numeric, dtype=bool),
            categories=categories,
            columns=[str(column) for column in frame.columns],
        )
        encoded.values = encoded.encode(frame)
        return encoded

    def encode(self, frame: pd.DataFrame) -> np.ndarray:
        result = np.full((len(frame), len(self.columns)), np.nan, dtype=float)
        for position, column in enumerate(self.columns):
            series = frame[column]
            if self.categorical_columns[position]:
                mapping = {value: index for index, value in enumerate(self.categories[column])}
                strings = series.astype("string")
                result[:, position] = strings.map(mapping).to_numpy(dtype=float, na_value=np.nan)
                result[np.isnan(result[:, position]), position] = np.nan
            else:
                result[:, position] = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
        return result

    def decode(self, scaled: np.ndarray, scaler: "ObservedScaler") -> np.ndarray:
        raw = scaler.inverse(scaled)
        for position, column in enumerate(self.columns):
            if self.categorical_columns[position]:
                values = self.categories[column]
                if not values:
                    raw[:, position] = np.nan
                    continue
                finite = np.isfinite(raw[:, position])
                decoded = np.full(len(raw), np.nan, dtype=float)
                decoded[finite] = np.clip(
                    np.rint(raw[finite, position]), 0, len(values) - 1
                )
                raw[:, position] = decoded
        return raw


@dataclass
class ObservedScaler:
    center: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, values: np.ndarray) -> "ObservedScaler":
        center = np.zeros(values.shape[1], dtype=float)
        scale = np.ones(values.shape[1], dtype=float)
        for column in range(values.shape[1]):
            observed = values[np.isfinite(values[:, column]), column]
            if observed.size:
                center[column] = float(observed.mean())
                deviation = float(observed.std())
                scale[column] = deviation if deviation > 0 else 1.0
        return cls(center, scale)

    def transform(self, values: np.ndarray) -> np.ndarray:
        return (values - self.center) / self.scale

    def inverse(self, values: np.ndarray) -> np.ndarray:
        return values * self.scale + self.center


def _calibrate_intercept(values: np.ndarray, expected_rate: float) -> float:
    low, high = -30.0, 30.0
    for _ in range(70):
        midpoint = (low + high) / 2
        probability = np.mean(1 / (1 + np.exp(-np.clip(values + midpoint, -35, 35))))
        if probability > expected_rate:
            high = midpoint
        else:
            low = midpoint
    return (low + high) / 2


def make_mask(
    complete_values: np.ndarray, mechanism: str, rate: float, rng: np.random.RandomState
) -> np.ndarray:
    """Generate an artificial mask; MAR keeps its driver observed."""
    if mechanism not in MECHANISMS:
        raise ValueError(f"Unsupported missingness mechanism: {mechanism}")
    if not 0 < rate < 1:
        raise ValueError("Mask rate must be strictly between zero and one.")
    rows, columns = complete_values.shape
    probabilities = np.zeros((rows, columns), dtype=float)
    if mechanism == "MCAR":
        probabilities.fill(rate)
    elif mechanism == "MAR":
        if columns < 2:
            raise ValueError("MAR masking requires at least two feature columns.")
        driver = complete_values[:, 0]
        target_rate = min(rate * columns / (columns - 1), 0.95)
        for column in range(1, columns):
            base = 2.0 * driver
            bias = _calibrate_intercept(base, target_rate)
            probabilities[:, column] = 1 / (1 + np.exp(-np.clip(base + bias, -35, 35)))
    else:
        for column in range(columns):
            base = 2.0 * complete_values[:, column]
            bias = _calibrate_intercept(base, rate)
            probabilities[:, column] = 1 / (1 + np.exp(-np.clip(base + bias, -35, 35)))

    mask = rng.random_sample((rows, columns)) < probabilities
    if mechanism == "MAR":
        mask[:, 0] = False
    for column in range(columns):
        if mask[:, column].sum() > rows - 5:
            mask[rng.choice(rows, size=min(5, rows), replace=False), column] = False
    for row in np.flatnonzero(mask.all(axis=1)):
        mask[row, rng.randint(columns)] = False
    if not mask.any() and rows and columns:
        candidates = np.argwhere(probabilities > 0)
        if candidates.size:
            mask[tuple(candidates[0])] = True
    return mask


def _project_mice_train_test(
    train: np.ndarray, test: np.ndarray, seed: int, n_imputations: int = N_IMPUTATIONS
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit repeated production-style Bayesian chained models on train, then transform test."""
    if n_imputations < 2:
        raise ValueError("At least two posterior draws are required for MICE.")
    finite = np.isfinite(train)
    mins = np.array(
        [np.min(train[finite[:, j], j]) if finite[:, j].any() else -np.inf for j in range(train.shape[1])]
    )
    maxs = np.array(
        [np.max(train[finite[:, j], j]) if finite[:, j].any() else np.inf for j in range(train.shape[1])]
    )
    constant = np.isfinite(mins) & np.isfinite(maxs) & (mins >= maxs)
    mins[constant] -= 1e-8
    maxs[constant] += 1e-8
    train_draws = []
    test_draws = []
    for draw in range(n_imputations):
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            sample_posterior=True,
            max_iter=10,
            random_state=seed + draw,
            min_value=mins,
            max_value=maxs,
            skip_complete=True,
            keep_empty_features=True,
        )
        # This fit_transform sees training rows only; test rows are passed to transform afterward.
        train_draws.append(imputer.fit_transform(train))
        test_draws.append(imputer.transform(test))
    train_stack = np.stack(train_draws)
    test_stack = np.stack(test_draws)
    return train_stack.mean(axis=0), test_stack.mean(axis=0), test_stack.std(axis=0, ddof=1)


def _fit_transform_method(
    method: str, train: np.ndarray, test: np.ndarray, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    if method in {"mean", "median"}:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            statistic = (
                np.nanmean(train, axis=0) if method == "mean" else np.nanmedian(train, axis=0)
            )
        statistic = np.where(np.isfinite(statistic), statistic, 0.0)
        return (
            np.where(np.isnan(train), statistic, train),
            np.where(np.isnan(test), statistic, test),
            None,
        )
    if method == "knn5":
        imputer = KNNImputer(n_neighbors=5, keep_empty_features=True)
        return imputer.fit_transform(train), imputer.transform(test), None
    if method == "iterative_single":
        imputer = IterativeImputer(
            sample_posterior=False,
            max_iter=10,
            random_state=seed,
            skip_complete=True,
            keep_empty_features=True,
        )
        return imputer.fit_transform(train), imputer.transform(test), None
    if method == "mice_multiple_NEW":
        filled_train, filled_test, uncertainty = _project_mice_train_test(train, test, seed)
        return filled_train, filled_test, uncertainty
    raise ValueError(f"Unknown imputation method: {method}")


def _project_mice_complete(
    masked: np.ndarray, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    _, filled, uncertainty = _project_mice_train_test(masked, masked, seed)
    observed = np.isfinite(masked)
    filled[observed] = masked[observed]
    uncertainty[observed] = np.nan
    return filled, uncertainty


def _metric_rows(
    truth: np.ndarray,
    estimate_scaled: np.ndarray,
    mask: np.ndarray,
    encoder: EncodedFrame,
    scaler: ObservedScaler,
    prefix: str = "",
    numeric_metric_columns: np.ndarray | None = None,
) -> dict[str, float | int]:
    truth_raw = truth
    estimate_raw = encoder.decode(estimate_scaled, scaler)
    numeric_columns = (
        encoder.numeric_columns
        if numeric_metric_columns is None
        else numeric_metric_columns
    )
    numeric_mask = mask & numeric_columns[np.newaxis, :]
    categorical_mask = mask & encoder.categorical_columns[np.newaxis, :]
    truth_scaled = scaler.transform(truth_raw)
    numeric_rmse = (
        float(np.sqrt(np.mean((estimate_scaled[numeric_mask] - truth_scaled[numeric_mask]) ** 2)))
        if numeric_mask.any()
        else np.nan
    )
    categorical_accuracy = (
        float(np.mean(np.rint(estimate_raw[categorical_mask]) == truth_raw[categorical_mask]))
        if categorical_mask.any()
        else np.nan
    )
    return {
        f"{prefix}numeric_rmse": numeric_rmse,
        f"{prefix}categorical_accuracy": categorical_accuracy,
        f"{prefix}categorical_error_rate": (
            1.0 - categorical_accuracy if np.isfinite(categorical_accuracy) else np.nan
        ),
        f"{prefix}n_numeric_evaluated": int(numeric_mask.sum()),
        f"{prefix}n_categorical_evaluated": int(categorical_mask.sum()),
    }


def _uncertainty_metrics(
    truth: np.ndarray, estimate: np.ndarray, sd: np.ndarray, mask: np.ndarray,
    encoder: EncodedFrame, scaler: ObservedScaler,
    numeric_metric_columns: np.ndarray | None = None,
) -> tuple[float, float]:
    numeric_columns = (
        encoder.numeric_columns
        if numeric_metric_columns is None
        else numeric_metric_columns
    )
    numeric_mask = mask & numeric_columns[np.newaxis, :] & np.isfinite(sd)
    if not numeric_mask.any():
        return np.nan, np.nan
    actual = truth[numeric_mask]
    predicted = scaler.inverse(estimate)[numeric_mask]
    standard_deviation = sd[numeric_mask] * np.tile(scaler.scale, (len(sd), 1))[numeric_mask]
    half_width = stats.t.ppf(0.95, N_IMPUTATIONS - 1) * standard_deviation * np.sqrt(1 + 1 / N_IMPUTATIONS)
    coverage = float(np.mean(np.abs(actual - predicted) <= half_width))
    rho = (
        float(stats.spearmanr(standard_deviation, np.abs(actual - predicted)).correlation)
        if np.std(standard_deviation) > 0
        else np.nan
    )
    return coverage, rho


def run_protocol_a(
    name: str, frame: pd.DataFrame, repeats: int, seed: int
) -> tuple[list[dict], str | None]:
    target_name = str(frame.attrs["target_column"])
    target = frame[target_name]
    features = frame.drop(columns=[target_name])
    complete_columns = [
        column for column in features
        if features[column].notna().all() and features[column].nunique(dropna=True) > 1
    ]
    if target.isna().any():
        usable = target.notna()
        features, target = features.loc[usable], target.loc[usable]
    features = features.loc[:, complete_columns]
    if len(features) < 100:
        return [], f"Protocol A skipped: only {len(features)} complete-target rows (minimum 100)."
    if features.shape[1] < 2:
        return [], f"Protocol A skipped: only {features.shape[1]} naturally complete feature columns."

    encoded = EncodedFrame.fit_transformer(features)
    complete_raw = encoded.values.copy()
    if not np.isfinite(complete_raw).all():
        raise ValueError(f"{name}: Protocol A complete columns contain non-finite encoded values.")
    mechanism_scale = ObservedScaler.fit(complete_raw)
    mechanism_values = mechanism_scale.transform(complete_raw)
    full_data_std = complete_raw.std(axis=0)
    numeric_metric_columns = encoded.numeric_columns & (full_data_std >= 1e-8)
    excluded_low_std = [
        encoded.columns[index]
        for index in np.flatnonzero(encoded.numeric_columns & (full_data_std < 1e-8))
    ]
    if excluded_low_std:
        print(
            f"PROTOCOL A EXCLUDED LOW-STD NUMERIC COLUMNS {name}: "
            f"{', '.join(excluded_low_std)} (full-data std < 1e-8)",
            flush=True,
        )
    rows: list[dict] = []
    for mechanism, rate, trial in itertools.product(MECHANISMS, MASK_RATES, range(repeats)):
        trial_seed = seed + 100_000 * list(DATASETS).index(name) + 1_000 * trial + int(rate * 100)
        mask = make_mask(
            mechanism_values,
            mechanism,
            rate,
            np.random.RandomState(trial_seed + MECHANISMS.index(mechanism)),
        )
        # A fixed full-data scaler makes every method/mechanism use the same
        # feature scales; fitting after masking would distort MNAR evaluation.
        scaler = mechanism_scale
        scaled = scaler.transform(complete_raw)
        masked = np.where(mask, np.nan, scaled)
        for method in METHODS:
            if method == "mice_multiple_NEW":
                estimate, uncertainty = _project_mice_complete(masked, trial_seed)
                sd = uncertainty
            else:
                estimate, _, sd = _fit_transform_method(method, masked, masked, trial_seed)
            metrics = _metric_rows(
                complete_raw,
                estimate,
                mask,
                encoded,
                scaler,
                numeric_metric_columns=numeric_metric_columns,
            )
            coverage, spearman = (
                _uncertainty_metrics(
                    complete_raw,
                    estimate,
                    sd,
                    mask,
                    encoded,
                    scaler,
                    numeric_metric_columns,
                )
                if sd is not None
                else (np.nan, np.nan)
            )
            rows.append({
                "protocol": "A_ground_truth_masking",
                "dataset": name,
                "mechanism": mechanism,
                "mask_rate": rate,
                "trial": trial,
                "method": method,
                "realized_mask_rate": float(mask.mean()),
                **metrics,
                "uncertainty_coverage90_numeric": coverage,
                "uncertainty_spearman_numeric": spearman,
            })
    return rows, None


def _natural_loss(metric_name: str, row: dict) -> float:
    if metric_name == "accuracy":
        return 1.0 - float(row["accuracy"])
    return float(row[metric_name])


def run_protocol_b(
    name: str,
    features: pd.DataFrame,
    target: pd.Series,
    task_type: str,
    repeats: int,
    seed: int,
) -> list[dict]:
    usable_rows = target.notna()
    features = features.loc[usable_rows].reset_index(drop=True)
    target = target.loc[usable_rows].reset_index(drop=True)
    if len(features) < 5:
        return []
    is_classification = task_type == "classification"
    if is_classification:
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(target.astype(str))
        splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        splits = splitter.split(features, y)
    else:
        y = pd.to_numeric(target, errors="coerce").to_numpy(dtype=float)
        valid = np.isfinite(y)
        features, y = features.loc[valid].reset_index(drop=True), y[valid]
        splitter = KFold(n_splits=5, shuffle=True, random_state=seed)
        splits = splitter.split(features)

    rows: list[dict] = []
    for repeat in range(repeats):
        if repeat:
            splitter = (
                StratifiedKFold(n_splits=5, shuffle=True, random_state=seed + repeat)
                if is_classification
                else KFold(n_splits=5, shuffle=True, random_state=seed + repeat)
            )
            splits = splitter.split(features, y) if is_classification else splitter.split(features)
        for fold, (train_index, test_index) in enumerate(splits):
            train_frame = features.iloc[train_index].reset_index(drop=True)
            test_frame = features.iloc[test_index].reset_index(drop=True)
            encoder = EncodedFrame.fit_transformer(train_frame)
            train_raw = encoder.values
            test_raw = encoder.encode(test_frame)
            scaler = ObservedScaler.fit(train_raw)
            train_encoded = scaler.transform(train_raw)
            test_encoded = scaler.transform(test_raw)
            # Every imputer below is fitted using this training fold only. Test-fold
            # values are transformed, never included in fit or fit_transform.
            train_y, test_y = y[train_index], y[test_index]
            for method_index, method in enumerate(METHODS):
                fit_seed = seed + 100_000 * list(DATASETS).index(name) + repeat * 1_000 + fold * 20 + method_index
                imputed_train, imputed_test, _ = _fit_transform_method(
                    method, train_encoded, test_encoded, fit_seed
                )
                if is_classification:
                    model = RandomForestClassifier(
                        n_estimators=100, random_state=seed, n_jobs=1, class_weight="balanced"
                    )
                    model.fit(imputed_train, train_y)
                    predictions = model.predict(imputed_test)
                    predictive_metrics: dict[str, float] = {
                        "accuracy": float(np.mean(predictions == test_y))
                    }
                    if len(model.classes_) == 2:
                        probabilities = model.predict_proba(imputed_test)[:, 1]
                        predictive_metrics["auc"] = float(roc_auc_score(test_y, probabilities))
                    else:
                        predictive_metrics["auc"] = np.nan
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=seed, n_jobs=1)
                    model.fit(imputed_train, train_y)
                    predictions = model.predict(imputed_test)
                    predictive_metrics = {
                        "rmse": float(np.sqrt(np.mean((predictions - test_y) ** 2)))
                    }

                observed_mask = np.isfinite(test_encoded)
                holdout_rng = np.random.RandomState(fit_seed + 50_000)
                holdout_mask = (holdout_rng.random_sample(test_encoded.shape) < 0.10) & observed_mask
                if not holdout_mask.any() and observed_mask.any():
                    holdout_mask.flat[np.flatnonzero(observed_mask)[0]] = True
                corrupted_test = np.where(holdout_mask, np.nan, test_encoded)
                _, heldout_filled, _ = _fit_transform_method(
                    method, train_encoded, corrupted_test, fit_seed
                )
                holdout_metrics = _metric_rows(
                    test_raw, heldout_filled, holdout_mask, encoder, scaler, prefix="heldout_"
                )
                rows.append({
                    "protocol": "B_natural_missingness",
                    "label": "natural missingness",
                    "dataset": name,
                    "task_type": task_type,
                    "repeat": repeat,
                    "fold": fold,
                    "method": method,
                    **predictive_metrics,
                    **holdout_metrics,
                    "heldout_observed_rate": float(holdout_mask.sum() / max(1, observed_mask.sum())),
                    "natural_missing_rate_test_features": float(np.isnan(test_raw).mean()),
                })
    return rows


def _significance_a(raw: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "metric", "dataset", "mechanism", "vs", "mean_loss_diff",
        "project_mice_wins", "pairs", "p_value", "p_holm", "project_mice_won",
    ]
    if raw.empty:
        return pd.DataFrame(columns=columns)
    comparisons: list[dict] = []
    metrics = ("numeric_rmse", "categorical_error_rate")
    for metric in metrics:
        pivot = raw.pivot_table(
            index=["dataset", "mechanism", "mask_rate", "trial"], columns="method", values=metric
        )
        for (dataset, mechanism), block in pivot.groupby(level=["dataset", "mechanism"]):
            for other in METHODS:
                if other == "mice_multiple_NEW" or other not in block:
                    continue
                pairs = block[["mice_multiple_NEW", other]].dropna()
                if pairs.empty:
                    continue
                diff = pairs["mice_multiple_NEW"] - pairs[other]
                pvalue = float(stats.wilcoxon(diff).pvalue) if (diff != 0).any() else 1.0
                comparisons.append({
                    "protocol": "B_natural_missingness",
                    "label": "natural missingness",
                    "metric": metric,
                    "dataset": dataset,
                    "mechanism": mechanism,
                    "vs": other,
                    "mean_loss_diff": float(diff.mean()),
                    "project_mice_wins": int((diff < 0).sum()),
                    "pairs": int(len(diff)),
                    "p_value": pvalue,
                })
    result = pd.DataFrame(comparisons, columns=columns)
    if not result.empty:
        result["p_holm"] = holm_adjust(result["p_value"].to_numpy())
        result["project_mice_won"] = result["mean_loss_diff"] < 0
    return result


def _significance_b(raw: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "protocol", "label", "metric", "dataset", "vs", "mean_loss_diff",
        "project_mice_wins", "pairs", "p_value", "p_holm", "project_mice_won",
    ]
    if raw.empty:
        return pd.DataFrame(columns=columns)
    comparisons: list[dict] = []
    metric_columns = ["accuracy", "rmse", "heldout_numeric_rmse", "heldout_categorical_error_rate"]
    for metric in metric_columns:
        if metric not in raw:
            continue
        pivot = raw.pivot_table(
            index=["dataset", "repeat", "fold"], columns="method", values=metric
        )
        for dataset, block in pivot.groupby(level="dataset"):
            for other in METHODS:
                if other == "mice_multiple_NEW" or other not in block:
                    continue
                pairs = block[["mice_multiple_NEW", other]].dropna()
                if pairs.empty:
                    continue
                if metric in {"accuracy"}:
                    diff = (1.0 - pairs["mice_multiple_NEW"]) - (1.0 - pairs[other])
                else:
                    diff = pairs["mice_multiple_NEW"] - pairs[other]
                pvalue = float(stats.wilcoxon(diff).pvalue) if (diff != 0).any() else 1.0
                comparisons.append({
                    "metric": metric,
                    "dataset": dataset,
                    "vs": other,
                    "mean_loss_diff": float(diff.mean()),
                    "project_mice_wins": int((diff < 0).sum()),
                    "pairs": int(len(diff)),
                    "p_value": pvalue,
                })
    result = pd.DataFrame(comparisons, columns=columns)
    if not result.empty:
        result["p_holm"] = holm_adjust(result["p_value"].to_numpy())
        result["project_mice_won"] = result["mean_loss_diff"] < 0
    return result


def _default_output_dir() -> Path:
    root = EXPERIMENTS_DIR / "results"
    candidate = root / f"real_datasets_{date.today().isoformat()}"
    suffix = 1
    while candidate.exists():
        candidate = root / f"real_datasets_{date.today().isoformat()}_{suffix}"
        suffix += 1
    return candidate


def _validate_output_path(path: Path) -> None:
    protected = (EXPERIMENTS_DIR / "results" / "paper_run_2026-10-11").resolve()
    resolved = path.resolve()
    if resolved == protected or protected in resolved.parents:
        raise ValueError("Refusing to write inside the frozen paper_run_2026-10-11 results.")
    if resolved.exists() and any(resolved.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {resolved}")


def _write_cache_and_manifest(
    name: str,
    features: pd.DataFrame,
    target: pd.Series,
    spec: DatasetSpec,
    fetched: dict,
) -> tuple[pd.DataFrame, Path]:
    table = features.copy()
    table[target.name] = target.to_numpy()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{name}.csv"
    table.to_csv(cache_file, index=False)
    write_manifest_record(
        spec,
        table,
        cache_file,
        MANIFEST_PATH,
        feature_types=fetched["feature_types"],
        numeric_coercion_counts=fetched["numeric_coercion_counts"],
        raw_dtypes=fetched["raw_dtypes"],
        raw_nunique=fetched["raw_nunique"],
    )
    return table, cache_file


def _stratified_row_cap(
    features: pd.DataFrame,
    target: pd.Series,
    max_rows: int | None,
    seed: int,
) -> tuple[pd.DataFrame, pd.Series]:
    if max_rows is None or len(features) <= max_rows:
        return features.reset_index(drop=True), target.reset_index(drop=True)
    selected_features, _, selected_target, _ = train_test_split(
        features,
        target,
        train_size=max_rows,
        random_state=seed,
        stratify=target.astype(str),
    )
    return (
        selected_features.reset_index(drop=True),
        selected_target.reset_index(drop=True),
    )


def run(args: argparse.Namespace) -> Path:
    validate_registry()
    requested = args.datasets or (list(QUICK_DATASETS) if args.quick else list(DATASETS))
    if args.quick:
        requested = requested[:3]
    unknown = [name for name in requested if name not in DATASETS]
    if unknown:
        raise ValueError(f"Unknown dataset name(s): {', '.join(unknown)}")
    if not requested:
        raise ValueError("Select at least one dataset.")

    repeats = 1 if args.quick else args.repeats
    if repeats < 1:
        raise ValueError("--repeats must be at least 1.")
    output_dir = Path(args.out).expanduser() if args.out else _default_output_dir()
    _validate_output_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    protocol_a_rows: list[dict] = []
    protocol_b_rows: list[dict] = []
    protocol_a_significance = pd.DataFrame()
    protocol_b_significance = pd.DataFrame()
    summary: list[dict] = []
    for name in requested:
        spec = DATASETS[name]
        try:
            features, target, fetched = fetch_dataset(spec, CACHE_DIR)
        except Exception as error:
            summary.append({
                **asdict(spec),
                "load_status": "failed",
                "load_failure_reason": f"{type(error).__name__}: {error}",
                "protocol_a_status": "not_run",
                "protocol_b_status": "not_run",
            })
            print(f"LOAD FAILED {name}: {type(error).__name__}: {error}", flush=True)
            continue
        table, cache_file = _write_cache_and_manifest(
            name, features, target, spec, fetched
        )
        original_rows = len(features)
        features, target = _stratified_row_cap(
            features, target, args.max_rows, args.seed
        )
        if len(features) != original_rows:
            print(
                f"ROW CAP {name}: stratified {original_rows} -> {len(features)} "
                f"(max_rows={args.max_rows}, seed={args.seed})",
                flush=True,
            )
        combined = features.copy()
        combined[target.name] = target
        combined.attrs["target_column"] = target.name
        incomplete_feature_columns = [
            column for column in features if not features[column].notna().all()
        ]
        constant_complete_columns = [
            column for column in features
            if features[column].notna().all() and features[column].nunique(dropna=True) <= 1
        ]
        a_rows: list[dict] = []
        a_skip = None
        if args.protocol in {"A", "both"}:
            a_rows, a_skip = run_protocol_a(name, combined, repeats, args.seed)
            protocol_a_rows.extend(a_rows)
            if a_skip:
                print(f"PROTOCOL A SKIP {name}: {a_skip}", flush=True)
        b_rows: list[dict] = []
        b_skip = None
        if args.protocol in {"B", "both"}:
            if not features.isna().to_numpy().any():
                b_skip = "Protocol B skipped: no naturally missing predictor entries."
                print(f"PROTOCOL B SKIP {name}: {b_skip}", flush=True)
            else:
                b_rows = run_protocol_b(name, features, target, spec.task_type, repeats, args.seed)
                protocol_b_rows.extend(b_rows)
        feature_numeric = sum(
            pd.api.types.is_numeric_dtype(features[column]) for column in features.columns
        )
        for column in features.columns:
            print(
                f"DTYPE {name}.{column}: metadata={fetched['feature_types'][column]} "
                f"raw={fetched['raw_dtypes'][column]} final={features[column].dtype} "
                f"nunique={fetched['raw_nunique'][column]}",
                flush=True,
            )
        for column, count in fetched["numeric_coercion_counts"].items():
            if count:
                print(
                    f"NUMERIC COERCION {name}.{column}: new_missing={count}",
                    flush=True,
                )
        summary.append({
            **asdict(spec),
            "n_numeric": int(feature_numeric),
            "n_categorical": int(len(features.columns) - feature_numeric),
            "n_rows_evaluated": int(len(features)),
            "natural_missing_fraction": float(features.isna().to_numpy().mean()),
            "load_status": "loaded",
            "load_failure_reason": "",
            "protocol_a_status": "skipped" if a_skip else ("completed" if args.protocol in {"A", "both"} else "not_requested"),
            "protocol_a_skip_reason": a_skip or "",
            "protocol_a_dropped_incomplete_columns": json.dumps(incomplete_feature_columns),
            "protocol_a_dropped_constant_columns": json.dumps(constant_complete_columns),
            "protocol_b_status": (
                "skipped_no_natural_missingness" if b_skip
                else ("completed" if args.protocol in {"B", "both"} else "not_requested")
            ),
            "protocol_b_skip_reason": b_skip or "",
            "cache_sha256": write_manifest_record(
                spec,
                table,
                cache_file,
                MANIFEST_PATH,
                feature_types=fetched["feature_types"],
                numeric_coercion_counts=fetched["numeric_coercion_counts"],
                raw_dtypes=fetched["raw_dtypes"],
                raw_nunique=fetched["raw_nunique"],
            )["sha256"],
            "data_id": fetched["data_id"],
            "version": fetched["version"],
        })
        print(
            f"LOADED {name}: rows={len(features)} features={features.shape[1]} "
            f"natural_missing={features.isna().to_numpy().mean():.4f} "
            f"OpenML={fetched['data_id']}v{fetched['version']}",
            flush=True,
        )

    if args.protocol in {"A", "both"}:
        a_frame = pd.DataFrame(protocol_a_rows)
        if a_frame.empty:
            a_frame = pd.DataFrame(columns=[
                "protocol", "dataset", "mechanism", "mask_rate", "trial", "method",
                "realized_mask_rate", "numeric_rmse", "categorical_accuracy",
                "categorical_error_rate", "n_numeric_evaluated", "n_categorical_evaluated",
                "uncertainty_coverage90_numeric", "uncertainty_spearman_numeric",
            ])
        a_frame.to_csv(output_dir / "protocol_a_ground_truth.csv", index=False)
        protocol_a_significance = _significance_a(a_frame)
        protocol_a_significance.to_csv(output_dir / "protocol_a_significance.csv", index=False)
    if args.protocol in {"B", "both"}:
        b_frame = pd.DataFrame(protocol_b_rows)
        if b_frame.empty:
            b_frame = pd.DataFrame(columns=[
                "protocol", "label", "dataset", "task_type", "repeat", "fold",
                "method", "accuracy", "auc", "rmse", "heldout_numeric_rmse",
                "heldout_categorical_accuracy", "heldout_categorical_error_rate",
                "heldout_n_numeric_evaluated", "heldout_n_categorical_evaluated",
                "heldout_observed_rate", "natural_missing_rate_test_features",
            ])
        b_frame.to_csv(output_dir / "protocol_b_natural_missingness.csv", index=False)
        protocol_b_significance = _significance_b(b_frame)
        protocol_b_significance.to_csv(output_dir / "protocol_b_significance.csv", index=False)
    summary_frame = pd.DataFrame(summary)
    summary_frame.to_csv(output_dir / "dataset_summary.csv", index=False)
    run_info = {
        "protocol": args.protocol,
        "seed": args.seed,
        "max_rows": args.max_rows,
        "repeats": repeats,
        "mask_rates_protocol_a": list(MASK_RATES),
        "mechanisms_protocol_a": list(MECHANISMS),
        "natural_missingness_label_protocol_b": "natural missingness",
        "n_imputations": N_IMPUTATIONS,
        "datasets_requested": requested,
        "manifest": str(MANIFEST_PATH),
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(run_info, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nOutput directory: {output_dir.resolve()}")
    print(f"Successfully loaded {sum(row['load_status'] == 'loaded' for row in summary)} of {len(requested)} requested datasets.")
    print(summary_frame[["name", "n_rows", "n_numeric", "n_categorical", "natural_missing_fraction", "load_status"]].to_string(index=False))
    if args.protocol in {"A", "both"} and protocol_a_rows:
        print("\nProtocol A rows:", len(protocol_a_rows))
        print(pd.DataFrame(protocol_a_rows).groupby("method").numeric_rmse.mean().to_string())
        not_won = protocol_a_significance.loc[~protocol_a_significance["project_mice_won"]]
        print(f"Protocol A MICE did not win on {len(not_won)} paired dataset/mechanism/metric comparisons.")
        if not not_won.empty:
            print(not_won[["dataset", "mechanism", "metric", "vs", "mean_loss_diff", "p_holm"]].to_string(index=False))
    if args.protocol in {"B", "both"} and protocol_b_rows:
        print("\nProtocol B (natural missingness) rows:", len(protocol_b_rows))
        b_frame = pd.DataFrame(protocol_b_rows)
        metric_columns = [
            column for column in ("accuracy", "auc", "rmse", "heldout_numeric_rmse",
                                  "heldout_categorical_accuracy")
            if column in b_frame.columns
        ]
        print(b_frame.groupby(["dataset", "method"])[metric_columns].mean().to_string())
        not_won = protocol_b_significance.loc[~protocol_b_significance["project_mice_won"]]
        print(f"\nProtocol B MICE did not win on {len(not_won)} paired dataset/metric comparisons.")
        if not not_won.empty:
            print(not_won[["dataset", "metric", "vs", "mean_loss_diff", "p_holm"]].to_string(index=False))
    return output_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", help="Dataset names from datasets/registry.py.")
    parser.add_argument("--protocol", choices=("A", "B", "both"), default="both")
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-rows",
        type=int,
        default=5000,
        help="Fixed-seed stratified row cap for larger datasets; smaller datasets are unchanged.",
    )
    parser.add_argument("--out", help="New output directory; refuses to overwrite nonempty directories.")
    parser.add_argument("--quick", action="store_true", help="Use up to three small datasets and one repeat.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
