"""Statistical diagnostics for the Study 2 synthetic validation work."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from scipy.stats import beta, t


def exact_binomial_interval(
    successes: int, trials: int, confidence_level: float = 0.95
) -> tuple[float, float]:
    """Return a two-sided Clopper-Pearson interval for a binomial proportion."""
    if isinstance(trials, bool) or not isinstance(trials, (int, np.integer)) or trials < 1:
        raise ValueError("trials must be a positive integer")
    if (
        isinstance(successes, bool)
        or not isinstance(successes, (int, np.integer))
        or not 0 <= successes <= trials
    ):
        raise ValueError("successes must be an integer between zero and trials")
    if (
        isinstance(confidence_level, bool)
        or not math.isfinite(float(confidence_level))
        or not 0 < float(confidence_level) < 1
    ):
        raise ValueError("confidence_level must be strictly between zero and one")

    alpha = 1.0 - float(confidence_level)
    lower = 0.0 if successes == 0 else float(
        beta.ppf(alpha / 2.0, successes, trials - successes + 1)
    )
    upper = 1.0 if successes == trials else float(
        beta.ppf(1.0 - alpha / 2.0, successes + 1, trials - successes)
    )
    return lower, upper


def summarize_no_missing_gate(
    covered: Sequence[bool], nominal_coverage: float = 0.95
) -> dict[str, Any]:
    """Report exact coverage uncertainty and whether nominal coverage is compatible.

    The gate passes only when nominal coverage lies in the pre-specified
    two-sided exact binomial confidence interval. It is a sanity check, not
    evidence that masked-data methods are calibrated.
    """
    if len(covered) == 0:
        raise ValueError("covered must contain every scheduled no-missing replicate")
    if not math.isfinite(nominal_coverage) or not 0 < nominal_coverage < 1:
        raise ValueError("nominal_coverage must be strictly between zero and one")
    if any(not isinstance(value, (bool, np.bool_)) for value in covered):
        raise ValueError("covered values must be boolean")
    successes = sum(bool(value) for value in covered)
    interval = exact_binomial_interval(successes, len(covered))
    return {
        "successes": successes,
        "trials": len(covered),
        "coverage": successes / len(covered),
        "confidence_level": 0.95,
        "exact_binomial_interval": interval,
        "nominal_coverage": nominal_coverage,
        "gate_pass": interval[0] <= nominal_coverage <= interval[1],
        "gate_rule": "nominal coverage lies inside the two-sided 95% Clopper-Pearson interval",
    }


def variance_decomposition(
    within_variance: float,
    between_variance: float,
    imputations: int,
    complete_data_df: float | None = None,
) -> dict[str, Any]:
    """Calculate Rubin variance contributions and finite-imputation diagnostics.

    `fraction_of_missing_information` reports the Rubin lambda fraction.
    `finite_df_adjusted_fmi` reports the finite-df-adjusted FMI gamma when a
    complete-data degrees-of-freedom value is supplied.
    """
    if (
        isinstance(imputations, bool)
        or not isinstance(imputations, (int, np.integer))
        or imputations < 2
    ):
        raise ValueError("imputations must be an integer of at least two")
    values = np.asarray([within_variance, between_variance], dtype=float)
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError("within and between variances must be finite and non-negative")
    within, between = map(float, values)
    total = within + (1.0 + 1.0 / int(imputations)) * between
    if not math.isfinite(total):
        raise ValueError("total variance must be finite")
    if within == 0:
        relative_increase = None if between > 0 else 0.0
        riv_status = (
            "undefined_zero_within_positive_between"
            if between > 0
            else "defined_zero_variance"
        )
    else:
        relative_increase = (1.0 + 1.0 / imputations) * between / within
        if not math.isfinite(relative_increase):
            relative_increase = None
            riv_status = "undefined_overflow"
        else:
            riv_status = "defined"
    if total == 0:
        between_fraction = 0.0
        within_fraction = 0.0
        lambda_fraction = None
        finite_df_adjusted_fmi = None
        barnard_rubin_degrees_of_freedom = None
    else:
        between_component = (1.0 + 1.0 / imputations) * between
        between_fraction = between_component / total
        within_fraction = within / total
        lambda_fraction = between_fraction
        if complete_data_df is not None:
            if not math.isfinite(float(complete_data_df)) or float(complete_data_df) <= 0:
                raise ValueError("complete_data_df must be finite and positive when provided")
            if within == 0 and between > 0:
                barnard_rubin_degrees_of_freedom = 0.0
                finite_df_adjusted_fmi = None
            else:
                old_df = (imputations - 1) / lambda_fraction**2 if lambda_fraction > 0 else math.inf
                observed_df = (
                    ((float(complete_data_df) + 1.0) / (float(complete_data_df) + 3.0))
                    * float(complete_data_df)
                    * (1.0 - lambda_fraction)
                )
                if observed_df <= 0:
                    barnard_rubin_degrees_of_freedom = 0.0
                    finite_df_adjusted_fmi = None
                else:
                    barnard_rubin_degrees_of_freedom = 1.0 / (1.0 / old_df + 1.0 / observed_df)
                    if within > 0:
                        r_value = relative_increase if relative_increase is not None else 0.0
                        finite_df_adjusted_fmi = (
                            r_value + 2.0 / (barnard_rubin_degrees_of_freedom + 3.0)
                        ) / (1.0 + r_value)
                    else:
                        finite_df_adjusted_fmi = None
        else:
            barnard_rubin_degrees_of_freedom = None
            finite_df_adjusted_fmi = None
    result = {
        "within_imputation_variance": within,
        "between_imputation_variance": between,
        "total_variance": total,
        "relative_increase_in_variance": relative_increase,
        "relative_increase_in_variance_status": riv_status,
        "fraction_of_missing_information": lambda_fraction,
        "lambda_fraction": lambda_fraction,
        "finite_df_adjusted_fmi": finite_df_adjusted_fmi,
        "barnard_rubin_degrees_of_freedom": barnard_rubin_degrees_of_freedom,
        "relative_efficiency": None if lambda_fraction is None else 1.0 / (1.0 + lambda_fraction / imputations),
        "within_variance_share": within_fraction,
        "between_variance_share": between_fraction,
    }
    return result


def interval_score(
    lower: float,
    upper: float,
    truth: float,
    alpha: float = 0.05,
) -> float:
    """Return the central interval score for a finite interval.

    Lower is better; for a 95% interval use alpha=0.05.
    """
    if not math.isfinite(lower) or not math.isfinite(upper) or not math.isfinite(truth):
        raise ValueError("lower, upper, and truth must be finite")
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be finite and strictly between 0 and 1")
    if lower > upper:
        raise ValueError("lower must be less than or equal to upper")
    width = upper - lower
    if lower <= truth <= upper:
        return width
    if truth < lower:
        return width + (2.0 / alpha) * (lower - truth)
    return width + (2.0 / alpha) * (truth - upper)


def summarize_pmm_donor_draws(draws: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize compact per-imputation PMM donor diagnostics."""
    if not draws:
        return {
            "imputation_draws": 0,
            "missing_cells": 0,
            "donor_support_violations": 0,
            "mean_selected_distance": None,
            "median_draw_mean_selected_distance": None,
            "mean_draw_median_selected_distance": None,
            "mean_draw_distance_p95": None,
            "max_selected_distance": None,
            "mean_distance_outlier_fraction": None,
            "mean_available_donor_copies": None,
            "minimum_available_donor_copies": None,
            "maximum_available_donor_copies": None,
            "candidate_donor_count_per_recipient": None,
            "mean_unique_source_donors_available": None,
            "donor_pool_target_support": None,
            "mean_candidates_tied_at_k_boundary": None,
            "mean_unique_donor_copy_fraction": None,
            "mean_unique_source_donor_fraction": None,
            "mean_max_donor_copy_reuse": None,
            "max_donor_copy_reuse": None,
            "mean_max_source_donor_reuse": None,
            "max_source_donor_reuse": None,
            "mean_source_donor_selection_hhi": None,
            "mean_source_donor_selection_entropy": None,
        }

    count = sum(int(draw["missing_cells"]) for draw in draws)
    eligible_draws = [draw for draw in draws if int(draw["missing_cells"]) > 0]
    support_bounds = [
        draw["donor_pool_target_support"]
        for draw in eligible_draws
        if draw.get("donor_pool_target_support") is not None
    ]
    draw_means = [
        float(draw["selected_distance_mean"])
        for draw in draws
        if int(draw["missing_cells"]) > 0
    ]
    return {
        "imputation_draws": len(draws),
        "missing_cells": count,
        "donor_support_violations": sum(
            int(draw["donor_support_violations"]) for draw in draws
        ),
        "mean_selected_distance": _weighted_mean(
            [(float(draw["selected_distance_mean"]), int(draw["missing_cells"]))
             for draw in draws if int(draw["missing_cells"]) > 0]
        ),
        "median_draw_mean_selected_distance": (
            float(np.median(draw_means)) if draw_means else None
        ),
        "mean_draw_median_selected_distance": _weighted_mean(
            [(float(draw["selected_distance_median"]), int(draw["missing_cells"]))
             for draw in draws if int(draw["missing_cells"]) > 0]
        ),
        "mean_draw_distance_p95": _weighted_mean(
            [(float(draw["selected_distance_p95"]), int(draw["missing_cells"]))
             for draw in draws if int(draw["missing_cells"]) > 0]
        ),
        "max_selected_distance": max(
            (float(draw["selected_distance_max"]) for draw in draws
             if int(draw["missing_cells"]) > 0),
            default=None,
        ),
        "mean_distance_outlier_fraction": _weighted_mean(
            [(float(draw["distance_outlier_fraction"]), int(draw["missing_cells"]))
             for draw in draws if int(draw["missing_cells"]) > 0]
        ),
        "mean_available_donor_copies": _mean_optional(
            draw.get("donor_count") for draw in draws if int(draw["missing_cells"]) > 0
        ),
        "minimum_available_donor_copies": min(
            (
                int(draw["donor_count"])
                for draw in draws
                if int(draw["missing_cells"]) > 0
            ),
            default=None,
        ),
        "maximum_available_donor_copies": max(
            (
                int(draw["donor_count"])
                for draw in draws
                if int(draw["missing_cells"]) > 0
            ),
            default=None,
        ),
        "candidate_donor_count_per_recipient": _mean_optional(
            draw.get("candidate_donor_count_per_recipient")
            for draw in eligible_draws
        ),
        "mean_unique_source_donors_available": _mean_optional(
            draw.get("unique_source_donors_available") for draw in draws
        ),
        "donor_pool_target_support": (
            (
                min(float(bounds[0]) for bounds in support_bounds),
                max(float(bounds[1]) for bounds in support_bounds),
            )
            if support_bounds
            else None
        ),
        "mean_candidates_tied_at_k_boundary": _weighted_mean(
            [
                (
                    float(draw["mean_candidates_tied_at_k_boundary"]),
                    int(draw["missing_cells"]),
                )
                for draw in eligible_draws
                if draw.get("mean_candidates_tied_at_k_boundary") is not None
            ]
        ),
        "mean_unique_donor_copy_fraction": _mean_optional(
            draw.get("unique_donor_copy_fraction") for draw in draws
        ),
        "mean_unique_source_donor_fraction": _mean_optional(
            draw.get("unique_source_donor_fraction") for draw in draws
        ),
        "mean_max_donor_copy_reuse": _mean_optional(
            draw.get("max_donor_copy_reuse") for draw in draws
        ),
        "max_donor_copy_reuse": max(
            (int(draw["max_donor_copy_reuse"]) for draw in draws),
            default=0,
        ),
        "mean_max_source_donor_reuse": _mean_optional(
            draw.get("max_source_donor_reuse") for draw in draws
        ),
        "max_source_donor_reuse": max(
            (int(draw["max_source_donor_reuse"]) for draw in draws),
            default=0,
        ),
        "mean_source_donor_selection_hhi": _mean_optional(
            draw.get("source_donor_selection_hhi") for draw in draws
        ),
        "mean_source_donor_selection_entropy": _mean_optional(
            draw.get("source_donor_selection_entropy") for draw in draws
        ),
    }


def true_conditional_mean(
    dgp: str, x1: Sequence[float] | np.ndarray, parameters: Mapping[str, float]
) -> np.ndarray:
    """Evaluate an analytic E[x2 | x1] for the registered synthetic DGP families."""
    values = np.asarray(x1, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("x1 must be a finite one-dimensional sequence")
    if dgp == "dgp1_bivariate_normal":
        required = ("mu1", "mu2", "sigma1", "sigma2", "correlation")
        _require_parameters(parameters, required)
        sigma1 = float(parameters["sigma1"])
        sigma2 = float(parameters["sigma2"])
        if sigma1 <= 0 or sigma2 <= 0 or abs(float(parameters["correlation"])) >= 1:
            raise ValueError("DGP 1 scales must be positive and correlation in (-1, 1)")
        slope = float(parameters["correlation"]) * sigma2 / sigma1
        result = float(parameters["mu2"]) + slope * (values - float(parameters["mu1"]))
    elif dgp == "dgp2_lognormal":
        required = ("alpha", "beta", "sigma_e")
        _require_parameters(parameters, required)
        if float(parameters["sigma_e"]) <= 0:
            raise ValueError("DGP 2 sigma_e must be positive")
        result = np.exp(
            float(parameters["alpha"])
            + float(parameters["beta"]) * values
            + 0.5 * float(parameters["sigma_e"]) ** 2
        )
    elif dgp == "dgp3_quadratic":
        required = ("alpha", "beta", "gamma", "sigma1")
        _require_parameters(parameters, required)
        if float(parameters["sigma1"]) <= 0:
            raise ValueError("DGP 3 sigma1 must be positive")
        if float(parameters["gamma"]) == 0:
            raise ValueError("DGP 3 gamma must be nonzero")
        result = (
            float(parameters["alpha"])
            + float(parameters["beta"]) * values
            + float(parameters["gamma"])
            * (values**2 - float(parameters["sigma1"]) ** 2)
        )
    else:
        raise ValueError(f"unknown DGP: {dgp}")
    if not np.isfinite(result).all():
        raise ValueError("analytic conditional mean is not finite")
    return np.asarray(result, dtype=float)


def dgp_conditional_diagnostic(
    dgp: str,
    parameters: Mapping[str, float],
    x1: Sequence[float] | np.ndarray,
    imputation_model_conditional_mean: Sequence[float] | np.ndarray,
    *,
    masked_outcome_truth: Sequence[float] | np.ndarray | None = None,
    bins: int = 5,
) -> dict[str, Any]:
    """Compare supplied imputation-model predictions with analytic DGP truth."""
    truth = true_conditional_mean(dgp, x1, parameters)
    result = conditional_prediction_diagnostics(
        x1,
        truth,
        imputation_model_conditional_mean,
        observed_outcome=masked_outcome_truth,
        bins=bins,
    )
    return {
        "dgp": dgp,
        "dgp_parameters": dict(parameters),
        "prediction_source": "imputation-model conditional mean supplied by caller",
        **result,
    }


def conditional_prediction_diagnostics(
    x1: Sequence[float] | np.ndarray,
    true_mean: Sequence[float] | np.ndarray,
    predicted_mean: Sequence[float] | np.ndarray,
    *,
    observed_outcome: Sequence[float] | np.ndarray | None = None,
    bins: int = 5,
) -> dict[str, Any]:
    """Report conditional-mean error over ordered x1 quantile regions.

    Optional outcome error is prediction error against masked truth and is
    intended only for synthetic DGP diagnostic outputs.
    """
    x = np.asarray(x1, dtype=float)
    truth = np.asarray(true_mean, dtype=float)
    prediction = np.asarray(predicted_mean, dtype=float)
    if x.ndim != 1 or truth.shape != x.shape or prediction.shape != x.shape:
        raise ValueError("x1, true_mean, and predicted_mean must be equal-length vectors")
    if x.size == 0 or not np.isfinite(x).all() or not np.isfinite(truth).all() or not np.isfinite(prediction).all():
        raise ValueError("conditional diagnostic inputs must be non-empty and finite")
    if isinstance(bins, bool) or not isinstance(bins, (int, np.integer)) or bins < 1:
        raise ValueError("bins must be a positive integer")
    outcome = None
    if observed_outcome is not None:
        outcome = np.asarray(observed_outcome, dtype=float)
        if outcome.shape != x.shape or not np.isfinite(outcome).all():
            raise ValueError("observed_outcome must be finite and have the same shape")

    edges = np.unique(np.quantile(x, np.linspace(0.0, 1.0, int(bins) + 1)))
    bin_ids = np.zeros(x.size, dtype=int) if edges.size < 2 else np.digitize(
        x, edges[1:-1], right=True
    )
    rows = []
    for bin_id in sorted(set(int(value) for value in bin_ids)):
        selected = bin_ids == bin_id
        conditional_error = prediction[selected] - truth[selected]
        row: dict[str, Any] = {
            "region": bin_id + 1,
            "n": int(selected.sum()),
            "x1_min": float(np.min(x[selected])),
            "x1_max": float(np.max(x[selected])),
            "true_conditional_mean": float(np.mean(truth[selected])),
            "predicted_conditional_mean": float(np.mean(prediction[selected])),
            "conditional_mean_bias": float(np.mean(conditional_error)),
            "conditional_mean_rmse": float(np.sqrt(np.mean(conditional_error**2))),
        }
        if outcome is not None:
            row["outcome_prediction_rmse"] = float(
                np.sqrt(np.mean((prediction[selected] - outcome[selected]) ** 2))
            )
        rows.append(row)
    errors = prediction - truth
    return {
        "diagnostic_scope": "synthetic known-DGP only; not a real-data performance metric",
        "n": int(x.size),
        "conditional_mean_bias": float(np.mean(errors)),
        "conditional_mean_rmse": float(np.sqrt(np.mean(errors**2))),
        "regions": rows,
    }


def paired_coverage_difference(
    method_records: Sequence[Mapping[str, Any]],
    comparator_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return replicate-paired method-minus-comparator coverage differences."""
    def keyed(records: Sequence[Mapping[str, Any]]) -> dict[str, tuple[bool, bool]]:
        output: dict[str, tuple[bool, bool]] = {}
        for record in records:
            replicate_id = record.get("replicate_id")
            if replicate_id is None or replicate_id in output:
                raise ValueError("records require unique, non-null replicate_id values")
            status = record.get("status")
            lower = _finite_number(record.get("ci_lower"))
            upper = _finite_number(record.get("ci_upper"))
            truth = _finite_number(record.get("truth"))
            valid = bool(
                status == "success"
                and lower is not None
                and upper is not None
                and lower <= upper
                and truth is not None
            )
            output[str(replicate_id)] = (
                bool(valid and lower <= truth <= upper),
                valid,
            )
        return output

    method = keyed(method_records)
    comparator = keyed(comparator_records)
    shared = sorted(method.keys() & comparator.keys())
    if not shared:
        raise ValueError("method records must share at least one replicate_id")
    paired = [
        replicate
        for replicate in shared
        if method[replicate][1] and comparator[replicate][1]
    ]
    if not paired:
        raise ValueError("no shared replicates have valid finite intervals for both methods")
    paired_rows = [
        {
            "replicate_id": replicate,
            "method_covered": method[replicate][0],
            "comparator_covered": comparator[replicate][0],
            "difference": int(method[replicate][0]) - int(comparator[replicate][0]),
        }
        for replicate in paired
    ]
    differences = [row["difference"] for row in paired_rows]
    mean_difference = float(np.mean(differences))
    if len(differences) > 1:
        standard_error = float(np.std(differences, ddof=1) / math.sqrt(len(differences)))
        critical = float(t.ppf(0.975, df=len(differences) - 1))
        half_width = critical * standard_error
    else:
        standard_error = None
        half_width = None
    counts = Counter(differences)
    return {
        "paired_replicates": len(paired),
        "coverage_difference_method_minus_comparator": mean_difference,
        "paired_mc_standard_error": standard_error,
        "paired_student_t_95_mc_interval": (
            (mean_difference - half_width, mean_difference + half_width)
            if half_width is not None
            else None
        ),
        "method_only_covers": counts[1],
        "comparator_only_covers": counts[-1],
        "both_cover": sum(
            method[replicate][0] and comparator[replicate][0] for replicate in paired
        ),
        "neither_covers": sum(
            not method[replicate][0] and not comparator[replicate][0] for replicate in paired
        ),
        "paired_replicate_differences": paired_rows,
        "shared_scheduled_replicates": len(shared),
        "paired_valid_interval_replicates": len(paired),
        "excluded_pairs_without_two_valid_intervals": len(shared) - len(paired),
        "interpretation": "descriptive paired Monte Carlo difference; no superiority claim",
    }


def _require_parameters(parameters: Mapping[str, float], names: Sequence[str]) -> None:
    missing = [name for name in names if name not in parameters]
    if missing:
        raise ValueError(f"missing DGP parameters: {missing}")
    if not all(math.isfinite(float(parameters[name])) for name in names):
        raise ValueError("DGP parameters must be finite")


def _finite_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _mean_optional(values: Any) -> float | None:
    finite = [
        float(value)
        for value in values
        if value is not None and math.isfinite(float(value))
    ]
    return float(np.mean(finite)) if finite else None


def _weighted_mean(values: Sequence[tuple[float, int]]) -> float | None:
    denominator = sum(weight for _, weight in values)
    if denominator == 0:
        return None
    return sum(value * weight for value, weight in values) / denominator
