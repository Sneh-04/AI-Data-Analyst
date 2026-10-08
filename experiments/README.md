# Experiments

Real benchmarks against the project's actual code (`ml-service/app/services/`),
run on real, bundled, publicly available datasets — no network access, no
fabricated numbers. Every number below came from an actual run; re-run with
`PYTHONPATH=../ml-service python3 <script>.py` to reproduce.

New dependencies needed beyond `ml-service/requirements.txt`: `scipy`, `tabulate`
(`pip install scipy tabulate`).

## 1. Imputation benchmark (`imputation_benchmark.py`)

**Dataset:** `sklearn.datasets.load_diabetes` (442 patients, 10 real physiological
features). The `bmi` column is artificially masked under MCAR at 10/20/30% rates
(10 random-seed trials each), so the true value is always known and RMSE is a
real ground-truth error, not a proxy.

**Methods (all from `cleaning_service.py`, not reimplemented):** mean, median,
KNN (k=5), and our "multiple imputation with uncertainty" (bootstrap resampling
from the observed marginal distribution).

| mask_rate | method | mean_rmse | uncertainty_spearman |
|---|---|---|---|
| 0.10–0.30 | **knn_k5** | **0.042–0.044** (best) | n/a |
| 0.10–0.30 | mean | 0.047–0.048 | n/a |
| 0.10–0.30 | median | 0.047–0.049 | n/a |
| 0.10–0.30 | multiple_imputation | 0.050–0.053 (**worst**) | **0.02–0.05** (≈0, not meaningfully calibrated) |

**Honest finding — this is a real weakness, not a win:** our "uncertainty-aware"
multiple imputation is currently *worse* than plain mean/median, and its
per-cell uncertainty does **not** correlate with actual error (Spearman ≈ 0.03,
should be meaningfully positive for a calibrated estimate). Root cause: it
resamples from the target column's own marginal distribution only — it never
looks at the other 9 correlated features, which is exactly why KNN (which does)
wins by a clear margin. The current implementation adds variance without
adding the cross-feature signal that would make it accurate. **This means the
"uncertainty-aware imputation ✅" status claimed earlier in this project's audit
was wrong to call a clean win — it's implemented and testable, but the method
itself needs to become feature-aware (e.g. regress-then-resample-residuals, a
real MICE step) before it's a defensible research contribution.**

## 2. Forecasting benchmark (`forecasting_benchmark.py`)

**Dataset:** statsmodels' built-in Mauna Loa CO2 series (real atmospheric
measurements 1958–2001, resampled to monthly, 526 points) — genuine trend +
genuine annual seasonality + real noise.

**Evaluation:** 6 walk-forward windows (expanding training window, 12-month
horizon each), using the project's actual `run_forecast()` for `"auto"` mode
and every individual `CANDIDATES` model for comparison.

| method | mean MASE | std MASE |
|---|---|---|
| **auto (ours)** | **2.136** (best) | 0.459 |
| naive | 2.290 | 0.480 |
| arima | 2.685 | 1.052 |
| sarima | 3.175 | 1.142 |
| seasonal_naive | 3.275 | 0.477 |
| holt | 7.409 (worst) | 3.916 |

**Honest finding — this is a real, positive, defensible result:** `auto` beats
every individual fixed-model baseline, including plain naive, on mean MASE
across 6 independent windows. It isn't a trivial win from always picking naive
either — per-window detail shows it actually switches to `arima` or
`seasonal_naive` when the meta-features justify it (window 2 and 3), and still
comes out ahead on average. **This is the strongest evidence-backed claim in
the project so far** and the one most ready to go into a paper's results
section as-is.

## What this does NOT cover yet (honest gaps)

- **RAG / chat retrieval quality** — no eval here; needs a live LLM API key and
  a labeled question-answer set, which this sandbox can't exercise.
- **Data quality / drift scoring** — no eval here; "is the health score
  actually a good proxy for real data quality" needs a labeled corpus of
  known-good vs known-bad datasets, which doesn't exist yet.
- **Statistical significance testing** — the tables above report means/stds
  over small windows (6-10), not paired significance tests (e.g. Diebold-Mariano
  for the forecasting comparison). Worth adding before a paper submission.
- **Single dataset per benchmark** — one real dataset each, not a panel. The
  forecasting result in particular should be checked against at least one more
  real series (e.g. a monthly retail/economic series) before claiming it
  generalizes beyond CO2's specific trend+seasonality shape.
