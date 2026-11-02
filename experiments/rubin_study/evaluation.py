"""Separate inferential coverage from interval-generation reliability."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from numbers import Integral
from typing import Any

from rubin_study.diagnostics import exact_binomial_interval, variance_decomposition

def _finite_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def summarize_replicates(
    records: Sequence[Mapping[str, Any]], nominal_coverage: float = 0.95
) -> dict[str, Any]:
    """Summarize coverage and reliability over every scheduled replicate.

    A valid finite interval requires ``status == "success"``, finite ordered
    endpoints, finite width, and finite truth. Failed runs, undefined
    intervals, and invalid intervals are mutually exclusive categories.
    """
    if not records:
        raise ValueError("records must contain every scheduled replicate")
    if not math.isfinite(nominal_coverage) or not 0 < nominal_coverage < 1:
        raise ValueError("nominal_coverage must be strictly between zero and one")

    failures: Counter[str] = Counter()
    covered = 0
    finite_intervals = 0
    widths: list[float] = []
    biases: list[float] = []
    estimates: list[float] = []
    standard_errors: list[float] = []
    pooled_degrees_of_freedom: list[float] = []
    pooling_diagnostics: list[dict[str, Any]] = []

    for row in records:
        status = row.get("status")
        truth = _finite_number(row.get("truth"))
        estimate_value = row.get("pooled_estimate")
        if estimate_value is None:
            estimate_value = row.get("estimate")
        estimate = _finite_number(estimate_value)
        if truth is not None and estimate is not None:
            estimates.append(estimate)
            biases.append(estimate - truth)
        standard_error = _finite_number(row.get("pooled_standard_error"))
        if standard_error is None:
            standard_error = _finite_number(row.get("standard_error"))
        if standard_error is not None and standard_error >= 0:
            standard_errors.append(standard_error)
        degrees_of_freedom = _finite_number(
            row.get("pooled_degrees_of_freedom", row.get("degrees_of_freedom"))
        )
        if degrees_of_freedom is not None and degrees_of_freedom >= 0:
            pooled_degrees_of_freedom.append(degrees_of_freedom)
        within = _finite_number(row.get("within_imputation_variance"))
        between = _finite_number(row.get("between_imputation_variance"))
        imputations = row.get("imputations", row.get("m"))
        if (
            within is not None
            and between is not None
            and isinstance(imputations, Integral)
            and not isinstance(imputations, bool)
            and imputations >= 2
        ):
            pooling_diagnostics.append(
                variance_decomposition(within, between, imputations)
            )

        if status in {"failed", "error"}:
            failures["failed_run"] += 1
            continue
        if status in {"invalid", "invalid_interval"}:
            failures["invalid_interval"] += 1
            continue
        if status in {"undefined", "undefined_interval"}:
            failures["undefined_interval"] += 1
            continue
        if status != "success":
            raise ValueError(f"unknown replicate status: {status!r}")

        lower = _finite_number(row.get("ci_lower"))
        upper = _finite_number(row.get("ci_upper"))

        if lower is None or upper is None:
            failures["undefined_interval"] += 1
            continue
        width = upper - lower
        if lower > upper or truth is None or not math.isfinite(width):
            failures["invalid_interval"] += 1
            continue

        finite_intervals += 1
        widths.append(width)
        is_covered = lower <= truth <= upper
        covered += int(is_covered)

    scheduled = len(records)
    failure_count = sum(failures.values())
    coverage = covered / finite_intervals if finite_intervals else None
    coverage_interval = (
        exact_binomial_interval(covered, finite_intervals)
        if finite_intervals
        else None
    )
    estimate_sd = math.sqrt(_sample_variance(estimates)) if len(estimates) > 1 else None
    mean_bias = sum(biases) / len(biases) if biases else None
    mean_standard_error = (
        sum(standard_errors) / len(standard_errors) if standard_errors else None
    )
    variance_summary = {
        "within_imputation_variance": _mean(
            item["within_imputation_variance"] for item in pooling_diagnostics
        ),
        "between_imputation_variance": _mean(
            item["between_imputation_variance"] for item in pooling_diagnostics
        ),
        "total_variance": _mean(item["total_variance"] for item in pooling_diagnostics),
        "relative_increase_in_variance": _mean(
            item["relative_increase_in_variance"] for item in pooling_diagnostics
        ),
        "relative_increase_in_variance_undefined_count": sum(
            item["relative_increase_in_variance"] is None
            for item in pooling_diagnostics
        ),
        "fraction_of_missing_information": _mean(
            item["fraction_of_missing_information"] for item in pooling_diagnostics
        ),
        "relative_efficiency": _mean(
            item["relative_efficiency"] for item in pooling_diagnostics
        ),
        "within_variance_share": _mean(
            item["within_variance_share"] for item in pooling_diagnostics
        ),
        "between_variance_share": _mean(
            item["between_variance_share"] for item in pooling_diagnostics
        ),
    }
    return {
        "nominal_coverage": nominal_coverage,
        "scheduled_runs": scheduled,
        "finite_interval_runs": finite_intervals,
        "covered_finite_runs": covered,
        "coverage_among_finite_intervals": (
            coverage
        ),
        "exact_95_percent_binomial_interval": coverage_interval,
        "failure_counts": {
            category: failures.get(category, 0)
            for category in ("failed_run", "invalid_interval", "undefined_interval")
        },
        "failed_or_invalid_or_undefined_runs": failure_count,
        "failure_rate": failure_count / scheduled,
        "all_scheduled_operational_success_adjusted_coverage": covered / scheduled,
        "mean_interval_width_finite_intervals": (
            sum(widths) / len(widths) if widths else None
        ),
        "mean_bias_available_estimates": (
            mean_bias
        ),
        "mean_absolute_bias_available_estimates": (
            sum(abs(value) for value in biases) / len(biases) if biases else None
        ),
        "rmse_available_estimates": (
            math.sqrt(
                sum(value**2 for value in biases) / len(biases)
            )
            if biases
            else None
        ),
        "estimate_variance_available_estimates": (
            _sample_variance(estimates) if len(estimates) > 1 else None
        ),
        "empirical_estimate_sd_available_estimates": estimate_sd,
        "mean_pooled_standard_error_available": mean_standard_error,
        "mean_pooled_degrees_of_freedom_available": (
            _mean(pooled_degrees_of_freedom) if pooled_degrees_of_freedom else None
        ),
        "mean_pooled_se_to_empirical_sd": (
            mean_standard_error / estimate_sd
            if mean_standard_error is not None and estimate_sd not in (None, 0.0)
            else None
        ),
        "mean_variance_decomposition": variance_summary,
        "variance_decomposition_denominator": len(pooling_diagnostics),
        "width_denominator": len(widths),
        "bias_denominator": len(biases),
        "variance_denominator": len(estimates),
    }


def _sample_variance(values: Sequence[float]) -> float:
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _mean(values: Sequence[float] | Any) -> float | None:
    finite = [
        float(value)
        for value in values
        if value is not None and math.isfinite(float(value))
    ]
    return sum(finite) / len(finite) if finite else None
