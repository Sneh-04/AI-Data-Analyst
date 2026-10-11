"""
Forecasting benchmark v2 -- six real series, walk-forward evaluation, ablations, significance tests.

Uses the project's ACTUAL forecasting code (ml-service/app/services/forecasting_service.py).

Series (real, bundled with statsmodels, no network):
  co2        Mauna Loa CO2, monthly   (strong trend + strong annual seasonality)   h=12
  realgdp    US real GDP, quarterly   (strong trend, no seasonality after SA)       h=4
  unemp      US unemployment, quarterly (cyclical, no stable seasonality)           h=4
  cpi        US CPI, quarterly        (smooth trend)                                h=4
  sunspots   annual sunspot counts    (~11-year cycle, no calendar seasonality)     h=5
  nile       annual Nile flow         (level shift, noisy)                          h=5

Evaluation: N_WINDOWS non-overlapping walk-forward origins per series (the last N_WINDOWS*h
points are the test windows; each model is refit on the data before its window). The "auto"
variants do their own inner rolling-origin backtest on the training data only -> no leakage.

Arms
  naive, seasonal_naive, holt, arima, sarima, ensemble     fixed models (seasonal period inferred)
  auto                    production: inferred period + shortlist, ensemble off
  auto_legacy             what shipped BEFORE this work: seasonal period hardcoded to 7
  auto_no_shortlist       ablation: backtest every candidate instead of shortlisting
  auto_with_ensemble      ablation: production plus the equal-weight ensemble as a candidate
  oracle_best_fixed       NOT a real method: per-window best of the fixed models (selection-regret bound)

Metric: MASE (scaled by the in-sample one-step naive MAE, Hyndman & Koehler 2006) -- scale-free so
it can be averaged across series. Also reported: relative MASE vs naive (geometric mean), mean
rank, win-rate, paired Wilcoxon signed-rank tests on per-window MASE (Holm-adjusted).

Run:  python3 forecasting_benchmark.py        (from experiments/)
"""
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.datasets import co2, macrodata, nile, sunspots

from common import RESULTS_DIR, holm_adjust, save_environment
from app.services import forecasting_service as fs

warnings.filterwarnings("ignore")
N_WINDOWS = 8


def load_series() -> dict[str, tuple[pd.DataFrame, int]]:
    out = {}
    monthly = co2.load().data["co2"].resample("MS").mean().interpolate()
    out["co2"] = (pd.DataFrame({"date": monthly.index, "value": monthly.values}), 12)
    mac = macrodata.load_pandas().data
    quarter_month = ((mac["quarter"].astype(int) - 1) * 3 + 1).astype(str).str.zfill(2)
    dates = pd.to_datetime(mac["year"].astype(int).astype(str) + "-" + quarter_month + "-01")
    for col in ["realgdp", "unemp", "cpi"]:
        out[col] = (pd.DataFrame({"date": dates, "value": mac[col].values}), 4)
    sun = sunspots.load_pandas().data
    out["sunspots"] = (pd.DataFrame({"date": pd.to_datetime(sun["YEAR"].astype(int).astype(str) + "-01-01"),
                                     "value": sun["SUNACTIVITY"].values}), 5)
    nl = nile.load_pandas().data
    out["nile"] = (pd.DataFrame({"date": pd.to_datetime(nl["year"].astype(int).astype(str) + "-01-01"),
                                 "value": nl["volume"].values}), 5)
    return out


def score(actual, forecast, train_values):
    return fs._mase(actual, np.asarray(forecast, dtype=float), pd.Series(train_values))


def run_series(name, df, horizon):
    rows = []
    n = len(df)
    for w in range(N_WINDOWS):
        test_end = n - w * horizon
        test_start = test_end - horizon
        train_df, test_df = df.iloc[:test_start], df.iloc[test_start:test_end]
        if len(train_df) < 30:
            continue
        actual = test_df["value"].values
        train_series = fs._prep_series(train_df, "date", "value")
        period = fs._infer_seasonal_period(train_series)
        base = {"series": name, "window": w, "train_size": len(train_df), "seasonal_period": period}

        for model in ["naive", "seasonal_naive", "holt", "arima", "sarima", "ensemble"]:
            if model in ("seasonal_naive", "sarima") and period <= 1:
                continue  # no seasonal cycle for this series: arm not applicable
            try:
                out = fs.run_forecast(train_df, "date", "value", horizon, model=model)
                mase = score(actual, [p["value"] for p in out["forecast"]], train_series.values)
            except Exception:
                mase = np.nan
            rows.append({**base, "method": model, "mase": mase, "picked": ""})

        arms = {
            "auto": dict(),
            "auto_legacy": dict(seasonal_period=7),
            "auto_no_shortlist": dict(use_shortlist=False),
            "auto_with_ensemble": dict(include_ensemble=True),
        }
        for arm, kwargs in arms.items():
            t0 = time.perf_counter()
            try:
                out = fs.run_forecast(train_df, "date", "value", horizon, model="auto", **kwargs)
                mase = score(actual, [p["value"] for p in out["forecast"]], train_series.values)
                picked = out["model_used"]
            except Exception:
                mase, picked = np.nan, "FAILED"
            rows.append({**base, "method": arm, "mase": mase, "picked": picked,
                         "seconds": time.perf_counter() - t0})
    return rows


def main():
    series = load_series()
    started = time.time()
    rows = []
    for name, (df, horizon) in series.items():
        rows.extend(run_series(name, df, horizon))
        print(f"  {name} done ({time.time() - started:.0f}s)", flush=True)
    raw = pd.DataFrame(rows)

    fixed = ["naive", "seasonal_naive", "holt", "arima", "sarima", "ensemble"]
    oracle = (raw[raw.method.isin(fixed)].groupby(["series", "window"]).mase.min().reset_index()
              .assign(method="oracle_best_fixed", picked="", seasonal_period=np.nan, train_size=np.nan))
    raw = pd.concat([raw, oracle], ignore_index=True)
    raw.to_csv(f"{RESULTS_DIR}/forecasting_raw.csv", index=False)

    wide = raw.pivot_table(index=["series", "window"], columns="method", values="mase")
    per_series = raw.groupby(["series", "method"]).mase.mean().unstack("method")
    per_series.round(4).to_csv(f"{RESULTS_DIR}/forecasting_per_series_mase.csv")

    # aggregate across all (series, window) pairs
    methods = [m for m in ["naive", "seasonal_naive", "holt", "arima", "sarima", "ensemble", "auto",
                           "auto_legacy", "auto_no_shortlist", "auto_with_ensemble", "oracle_best_fixed"] if m in wide]
    ranks = wide[[m for m in methods if m != "oracle_best_fixed"]].rank(axis=1, method="average")
    runtime = raw.groupby("method").seconds.mean()
    summary = pd.DataFrame({
        "mean_mase": wide[methods].mean(),
        "mean_seconds_per_window": runtime.reindex(methods),
        "median_mase": wide[methods].median(),
        "rel_mase_vs_naive_geomean": np.exp(np.log(wide[methods].div(wide["naive"], axis=0)).mean()),
        "mean_rank": ranks.mean(),
        "windows_scored": wide[methods].count(),
    }).loc[methods].round(4)
    summary.to_csv(f"{RESULTS_DIR}/forecasting_summary.csv")

    tests = []
    for a, b in [("auto", "naive"), ("auto", "arima"), ("auto", "ensemble"), ("auto", "auto_legacy"),
                 ("auto", "auto_no_shortlist"), ("auto", "auto_with_ensemble"), ("ensemble", "naive"),
                 ("auto", "oracle_best_fixed"), ("auto", "sarima")]:
        pair = wide[[a, b]].dropna()
        diff = pair[a] - pair[b]
        p = stats.wilcoxon(diff).pvalue if (diff != 0).any() else 1.0
        tests.append({"a": a, "b": b, "mean_mase_diff(a-b)": diff.mean(), "a_wins": int((diff < 0).sum()),
                      "pairs": len(diff), "p_value": p})
    # the one strongly seasonal series: does the period fix matter where it should?
    co2_pair = wide.loc["co2"][["auto", "auto_legacy"]].dropna()
    d = co2_pair["auto"] - co2_pair["auto_legacy"]
    tests.append({"a": "auto[co2 only]", "b": "auto_legacy[co2 only]", "mean_mase_diff(a-b)": d.mean(),
                  "a_wins": int((d < 0).sum()), "pairs": len(d), "p_value": stats.wilcoxon(d).pvalue})
    tests = pd.DataFrame(tests)
    tests["p_holm"] = holm_adjust(tests["p_value"].values)
    tests.round(5).to_csv(f"{RESULTS_DIR}/forecasting_significance.csv", index=False)

    picks = raw[raw.method == "auto"].groupby(["series", "picked"]).size().unstack(fill_value=0)
    picks.to_csv(f"{RESULTS_DIR}/forecasting_auto_choices.csv")
    save_environment({"forecasting": {"n_windows": N_WINDOWS, "series": {k: v[1] for k, v in series.items()}}},
                     "environment_forecasting.json")

    print("\nMean MASE per series:")
    print(per_series.round(3).to_markdown())
    print("\nAggregate over all series x windows:")
    print(summary.to_markdown())
    print("\nPaired Wilcoxon (per-window MASE, Holm-adjusted):")
    print(tests.round(4).to_markdown(index=False))
    print("\nWhat 'auto' picked:")
    print(picks.to_markdown())
    print(f"\nTotal runtime {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
