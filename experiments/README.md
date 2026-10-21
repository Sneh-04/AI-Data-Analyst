# Reproducible experiments

The scripts invoke the project's implementation in `ml-service/app/services/`.
The legacy benchmark commands below write to `experiments/results/`; the
supplementary research scripts default to a new temporary output directory.
The datasets are bundled with scikit-learn and statsmodels, so the runs do not
download data.

## Real-dataset imputation extension

`datasets/registry.py` contains 15 OpenML datasets whose names, IDs, versions,
targets, task types, dimensions, and missingness have been verified with
`fetch_openml`. Downloads and canonical CSV cache files are stored in
`datasets/cache/`, which is ignored by Git. The verified tabular CSV is the
first-choice source on later runs; per-dataset OpenML feature-type metadata
sidecars live in the tracked `datasets/metadata/` directory and are hash-checked
against the manifest. Metadata fetched for a custom/test cache is written to
that cache's `feature_metadata/` subdirectory.
Only a cache miss can call the OpenML feature-metadata endpoint or
`fetch_openml` (which may use scikit-learn's own `data_home` cache before
downloading from OpenML). Network fetches retry transient URL, connection,
timeout, and retryable HTTP errors up to three times with exponential
backoff; invalid payloads and other non-network errors fail immediately.
`datasets/manifest.json` records
the resolved OpenML ID/version, table shape and dtypes, OpenML feature types,
raw/final dtypes and cardinalities, per-column missing rates, numeric-string
coercions, CSV SHA-256, fetch date, and library versions. Numeric-vs-categorical
encoding follows OpenML feature metadata rather than parser-inferred pandas
dtypes. The Telco `TotalCharges` string column is explicitly parsed as numeric;
11 invalid values become missing and are recorded in the manifest. The raw
data should not be committed or redistributed without checking upstream terms.

Run the extension from the repository root:

```sh
PYTHONPATH=ml-service .venv/bin/python experiments/run_real_datasets.py --quick
PYTHONPATH=ml-service .venv/bin/python experiments/run_real_datasets.py \
  --protocol both --repeats 12 --seed 42
```

`--datasets` accepts registry names, `--protocol` selects `A`, `B`, or `both`,
`--out` selects a new output directory, and `--max-rows` defaults to 5000.
Datasets larger than the cap are subsampled with fixed-seed (`--seed`) target
stratification; datasets at or below the cap are unchanged. The uncapped
download is retained in the dataset cache, while the run config records the
cap and summary records the evaluated row count. The default output path is a unique
`experiments/results/real_datasets_<date>/`; a non-empty output directory and
the frozen `paper_run_2026-10-11/` tree are never overwritten. `--quick` uses
up to three smaller datasets and one repeat for a smoke run.

The two protocols and their estimates must not be pooled:

- **Protocol A (ground-truth masking):** drop naturally incomplete predictor
  columns, retain rows with an observed target, then mask complete features at
  10%, 20%, and 30% using MCAR, MAR, and MNAR. Datasets with fewer than 100
  rows are logged as skipped. Numeric RMSE uses each feature's standard
  deviation computed once from the full pre-mask data, identically across
  methods and mechanisms; numeric and categorical outcomes are never pooled.
  Numeric features with full-data standard deviation below `1e-8` are excluded
  from numeric scoring and logged. Trial CSVs include numeric RMSE in these
  standardized units, categorical accuracy/error rate, and numeric-only MICE
  uncertainty coverage/Spearman metrics. Paired Wilcoxon tests compare MICE
  with each baseline, followed by Holm correction.
- **Protocol B (natural missingness):** preserve naturally missing feature
  values and report fixed Random Forest 5-fold predictive metrics, plus
  recovery on a 10% holdout of observed test-fold cells. Each fold fits its
  encoder/scaler, imputer, and predictive model using training-fold data only;
  the fitted imputer only transforms the held-out fold. Outputs explicitly
  identify these rows as `natural missingness`. Paired fold tests are Holm
  corrected.

Categorical columns are ordinal-encoded within the experiment and decoded by
rounding the imputed ordinal code to the nearest observed category. The
production feature-aware MICE and KNN implementations model numeric columns;
categorical columns in the service use a separate mode fallback, rather than
being modeled jointly. Thus the real-dataset benchmark's ordinal handling is a
harness-only adapter and does not imply production categorical MICE support.
Ordinal codes impose an artificial order on categories and can affect
distance/regression imputers. When a masked column has only one observed value,
the benchmark's MICE adapter minimally widens that feature's bounds so
scikit-learn's iterative imputer can fit; the production service implementation
remains unchanged. Pima Diabetes zero values in `plas`, `pres`,
`skin`, `insu`, and `mass` are treated as sentinel missing values before either
protocol; this is documented in the registry and manifest.

`run_stage.py` runs one dataset at a time into `<out>/<dataset>/`, checks
`run_config.json`, the dataset summary, and exact protocol row counts before
skipping a completed result, and retries failed/incomplete attempts at most
three times. Attempt results are written to temporary sibling directories and
only promoted after completion checks pass. It appends status and elapsed time
to `stage_status.jsonl`.

Tables can be regenerated only from saved CSVs. Multiple run directories
(including separate stages and per-dataset reruns) are merged in memory; the
table builder rejects duplicate dataset/mechanism/rate/trial-or-fold/method
keys and leaves input CSVs untouched:

```sh
PYTHONPATH=ml-service .venv/bin/python experiments/make_real_dataset_tables.py \
  --input-dir experiments/results/real_datasets_<stage1> \
    experiments/results/real_datasets_<stage2> \
  --out experiments/results/real_datasets_<date>/tables
```

The table-time inclusion rules are declared before looking at method
comparisons and are written to `tables/rules.json`:

- Protocol A headline tables require at least 5 retained complete columns and
  at least 2 retained numeric columns. Other datasets appear in supplementary
  tables with an `exclusion_reason`.
- Protocol B downstream-performance headline tables exclude datasets whose
  mean-imputer accuracy is at least 0.999; these remain in supplementary
  tables with the reason. Held-out-observed recovery tables include every
  Protocol B dataset.

  Headline inclusion is applied consistently to Protocol A win/tie/loss,
  non-winning-cell, uncertainty, dataset-level significance, and effect-size
  tables, and to Protocol B downstream accuracy/AUC significance and effect-size
  tables. Held-out recovery results retain all Protocol B datasets. Corresponding
  all-dataset outputs use the `_all_datasets_supplementary` suffix.

  For Protocol A win/tie/loss counts, each dataset × mechanism × mask-rate cell
  first selects the best conventional baseline by the lowest mean-imputer-relative
  numeric RMSE among mean, median, KNN5, and single IterativeImputer. Each method
  is then compared against that selected baseline: a win is more than 1% lower
  RMSE, a tie is within 1%, and a loss is more than 1% higher. Categorical
  metrics are evaluated with the harness ordinal-encoding adapter; this is not
  production behavior (production uses a mode fallback) and is not for headline
  claims. All Protocol A uncertainty coverage rows label their nominal 0.90
  interval target. `tables/HEADLINE_SUMMARY.md` provides the compact saved-CSV-only
  headline output.

The original Protocol A/B significance CSVs pair method scores across
masking trials/rates (A) or repeated folds (B) within each dataset, so their
paired observations are not independent datasets. The table builder preserves
those tests and additionally writes dataset-level Wilcoxon signed-rank tests:
Protocol A averages repeats/rates within dataset and mechanism; Protocol B
averages folds/repeats within dataset. Holm correction is applied, and
`low_power_n_lt_10` flags comparisons with fewer than ten datasets.
Dataset-level tables additionally report the minimum attainable exact
two-sided p-value, Holm family size, whether alpha=.05 is attainable at that
sample size, and a plain-text power note. These transparency columns do not
alter existing p-values.

Table labels identify Pima Diabetes as sentinel-coded missingness (zeros treated
as missing), distinguish datasets with less than 1% natural missingness in
Protocol B, and mark Cylinder Bands as marginal when its saved Protocol A
coverage is seven retained columns, two numeric columns. Effect-size tables
compare project MICE to each baseline using dataset-level medians and
10,000-resample percentile bootstrap 95% intervals (seed 42). A complete
Markdown results pack is written to `tables/RESULTS_PACK.md` from saved CSVs.

Loader, metadata-cache, retry, merge, and fixture tests run offline. The
network loader test is marked `network` and skipped unless
`RUN_OPENML_TESTS=1`.

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
expanding natural-missingness coverage and interval calibration/width checks
before describing uncertainty as calibrated.
See the
[`implementation roadmap`](../research/implementation-roadmap.md)
for remaining priorities. No significance test is reported: the current small
set of related origins in the original one-series forecasting benchmark does
not justify treating them as independent replicates. The separate M3 results
and their limitations are recorded below.

## Supplementary research-upgrade experiments

The supplementary suite adds a three-dataset MCAR/MAR/MNAR imputation
benchmark, an MNAR-signal detector study, six-series rolling-origin forecasting,
a 20-series M3 Monthly extension, and a controlled data-quality corruption
study. These use the
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

<!-- BEGIN GENERATED FROZEN PAPER RESULTS -->
### Frozen forecasting evidence

The supplementary frozen run evaluates 20 M3 Monthly series over 80 scored windows.
Auto's mean series-level MASE was 1.97262782; fixed ARIMA's was 1.91571923. For the
paired Auto-minus-ARIMA comparison, the mean difference was 0.05690859 over 20 series,
with 9 Auto wins; raw p=0.784126281738 and Holm-adjusted p=1. It was not significant
after Holm correction. Across the seven Auto-versus-alternative comparisons, 0 were
significant after Holm correction. See the full [model
summary](results/paper_run_2026-10-11/followup_tables/m3_model_summary.csv), [Auto
comparisons](results/paper_run_2026-10-11/followup_tables/m3_auto_comparisons.csv), and
[series-level
results](results/paper_run_2026-10-11/followup_tables/m3_series_results.csv).

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
calculation](results/paper_run_2026-10-11/followup_tables/m3_shortlisting_noninferiority.csv)
and the [six-series per-series
results](results/paper_run_2026-10-11/followup_tables/six_series_shortlisting_by_series.csv).

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
metadata](results/paper_run_2026-10-11/forecasting_m3/m3_environment.json). M3 series
may share domains, so these results do not remove all dependence or establish
generalization beyond this dataset. Canonical environment pins are listed
[here](results/paper_run_2026-10-11/environment_pins.txt).
<!-- END GENERATED FROZEN PAPER RESULTS -->

See [`research-upgrade-status.md`](../research/research-upgrade-status.md) for
implemented-versus-measured distinctions, limits, and open research questions.

## Post-hoc MICE point-estimate ablation

`run_mice_ablation.py` is a separate exploratory analysis; it does not alter the
standard benchmark CLI or metrics. It compares the saved five-draw MICE variant
with 20/50-draw averages, a deterministic iterative estimate, and single-draw
IterativeImputer variants. The reproduction gate should be run against saved
Protocol A trial rows before a full run. Each dataset is written separately and
can be skipped when its config and complete output already exist:

```sh
PYTHONPATH=ml-service .venv/bin/python experiments/run_mice_ablation.py \
  --datasets adult bank-marketing breast-w credit-approval credit-g \
    cylinder-bands heart-statlog pc1 telco-customer-churn wine-quality-red \
  --repeats 2 --seed 42 --max-rows 5000 --out experiments/results/mice_ablation_DATE
PYTHONPATH=ml-service .venv/bin/python experiments/make_mice_ablation_tables.py \
  --input-dir experiments/results/mice_ablation_DATE
```

Replace `DATE` with the selected run date before invoking the commands.
The ablation is post-hoc exploratory and descriptive only: it does not report
p-values or support new significance claims. Its output contains per-dataset
median RMSE ratios, aggregate medians, counts below the `project_m5` ratio, and
draw-count uncertainty summaries, all computed from the saved ablation CSVs.
