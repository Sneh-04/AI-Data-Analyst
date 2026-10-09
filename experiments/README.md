# Reproducible experiments

The scripts invoke the project's implementation in `ml-service/app/services/`
and write raw trial/window rows and summaries under `experiments/results/`.
The datasets are bundled with scikit-learn and statsmodels, so the runs do not
download data.

## Reproduce

Use Python 3.13.9 and the pinned dependencies in `requirements.txt`:

```sh
python3.13 -m venv /tmp/ai-data-analyst-experiments
. /tmp/ai-data-analyst-experiments/bin/activate
python -m pip install -r experiments/requirements.txt
cd experiments
PYTHONPATH=../ml-service python imputation_benchmark.py
PYTHONPATH=../ml-service python forecasting_benchmark.py
```

The recorded run used Python 3.13.9, NumPy 2.3.5, pandas 2.3.3,
scikit-learn 1.7.2, SciPy 1.16.3, statsmodels 0.14.5, and tabulate 0.9.0.
The diabetes data description in `sklearn.datasets.load_diabetes()` cites the
source URL and Efron et al. (2004), but does not state a separate dataset
license; check the source terms before redistributing the data.

## Imputation

**Question:** Does conditioning on other observed features reduce reconstruction
error versus the previous marginal-bootstrap implementation?

**Data/protocol:** scikit-learn's bundled diabetes dataset (442 rows, 10
standardized predictor columns); mask only `bmi` under MCAR at 10%, 20%, and
30%. For each rate, use 10 mask seeds (42–51) and the same masked cells across
methods. The other nine features remain observed. RMSE is measured only at
masked cells. The table reports the mean and sample standard deviation of the
10 trial RMSEs. Uncertainty Spearman is calculated per trial between reported
spread and absolute error on masked cells, then averaged.

The production `multiple` strategy uses five stochastic scikit-learn
`IterativeImputer` runs with `BayesianRidge` and posterior sampling. The
previous five-draw marginal bootstrap is retained as a baseline. KNN uses
five neighbors and all ten columns. These are point-reconstruction comparisons;
the iterative strategy's between-imputation standard deviation is descriptive
spread, not a calibrated interval or total-variance estimate.

The generated table is
[`imputation_benchmark_report.md`](results/imputation_benchmark_report.md);
raw trials and the machine-generated numeric summary are
[`imputation_benchmark_raw.csv`](results/imputation_benchmark_raw.csv) and
[`imputation_benchmark_summary.csv`](results/imputation_benchmark_summary.csv).

**Result:** Conditioning improves mean RMSE over the old marginal bootstrap at
all tested rates. It does not consistently beat KNN: KNN has lower mean RMSE at
20% and 30%. The uncertainty/error rank correlations remain close to zero, so
this experiment does not support an uncertainty-calibration claim. This is a
single-dataset, single-target MCAR experiment; it says nothing about MAR, MNAR,
other data distributions, or inferential validity of multiple imputation.

## Forecasting

**Data/protocol:** statsmodels' bundled Mauna Loa CO2 observations (1958–2001),
resampled to monthly means (526 points). The script evaluates six expanding
training origins with a 12-month horizon; at each origin, automatic selection
and each fixed candidate use the same training data and horizon. `auto` uses
the project's actual `run_forecast()` implementation.

The auto selector chose naive at four origins, seasonal naive at one, and
ARIMA at one. These six origins come from one series and are not independent
series-level replications. The result is descriptive evidence on Mauna Loa CO2,
not evidence of generalization or statistical significance. The generated
aggregate and per-origin tables are in
[`forecasting_benchmark_report.md`](results/forecasting_benchmark_report.md).
Raw origins and aggregate summary are
[`forecasting_benchmark_raw.csv`](results/forecasting_benchmark_raw.csv) and
[`forecasting_benchmark_summary.csv`](results/forecasting_benchmark_summary.csv).

## Research basis and open gaps

The imputation design and its limitations are mapped to verified papers in
[`research-matrix.md`](../research/research-matrix.md). The next experiments
should add multiple datasets and explicit MAR/MNAR mechanisms, and evaluate
uncertainty with interval coverage and width before describing it as calibrated.
See the
[`implementation roadmap`](../research/implementation-roadmap.md)
for remaining priorities. No significance test is reported: the current small
set of highly related forecasting origins does not justify treating them as
independent replicates.
