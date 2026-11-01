
# AI Data Analyst

React frontend, Spring Boot API gateway, FastAPI ML service, and PostgreSQL
storage for data cleaning, quality checks, forecasting, and dataset questions.

## Quickstart

Create a local `.env` file from `.env.example` and set unique secrets before
starting the stack. For example, generate values with `openssl rand -hex 32`
for `JWT_SECRET`, `INTERNAL_API_KEY`, and `POSTGRES_PASSWORD`. Do not commit
`.env`.

```sh
cp .env.example .env
# Edit .env and set the generated secrets.
docker compose up --build
```

Open the frontend at [http://localhost:3000](http://localhost:3000). The API
gateway is at `http://localhost:8080` (`/health` is its readiness endpoint),
the ML service at `http://localhost:8000`, and PostgreSQL is published on
`localhost:5432`. Register an account in the UI to begin; the application does
not include a default user.

## Upload limits

The API defaults to a 20 MB file limit. Set `MAX_UPLOAD_SIZE` to change it.
Multipart overhead is accommodated by `MAX_UPLOAD_REQUEST_SIZE` (25 MB by
default); increase that value alongside the file limit when needed.

## Dataset deletion

Use the Delete action in My datasets to remove a dataset and its generated
versions and reports. The API marks the dataset unavailable before deleting
stored files and then removes the dataset row; PostgreSQL cascades the related
analysis, chat, report, and embedding records. If file cleanup fails, the
dataset remains inaccessible and the same delete action can be retried. After
deletion succeeds, another DELETE request for that dataset returns 404.

Deletion jobs retain their status and request/completion timestamps for
operational troubleshooting. Dataset and requester IDs are retained while a
deletion is pending or failed so it can be retried, then cleared in the same
transaction that completes deletion.

This local setup does not define backup retention or guarantee deletion from
external AI providers or infrastructure backups. Such copies may persist under
their respective retention policies; do not treat active-storage deletion as
proof that backup copies have expired. Production backup retention and provider
data-retention policies have not been verified.

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
