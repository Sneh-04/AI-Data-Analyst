import numpy as np
import pandas as pd
import pytest

from app.services import forecasting_service as fs


def _frame(n, freq, seasonal_period=None, trend=0.0, noise=0.1, seed=0):
    rng = np.random.RandomState(seed)
    t = np.arange(n)
    values = 50 + trend * t + noise * rng.randn(n)
    if seasonal_period:
        values = values + 5 * np.sin(2 * np.pi * t / seasonal_period)
    return pd.DataFrame({"date": pd.date_range("2015-01-01", periods=n, freq=freq), "value": values})


@pytest.mark.parametrize(
    "freq,expected",
    [("D", 7), ("W", 52), ("MS", 12), ("QS", 4), ("YS", 1),
     ("h", 24), ("2h", 12), ("30min", 48), ("15min", 96)],
)
def test_seasonal_period_inferred_from_date_spacing(freq, expected):
    series = fs._prep_series(_frame(60, freq), "date", "value")
    assert fs._infer_seasonal_period(series) == expected


def test_seasonal_naive_and_sarima_use_inferred_period_on_monthly_data():
    df = _frame(120, "MS", seasonal_period=12, trend=0.05)
    out = fs.run_forecast(df, "date", "value", periods=12)
    assert out["seasonal_period"] == 12
    assert out["meta_features"]["seasonal_period"] == 12
    assert out["model_comparison"]["seasonal_naive"]["mase"] < out["model_comparison"]["naive"]["mase"]


def test_trend_without_seasonality_is_not_mistaken_for_seasonal():
    df = _frame(80, "QS", trend=1.0, noise=0.2)  # strong trend, no cycle
    series = fs._prep_series(df, "date", "value")
    meta = fs._compute_meta_features(series, seasonal_period=4)
    assert meta["seasonal_strength"] < 0.3
    assert "sarima" not in fs._shortlist_candidates(meta)


def test_real_seasonal_series_is_shortlisted_for_sarima():
    df = _frame(120, "MS", seasonal_period=12, trend=0.05)
    meta = fs._compute_meta_features(fs._prep_series(df, "date", "value"), seasonal_period=12)
    assert meta["seasonal_strength"] > 0.3
    assert "sarima" in fs._shortlist_candidates(meta)


def test_auto_response_keeps_backward_compatible_keys_and_shapes():
    out = fs.run_forecast(_frame(60, "D", seasonal_period=7), "date", "value", periods=7)
    for key in ("model_used", "model_comparison", "backtest_splits_used", "meta_features", "candidates_evaluated", "forecast"):
        assert key in out
    assert len(out["forecast"]) == 7 and set(out["forecast"][0]) == {"period", "value"}
    for scores in out["model_comparison"].values():
        assert {"mape", "rmse", "mase"} <= set(scores)


def test_ensemble_is_the_mean_of_its_components():
    train = fs._prep_series(_frame(60, "D", seasonal_period=7), "date", "value")
    ensemble = np.asarray(fs._fit_ensemble(train, 5, seasonal_periods=7))
    parts = [np.asarray(f(train, 5)) for f in (fs._fit_naive, fs._fit_holt, fs._fit_arima)]
    parts.append(np.asarray(fs._fit_seasonal_naive(train, 5, seasonal_periods=7)))
    assert np.allclose(ensemble, np.mean(parts, axis=0))


def test_ablation_flags_change_the_candidate_set():
    df = _frame(80, "MS", seasonal_period=12, trend=0.05)
    default = fs.run_forecast(df, "date", "value", 12)
    with_ens = fs.run_forecast(df, "date", "value", 12, include_ensemble=True)
    no_short = fs.run_forecast(df, "date", "value", 12, use_shortlist=False)
    assert "ensemble" not in default["candidates_evaluated"]          # ensemble is opt-in
    assert "ensemble" in with_ens["candidates_evaluated"]
    assert set(default["candidates_evaluated"]) <= set(no_short["candidates_evaluated"])
    legacy = fs.run_forecast(df, "date", "value", 12, seasonal_period=7)
    assert legacy["seasonal_period"] == 7


def test_explicit_model_and_short_series_behaviour():
    df = _frame(40, "D")
    out = fs.run_forecast(df, "date", "value", 5, model="naive")
    assert out["model_used"] == "naive" and len(out["forecast"]) == 5
    assert "error" in fs.run_forecast(df.head(5), "date", "value", 3)


def test_mase_matches_hand_computation():
    train = pd.Series([1.0, 2.0, 4.0, 7.0])           # naive one-step MAE = (1+2+3)/3 = 2
    assert fs._mase(np.array([10.0, 12.0]), np.array([9.0, 10.0]), train) == pytest.approx(1.5 / 2.0)


def test_mase_rejects_unscorable_or_misaligned_inputs():
    constant_train = pd.Series([4.0] * 10)
    assert np.isnan(fs._mase([4.0], [4.0], constant_train))
    assert np.isnan(fs._mase([1.0, 2.0], [1.0], pd.Series([0.0, 1.0, 2.0])))
    assert np.isnan(fs._mase([1.0], [np.inf], pd.Series([0.0, 1.0, 2.0])))


def test_auto_forecast_does_not_claim_selection_without_backtest_splits():
    df = _frame(10, "D")
    result = fs.run_forecast(df, "date", "value", periods=3)
    assert "error" in result and "backtest split" in result["error"]
    assert fs.run_forecast(df, "date", "value", periods=3, model="naive")["model_used"] == "naive"


def test_constant_series_uses_naive_without_claiming_an_unscorable_mase_selection():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=24, freq="D"),
        "value": np.full(24, 5.0),
    })
    result = fs.run_forecast(df, "date", "value", periods=3)
    assert result["model_used"] == "naive"
    assert result["selection_metric"] is None
    assert "without a model-selection claim" in result["selection_message"]
    assert all(metrics["mase"] is None for metrics in result["model_comparison"].values())


def test_model_selection_uses_unrounded_mase_scores(monkeypatch):
    def offset_forecast(offset):
        def fit(train, horizon):
            values = np.arange(train.iloc[-1] + 1, train.iloc[-1] + horizon + 1) - offset
            return pd.Series(values, index=range(horizon))
        return fit

    monkeypatch.setitem(fs.CANDIDATES, "naive", offset_forecast(0.004))
    monkeypatch.setitem(fs.CANDIDATES, "holt", offset_forecast(0.003))
    df = pd.DataFrame({
        "date": pd.date_range("2000-01-01", periods=18, freq="YS"),
        "value": np.arange(18.0),
    })

    result = fs.run_forecast(df, "date", "value", periods=3)

    assert result["model_comparison"]["naive"]["mase"] == 0.0
    assert result["model_comparison"]["holt"]["mase"] == 0.0
    assert result["model_used"] == "holt"


@pytest.mark.parametrize(
    "values,error_text",
    [
        (["bad"] + list(range(9)), "non-numeric"),
        (list(range(10)), "duplicate timestamps"),
    ],
)
def test_forecast_rejects_invalid_values_and_duplicate_timestamps(values, error_text):
    dates = pd.date_range("2024-01-01", periods=len(values))
    if error_text == "duplicate timestamps":
        dates = pd.DatetimeIndex([dates[0]] * len(values))
    df = pd.DataFrame({"date": dates, "value": values})
    with pytest.raises(ValueError, match=error_text):
        fs.run_forecast(df, "date", "value", periods=3, model="naive")


def test_missing_forecast_cells_are_dropped_but_blank_fields_are_not_rejected():
    df = _frame(15, "D")
    df["value"] = df["value"].astype(object)
    df.loc[0, "value"] = np.nan
    df.loc[1, "date"] = ""
    df.loc[2, "value"] = ""

    series = fs._prep_series(df, "date", "value")

    assert len(series) == 12


def test_rolling_origin_splits_are_ordered_and_leak_free():
    series = pd.Series(np.arange(50.0))
    splits = fs._rolling_origin_splits(series, holdout_size=5, n_splits=3)
    assert len(splits) == 3
    for train, test in splits:
        assert train.index.max() < test.index.min()
