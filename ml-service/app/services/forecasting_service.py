"""
Upgrades over repo's utils/ forecasting (Exponential Smoothing / Holt's only):
- Adds ARIMA and SARIMA (statsmodels)
- 'auto' mode fits all candidates, backtests on a holdout tail, and picks
  the lowest-MAPE model instead of forcing the user to choose one
- Returns per-model accuracy so the frontend can show a comparison table

LSTM / Prophet are natural next additions once torch/prophet are on the
ml-service image — left as clearly marked extension points below so the
interface doesn't need to change when they're added.
"""
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def _prep_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    ts = df[[date_col, value_col]].dropna().copy()
    ts[date_col] = pd.to_datetime(ts[date_col], errors="coerce")
    ts = ts.dropna(subset=[date_col]).sort_values(date_col)
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
    actual, predicted = np.array(actual), np.array(predicted)
    mae = np.mean(np.abs(actual - predicted))
    # Compute MAE of one-step naive forecast on training series
    naive_mae = np.mean(np.abs(np.diff(train_series.values)))
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


CANDIDATES = {"naive": _fit_naive, "seasonal_naive": _fit_seasonal_naive, "holt": _fit_holt, "arima": _fit_arima, "sarima": _fit_sarima}


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


def _compute_meta_features(series: pd.Series) -> dict:
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
    if n >= 14:
        try:
            autocorr = pd.Series(values).autocorr(lag=7)
            seasonal_strength = float(autocorr) if np.isfinite(autocorr) else 0.0
        except Exception:
            seasonal_strength = 0.0

    return {
        "length": n,
        "noise_ratio": round(noise_ratio, 3),
        "trend_strength": round(trend_strength, 3),
        "seasonal_strength": round(seasonal_strength, 3),
    }


def _shortlist_candidates(meta_features: dict) -> list[str]:
    """naive/holt are always cheap and always included as baselines (Hewamalage
    et al. 2022). ARIMA needs enough points to fit reliably; SARIMA/seasonal_naive
    are only worth their extra cost when the series actually shows weekly
    seasonality -- fitting a seasonal model on a non-seasonal series wastes
    compute and can still "win" on a noisy single split, which is exactly the
    overcomplicated-model risk the rolling-origin backtest is meant to guard
    against.
    """
    shortlist = ["naive", "holt", "seasonal_naive"]
    if meta_features["length"] >= 20:
        shortlist.append("arima")
    if meta_features["seasonal_strength"] > 0.3 and meta_features["length"] >= 21:
        shortlist.append("sarima")
    return shortlist


def run_forecast(df: pd.DataFrame, date_col: str, value_col: str, periods: int, model: str = "auto") -> dict:
    series = _prep_series(df, date_col, value_col)
    if len(series) < 10:
        return {"error": "Need at least 10 valid time-ordered data points to forecast."}

    if model != "auto":
        fit_fn = CANDIDATES.get(model, _fit_holt)
        forecast = fit_fn(series, periods)
        return {
            "model_used": model,
            "forecast": [{"period": i + 1, "value": round(float(v), 2)} for i, v in enumerate(forecast)],
        }

    # auto: rolling-origin backtest shortlisted candidates and pick the lowest MASE
    holdout_size = max(3, min(periods, int(len(series) * 0.2)))
    n_splits = 2 if len(series) > 5000 else 3  # Limit expensive ARIMA/SARIMA fitting for large series.
    splits = _rolling_origin_splits(series, holdout_size, n_splits=n_splits)

    meta_features = _compute_meta_features(series)
    shortlisted_names = _shortlist_candidates(meta_features)
    candidates_to_run = {name: fn for name, fn in CANDIDATES.items() if name in shortlisted_names}

    scores = {}
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
            scores[name] = {
                metric: round(float(np.mean([value for value in values if np.isfinite(value)])), 2)
                if any(np.isfinite(value) for value in values) else None
                for metric, values in metric_values.items()
            }
        else:
            scores[name] = {
                "mape": None,
                "rmse": None,
                "mase": None,
                "error": errors[-1] if errors else "Model failed on all backtest splits.",
            }

    # Select best model by MASE (more robust than MAPE for unstable values; Hewamalage et al. 2022)
    best_model = min(scores, key=lambda k: scores[k]["mase"] if scores[k]["mase"] is not None else float("inf"))
    final_forecast = CANDIDATES[best_model](series, periods)

    return {
        "model_used": best_model,
        "model_comparison": scores,
        "backtest_splits_used": len(splits),
        "meta_features": meta_features,
        "candidates_evaluated": list(candidates_to_run.keys()),
        "forecast": [{"period": i + 1, "value": round(float(v), 2)} for i, v in enumerate(final_forecast)],
    }
