# Study 2 performance feasibility benchmark

- Status: performance-only; no Study 2 coverage results generated.
- Sample size / imputations: n=500, m=20.
- Fixture design: One synthetic fixture per DGP/mechanism and 10%/50% missingness; fixture parameters are not protocol DGP parameters.
- Environment: Python 3.14.5, scikit-learn 1.9.1, 8 logical CPUs.
- Environment/manifest version differences: {"numpy": {"actual": "2.5.3", "declared": "2.3.5"}, "pandas": {"actual": "3.0.6", "declared": "2.3.3"}, "scikit_learn": {"actual": "1.9.1", "declared": "1.7.2"}, "scipy": {"actual": "1.18.1", "declared": "1.16.3"}}.
- Runtime samples are measured in isolated processes; peak RSS includes interpreter and imported-library memory.
- Workload projections assume equal average cost per configured sample/mask condition and use six timing scenarios; ranges use scenario minima/maxima.
- Parallel wall times are arithmetic projections at assumed 75% efficiency for 4 workers and 55% for 8; parallel execution was not run.
- Memory projections multiply the largest measured worker peak by worker count; this is conservative and excludes IPC/scheduler overhead.
- Host assessment: 8.00 GiB physical RAM
- Current free disk: 10.43 GiB. See JSON for projected memory fit; no runtime feasibility cutoff was prespecified.
- Study-result storage volume is not estimated: the inferential run output schema/runner remains unfinalized.
- The active v5 workload is 6,300 sample/mask replicates; 63,000 is shown only as a 1,000-replicate scale projection. Neither projection changes or authorizes the study protocol.
- This benchmark reports no empirical bias, coverage, or method ranking. Full Study 2 remains blocked by protocol freeze requirements.

See `runtime_samples.csv`, `feasibility_estimates.csv`, and `benchmark_results.json`.
