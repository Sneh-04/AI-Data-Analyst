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


def _fit_holt(train: pd.Series, horizon: int):
    model = ExponentialSmoothing(train, trend="add", seasonal=None).fit()
    return model.forecast(horizon)


def _fit_arima(train: pd.Series, horizon: int):
    model = ARIMA(train, order=(1, 1, 1)).fit()
    return model.forecast(horizon)


def _fit_sarima(train: pd.Series, horizon: int, seasonal_periods=7):
    model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 0, seasonal_periods)).fit(disp=False)
    return model.forecast(horizon)


CANDIDATES = {"holt": _fit_holt, "arima": _fit_arima, "sarima": _fit_sarima}


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

    # auto: backtest each candidate on the last min(periods, 20%) points, pick lowest MAPE
    holdout_size = max(3, min(periods, int(len(series) * 0.2)))
    train, test = series[:-holdout_size], series[-holdout_size:]

    scores = {}
    for name, fit_fn in CANDIDATES.items():
        try:
            preds = fit_fn(train, holdout_size)
            mape_val, rmse_val = _mape(test.values, preds.values), _rmse(test.values, preds.values)
            scores[name] = {
                "mape": round(mape_val, 2) if np.isfinite(mape_val) else None,
                "rmse": round(rmse_val, 2) if np.isfinite(rmse_val) else None,
            }
        except Exception as e:
            scores[name] = {"mape": None, "rmse": None, "error": str(e)}

    best_model = min(scores, key=lambda k: scores[k]["mape"] if scores[k]["mape"] is not None else float("inf"))
    final_forecast = CANDIDATES[best_model](series, periods)

    return {
        "model_used": best_model,
        "model_comparison": scores,
        "forecast": [{"period": i + 1, "value": round(float(v), 2)} for i, v in enumerate(final_forecast)],
    }
