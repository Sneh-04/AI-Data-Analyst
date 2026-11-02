import math

import pytest

from rubin_study.evaluation import summarize_replicates


def test_coverage_and_operational_reliability_are_reported_separately():
    records = [
        {
            "status": "success",
            "ci_lower": 0.0,
            "ci_upper": 2.0,
            "truth": 1.0,
            "estimate": 1.0,
        },
        {
            "status": "success",
            "ci_lower": 1.1,
            "ci_upper": 2.0,
            "truth": 1.0,
            "estimate": 2.0,
        },
        {
            "status": "success",
            "ci_lower": None,
            "ci_upper": None,
            "interval_reason": "zero degrees of freedom",
        },
        {"status": "failed", "error_type": "imputation error"},
        {
            "status": "success",
            "ci_lower": 2.0,
            "ci_upper": 1.0,
            "truth": 1.0,
            "estimate": 1.5,
        },
    ]

    result = summarize_replicates(records)

    assert result["scheduled_runs"] == 5
    assert result["finite_interval_runs"] == 2
    assert result["covered_finite_runs"] == 1
    assert result["coverage_among_finite_intervals"] == 0.5
    assert result["failure_counts"] == {
        "failed_run": 1,
        "invalid_interval": 1,
        "undefined_interval": 1,
    }
    assert result["failed_or_invalid_or_undefined_runs"] == 3
    assert result["failure_rate"] == 0.6
    assert result["all_scheduled_operational_success_adjusted_coverage"] == 0.2
    assert result["mean_interval_width_finite_intervals"] == pytest.approx(1.45)
    assert result["mean_bias_available_estimates"] == pytest.approx(0.5)
    assert result["estimate_variance_available_estimates"] == pytest.approx(0.25)
    assert result["bias_denominator"] == 3
    assert result["variance_denominator"] == 3


def test_no_finite_intervals_keeps_coverage_undefined_but_failure_rate_defined():
    result = summarize_replicates([
        {"status": "failed"},
        {"status": "success", "ci_lower": None, "ci_upper": None},
    ])
    assert result["coverage_among_finite_intervals"] is None
    assert result["finite_interval_runs"] == 0
    assert result["failure_rate"] == 1.0
    assert result["all_scheduled_operational_success_adjusted_coverage"] == 0.0
    assert result["mean_interval_width_finite_intervals"] is None


def test_invalid_coverage_level_and_empty_schedule_fail_explicitly():
    with pytest.raises(ValueError, match="every scheduled"):
        summarize_replicates([])
    with pytest.raises(ValueError, match="strictly between"):
        summarize_replicates([{"status": "failed"}], nominal_coverage=1.0)


def test_nonfinite_or_non_numeric_interval_endpoints_are_not_coverage():
    result = summarize_replicates([
        {
            "status": "success",
            "ci_lower": math.nan,
            "ci_upper": "not-a-number",
            "truth": 0.0,
        }
    ])
    assert result["failure_counts"]["undefined_interval"] == 1
    assert result["coverage_among_finite_intervals"] is None


def test_explicit_interval_statuses_use_their_own_failure_categories():
    result = summarize_replicates([
        {"status": "failed"},
        {"status": "invalid_interval"},
        {"status": "undefined_interval"},
    ])
    assert result["failure_counts"] == {
        "failed_run": 1,
        "invalid_interval": 1,
        "undefined_interval": 1,
    }


def test_finite_endpoints_with_overflowing_width_are_invalid():
    result = summarize_replicates([
        {
            "status": "success",
            "ci_lower": -1e308,
            "ci_upper": 1e308,
            "truth": 0.0,
        }
    ])
    assert result["failure_counts"]["invalid_interval"] == 1
    assert result["finite_interval_runs"] == 0


def test_cell_summary_includes_exact_coverage_interval_and_rubin_decomposition():
    result = summarize_replicates([
        {
            "status": "success",
            "ci_lower": 0.0,
            "ci_upper": 2.0,
            "truth": 1.0,
            "pooled_estimate": 1.0,
            "pooled_standard_error": 0.5,
            "pooled_degrees_of_freedom": 10,
            "within_imputation_variance": 0.16,
            "between_imputation_variance": 0.04,
            "imputations": 20,
        },
        {
            "status": "success",
            "ci_lower": 0.0,
            "ci_upper": 2.0,
            "truth": 1.0,
            "pooled_estimate": 1.2,
            "pooled_standard_error": 0.6,
            "pooled_degrees_of_freedom": 9,
            "within_imputation_variance": 0.25,
            "between_imputation_variance": 0.05,
            "imputations": 20,
        },
    ])
    assert result["exact_95_percent_binomial_interval"] is not None
    decomposition = result["mean_variance_decomposition"]
    assert decomposition["within_imputation_variance"] == pytest.approx(0.205)
    assert decomposition["between_imputation_variance"] == pytest.approx(0.045)
    assert decomposition["fraction_of_missing_information"] is not None
    assert decomposition["relative_efficiency"] is not None
    assert decomposition["within_variance_share"] + decomposition["between_variance_share"] == pytest.approx(1)
    assert result["mean_pooled_degrees_of_freedom_available"] == pytest.approx(9.5)
