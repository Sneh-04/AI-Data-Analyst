import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import load_diabetes

from app.services.cleaning_service import (
    _multiple_impute_column, _multiple_impute_dataframe, fill_missing_values, handle_outliers_iqr)


@pytest.fixture
def correlated_frame():
    rng = np.random.RandomState(0)
    x = rng.randn(300)
    return pd.DataFrame({"x": x, "y": 2 * x + 0.1 * rng.randn(300), "z": rng.randn(300)})


def test_multiple_imputation_fills_everything_and_reports_uncertainty(correlated_frame):
    df = correlated_frame.copy()
    df.loc[[3, 10, 50], "y"] = np.nan
    filled, log = fill_missing_values(df, strategy="multiple")
    assert filled.isna().sum().sum() == 0
    assert len(log) == 3
    assert all(e["strategy_used"] == "multiple_imputation" and "imputation_uncertainty" in e for e in log)


def test_feature_aware_imputation_beats_marginal_when_columns_are_correlated(correlated_frame):
    truth = correlated_frame["y"].copy()
    rng = np.random.RandomState(1)
    hide = rng.rand(len(truth)) < 0.2
    df = correlated_frame.copy()
    df.loc[hide, "y"] = np.nan
    mice, _ = _multiple_impute_dataframe(df, n_imputations=5, random_state=1)
    marginal, _ = _multiple_impute_column(df["y"], random_state=1)
    err_mice = np.sqrt(np.mean((mice.loc[hide, "y"] - truth[hide]) ** 2))
    err_marg = np.sqrt(np.mean((marginal[hide] - truth[hide]) ** 2))
    assert err_mice < 0.5 * err_marg  # y = 2x + noise is almost fully recoverable from x


def test_uncertainty_is_informative_in_the_right_direction():
    rng = np.random.RandomState(2)
    x = rng.randn(500)
    df = pd.DataFrame({"x": x, "y": 2 * x + 0.3 * rng.randn(500), "z": rng.randn(500)})
    hide = rng.rand(500) < 0.2
    masked = df.copy()
    masked.loc[hide, "y"] = np.nan
    filled, unc = _multiple_impute_dataframe(masked, n_imputations=10, random_state=2)
    uncertainty_by_index = unc["y"]
    assert set(uncertainty_by_index) == set(masked.index[hide])
    assert all(value > 0 for value in uncertainty_by_index.values())


def test_single_numeric_column_falls_back_to_marginal_method():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0, 4.0, np.nan, 6.0]})
    filled, log = fill_missing_values(df, strategy="multiple")
    assert filled["a"].isna().sum() == 0 and len(log) == 2


def test_multiple_imputation_leaves_observed_values_and_categoricals_alone():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0, 4.0], "b": [2.0, 4.0, np.nan, 8.0], "c": ["u", None, "u", "v"]})
    filled, _ = fill_missing_values(df, strategy="multiple")
    assert filled.loc[0, "a"] == 1.0 and filled.loc[3, "b"] == 8.0
    assert filled["c"].isna().sum() == 0 and filled.loc[1, "c"] == "u"


def test_all_missing_column_does_not_crash():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [np.nan] * 4, "c": [2.0, np.nan, 6.0, 8.0]})
    filled, _ = fill_missing_values(df, strategy="multiple")
    assert filled["c"].isna().sum() == 0


def test_realistic_table_runs_fast_and_accurately():
    df = load_diabetes(as_frame=True).frame.drop(columns="target")
    mask = np.random.RandomState(0).rand(*df.shape) < 0.2
    filled, _ = fill_missing_values(df.mask(mask), strategy="multiple")
    rmse = np.sqrt(((filled.values - df.values)[mask] ** 2).mean())
    assert rmse < df.std().mean()  # better than predicting a constant


def test_default_strategy_and_outliers_unchanged():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0, 100.0], "b": ["x", None, "x", "y"]})
    filled, log = fill_missing_values(df)
    assert filled["a"].isna().sum() == 0 and {e["strategy_used"] for e in log} == {"median", "mode"}
    capped, outlier_log = handle_outliers_iqr(filled, "a")
    assert capped["a"].max() < 100 and len(outlier_log) == 1


def test_knn_preserves_unfillable_numeric_column_and_imputes_string_dtype():
    df = pd.DataFrame({
        "numeric": [1.0, np.nan, 3.0, 4.0, 5.0, 6.0],
        "all_missing": [np.nan] * 6,
        "category": pd.Series(["x", pd.NA, "x", "y", "y", "x"], dtype="string"),
    })
    filled, repair_log = fill_missing_values(df, strategy="knn")
    assert filled["numeric"].notna().all()
    assert filled["all_missing"].isna().all()
    assert filled["category"].notna().all()
    assert filled.loc[1, "category"] == "x"
    assert len(repair_log) == 2
