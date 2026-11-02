import csv
import json
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest

from rubin_study.diagnostics import (
    conditional_prediction_diagnostics,
    dgp_conditional_diagnostic,
    exact_binomial_interval,
    interval_score,
    paired_coverage_difference,
    summarize_no_missing_gate,
    true_conditional_mean,
    variance_decomposition,
)
from rubin_study.reporting import write_study_report
from rubin_study.study2_methods import impute_uncertainty_ablation
import benchmark_rubin_study
from benchmark_rubin_study import build_performance_fixture, estimate_workload


def test_exact_binomial_interval_and_no_missing_compatibility_gate():
    lower, upper = exact_binomial_interval(950, 1000)
    assert lower < 0.95 < upper
    gate = summarize_no_missing_gate([True] * 85 + [False] * 15)
    assert gate["coverage"] == 0.85
    assert gate["exact_binomial_interval"][1] < 0.95
    assert gate["gate_pass"] is False


def test_variance_decomposition_reconciles_and_reports_finite_m_efficiency():
    result = variance_decomposition(2.0, 3.0, 4, complete_data_df=20)
    assert result["total_variance"] == pytest.approx(5.75)
    assert result["relative_increase_in_variance"] == pytest.approx(1.875)
    assert result["fraction_of_missing_information"] == pytest.approx(3.75 / 5.75)
    assert result["lambda_fraction"] == pytest.approx(3.75 / 5.75)
    assert result["finite_df_adjusted_fmi"] is not None
    assert result["relative_efficiency"] == pytest.approx(
        1 / (1 + result["fraction_of_missing_information"] / 4)
    )
    assert result["within_variance_share"] + result["between_variance_share"] == pytest.approx(1)


def test_interval_score_rewards_coverage_and_penalizes_misses():
    assert interval_score(0.5, 1.5, 1.0, alpha=0.05) == pytest.approx(1.0)
    assert interval_score(0.5, 1.5, 2.0, alpha=0.05) == pytest.approx(1.0 + 2 / 0.05 * 0.5)


@pytest.mark.parametrize("alpha", [0.0, 1.0, -0.1, np.nan, np.inf, -np.inf])
def test_interval_score_rejects_invalid_alpha(alpha):
    with pytest.raises(ValueError, match="alpha"):
        interval_score(0.5, 1.5, 1.0, alpha=alpha)


def test_interval_score_accepts_near_boundary_alpha():
    assert interval_score(0.5, 1.5, 2.0, alpha=0.999) == pytest.approx(
        1.0 + 2 / 0.999 * 0.5
    )


def test_variance_decomposition_marks_undefined_riv_without_success_fallback():
    result = variance_decomposition(0.0, 1.0, 20, complete_data_df=20)
    assert result["relative_increase_in_variance"] is None
    assert result["relative_increase_in_variance_status"] == (
        "undefined_zero_within_positive_between"
    )
    assert result["fraction_of_missing_information"] == 1.0
    assert result["finite_df_adjusted_fmi"] is None
    assert result["within_variance_share"] == 0.0
    assert result["between_variance_share"] == 1.0


def test_paired_coverage_difference_uses_only_valid_intervals_in_both_methods():
    method = [
        {"replicate_id": i, "status": "success", "ci_lower": 0, "ci_upper": 2, "truth": 1}
        for i in range(3)
    ] + [{"replicate_id": 3, "status": "failed"}]
    comparator = [
        {"replicate_id": 0, "status": "success", "ci_lower": 2, "ci_upper": 3, "truth": 1},
        {"replicate_id": 1, "status": "success", "ci_lower": 0, "ci_upper": 2, "truth": 1},
        {"replicate_id": 2, "status": "success", "ci_lower": 0, "ci_upper": 2, "truth": 1},
        {"replicate_id": 3, "status": "success", "ci_lower": 0, "ci_upper": 2, "truth": 1},
    ]
    result = paired_coverage_difference(method, comparator)
    assert result["shared_scheduled_replicates"] == 4
    assert result["paired_valid_interval_replicates"] == 3
    assert result["excluded_pairs_without_two_valid_intervals"] == 1
    assert result["coverage_difference_method_minus_comparator"] == pytest.approx(1 / 3)
    assert result["method_only_covers"] == 1
    assert result["comparator_only_covers"] == 0
    assert result["interpretation"].startswith("descriptive paired")


@pytest.mark.parametrize(
    ("dgp", "parameters", "expected"),
    [
        (
            "dgp1_bivariate_normal",
            {"mu1": 0, "mu2": 1, "sigma1": 2, "sigma2": 3, "correlation": 0.5},
            np.array([0.25, 1, 1.75]),
        ),
        (
            "dgp2_lognormal",
            {"alpha": 0, "beta": 1, "sigma_e": 0.2},
            np.exp(np.array([-1, 0, 1]) + 0.02),
        ),
        (
            "dgp3_quadratic",
            {"alpha": 2, "beta": 1, "gamma": 0.5, "sigma1": 1},
            np.array([1, 1.5, 3]),
        ),
    ],
)
def test_registered_dgp_conditional_mean_formulas(dgp, parameters, expected):
    np.testing.assert_allclose(
        true_conditional_mean(dgp, [-1, 0, 1], parameters), expected
    )


def test_conditional_diagnostics_report_regionwise_error_as_synthetic_only():
    result = conditional_prediction_diagnostics(
        x1=[-2, -1, 0, 1, 2],
        true_mean=[4, 1, 0, 1, 4],
        predicted_mean=[3, 1, 0, 1, 5],
        observed_outcome=[4, 2, 0, 0, 5],
        bins=2,
    )
    assert result["diagnostic_scope"].startswith("synthetic known-DGP only")
    assert result["n"] == 5
    assert len(result["regions"]) == 2
    assert all("outcome_prediction_rmse" in region for region in result["regions"])


def test_dgp_conditional_diagnostic_compares_supplied_model_predictions_to_truth():
    result = dgp_conditional_diagnostic(
        "dgp3_quadratic",
        {"alpha": 2, "beta": 1, "gamma": 0.5, "sigma1": 1},
        x1=[-1, 0, 1],
        imputation_model_conditional_mean=[1, 1.5, 3],
        masked_outcome_truth=[0.8, 1.7, 3.2],
        bins=3,
    )
    assert result["dgp"] == "dgp3_quadratic"
    assert result["conditional_mean_rmse"] == pytest.approx(0)
    assert result["regions"][0]["outcome_prediction_rmse"] > 0


def test_pmm_diagnostics_are_deterministic_bounded_and_do_not_change_imputations():
    frame = pd.DataFrame({
        "predictor": np.linspace(-2, 2, 80),
        "outcome": np.linspace(1, 4, 80) + np.sin(np.arange(80)) * 0.1,
    })
    frame.loc[[3, 9, 17, 26, 34, 41, 52, 61], "outcome"] = np.nan
    plain = impute_uncertainty_ablation(
        frame, 3, 123, "bootstrap_pmm_candidate", target_column="outcome"
    )
    traced, diagnostics = impute_uncertainty_ablation(
        frame,
        3,
        123,
        "bootstrap_pmm_candidate",
        target_column="outcome",
        return_diagnostics=True,
        diagnostic_detail_limit=2,
    )
    assert isinstance(plain, list)
    assert len(diagnostics["draws"]) == 3
    assert len(diagnostics["details"]) == 2
    assert all(draw["donor_support_violations"] == 0 for draw in diagnostics["draws"])
    assert all(draw["selected_distance_max"] >= 0 for draw in diagnostics["draws"])
    for expected, actual in zip(plain, traced, strict=True):
        np.testing.assert_array_equal(expected.to_numpy(), actual.to_numpy())


def test_report_writes_cellwise_table_plot_and_pair_tables(tmp_path):
    records = []
    for method, intervals in (
        ("candidate", [(0, 2), (2, 3)]),
        ("reference", [(2, 3), (0, 2)]),
    ):
        for replicate, (lower, upper) in enumerate(intervals):
            records.append({
                "dgp": "dgp1",
                "mechanism": "MCAR",
                "mask_rate": 0.1,
                "estimand": "mean",
                "method": method,
                "replicate_id": replicate,
                "status": "success",
                "ci_lower": lower,
                "ci_upper": upper,
                "truth": 1,
                "pooled_estimate": 1.2,
                "pooled_standard_error": 0.2,
                "within_imputation_variance": 0.03,
                "between_imputation_variance": 0.01,
                "imputations": 20,
                **(
                    {
                        "dgp": "dgp1",
                        "pmm_diagnostics": {
                            "draws": [{
                                "draw": 0,
                                "missing_cells": 2,
                                "donor_count": 8,
                                "unique_source_donors_available": 6,
                                "donor_support_violations": 0,
                                "selected_distance_mean": 0.2,
                                "selected_distance_median": 0.2,
                                "selected_distance_p95": 0.3,
                                "selected_distance_max": 0.3,
                                "distance_outlier_fraction": 0.0,
                                "unique_donor_copy_fraction": 0.25,
                                "unique_source_donor_fraction": 1 / 3,
                                "max_donor_copy_reuse": 1,
                                "max_source_donor_reuse": 1,
                                "source_donor_selection_hhi": 0.5,
                                "source_donor_selection_entropy": 0.69,
                            }],
                            "distance_definition": "test distance definition",
                            "distance_outlier_rule": "test outlier rule",
                            "donor_identity_definition": "test donor identity",
                        },
                        "conditional_diagnostics": {
                            "diagnostic_scope": "synthetic known-DGP only",
                            "conditional_mean_bias": 0.1,
                            "conditional_mean_rmse": 0.2,
                            "regions": [{
                                "region": 1,
                                "n": 2,
                                "true_conditional_mean": 1.0,
                                "predicted_conditional_mean": 1.1,
                                "conditional_mean_bias": 0.1,
                                "conditional_mean_rmse": 0.1,
                                "outcome_prediction_rmse": 0.3,
                            }],
                        },
                    }
                    if method == "candidate"
                    else {}
                ),
            })
    metadata = write_study_report(
        records,
        tmp_path,
        comparator="reference",
        no_missing_gate_records=[
            {"dgp": "dgp1", "estimand": "mean", "covered": value}
            for value in [True] * 95 + [False] * 5
        ],
    )
    assert metadata["reported_cells"] == 2
    assert (tmp_path / "cellwise_coverage.png").stat().st_size > 0
    assert (tmp_path / "pmm_donor_diagnostics.png").stat().st_size > 0
    assert (tmp_path / "conditional_mean_diagnostics.png").stat().st_size > 0
    assert (tmp_path / "report_metadata.json").exists()
    with (tmp_path / "cellwise_metrics.csv").open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 2
    assert rows[0]["exact_95_percent_binomial_interval"]
    with (tmp_path / "paired_coverage_replicates.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        paired = list(csv.DictReader(source))
    assert len(paired) == 2
    with (tmp_path / "variance_decomposition.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        variance_rows = list(csv.DictReader(source))
    assert len(variance_rows) == 4
    assert "fraction_of_missing_information" in variance_rows[0]
    with (tmp_path / "no_missing_gate.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        gates = list(csv.DictReader(source))
    assert len(gates) == 1
    assert gates[0]["gate_pass"] == "True"
    with (tmp_path / "pmm_donor_diagnostics.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        donor_rows = list(csv.DictReader(source))
    assert len(donor_rows) == 2
    with (tmp_path / "conditional_dgp_diagnostics.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        conditional_rows = list(csv.DictReader(source))
    assert len(conditional_rows) == 2


def test_feasibility_estimate_reports_scenarios_and_parallel_assumptions():
    measurements = [
        {"method": "mice_improper", "imputation_seconds_per_draw": 0.5, "analysis_and_pooling_seconds": 1, "peak_process_rss_bytes": 100},
        {"method": "mice_proper", "imputation_seconds_per_draw": 1.0, "analysis_and_pooling_seconds": 1, "peak_process_rss_bytes": 200},
        {"method": "bootstrap_pmm_candidate", "imputation_seconds_per_draw": 1.5, "analysis_and_pooling_seconds": 1, "peak_process_rss_bytes": 300},
    ]
    estimate = estimate_workload(measurements, {"example": 10})
    row = estimate["workload_scenarios"]["example"]
    assert row["sequential_estimated_hours_mean"] == pytest.approx(630 / 3600)
    assert row["parallel_estimates"]["4"]["estimated_wall_seconds"] == pytest.approx(
        630 / (4 * 0.75)
    )
    assert row["parallel_estimates"]["8"]["estimated_peak_worker_rss_bytes"] == 2400


@pytest.mark.parametrize(
    ("dgp", "mechanism"),
    [
        ("dgp1_bivariate_normal", "MCAR"),
        ("dgp2_lognormal", "MAR"),
        ("dgp3_quadratic", "MNAR"),
    ],
)
@pytest.mark.parametrize("rate", [0.1, 0.5])
def test_performance_fixtures_are_seeded_and_have_expected_scale(dgp, mechanism, rate):
    first = build_performance_fixture(dgp, mechanism, rate, n=500, seed=712)
    second = build_performance_fixture(dgp, mechanism, rate, n=500, seed=712)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 500
    assert first["x2"].isna().mean() == pytest.approx(rate, abs=0.06)


def test_benchmark_orchestration_records_actual_versions_and_method_scenarios(monkeypatch):
    def fake_run(command, **_kwargs):
        scenario = json.loads(command[-1])
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({
                **scenario,
                "imputation_seconds": 1.0,
                "imputation_seconds_per_draw": 0.05,
                "analysis_and_pooling_seconds": 0.1,
                "peak_process_rss_bytes": 1000,
            }),
            stderr="",
        )

    monkeypatch.setattr(benchmark_rubin_study.subprocess, "run", fake_run)
    monkeypatch.setattr(benchmark_rubin_study.platform, "platform", lambda: "test-platform")
    result = benchmark_rubin_study.run_benchmark(
        n=100, m=20, seed=10, worker_assumptions={1: 1.0}
    )
    assert len(result["measurements"]) == 18
    assert result["environment"]["scikit_learn"]
    assert "scikit_learn" in result["environment"]["declared_experiments_requirements"]
    assert result["feasibility"]["workload_scenarios"][
        "active_protocol_v5_1_100_replicates"
    ]["condition_count"] == 6300
