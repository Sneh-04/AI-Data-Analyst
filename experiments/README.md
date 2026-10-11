# Reproducible experiments

The scripts invoke the project's implementation in `ml-service/app/services/`.
The legacy benchmark commands below write to `experiments/results/`; the
supplementary research scripts default to a new temporary output directory.
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

## Missing-data imputation

The experiment applies configurable logistic missingness mechanisms to
scikit-learn's bundled `diabetes`, `wine`, and `breast_cancer` numeric feature
tables. Targets are respectively `bmi`, `alcohol`, and `mean radius`; MAR
propensity source features are respectively `bp`, `malic_acid`, and
`mean texture`.

- **MAR:** target missingness propensity is calibrated to the requested
  expected rate and depends on a fully observed, different numeric predictor.
- **MNAR:** target missingness propensity is calibrated to the requested
  expected rate and depends on the target's complete values. Complete target
  values are used only by the simulator to make a mask; they are kept separately
  and never passed to the imputation methods.
- A Bernoulli draw yields a realized missing fraction that can differ from the
  configured expected rate. Both configured and realized rates are recorded.
- Each dataset/mechanism/rate/trial produces one mask. Mean, median, KNN,
  deterministic BayesianRidge iterative imputation, and the production
  `strategy="multiple"` implementation all receive the same masked rows and
  observed predictors. Numeric scaling is computed from observed cells only
  and shared by all methods.
- RMSE and MAE are computed only for artificially masked target cells that
  were observed before simulation. Runtime is recorded per method, excluding
  mask generation, shared scaling, and metric calculation.
- Per-method error summaries report trial-level mean, sample standard deviation,
  and t-based 95% confidence intervals. A separate comparison file reports
  paired proposed-minus-baseline RMSE/MAE differences and exploratory,
  unadjusted t-based 95% intervals over identical trial masks. These intervals
  describe repeated-mask variability on each fixed dataset, not uncertainty
  across datasets or populations; they are not confirmatory significance tests.
  Runtime is measured per method and summarized descriptively by mean and
  standard deviation, without confidence intervals because timings are
  environment-sensitive and can be strongly skewed.

Only numerical targets and numerical predictors are included in these
comparisons. Categorical predictor columns are omitted from every method's
model matrix, categorical target metrics are unsupported, and the experiment
does not measure the production service's categorical mode fallback. Boolean
and all-missing predictor columns are excluded; non-finite numeric values,
constant targets, and constant MAR source predictors are rejected. Bundled
datasets are used without network downloads. Verify each upstream dataset's
license before redistributing data.

Reproduce both the experiment and its unit tests:

```sh
cd experiments
PYTHONPATH=../ml-service python -m unittest discover -s tests -v
PYTHONPATH=../ml-service python imputation_benchmark.py
```

Configure seeds, repetitions, rates, mechanisms, datasets, and output location
with `--seed`, `--trials`, `--mask-rates`, `--mechanisms`, `--datasets`, and
`--output-dir`. Example:

```sh
PYTHONPATH=../ml-service python imputation_benchmark.py \
  --seed 42 --trials 10 --mechanisms mar mnar \
  --mask-rates 0.1 0.2 0.3 0.4 \
  --datasets diabetes wine breast_cancer
```

Raw trial rows, aggregate numeric results, paired method-difference intervals,
and the generated Markdown report are
[`imputation_benchmark_raw.csv`](results/imputation_benchmark_raw.csv),
[`imputation_benchmark_summary.csv`](results/imputation_benchmark_summary.csv),
[`imputation_benchmark_comparisons.csv`](results/imputation_benchmark_comparisons.csv),
and [`imputation_benchmark_report.md`](results/imputation_benchmark_report.md).
Do not interpret one run as evidence that the proposed method is better: use
the report's per-condition results and variability. Between-imputation spread
is not an evaluated predictive interval; coverage and width remain a separate
open task.

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
[`research-matrix.md`](../research/research-matrix.md). Next steps include
adding MCAR comparisons, categorical/mixed-type evaluation, real incomplete
datasets where ground truth is available, and interval coverage/width checks
before describing uncertainty as calibrated.
See the
[`implementation roadmap`](../research/implementation-roadmap.md)
for remaining priorities. No significance test is reported: the current small
set of highly related forecasting origins does not justify treating them as
independent replicates.

## Supplementary research-upgrade experiments

The supplementary suite adds a three-dataset MCAR/MAR/MNAR imputation
benchmark, an MNAR-signal detector study, six-series rolling-origin forecasting
and ablations, and a controlled data-quality corruption study. These use the
production ML-service functions and are distinct from the existing
`imputation_benchmark.py` and `forecasting_benchmark.py`; the research copies
are named `*_research_benchmark.py` so neither existing experiment entry point
nor its saved results are replaced.

The historical results in `results/` were copied from the research-upgrade
folder and are evidence from that prior run, not results produced during this
integration. The supplementary scripts never write there by default. The
runner creates a unique temporary output directory unless
`AI_DATA_ANALYST_RESULTS_DIR` is explicitly set:

```sh
PYTHON=/path/to/python AI_DATA_ANALYST_RESULTS_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-data-analyst-research.XXXXXX")" \
  sh run_research_benchmarks.sh
```

Omit `AI_DATA_ANALYST_RESULTS_DIR` to let the runner create and print a unique
temporary results directory automatically.

See [`research-upgrade-status.md`](../research/research-upgrade-status.md) for
implemented-versus-measured distinctions, limits, and open research questions.
