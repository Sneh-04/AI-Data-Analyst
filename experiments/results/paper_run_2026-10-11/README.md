# Paper run reproducibility and forecasting extension

This run-specific note supersedes any earlier environment/result summaries for
the frozen evidence in this directory.

## Canonical imputation evidence and reproducibility

The canonical imputation CSVs remain the originally frozen files under
[`imputation/`](imputation/). Two new benchmark executions in fresh output
folders, using the canonical run's environment, produced byte-identical raw,
summary, significance, and environment files:

| file                        |   run_1_bytes |   run_2_bytes | byte_identical   |
|-----------------------------|---------------|---------------|------------------|
| imputation_raw.csv          |        130699 |        130699 | True             |
| imputation_summary.csv      |          6249 |          6249 | True             |
| imputation_significance.csv |          5734 |          5734 | True             |
| environment_imputation.json |           332 |           332 | True             |

The original frozen run and repeat runs record Python 3.14.5,
NumPy 2.5.3, pandas 3.0.6, scikit-learn
1.9.1, SciPy 1.18.1, and statsmodels
0.15.0. Pin these versions to reproduce the canonical
numbers; see [`environment_pins.txt`](environment_pins.txt).

The earlier saved run records Python 3.12.3, NumPy 1.26.4,
pandas 2.2.2, scikit-learn 1.5.1, SciPy
1.13.1, and statsmodels 0.14.2. The matched raw-row
comparison is preserved in
[`imputation_prior_run_comparison.txt`](imputation_prior_run_comparison.txt):

```text
Frozen raw rows: 1728
Prior raw rows: 1728
Rows with keys only in frozen run: 0
Rows with keys only in prior run: 0
rmse: 454 differing matched rows; maximum absolute finite difference=0.0791638393319
n_masked: 0 differing matched rows; maximum absolute finite difference=0
coverage90: 112 differing matched rows; maximum absolute finite difference=0.0666666666667
interval_width: 288 differing matched rows; maximum absolute finite difference=0.152820714679
uncertainty_spearman: 493 differing matched rows; maximum absolute finite difference=0.109767545813
```

This supports environment-dependent results, not unseeded randomness in the
same recorded environment. The canonical CSVs were not replaced by either
repeat execution.

## Forecasting results and shortlisting

The frozen 6-series, 48-window Auto versus no-shortlist comparison
has mean per-series MASE difference (Auto minus no-shortlist)
-0.05152810. The pre-specified one-sided 95% t
upper bound (five degrees of freedom) is
0.05230352; the percentile-bootstrap upper bound
is 0.00000000. The fixed non-inferiority
margin is 0.05 MASE. **Non-inferiority not
established**: the t upper bound narrowly exceeds the margin, and both bounds
are required to be below the margin. This does not support an equivalence
claim. Full paired per-series results are in
[`followup_tables/six_series_shortlisting_by_series.csv`](followup_tables/six_series_shortlisting_by_series.csv).

Mean measured runtime per forecast window in this six-series run was
0.30891051 seconds for Auto and
0.39076093 seconds for Auto without
shortlisting.

An additional M3 Monthly evaluation uses a deterministic subset of
20 series from 1043
eligible source series and 4 rolling
windows per series, with a horizon of 18. Source:
[M3 Monthly Dataset, DOI 10.5281/zenodo.4656298](https://zenodo.org/records/4656298),
licensed CC BY 4.0. Series selection is specified in
[`forecasting_m3/m3_environment.json`](forecasting_m3/m3_environment.json);
eligibility and source order determine the evenly spaced subset, which was
frozen before any model was run. The selected input observations and raw
forecasts are also saved there.

On M3, Auto's mean per-series MASE was 1.97262782
versus 1.95390802 without shortlisting (paired
difference 0.01871981,
Holm-adjusted p=0.89856247). Mean measured
runtime per window was 0.21555068 seconds
versus 0.36797288; the mean per-series runtime
reduction was 43.64884549 percent (paired
runtime Wilcoxon p=2.6702881e-05). This is
descriptive timing evidence on the selected subset; see
[`followup_tables/m3_series_results.csv`](followup_tables/m3_series_results.csv)
for all series-level scores.

Against fixed ARIMA on the same 20 M3 series, Auto's paired mean per-series
MASE difference (Auto minus ARIMA) was
0.05690859
(9 Auto wins of 20 pairs;
raw p=0.784126281738, Holm-adjusted p=1).
This comparison was not significant after Holm correction.

The same fixed +0.05 MASE non-inferiority
analysis was applied to the 20 per-series Auto-minus-no-shortlist differences.
The mean difference was 0.01871981; the
one-sided 95% t upper bound (df=19) was
0.04802643, and the percentile-bootstrap
upper bound was 0.05261873. **Non-inferiority
not established** because the bootstrap bound exceeds the margin, despite the
t bound being below it. The same test on six series narrowly failed because
its t upper bound was 0.05230352, above the
margin. The M3 extension applies the already-fixed margin; its result does
not erase the six-series failure. See
[`followup_tables/m3_shortlisting_noninferiority.csv`](followup_tables/m3_shortlisting_noninferiority.csv)
for the generated calculation.

## Generated evidence and reproducibility

- [`followup_tables/`](followup_tables/) contains machine-generated CSV and
  Markdown analyses, including series-level and model-level summaries.
- [`forecasting_m3/`](forecasting_m3/) contains the open source archive, its
  SHA-256-recorded metadata, the deterministic selected data, raw evaluations,
  and execution log.
- [`reproducibility/`](reproducibility/) contains both complete fresh
  imputation run outputs and logs.
- Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml-service .venv/bin/python
  experiments/results/paper_run_2026-10-11/analyze_followup.py` from the
  repository root to regenerate the follow-up tables and this note from saved
  CSV/JSON evidence.
