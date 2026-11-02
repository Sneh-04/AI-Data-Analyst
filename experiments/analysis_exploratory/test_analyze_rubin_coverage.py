import pandas as pd
import pytest

from experiments.analysis_exploratory.analyze_rubin_coverage import (
    paired_difference,
    undercoverage_decomposition,
)


def test_undercoverage_decomposition_reports_bias_sd_se_and_miss_direction():
    frame = pd.DataFrame(
        [
            {
                "status": "success",
                "truth": 10.0,
                "estimate": 8.0,
                "bias": -2.0,
                "standard_error": 1.0,
                "ci_lower": 7.0,
                "ci_upper": 9.0,
            },
            {
                "status": "success",
                "truth": 10.0,
                "estimate": 12.0,
                "bias": 2.0,
                "standard_error": 2.0,
                "ci_lower": 11.0,
                "ci_upper": 13.0,
            },
            {
                "status": "success",
                "truth": 10.0,
                "estimate": 12.0,
                "bias": 2.0,
                "standard_error": 4.0,
                "ci_lower": 9.0,
                "ci_upper": 13.0,
            },
        ]
    )

    result = undercoverage_decomposition(frame)

    assert result["n_intervals"] == 3
    assert result["mean_bias"] == pytest.approx(2.0 / 3.0)
    assert result["empirical_sd_estimate"] == pytest.approx((16.0 / 3.0) ** 0.5)
    assert result["mean_pooled_se"] == pytest.approx(7.0 / 3.0)
    assert result["mean_se_to_empirical_sd"] == pytest.approx(
        (7.0 / 3.0) / (16.0 / 3.0) ** 0.5
    )
    assert result["n_noncovering"] == 2
    assert result["share_noncovering_above_truth"] == pytest.approx(0.5)
    assert result["share_noncovering_below_truth"] == pytest.approx(0.5)


def test_paired_difference_counts_discordances_and_bootstraps_datasets():
    rows = []
    paired_coverages = {
        "dataset-a": [(True, False), (False, False)],
        "dataset-b": [(False, True), (False, False)],
    }
    for dataset, pairs in paired_coverages.items():
        for trial, (improper_covers, proper_covers) in enumerate(pairs):
            for method, covers in (
                ("mice_improper", improper_covers),
                ("mice_proper", proper_covers),
            ):
                rows.append(
                    {
                        "dataset": dataset,
                        "mechanism": "MCAR",
                        "mask_rate": 0.3,
                        "estimand": "mean",
                        "trial": trial,
                        "trial_seed": 100 + trial,
                        "mask_seed": 200 + trial,
                        "method": method,
                        "status": "success",
                        "truth": 0.0,
                        "estimate": 0.0,
                        "ci_lower": -1.0 if covers else 1.0,
                        "ci_upper": 1.0 if covers else 2.0,
                    }
                )

    result = paired_difference(pd.DataFrame(rows), n_bootstrap=2_000, seed=42)

    assert result["n_pairs"] == 4
    assert result["n_datasets"] == 2
    assert result["improper_covers_proper_does_not"] == 1
    assert result["proper_covers_improper_does_not"] == 1
    assert result["coverage_difference_improper_minus_proper"] == pytest.approx(0)
    assert result["bootstrap_ci_lower"] == pytest.approx(-0.5)
    assert result["bootstrap_ci_upper"] == pytest.approx(0.5)
