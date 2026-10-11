import numpy as np
import pandas as pd
import pytest

from app.services.health_service import calculate_health_score, detect_mnar_signals


def test_clean_table_scores_high():
    df = pd.DataFrame({"a": np.arange(100.0), "b": np.arange(100.0)[::-1] * 1.5})
    assert calculate_health_score(df)["score"] >= 90


def test_sentinel_values_are_counted_as_missing():
    df = pd.DataFrame({"a": ["x", "N/A", "-99", "y", "unknown"], "b": [1, 2, 3, 4, 5]})
    out = calculate_health_score(df)
    assert out["sentinel_missing_count"] == 3


def test_weights_must_sum_to_one_and_are_reported():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError):
        calculate_health_score(df, weights={"completeness": 0.5, "uniqueness": 0.5, "consistency": 0.5, "outliers": 0.5})
    out = calculate_health_score(df, weights={"completeness": 0.7, "uniqueness": 0.1, "consistency": 0.1, "outliers": 0.1})
    assert out["weights_used"]["completeness"] == pytest.approx(0.7)


def test_mnar_signal_detected_when_missingness_depends_on_another_column():
    rng = np.random.RandomState(0)
    driver = rng.randn(400)
    target = rng.randn(400)
    target[driver > 0.5] = np.nan
    signals = detect_mnar_signals(pd.DataFrame({"driver": driver, "target": target}))
    assert any("target" in s and "driver" in s for s in signals)


def test_no_mnar_signal_for_random_missingness():
    rng = np.random.RandomState(1)
    df = pd.DataFrame({"a": rng.randn(500), "b": rng.randn(500)})
    df.loc[rng.rand(500) < 0.1, "b"] = np.nan
    assert detect_mnar_signals(df) == []


def test_previous_score_gives_a_trend():
    df = pd.DataFrame({"a": np.arange(50.0)})
    assert calculate_health_score(df).get("score_trend") is None  # no previous score -> no trend claimed
    out = calculate_health_score(df, previous_score=50)
    assert out["score_trend"] == "improving" and out["previous_score"] == 50


def test_numeric_placeholders_outside_the_normal_range_are_detected():
    rng = np.random.RandomState(0)
    values = rng.normal(50, 5, 200)
    values[:20] = -99
    out = calculate_health_score(pd.DataFrame({"a": values, "b": rng.normal(0, 1, 200)}))
    assert out["sentinel_missing_count"] == 20
    assert out["completeness"] < 100


def test_legitimate_values_equal_to_a_sentinel_are_not_penalised():
    # a column whose real range includes 9999 must not be treated as hidden-missing
    values = np.linspace(9000, 11000, 200)
    out = calculate_health_score(pd.DataFrame({"a": values}))
    assert out["sentinel_missing_count"] == 0


def test_string_dtype_sentinels_are_included_in_missingness():
    df = pd.DataFrame({"label": pd.Series(["ok", pd.NA, "-99"], dtype="string")})
    assert calculate_health_score(df)["sentinel_missing_count"] == 1


@pytest.mark.parametrize(
    "weights",
    [
        {"completeness": 1.0},
        {"completeness": 1.0, "uniqueness": 0.0, "consistency": 0.0, "unexpected": 0.0},
        {"completeness": -0.1, "uniqueness": 0.5, "consistency": 0.3, "outliers": 0.3},
    ],
)
def test_invalid_health_weight_shapes_and_values_are_rejected(weights):
    with pytest.raises(ValueError):
        calculate_health_score(pd.DataFrame({"a": [1.0, 2.0]}), weights=weights)
