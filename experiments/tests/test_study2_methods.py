from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import BayesianRidge

from rubin_study import study2_methods
from rubin_study.study2_methods import (
    PMMDonorPoolError,
    PMMModelFitError,
    _STREAM_COEFFICIENT,
    _fit_conditional_model,
    _predictor_design,
    _sample_posterior_coefficients,
    _stream,
    impute_uncertainty_ablation,
    imputation_stream_manifest,
)


def _target_only_frame() -> pd.DataFrame:
    rng = np.random.RandomState(81)
    predictor = np.linspace(-2.0, 2.0, 80)
    auxiliary = 0.7 * predictor + rng.normal(0, 0.5, len(predictor))
    outcome = 1.5 + 2.2 * predictor + 0.6 * auxiliary + rng.normal(
        0, 0.25, len(predictor)
    )
    frame = pd.DataFrame(
        {"predictor": predictor, "auxiliary": auxiliary, "outcome": outcome}
    )
    frame.loc[frame.index[::4], "outcome"] = np.nan
    return frame


def test_posterior_draw_matches_frozen_coefficient_fixture():
    design = np.array([
        [1.0, -1.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [1.0, 2.0],
        [1.0, 3.0],
    ])
    target = np.array([1.0, 1.8, 3.2, 3.9, 5.1])
    model = BayesianRidge(fit_intercept=False).fit(design, target)

    np.testing.assert_allclose(
        model.coef_,
        [1.9640227620633042, 1.031147111736075],
        rtol=2e-5,
        atol=1e-8,
    )
    np.testing.assert_allclose(
        model.sigma_,
        [
            [0.0090611754800291, -0.0030179178356598],
            [-0.0030179178356598, 0.0030253398087096],
        ],
        rtol=2e-5,
        atol=1e-9,
    )
    draw = _sample_posterior_coefficients(model, np.random.default_rng(2026))
    np.testing.assert_allclose(
        draw,
        [1.9542419526816814, 1.071369247137405],
        rtol=2e-5,
        atol=1e-8,
    )


def test_explicit_intercept_is_in_posterior_covariance_and_draw():
    predictor = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
    target = 7.0 + 1.5 * predictor + np.array([0.3, -0.2, 0.1, 0.2, -0.1, 0.05])
    explicit_design = np.column_stack((np.ones(len(predictor)), predictor))

    centered_intercept_model = BayesianRidge(fit_intercept=True).fit(
        predictor[:, None], target
    )
    explicit_intercept_model = BayesianRidge(fit_intercept=False).fit(
        explicit_design, target
    )

    assert centered_intercept_model.sigma_.shape == (1, 1)
    assert explicit_intercept_model.coef_.shape == (2,)
    assert explicit_intercept_model.sigma_.shape == (2, 2)
    assert explicit_intercept_model.sigma_[0, 0] > 0
    assert np.isfinite(explicit_intercept_model.sigma_).all()
    assert not np.allclose(
        centered_intercept_model.predict(predictor[:, None]),
        explicit_design @ explicit_intercept_model.coef_,
    )

    draws = np.array([
        _sample_posterior_coefficients(
            explicit_intercept_model, np.random.default_rng(seed)
        )
        for seed in range(500)
    ])
    assert draws[:, 0].std(ddof=1) > 0
    assert np.isclose(
        np.cov(draws.T, ddof=1)[0, 0],
        explicit_intercept_model.sigma_[0, 0],
        rtol=0.15,
    )


def test_posterior_sampler_rejects_bad_covariance_dimensions_and_values():
    with pytest.raises(ValueError, match="dimensions"):
        _sample_posterior_coefficients(
            SimpleNamespace(coef_=np.array([0.0, 1.0]), sigma_=np.eye(1)),
            np.random.default_rng(1),
        )
    with pytest.raises(ValueError, match="positive semidefinite"):
        _sample_posterior_coefficients(
            SimpleNamespace(coef_=np.array([0.0]), sigma_=np.array([[-0.1]])),
            np.random.default_rng(1),
        )
    with pytest.raises(ValueError, match="symmetric"):
        _sample_posterior_coefficients(
            SimpleNamespace(coef_=np.array([0.0, 1.0]), sigma_=np.array([[1.0, 1.0], [0.0, 1.0]])),
            np.random.default_rng(1),
        )


def test_all_ablation_variants_complete_data_and_preserve_observed_values():
    masked = _target_only_frame()
    methods = ("posterior_only", "bootstrap_only", "bootstrap_pmm_candidate")
    for method in methods:
        completed = impute_uncertainty_ablation(
            masked,
            m=3,
            seed=127,
            method=method,
            target_column="outcome",
        )
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


def test_posterior_only_uses_coefficient_draw_without_bootstrap_or_residual_noise():
    masked = _target_only_frame()
    seed = 291
    new = impute_uncertainty_ablation(
        masked, m=3, seed=seed, method="posterior_only", target_column="outcome"
    )
    target = masked["outcome"].to_numpy()
    observed = np.isfinite(target)
    predictors = masked[["predictor", "auxiliary"]].to_numpy()
    model, mean, scale, active = _fit_conditional_model(
        predictors[observed], target[observed]
    )
    coefficients = _sample_posterior_coefficients(
        model, _stream(seed, 0, _STREAM_COEFFICIENT)
    )
    expected_design = _predictor_design(
        predictors[~observed], mean, scale, active
    )
    np.testing.assert_allclose(
        new[0].loc[~masked["outcome"].notna(), "outcome"].to_numpy(),
        expected_design @ coefficients,
    )
    assert any(
        not np.allclose(new[0]["outcome"], frame["outcome"])
        for frame in new[1:]
    )


@pytest.mark.parametrize("method", ["posterior_only", "bootstrap_only", "bootstrap_pmm_candidate"])
def test_ablation_variants_reproduce_for_fixed_seed(method):
    masked = _target_only_frame()
    arguments = {
        "df": masked,
        "m": 3,
        "seed": 309,
        "method": method,
        "target_column": "outcome",
    }
    first = impute_uncertainty_ablation(**arguments)
    second = impute_uncertainty_ablation(**arguments)
    for left, right in zip(first, second, strict=True):
        pd.testing.assert_frame_equal(left, right)


def test_stream_manifest_uses_distinct_entropy_keys_for_each_random_role():
    manifest = imputation_stream_manifest(120, 4, "bootstrap_pmm_candidate")
    keys = [tuple(item["seed_sequence_entropy"]) for item in manifest["streams"]]
    assert len(keys) == 12
    assert len(set(keys)) == len(keys)
    assert {item["role"] for item in manifest["streams"]} == {
        "bootstrap_rows", "coefficient_posterior", "donor_selection"
    }
    assert all(item["seed_sequence_entropy"][0] == 120 for item in manifest["streams"])


def test_bootstrap_pmm_values_are_drawn_from_each_bootstrap_donor_pool():
    masked = _target_only_frame()
    seed = 115
    completed = impute_uncertainty_ablation(
        masked,
        m=3,
        seed=seed,
        method="bootstrap_pmm_candidate",
        target_column="outcome",
    )
    observed = masked["outcome"].notna().to_numpy()
    original_values = masked["outcome"].to_numpy()
    for draw, frame in enumerate(completed):
        bootstrap_rows = _stream(seed, draw, 1).integers(
            0, len(masked), size=len(masked)
        )
        donor_values = original_values[bootstrap_rows[observed[bootstrap_rows]]]
        assert donor_values.size > 0
        imputed_values = frame.loc[~masked["outcome"].notna(), "outcome"].to_numpy()
        assert set(imputed_values).issubset(set(donor_values))


def test_bootstrap_only_uses_bootstrap_variation_without_posterior_sampling():
    masked = _target_only_frame()
    first = impute_uncertainty_ablation(
        masked, m=3, seed=81, method="bootstrap_only"
    )
    repeated = impute_uncertainty_ablation(
        masked, m=3, seed=81, method="bootstrap_only"
    )
    for left, right in zip(first, repeated, strict=True):
        pd.testing.assert_frame_equal(left, right)
    assert any(
        not np.allclose(first[0].to_numpy(), other.to_numpy())
        for other in first[1:]
    )


def test_bootstrap_only_disables_iterative_posterior_sampling(monkeypatch):
    observed_flags = []
    original = study2_methods._study2_iterative_imputer

    def tracking_imputer(seed, sample_posterior):
        observed_flags.append(sample_posterior)
        return original(seed, sample_posterior)

    monkeypatch.setattr(
        study2_methods, "_study2_iterative_imputer", tracking_imputer
    )
    study2_methods.impute_uncertainty_ablation(
        _target_only_frame(), m=3, seed=20, method="bootstrap_only"
    )
    assert observed_flags == [False, False, False]


def test_bootstrap_pmm_rejects_incomplete_predictors_and_bad_donor_count():
    masked = _target_only_frame()
    masked.loc[0, "auxiliary"] = np.nan
    with pytest.raises(ValueError, match="complete predictors"):
        impute_uncertainty_ablation(
            masked, m=2, seed=1, method="bootstrap_pmm_candidate", target_column="outcome"
        )

    with pytest.raises(ValueError, match="positive integer"):
        impute_uncertainty_ablation(
            _target_only_frame(),
            m=2,
            seed=1,
            method="bootstrap_pmm_candidate",
            target_column="outcome",
            donor_count=0,
        )

    few_donors = pd.DataFrame({
        "predictor": np.arange(8, dtype=float),
        "outcome": [1.0, 2.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
    })
    with pytest.raises(PMMDonorPoolError, match="at least 5 are required") as error:
        impute_uncertainty_ablation(
            few_donors,
            m=2,
            seed=1,
            method="bootstrap_pmm_candidate",
            target_column="outcome",
        )
    assert error.value.failure_stage == "donor_pool"


def test_candidate_and_posterior_only_reject_all_missing_targets():
    masked = _target_only_frame()
    masked["outcome"] = np.nan
    for method in ("posterior_only", "bootstrap_pmm_candidate"):
        with pytest.raises(ValueError, match="entirely missing"):
            impute_uncertainty_ablation(
                masked,
                m=2,
                seed=1,
                method=method,
                target_column="outcome",
            )


def test_bootstrap_pmm_rejects_only_constant_predictors():
    masked = pd.DataFrame({
        "constant": np.ones(100),
        "outcome": [*np.arange(90, dtype=float), *([np.nan] * 10)],
    })
    with pytest.raises(PMMModelFitError, match="nonconstant predictor") as error:
        impute_uncertainty_ablation(
            masked,
            m=2,
            seed=1,
            method="bootstrap_pmm_candidate",
            target_column="outcome",
        )
    assert error.value.failure_stage == "conditional_model_fit"


def test_posterior_only_requires_one_named_target_and_complete_predictors():
    masked = _target_only_frame()
    with pytest.raises(ValueError, match="target_column"):
        impute_uncertainty_ablation(
            masked, m=2, seed=1, method="posterior_only"
        )
    masked.loc[0, "auxiliary"] = np.nan
    with pytest.raises(ValueError, match="complete predictors"):
        impute_uncertainty_ablation(
            masked,
            m=2,
            seed=1,
            method="posterior_only",
            target_column="outcome",
        )
