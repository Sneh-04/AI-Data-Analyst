"""
Upgrades over repo's utils/ forecasting (Exponential Smoothing / Holt's only):
- Adds ARIMA and SARIMA (statsmodels)
- 'auto' mode backtests shortlisted candidates on rolling origins and selects
  the lowest-MASE model instead of forcing the user to choose one
- Returns per-model accuracy so the frontend can show a comparison table

LSTM / Prophet are natural next additions once torch/prophet are on the
ml-service image — left as clearly marked extension points below so the
interface doesn't need to change when they're added.
"""
import warnings
from functools import partial

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def _prep_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    if date_col == value_col:
        raise ValueError("Date and value columns must be different.")

    ts = df[[date_col, value_col]].copy()
    raw_dates = ts[date_col]
    parsed_dates = pd.to_datetime(raw_dates, errors="coerce")
    empty_dates = raw_dates.astype("string").str.strip().eq("").fillna(False)
    invalid_dates = raw_dates.notna() & ~empty_dates & parsed_dates.isna()
    if invalid_dates.any():
        raise ValueError("The date column contains invalid dates.")

    raw_values = ts[value_col]
    parsed_values = pd.to_numeric(raw_values, errors="coerce")
    empty_values = raw_values.astype("string").str.strip().eq("").fillna(False)
    invalid_values = raw_values.notna() & ~empty_values & parsed_values.isna()
    if invalid_values.any():
        raise ValueError("The value column contains non-numeric values.")
    if np.isinf(parsed_values.dropna().to_numpy(dtype=float)).any():
        raise ValueError("The value column contains infinite values.")

    ts[date_col] = parsed_dates
    ts[value_col] = parsed_values
    ts = ts.dropna(subset=[date_col, value_col]).sort_values(date_col)
    if ts[date_col].duplicated().any():
        raise ValueError("The date column contains duplicate timestamps.")
    series = ts.set_index(date_col)[value_col].astype(float)
    return series


def _mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def _rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.array(actual) - np.array(predicted)) ** 2)))


def _mase(actual: np.ndarray, predicted: np.ndarray, train_series: pd.Series) -> float:
    """Mean Absolute Scaled Error: more robust than MAPE for near-zero values (Hewamalage et al. 2022)."""
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    train_values = np.asarray(train_series.values, dtype=float)
    if (
        actual.ndim != 1
        or predicted.ndim != 1
        or actual.size == 0
        or actual.shape != predicted.shape
        or not np.isfinite(actual).all()
        or not np.isfinite(predicted).all()
        or train_values.size < 2
        or not np.isfinite(train_values).all()
    ):
        return float("nan")
    mae = np.mean(np.abs(actual - predicted))
    # Compute MAE of one-step naive forecast on training series
    naive_mae = np.mean(np.abs(np.diff(train_values)))
    if naive_mae == 0:
        return float("nan") if mae == 0 else float("inf")
    return float(mae / naive_mae)


def _fit_holt(train: pd.Series, horizon: int):
    model = ExponentialSmoothing(train, trend="add", seasonal=None).fit()
    return model.forecast(horizon)


def _fit_arima(train: pd.Series, horizon: int):
    model = ARIMA(train, order=(1, 1, 1)).fit()
    return model.forecast(horizon)


def _fit_sarima(train: pd.Series, horizon: int, seasonal_periods=7):
    model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 0, seasonal_periods)).fit(disp=False)
    return model.forecast(horizon)


def _fit_naive(train: pd.Series, horizon: int):
    """Naive baseline: repeat last observed value for all forecast periods (Hewamalage et al. 2022)."""
    last_value = train.iloc[-1]
    return pd.Series([last_value] * horizon, index=range(horizon))


def _fit_seasonal_naive(train: pd.Series, horizon: int, seasonal_periods: int = 7):
    """Seasonal naive baseline: repeat value from seasonal_periods steps ago, cycling if needed (Hewamalage et al. 2022)."""
    forecast = []
    train_len = len(train)
    for i in range(horizon):
        idx = train_len - seasonal_periods + (i % seasonal_periods)
        if idx >= 0:
            forecast.append(train.iloc[idx])
        else:
            forecast.append(train.iloc[-1])
    return pd.Series(forecast, index=range(horizon))


def _infer_seasonal_period(series: pd.Series) -> int:
    """Infer a common seasonal cycle from the median spacing of date observations."""
    index = series.index
    if not isinstance(index, pd.DatetimeIndex) or len(index) < 3:
        return 7
    spacing_seconds = float(
        np.median(np.diff(index.values).astype("timedelta64[s]").astype(float))
    )
    if spacing_seconds <= 0:
        return 1
    if spacing_seconds < 86400:
        observations_per_day = 86400 / spacing_seconds
        rounded_period = round(observations_per_day)
        if rounded_period > 1 and abs(observations_per_day - rounded_period) <= rounded_period * 0.02:
            return rounded_period

    spacing_days = spacing_seconds / 86400.0
    if spacing_days <= 1.5:
        return 7
    if 6 <= spacing_days <= 8:
        return 52
    if 27 <= spacing_days <= 32:
        return 12
    if 85 <= spacing_days <= 95:
        return 4
    return 1


def _fit_ensemble(train: pd.Series, horizon: int, seasonal_periods: int = 7):
    components = [_fit_naive, _fit_holt, _fit_arima]
    if seasonal_periods > 1 and len(train) >= 2 * seasonal_periods:
        components.append(partial(_fit_seasonal_naive, seasonal_periods=seasonal_periods))
    forecasts = []
    for fit_fn in components:
        try:
            forecasts.append(np.asarray(fit_fn(train, horizon), dtype=float))
        except Exception:
            continue
    if len(forecasts) < 2:
        raise ValueError("Ensemble needs at least two successful component models.")
    return pd.Series(np.mean(forecasts, axis=0), index=range(horizon))


CANDIDATES = {
    "naive": _fit_naive,
    "seasonal_naive": _fit_seasonal_naive,
    "holt": _fit_holt,
    "arima": _fit_arima,
    "sarima": _fit_sarima,
    "ensemble": _fit_ensemble,
}


def _rolling_origin_splits(
    series: pd.Series, holdout_size: int, n_splits: int = 3
) -> list[tuple[pd.Series, pd.Series]]:
    """Build recent-to-earlier rolling-origin train/test splits."""
    splits = []
    for split_number in range(1, n_splits + 1):
        test_end = len(series) - (split_number - 1) * holdout_size
        test_start = test_end - holdout_size
        train = series.iloc[:test_start]
        test = series.iloc[test_start:test_end]
        if len(train) < 10:
            break
        # Keep the most recent split first; earlier origins follow it.
        splits.append((train, test))
    return splits


def _compute_meta_features(series: pd.Series, seasonal_period: int | None = None) -> dict:
    """Series characteristics used to shortlist which candidates are worth
    backtesting, instead of always brute-force fitting all 5 on every split
    regardless of fit. AutoML-for-time-series tools still struggle to handle
    series quirks (trend/seasonality/noise) without this kind of guidance
    (Alsharef et al. 2022), and skipping clearly-inapplicable models reduces
    the resource cost flagged for foundation/complex models (Liang et al. 2024).
    """
    values = series.values.astype(float)
    n = len(values)
    diffs = np.diff(values) if n > 1 else np.array([0.0])
    value_std = np.std(values) + 1e-9
    noise_ratio = float(np.std(diffs) / value_std)

    trend_strength = 0.0
    if n > 2:
        slope = np.polyfit(np.arange(n), values, 1)[0]
        trend_strength = float(abs(slope) * n / value_std)

    seasonal_strength = 0.0
    if seasonal_period is None:
        if n >= 14:
            try:
                autocorr = pd.Series(values).autocorr(lag=7)
                seasonal_strength = float(autocorr) if np.isfinite(autocorr) else 0.0
            except Exception:
                seasonal_strength = 0.0
    elif seasonal_period > 1 and n >= 2 * seasonal_period + 2:
        try:
            autocorr = pd.Series(diffs).autocorr(lag=seasonal_period)
            seasonal_strength = float(autocorr) if np.isfinite(autocorr) else 0.0
        except Exception:
            seasonal_strength = 0.0

    return {
        "length": n,
        "noise_ratio": round(noise_ratio, 3),
        "trend_strength": round(trend_strength, 3),
        "seasonal_strength": round(seasonal_strength, 3),
        "seasonal_period": seasonal_period if seasonal_period is not None else 7,
    }


def _shortlist_candidates(meta_features: dict, include_ensemble: bool = False) -> list[str]:
    period = meta_features.get("seasonal_period", 7)
    length = meta_features["length"]
    shortlist = ["naive", "holt"]
    if period > 1:
        shortlist.append("seasonal_naive")
    if length >= 20:
        shortlist.append("arima")
    if period > 1 and meta_features["seasonal_strength"] > 0.3 and length >= max(21, 3 * period):
        shortlist.append("sarima")
    if include_ensemble and length >= 20:
        shortlist.append("ensemble")
    return shortlist


def _bind_period(fit_fn, seasonal_period: int):
    if fit_fn in (_fit_seasonal_naive, _fit_sarima, _fit_ensemble):
        period = max(seasonal_period, 1)
        if fit_fn is _fit_sarima and period == 1:
            period = 7
        return partial(fit_fn, seasonal_periods=period)
    return fit_fn


def run_forecast(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    periods: int,
    model: str = "auto",
    seasonal_period: int | None = None,
    use_shortlist: bool = True,
    include_ensemble: bool = False,
) -> dict:
    if periods < 1:
        raise ValueError("Forecast periods must be at least 1.")
    if model not in CANDIDATES and model != "auto":
        raise ValueError(f"Unsupported forecast model: {model}")
    series = _prep_series(df, date_col, value_col)
    if len(series) < 10:
        return {"error": "Need at least 10 valid time-ordered data points to forecast."}
    period = seasonal_period if seasonal_period is not None else _infer_seasonal_period(series)

    if model != "auto":
        fit_fn = _bind_period(CANDIDATES.get(model, _fit_holt), period)
        forecast = fit_fn(series, periods)
        return {
            "model_used": model,
            "forecast": [{"period": i + 1, "value": round(float(v), 2)} for i, v in enumerate(forecast)],
        }

    # auto: rolling-origin backtest shortlisted candidates and pick the lowest MASE
    holdout_size = max(3, min(periods, int(len(series) * 0.2)))
    n_splits = 2 if len(series) > 5000 else 3  # Limit expensive ARIMA/SARIMA fitting for large series.
    splits = _rolling_origin_splits(series, holdout_size, n_splits=n_splits)
    if not splits:
        return {
            "error": (
                "Auto model selection needs enough observations for at least one rolling-origin "
                "backtest split. Add more data or choose an explicit model such as 'naive'."
            )
        }

    meta_features = _compute_meta_features(series, seasonal_period=period)
    if use_shortlist:
        shortlisted_names = _shortlist_candidates(meta_features, include_ensemble=include_ensemble)
    else:
        shortlisted_names = [name for name in CANDIDATES if include_ensemble or name != "ensemble"]
    candidates_to_run = {
        name: _bind_period(fit_fn, period)
        for name, fit_fn in CANDIDATES.items()
        if name in shortlisted_names
    }

    scores = {}
    selection_scores = {}
    for name, fit_fn in candidates_to_run.items():
        metric_values = {"mape": [], "rmse": [], "mase": []}
        errors = []
        successful_splits = 0
        for train, test in splits:
            try:
                preds = fit_fn(train, holdout_size)
                metric_values["mape"].append(_mape(test.values, preds.values))
                metric_values["rmse"].append(_rmse(test.values, preds.values))
                metric_values["mase"].append(_mase(test.values, preds.values, train))
                successful_splits += 1
            except Exception as e:
                errors.append(str(e))
                continue

        if successful_splits:
            finite_mase = [
                value for value in metric_values["mase"] if np.isfinite(value)
            ]
            selection_scores[name] = (
                float(np.mean(finite_mase))
                if len(finite_mase) == len(splits)
                else None
            )
            scores[name] = {
                metric: round(float(np.mean([value for value in values if np.isfinite(value)])), 2)
                if any(np.isfinite(value) for value in values) else None
                for metric, values in metric_values.items()
            }
            scores[name]["mase"] = round(selection_scores[name], 2) if selection_scores[name] is not None else None
        else:
            selection_scores[name] = None
            scores[name] = {
                "mape": None,
                "rmse": None,
                "mase": None,
                "error": errors[-1] if errors else "Model failed on all backtest splits.",
            }

    # Only models with a finite MASE on every split are comparable.
    scored_models = [
        name for name, metrics in scores.items()
        if selection_scores[name] is not None and np.isfinite(selection_scores[name])
    ]
    selection_metric = "MASE" if scored_models else None
    selection_message = None
    if scored_models:
        best_model = min(scored_models, key=lambda name: selection_scores[name])
    else:
        best_model = "naive"
        selection_message = (
            "No candidate had a finite MASE on every backtest split; "
            "the naive baseline is shown without a model-selection claim."
        )
    final_forecast = _bind_period(CANDIDATES[best_model], period)(series, periods)

    return {
        "model_used": best_model,
        "selection_metric": selection_metric,
        "selection_message": selection_message,
        "model_comparison": scores,
        "backtest_splits_used": len(splits),
        "meta_features": meta_features,
        "seasonal_period": period,
        "candidates_evaluated": list(candidates_to_run.keys()),
        "forecast": [{"period": i + 1, "value": round(float(v), 2)} for i, v in enumerate(final_forecast)],
    }
