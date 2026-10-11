
# AI Data Analyst

React frontend, Spring Boot API gateway, FastAPI ML service, and PostgreSQL
storage for data cleaning, quality checks, forecasting, and dataset questions.

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
limited to one series and six walk-forward origins; it is not evidence of
generalization or statistical significance. See the
[`research matrix`](research/research-matrix.md) and
[`implementation roadmap`](research/implementation-roadmap.md).
