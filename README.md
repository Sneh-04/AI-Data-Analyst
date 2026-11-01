
# AI Data Analyst

React frontend, Spring Boot API gateway, FastAPI ML service, and PostgreSQL
storage for data cleaning, quality checks, forecasting, and dataset questions.

## Upload limits

The API defaults to a 20 MB file limit. Set `MAX_UPLOAD_SIZE` to change it.
Multipart overhead is accommodated by `MAX_UPLOAD_REQUEST_SIZE` (25 MB by
default); increase that value alongside the file limit when needed.

## Research experiments

Reproducible experiment methodology, limitations, and results are documented in
[`experiments/README.md`](experiments/README.md). To rerun the benchmarks from
the repository root after setting up Python 3.13.9:

```sh
python3.13 -m venv /tmp/ai-data-analyst-experiments
. /tmp/ai-data-analyst-experiments/bin/activate
python -m pip install -r experiments/requirements.txt
cd experiments
PYTHONPATH=../ml-service python imputation_benchmark.py
PYTHONPATH=../ml-service python forecasting_benchmark.py
```

The current imputation experiment evaluates numeric methods under simulated
MAR/MNAR masks across three bundled datasets. Results are descriptive and do
not establish that the proposed method outperforms deterministic iterative
imputation or KNN. Its reported between-imputation spread has not been shown
to be calibrated. Forecasting's lower mean MASE for automatic selection is
limited in the original bundled-data benchmark to one series and six
walk-forward origins. A separate frozen research run evaluates a fixed M3
Monthly subset; its evidence and limitations are summarized below. See the
[`research matrix`](research/research-matrix.md) and
[`implementation roadmap`](research/implementation-roadmap.md).

<!-- BEGIN GENERATED FROZEN PAPER RESULTS -->
### Frozen forecasting evidence

The supplementary frozen run evaluates 20 M3 Monthly series over 80 scored windows.
Auto's mean series-level MASE was 1.97262782; fixed ARIMA's was 1.91571923. For the
paired Auto-minus-ARIMA comparison, the mean difference was 0.05690859 over 20 series,
with 9 Auto wins; raw p=0.784126281738 and Holm-adjusted p=1. It was not significant
after Holm correction. Across the seven Auto-versus-alternative comparisons, 0 were
significant after Holm correction. See the full [model
summary](experiments/results/paper_run_2026-10-11/followup_tables/m3_model_summary.csv),
[Auto
comparisons](experiments/results/paper_run_2026-10-11/followup_tables/m3_auto_comparisons.csv),
and [series-level
results](experiments/results/paper_run_2026-10-11/followup_tables/m3_series_results.csv).

For shortlisting, differences are per-series mean MASE (Auto minus auto_no_shortlist),
with the series as the paired unit and four rolling windows averaged within each series.
The +0.05 MASE margin was fixed before the M3 results existed. On M3 (n=20), the mean
difference was 0.01871981; the one-sided 95% t upper bound (df=19) was 0.04802643, and
the percentile-bootstrap upper bound was 0.05261873. Non-inferiority was **not
established**: the percentile-bootstrap bound exceeds the margin, although the t upper
bound is below it. The earlier six-series test also **not established** (mean difference
-0.05152810; t upper bound, df=5, 0.05230352; bootstrap upper bound 0.00000000), because
the t upper bound narrowly exceeds the margin. Neither result establishes accuracy
equivalence. See the [M3 non-inferiority
calculation](experiments/results/paper_run_2026-10-11/followup_tables/m3_shortlisting_noninferiority.csv)
and the [six-series per-series
results](experiments/results/paper_run_2026-10-11/followup_tables/six_series_shortlisting_by_series.csv).

The M3 shortlisting comparison measured mean runtime of 0.21555068 seconds per window
with shortlisting and 0.36797288 without; the mean per-series runtime reduction was
43.64884549% (paired runtime Wilcoxon p=2.6702881e-05). This is evidence about measured
runtime on this subset, not an accuracy-equivalence result. The fixed-model and
per-series comparison tables are linked above.

Series were selected before model evaluation: 1043 source-order M3 Monthly series met
the length threshold of 102 observations, then 20 evenly spaced indices from first to
last were selected with integer `numpy.linspace` indices. Selection used series length
and source order only, not model scores or runtime. The full rule, selected IDs, and
pre-evaluation flag are recorded in [M3 environment
metadata](experiments/results/paper_run_2026-10-11/forecasting_m3/m3_environment.json).
M3 series may share domains, so these results do not remove all dependence or establish
generalization beyond this dataset. Canonical environment pins are listed
[here](experiments/results/paper_run_2026-10-11/environment_pins.txt).
<!-- END GENERATED FROZEN PAPER RESULTS -->
