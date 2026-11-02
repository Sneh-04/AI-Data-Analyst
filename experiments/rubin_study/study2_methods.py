"""Study 2-only uncertainty ablations and a bootstrap PMM candidate.

The v4 methods in :mod:`rubin_study.imputers` are intentionally unchanged.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, TypeAlias

import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

from rubin_study.imputers import (
    _restore_observed_values,
    _validated_numeric_frame,
)


Study2Method: TypeAlias = Literal[
    "posterior_only", "bootstrap_only", "bootstrap_pmm_candidate"
]

_STREAM_BOOTSTRAP = 1
_STREAM_COEFFICIENT = 2
_STREAM_DONOR = 3
_STREAM_IMPUTER = 4


class PMMDonorPoolError(ValueError):
    """PMM could not construct the required observed donor pool."""

    failure_stage = "donor_pool"


class PMMModelFitError(ValueError):
    """PMM conditional regression could not be fitted."""

    failure_stage = "conditional_model_fit"


def _validate_m_seed(m: int, seed: int) -> tuple[int, int]:
    if isinstance(m, bool) or not isinstance(m, (int, np.integer)) or m < 2:
        raise ValueError("m must be an integer of at least two")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    return int(m), int(seed)


def _study2_iterative_imputer(seed: int, sample_posterior: bool) -> IterativeImputer:
    return IterativeImputer(
        estimator=BayesianRidge(),
        sample_posterior=sample_posterior,
        max_iter=10,
        random_state=seed,
        skip_complete=True,
        keep_empty_features=True,
    )


def _stream(seed: int, draw: int, stream_id: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, draw, stream_id]))


def _stream_seed(seed: int, draw: int, stream_id: int) -> int:
    sequence = np.random.SeedSequence([seed, draw, stream_id])
    return int(sequence.generate_state(1, dtype=np.uint32)[0])


def imputation_stream_manifest(
    seed: int, m: int, method: Study2Method
) -> dict[str, object]:
    """Return the deterministic entropy keys used by each ablation draw."""
    m, seed = _validate_m_seed(m, seed)
    if method not in {
        "posterior_only", "bootstrap_only", "bootstrap_pmm_candidate"
    }:
        raise ValueError(f"unknown Study 2 method: {method}")
    stream_roles: dict[str, tuple[tuple[str, int], ...]] = {
        "posterior_only": (("coefficient_posterior", _STREAM_COEFFICIENT),),
        "bootstrap_only": (
            ("bootstrap_rows", _STREAM_BOOTSTRAP),
            ("imputer", _STREAM_IMPUTER),
        ),
        "bootstrap_pmm_candidate": (
            ("bootstrap_rows", _STREAM_BOOTSTRAP),
            ("coefficient_posterior", _STREAM_COEFFICIENT),
            ("donor_selection", _STREAM_DONOR),
        ),
    }
    return {
        "method": method,
        "seed": seed,
        "streams": [
            {
                "draw": draw,
                "role": role,
                "stream_id": stream_id,
                "seed_sequence_entropy": [seed, draw, stream_id],
            }
            for draw in range(m)
            for role, stream_id in stream_roles[method]
        ],
    }


def _sample_posterior_coefficients(
    model: BayesianRidge, rng: np.random.Generator
) -> np.ndarray:
    """Draw all coefficients from sklearn's conditional Gaussian posterior."""
    coefficients = np.asarray(model.coef_, dtype=float)
    covariance = np.asarray(model.sigma_, dtype=float)
    if coefficients.ndim != 1 or covariance.shape != (coefficients.size, coefficients.size):
        raise ValueError("BayesianRidge coefficient and covariance dimensions do not match")
    if not np.isfinite(coefficients).all() or not np.isfinite(covariance).all():
        raise ValueError("BayesianRidge posterior parameters must be finite")

    scale = max(float(np.max(np.abs(covariance))), np.finfo(float).tiny)
    symmetry_tolerance = 1e-10 * scale
    if not np.allclose(covariance, covariance.T, rtol=0.0, atol=symmetry_tolerance):
        raise ValueError("BayesianRidge posterior covariance must be symmetric")
    covariance = (covariance + covariance.T) * 0.5
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    eigenvalue_tolerance = 1e-10 * max(1.0, float(np.max(np.abs(eigenvalues))))
    if float(eigenvalues.min()) < -eigenvalue_tolerance:
        raise ValueError("BayesianRidge posterior covariance is not positive semidefinite")

    root = eigenvectors * np.sqrt(np.maximum(eigenvalues, 0.0))
    draw = coefficients + root @ rng.standard_normal(coefficients.size)
    if not np.isfinite(draw).all():
        raise ValueError("BayesianRidge posterior coefficient draw is not finite")
    return draw


def _predictor_design(
    predictor_values: np.ndarray,
    training_mean: np.ndarray,
    training_scale: np.ndarray,
    active_columns: np.ndarray,
) -> np.ndarray:
    standardized = (
        predictor_values[:, active_columns] - training_mean[active_columns]
    ) / training_scale[active_columns]
    return np.column_stack((np.ones(len(predictor_values)), standardized))


def _fit_conditional_model(
    training_predictors: np.ndarray, training_target: np.ndarray
) -> tuple[BayesianRidge, np.ndarray, np.ndarray, np.ndarray]:
    training_mean = training_predictors.mean(axis=0)
    raw_scale = training_predictors.std(axis=0, ddof=0)
    scale_floor = np.finfo(float).eps * np.maximum(1.0, np.abs(training_mean))
    active_columns = raw_scale > scale_floor
    if not active_columns.any():
        raise ValueError("conditional regression requires a nonconstant predictor")
    training_scale = np.where(active_columns, raw_scale, 1.0)
    training_design = _predictor_design(
        training_predictors, training_mean, training_scale, active_columns
    )
    model = BayesianRidge(fit_intercept=False)
    model.fit(training_design, training_target)
    if model.sigma_.shape != (training_design.shape[1], training_design.shape[1]):
        raise ValueError("BayesianRidge covariance omitted a design coefficient")
    return model, training_mean, training_scale, active_columns


def _posterior_only_draw(
    numeric: pd.DataFrame,
    target_column: str,
    predictor_columns: Sequence[str],
    seed: int,
    draw: int,
) -> pd.DataFrame:
    target = numeric[target_column].to_numpy(dtype=float)
    observed = np.isfinite(target)
    missing_rows = np.flatnonzero(~observed)
    if missing_rows.size == 0:
        return numeric.copy(deep=True)

    predictor_values = numeric.loc[:, predictor_columns].to_numpy(dtype=float)
    if not np.isfinite(predictor_values).all():
        raise ValueError("posterior_only requires complete predictors")
    model, training_mean, training_scale, active_columns = _fit_conditional_model(
        predictor_values[observed], target[observed]
    )
    coefficients = _sample_posterior_coefficients(
        model, _stream(seed, draw, _STREAM_COEFFICIENT)
    )
    recipient_design = _predictor_design(
        predictor_values[missing_rows], training_mean, training_scale, active_columns
    )
    completed_target = target.copy()
    completed_target[missing_rows] = recipient_design @ coefficients
    result = numeric.copy(deep=True)
    result[target_column] = completed_target
    return _restore_observed_values(result.to_numpy(dtype=float), numeric)


def _bootstrap_pmm_draw(
    numeric: pd.DataFrame,
    target_column: str,
    predictor_columns: Sequence[str],
    seed: int,
    draw: int,
    donor_count: int,
    draw_diagnostics: list[dict[str, object]] | None = None,
    detail_records: list[dict[str, object]] | None = None,
    detail_limit: int = 0,
) -> pd.DataFrame:
    target = numeric[target_column].to_numpy(dtype=float)
    observed = np.isfinite(target)
    missing_rows = np.flatnonzero(~observed)
    if missing_rows.size == 0:
        if draw_diagnostics is not None:
            draw_diagnostics.append({
                "draw": draw,
                "missing_cells": 0,
                "donor_count": int(observed.sum()),
                "donor_support_violations": 0,
                "candidate_donor_count_per_recipient": int(donor_count),
                "selected_distance_mean": None,
                "selected_distance_median": None,
                "selected_distance_max": None,
                "selected_distance_p95": None,
                "distance_outlier_fraction": None,
                "unique_donor_copy_fraction": None,
                "unique_source_donor_fraction": None,
                "max_source_donor_reuse": 0,
                "source_donor_selection_hhi": None,
                "source_donor_selection_entropy": None,
            })
        return numeric.copy(deep=True)

    predictor_values = numeric.loc[:, predictor_columns].to_numpy(dtype=float)
    if not np.isfinite(predictor_values).all():
        raise ValueError("bootstrap_pmm_candidate requires complete predictors")

    bootstrap_rng = _stream(seed, draw, _STREAM_BOOTSTRAP)
    bootstrap_rows = bootstrap_rng.integers(0, len(numeric), size=len(numeric))
    donor_rows = bootstrap_rows[observed[bootstrap_rows]]
    if donor_rows.size == 0:
        raise PMMDonorPoolError("bootstrap sample contains no observed target donors")
    if donor_rows.size < donor_count:
        raise PMMDonorPoolError(
            f"bootstrap sample has {donor_rows.size} donors; "
            f"at least {donor_count} are required"
        )

    try:
        model, training_mean, training_scale, active_columns = _fit_conditional_model(
            predictor_values[donor_rows], target[donor_rows]
        )
    except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
        raise PMMModelFitError(
            f"conditional BayesianRidge fit failed: {error}"
        ) from error
    coefficients = _sample_posterior_coefficients(
        model, _stream(seed, draw, _STREAM_COEFFICIENT)
    )

    donor_design = _predictor_design(
        predictor_values[donor_rows], training_mean, training_scale, active_columns
    )
    recipient_design = _predictor_design(
        predictor_values[missing_rows], training_mean, training_scale, active_columns
    )
    donor_predictions = donor_design @ coefficients
    recipient_predictions = recipient_design @ coefficients
    k = donor_count
    donor_rng = _stream(seed, draw, _STREAM_DONOR)
    completed_target = target.copy()

    selected_copy_positions: list[int] = []
    selected_source_positions: list[int] = []
    selected_distances: list[float] = []
    nearest_boundary_distances: list[float] = []
    boundary_tie_counts: list[int] = []
    for row, prediction in zip(missing_rows, recipient_predictions, strict=True):
        distances = np.abs(donor_predictions - prediction)
        tie_breakers = donor_rng.random(donor_rows.size)
        nearest = np.lexsort((tie_breakers, distances))[:k]
        selected = int(donor_rng.choice(nearest))
        completed_target[row] = target[donor_rows[selected]]
        if draw_diagnostics is not None:
            selected_copy_positions.append(selected)
            selected_source_positions.append(int(donor_rows[selected]))
            selected_distances.append(float(distances[selected]))
            boundary_distance = float(distances[nearest[-1]])
            nearest_boundary_distances.append(boundary_distance)
            tie_tolerance = 1e-12 * max(1.0, abs(boundary_distance))
            boundary_tie_counts.append(
                int(np.count_nonzero(np.abs(distances - boundary_distance) <= tie_tolerance))
            )
            if detail_records is not None and len(detail_records) < detail_limit:
                detail_records.append({
                    "draw": draw,
                    "recipient_position": int(row),
                    "selected_donor_source_position": int(donor_rows[selected]),
                    "selected_donor_bootstrap_copy": selected,
                    "selected_distance": float(distances[selected]),
                    "k_nearest_boundary_distance": float(distances[nearest[-1]]),
                })

    if draw_diagnostics is not None:
        distance_values = np.asarray(selected_distances, dtype=float)
        q25, q75 = np.quantile(distance_values, [0.25, 0.75])
        outlier_threshold = float(q75 + 1.5 * (q75 - q25))
        copy_counts = np.bincount(selected_copy_positions, minlength=donor_rows.size)
        source_counts = np.unique(selected_source_positions, return_counts=True)[1]
        source_probabilities = source_counts / missing_rows.size
        unique_source_donors = np.unique(donor_rows).size
        donor_pool_values = target[donor_rows]
        donor_pool_min = float(np.min(donor_pool_values))
        donor_pool_max = float(np.max(donor_pool_values))
        draw_diagnostics.append({
            "draw": draw,
            "missing_cells": int(missing_rows.size),
            "donor_count": int(donor_rows.size),
            "candidate_donor_count_per_recipient": int(k),
            "unique_source_donors_available": int(unique_source_donors),
            "donor_support_violations": int(
                np.count_nonzero(
                    (completed_target[missing_rows] < donor_pool_min)
                    | (completed_target[missing_rows] > donor_pool_max)
                )
            ),
            "donor_pool_target_support": (donor_pool_min, donor_pool_max),
            "selected_distance_mean": float(np.mean(distance_values)),
            "selected_distance_median": float(np.median(distance_values)),
            "selected_distance_max": float(np.max(distance_values)),
            "selected_distance_p95": float(np.quantile(distance_values, 0.95)),
            "distance_outlier_threshold": outlier_threshold,
            "distance_outlier_count": int(np.count_nonzero(distance_values > outlier_threshold)),
            "distance_outlier_fraction": float(np.mean(distance_values > outlier_threshold)),
            "mean_k_nearest_boundary_distance": float(np.mean(nearest_boundary_distances)),
            "mean_candidates_tied_at_k_boundary": float(np.mean(boundary_tie_counts)),
            "max_candidates_tied_at_k_boundary": int(np.max(boundary_tie_counts)),
            "unique_donor_copy_count": int(np.count_nonzero(copy_counts)),
            "unique_donor_copy_fraction": float(
                np.count_nonzero(copy_counts) / donor_rows.size
            ),
            "unique_source_donor_count": int(len(source_counts)),
            "unique_source_donor_fraction": float(len(source_counts) / unique_source_donors),
            "max_donor_copy_reuse": int(np.max(copy_counts)),
            "max_source_donor_reuse": int(np.max(source_counts)),
            "source_donor_selection_hhi": float(np.sum(source_probabilities**2)),
            "source_donor_selection_entropy": float(
                -np.sum(source_probabilities * np.log(source_probabilities))
            ),
        })

    result = numeric.copy(deep=True)
    result[target_column] = completed_target
    return _restore_observed_values(result.to_numpy(dtype=float), numeric)


def impute_uncertainty_ablation(
    df: pd.DataFrame,
    m: int,
    seed: int,
    method: Study2Method,
    *,
    target_column: str | None = None,
    donor_count: int = 5,
    return_diagnostics: bool = False,
    diagnostic_detail_limit: int = 0,
) -> list[pd.DataFrame] | tuple[list[pd.DataFrame], dict[str, object]]:
    """Generate completed frames for the isolated Study 2 uncertainty variants.

    Set ``return_diagnostics=True`` to receive compact per-draw PMM donor
    summaries plus at most ``diagnostic_detail_limit`` row-level selections.
    Diagnostics are observational and use no additional random draws.
    ``posterior_only`` fits the observed rows once per completed dataset and
    samples regression coefficients; it adds no residual noise or row
    bootstrap, isolating coefficient uncertainty.
    ``bootstrap_only`` has row bootstrap and no posterior sampling.
    ``bootstrap_pmm_candidate`` combines row bootstrap with a conditional
    BayesianRidge coefficient draw and PMM donor selection. Its explicit
    intercept is included in ``sigma_`` but shares BayesianRidge's
    empirical-Bayes coefficient prior; this is a candidate, not a claim of
    full Bayesian uncertainty propagation or statistical properness.
    """
    m, seed = _validate_m_seed(m, seed)
    if not isinstance(return_diagnostics, bool):
        raise ValueError("return_diagnostics must be a boolean")
    if (
        isinstance(diagnostic_detail_limit, bool)
        or not isinstance(diagnostic_detail_limit, (int, np.integer))
        or diagnostic_detail_limit < 0
    ):
        raise ValueError("diagnostic_detail_limit must be a non-negative integer")
    methods = {"posterior_only", "bootstrap_only", "bootstrap_pmm_candidate"}
    if method not in methods:
        raise ValueError(f"method must be one of {sorted(methods)}")
    numeric = _validated_numeric_frame(df)

    if method == "posterior_only":
        if target_column is None or target_column not in numeric.columns:
            raise ValueError("target_column must name the posterior_only target")
        predictor_columns = [column for column in numeric.columns if column != target_column]
        if not predictor_columns:
            raise ValueError("posterior_only requires at least one predictor")
        if numeric[predictor_columns].isna().any().any():
            raise ValueError("posterior_only requires complete predictors")
        if numeric[target_column].isna().all():
            raise ValueError("posterior_only target cannot be entirely missing")
        completed = [
            _posterior_only_draw(
                numeric, target_column, predictor_columns, seed, draw
            )
            for draw in range(m)
        ]
        return (completed, {"method": method, "draws": [], "details": []}) if return_diagnostics else completed

    if method == "bootstrap_only":
        completed_datasets: list[pd.DataFrame] = []
        for draw in range(m):
            bootstrap_rows = _stream(seed, draw, _STREAM_BOOTSTRAP).integers(
                0, len(numeric), size=len(numeric)
            )
            imputer = _study2_iterative_imputer(
                seed=_stream_seed(seed, draw, _STREAM_IMPUTER),
                sample_posterior=False,
            )
            bootstrap = numeric.iloc[bootstrap_rows]
            imputer.fit(bootstrap.to_numpy(copy=True))
            completed = imputer.transform(numeric.to_numpy(copy=True))
            completed_datasets.append(_restore_observed_values(completed, numeric))
        return (
            (completed_datasets, {"method": method, "draws": [], "details": []})
            if return_diagnostics
            else completed_datasets
        )

    if target_column is None or target_column not in numeric.columns:
        raise ValueError("target_column must name the single PMM target")
    if isinstance(donor_count, bool) or not isinstance(donor_count, (int, np.integer)) or donor_count < 1:
        raise ValueError("donor_count must be a positive integer")
    predictor_columns = [column for column in numeric.columns if column != target_column]
    if not predictor_columns:
        raise ValueError("bootstrap_pmm_candidate requires at least one predictor")
    if numeric[predictor_columns].isna().any().any():
        raise ValueError("bootstrap_pmm_candidate requires complete predictors")
    if numeric[target_column].isna().all():
        raise ValueError("bootstrap_pmm_candidate target cannot be entirely missing")

    draw_diagnostics: list[dict[str, object]] = []
    detail_records: list[dict[str, object]] = []
    completed_datasets = [
        _bootstrap_pmm_draw(
            numeric,
            target_column,
            predictor_columns,
            seed,
            draw,
            int(donor_count),
            draw_diagnostics if return_diagnostics else None,
            detail_records if return_diagnostics else None,
            int(diagnostic_detail_limit),
        )
        for draw in range(m)
    ]
    if return_diagnostics:
        return (
            completed_datasets,
            {
                "method": method,
                "draws": draw_diagnostics,
                "details": detail_records,
                "detail_limit": int(diagnostic_detail_limit),
                "distance_definition": (
                    "absolute difference between sampled conditional predictions, "
                    "in target units; predictor standardization is fit within each "
                    "bootstrap donor pool"
                ),
                "distance_outlier_rule": "strictly above Q3 + 1.5 * IQR within an imputation",
                "donor_identity_definition": (
                    "bootstrap-copy positions and original source-row positions are "
                    "both tracked; duplicate bootstrap copies remain distinct candidates"
                ),
            },
        )
    return completed_datasets
