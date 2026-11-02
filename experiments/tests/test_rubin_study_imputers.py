import numpy as np
import pandas as pd

from rubin_study.imputers import (
    analyze_column_mean,
    analyze_ols_coefficient,
    impute_m_datasets,
    naive_single_imputation_interval,
    pool_scalar_analysis,
)


def _masked_frame() -> pd.DataFrame:
    rng = np.random.RandomState(81)
    predictor = np.linspace(-2.0, 2.0, 120)
    auxiliary = 0.7 * predictor + rng.normal(0, 0.5, len(predictor))
    outcome = 1.5 + 2.2 * predictor + 0.6 * auxiliary + rng.normal(
        0, 0.25, len(predictor)
    )
    frame = pd.DataFrame(
        {"predictor": predictor, "auxiliary": auxiliary, "outcome": outcome},
        index=pd.Index(range(1000, 1120), name="record"),
    )
    frame.loc[frame.index[::4], "outcome"] = np.nan
    frame.loc[frame.index[1::7], "auxiliary"] = np.nan
    return frame


def test_imputation_methods_return_m_complete_frames_and_preserve_observed_values():
    masked = _masked_frame()

    for method in ("median", "knn", "mice_improper", "mice_proper"):
        completed = impute_m_datasets(masked, m=3, seed=127, method=method)

        assert len(completed) == 3
        for frame in completed:
            assert frame.shape == masked.shape
            assert frame.index.equals(masked.index)
            assert frame.columns.equals(masked.columns)
            assert frame.notna().all().all()
            np.testing.assert_array_equal(
                frame.where(masked.notna()).to_numpy(),
                masked.to_numpy(),
            )


def test_stochastic_methods_are_reproducible_for_the_same_seed():
    masked = _masked_frame()

    for method in ("mice_improper", "mice_proper"):
        first = impute_m_datasets(masked, m=3, seed=291, method=method)
        second = impute_m_datasets(masked, m=3, seed=291, method=method)

        for first_frame, second_frame in zip(first, second):
            pd.testing.assert_frame_equal(first_frame, second_frame)


def test_improper_mice_draws_differ():
    completed = impute_m_datasets(
        _masked_frame(), m=4, seed=309, method="mice_improper"
    )

    assert any(
        not np.allclose(
            completed[0].to_numpy(),
            draw.to_numpy(),
            rtol=0,
            atol=1e-12,
        )
        for draw in completed[1:]
    )


def test_proper_bootstrap_mice_differs_from_improper_mice():
    masked = _masked_frame()
    improper = impute_m_datasets(masked, m=3, seed=909, method="mice_improper")
    proper = impute_m_datasets(masked, m=3, seed=909, method="mice_proper")

    assert any(
        not np.allclose(left.to_numpy(), right.to_numpy(), rtol=0, atol=1e-12)
        for left, right in zip(improper, proper)
    )


def test_analysis_functions_return_estimate_variance_and_complete_data_df():
    completed = pd.DataFrame({
        "x": [0.0, 1.0, 2.0, 3.0, 4.0],
        "y": [1.0, 2.0, 2.0, 4.0, 6.0],
    })

    mean_q, mean_u, mean_df = analyze_column_mean(completed, "y")
    slope_q, slope_u, slope_df = analyze_ols_coefficient(
        completed, outcome="y", predictor="x"
    )

    assert mean_q == 3.0
    assert mean_u == completed["y"].var(ddof=1) / len(completed)
    assert mean_df == 4.0
    assert slope_q > 0
    assert slope_u >= 0
    assert slope_df == 3.0


def _heteroskedastic_ols_frame() -> pd.DataFrame:
    predictor = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    residual = np.array([1.0, -2.0, 2.0, -2.0, 1.0])
    return pd.DataFrame({
        "x": predictor,
        "y": 2.0 * predictor + residual,
    })


def test_hc3_slope_variance_matches_numpy_sandwich_reference():
    completed = _heteroskedastic_ols_frame()
    estimate, variance, complete_df = analyze_ols_coefficient(
        completed, outcome="y", predictor="x"
    )
    design = np.column_stack((np.ones(len(completed)), completed["x"].to_numpy()))
    response = completed["y"].to_numpy()
    bread = np.linalg.inv(design.T @ design)
    residual = response - design @ np.linalg.lstsq(design, response, rcond=None)[0]
    leverage = np.einsum("ij,jk,ik->i", design, bread, design)
    adjusted_residual_squared = (residual / (1.0 - leverage)) ** 2
    covariance = bread @ (
        design.T @ (design * adjusted_residual_squared[:, None])
    ) @ bread

    assert np.isclose(estimate, 2.0, rtol=0, atol=1e-15)
    assert complete_df == 3.0
    np.testing.assert_allclose(covariance[1, 1], 65.0 / 98.0, rtol=0, atol=1e-14)
    np.testing.assert_allclose(variance, covariance[1, 1], rtol=0, atol=1e-14)


def test_hc3_slope_variance_differs_from_classical_for_heteroskedastic_data():
    completed = _heteroskedastic_ols_frame()
    _, hc3_variance, _ = analyze_ols_coefficient(
        completed, outcome="y", predictor="x"
    )
    design = np.column_stack((np.ones(len(completed)), completed["x"].to_numpy()))
    response = completed["y"].to_numpy()
    residual = response - design @ np.linalg.lstsq(design, response, rcond=None)[0]
    classical_variance = (
        np.sum(residual**2)
        / (len(completed) - 2)
        * np.linalg.inv(design.T @ design)[1, 1]
    )

    np.testing.assert_allclose(classical_variance, 7.0 / 15.0, rtol=0, atol=1e-14)
    assert not np.isclose(hc3_variance, classical_variance)


def test_rubin_pooling_matches_hand_computed_example():
    completed_datasets = [
        pd.DataFrame({"value": [1.0, 2.0, 3.0]}),
        pd.DataFrame({"value": [2.0, 3.0, 4.0]}),
        pd.DataFrame({"value": [3.0, 4.0, 5.0]}),
    ]

    pooled = pool_scalar_analysis(
        completed_datasets,
        lambda frame: analyze_column_mean(frame, "value"),
    )

    expected_mean = 3.0
    expected_within = 1 / 3
    expected_between = 1.0
    expected_total = expected_within + (1 + 1 / 3) * expected_between
    assert pooled.estimate == expected_mean
    assert np.isclose(pooled.within_imputation_variance, expected_within)
    assert np.isclose(pooled.between_imputation_variance, expected_between)
    assert np.isclose(pooled.total_variance, expected_total)
    assert np.isclose(pooled.standard_error, 1.2909944487358056)
    assert np.isclose(pooled.missing_information_fraction, 0.8)
    assert np.isclose(pooled.degrees_of_freedom, 0.22288261515601776)
    assert pooled.confidence_interval is not None
    assert np.isclose(pooled.confidence_interval[0], -226725.47092045852)
    assert np.isclose(pooled.confidence_interval[1], 226731.47092045852)


def test_rubin_pooling_uses_hc3_slope_variances_with_barnard_rubin_df():
    base = _heteroskedastic_ols_frame()
    completed_datasets = []
    for slope_shift, residual_scale in ((-0.2, 0.8), (0.0, 1.0), (0.1, 1.2), (0.3, 1.5)):
        frame = base.copy()
        frame["y"] = (
            (2.0 + slope_shift) * frame["x"]
            + np.array([1.0, -2.0, 2.0, -2.0, 1.0]) * residual_scale
        )
        completed_datasets.append(frame)

    analyses = [
        analyze_ols_coefficient(frame, outcome="y", predictor="x")
        for frame in completed_datasets
    ]
    pooled = pool_scalar_analysis(
        completed_datasets,
        lambda frame: analyze_ols_coefficient(frame, outcome="y", predictor="x"),
    )
    expected_within = float(np.mean([result[1] for result in analyses]))
    expected_between = float(np.var([result[0] for result in analyses], ddof=1))
    expected_total = expected_within + (1 + 1 / len(analyses)) * expected_between
    fmi = (1 + 1 / len(analyses)) * expected_between / expected_total
    old_df = (len(analyses) - 1) / fmi**2
    complete_data_df = analyses[0][2]
    observed_df = (
        (complete_data_df + 1)
        / (complete_data_df + 3)
        * complete_data_df
        * (1 - fmi)
    )
    expected_barnard_rubin_df = 1 / (1 / old_df + 1 / observed_df)

    assert np.isclose(pooled.within_imputation_variance, expected_within)
    assert np.isclose(pooled.between_imputation_variance, expected_between)
    assert np.isclose(pooled.total_variance, expected_total)
    assert np.isclose(pooled.degrees_of_freedom, expected_barnard_rubin_df)
    assert pooled.confidence_interval is not None


def test_single_imputation_interval_is_explicitly_labeled_naive():
    result = naive_single_imputation_interval(
        estimate=2.0,
        within_variance=0.25,
        complete_data_df=9,
    )

    assert result["interval_type"] == "naive single imputation"
    assert result["confidence_interval"][0] < 2.0
    assert result["confidence_interval"][1] > 2.0
