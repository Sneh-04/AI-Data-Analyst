# EXPLORATORY (post-hoc, not pre-registered)

`analyze_rubin_coverage.py` reads the existing
`experiments/results/rubin_coverage_full_v4/raw.csv.gz` without modifying it.
It does not rerun or simulate any experiment. Generated tables and figures go
only to the new `experiments/results/rubin_coverage_full_v4_exploratory/`
directory and are explicitly labeled exploratory.

Run from the repository root:

```sh
python experiments/analysis_exploratory/analyze_rubin_coverage.py
pytest -q experiments/analysis_exploratory/test_analyze_rubin_coverage.py
```

MNAR sensitivity uses the recorded `delta_sd` values `-1, -0.5, 0, 0.5, 1`.
Union-interval coverage is counted only where all five levels have valid
intervals. Paired coverage differences match dataset/trial/mask seeds and use
a 2,000-replicate dataset-cluster bootstrap with seed 42. Figures are 3.5
inches wide (single-column IEEE width) and saved in PNG and PDF formats.
