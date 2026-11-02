# Study 2 methodology audit and implementation status

**Status:** Implementation validation only. No Study 2 experiment was run or
authorized. Historical v4 code, protocol, results, and figures were read-only.

## Findings

### 1. BayesianRidge intercept uncertainty

The v4 environment metadata records scikit-learn 1.9.1. In its tagged
[`BayesianRidge` source](https://github.com/scikit-learn/scikit-learn/blob/1.9.1/sklearn/linear_model/_bayes.py),
`fit_intercept=True` centers `X` and `y`, calculates `sigma_` over the
predictor coefficients, and then restores the intercept separately. Thus,
sampling `Normal(coef_, sigma_)` does not draw the intercept.

Adding a constant column and fitting `BayesianRidge(fit_intercept=False)`
does put the intercept in `coef_` and `sigma_`. It is not equivalent to
sklearn's centered-intercept fit: the explicit constant receives the same
zero-centered empirical-Bayes coefficient prior as the other columns.
`alpha_` and `lambda_` remain plug-in estimates; this implementation does not
integrate over their uncertainty. This is a conditional coefficient
approximation, not full Bayesian uncertainty propagation or proof of proper
multiple imputation.

The deterministic fixture test confirms a 2-by-2 covariance for the explicit
constant-plus-predictor design, finite positive-semidefinite covariance, and
intercept draw variation. On its small fixture, the active scikit-learn 1.5.1
runtime produced a maximum fitted-value difference of about 0.0054 between
the default centered-intercept model and the explicit-constant model. The
frozen posterior fixture also checks the coefficient mean, covariance, and
seeded coefficient draw. These are implementation checks, not a theoretical
justification.

Version compatibility remains a freeze gate: current runtime is
scikit-learn 1.5.1, `experiments/requirements.txt` pins 1.7.2, and the v4
recorded environment is 1.9.1. The fixture has not been executed in the v4
1.9.1 environment.

### 2. Uncertainty ablation and neutral PMM identifier

The Study 2-only helper now provides:

- `posterior_only`: fit the observed rows without bootstrap; sample
  coefficients and predict missing values without residual noise. Only the
  coefficient stream varies.
- `bootstrap_only`: resample rows and refit the BayesianRidge iterative
  imputer with posterior predictive sampling disabled. Bootstrap selection
  is the source of between-draw variation.
- `bootstrap_pmm_candidate`: bootstrap donor/training records, sample the
  conditional coefficient vector, then select a donor from the five nearest
  records. Duplicate bootstrap records retain multiplicity; fewer than five
  donor records is an explicit failure.

The variants use distinct `SeedSequence([seed, draw, stream_id])` entropy
keys, exposed by `imputation_stream_manifest`. The PMM candidate uses stream
IDs 1/2/3 for bootstrap/coefficient/donor selection; `bootstrap_only` also
uses ID 4 for the iterative imputer. Tests verify determinism, stream-key
uniqueness, observed-value preservation, donor membership, covariance
validity, and explicit input failures. No ablation performance results have
been generated. The ablation is diagnostic and does not change the primary
method ranking.

The identifier is consistently `bootstrap_pmm_candidate`; no code or
documentation classifies it as statistically proper.

### 3. Read-only v4 workload reconciliation

The workload audit derives dimensions from
`experiments/results/rubin_coverage_full_v4/run_config.json` and streams the
historical `raw.csv`:

| Quantity | Audited count |
|---|---:|
| Configured datasets × mechanisms × rates × trials | 10 × 3 × 3 × 100 |
| Expected mask cells | 9,000 |
| Observed mask cells | 9,000 |
| Missing / unexpected mask cells | 0 / 0 |
| Missing or inconsistent mask-seed records/cells | 0 / 0 |
| Successful paired `mice_proper`, m=20, delta=0 estimand rows | 18,000 |
| Missing paired estimand rows | 0 |
| Configured masked-condition raw rows | 252,000 |
| Other raw rows (no-missing sanity) | 2,000 |
| Total raw rows / successful status rows | 254,000 / 254,000 |

Therefore 900 is not the full workload for this run configuration. It is not
supported as a subset by the observed inventory. A full PMM extension at
`m=20`, reusing completed datasets for both estimands as the v4 benchmark
does, is up to 180,000 completed-data draws and 18,000 estimand-level
comparison rows. This count is an arithmetic projection, not an experiment
result.

### 4. Separate statistical coverage and reliability

`summarize_replicates` reports separately:

1. Coverage among finite, ordered intervals with finite width and finite
   truth, divided by valid finite intervals.
2. Failure rate, divided by all scheduled replicates, with mutually
   exclusive `failed_run`, `invalid_interval` (reversed bounds, invalid
   truth, or non-finite width), and `undefined_interval` categories.
3. All-scheduled operational success-adjusted coverage, divided by all
   scheduled replicates; every failed/invalid/undefined interval is uncovered.

Bias and estimate variance use finite point estimates with finite truth, even
when the interval is invalid or undefined; each metric returns its own
denominator. Width uses valid finite intervals only.

## Validation performed

- Focused Study 2 tests: **24 passed**.
- Python `compileall` on the new Study 2 modules and tests: **passed**.
- Read-only v4 workload audit: **9,000/9,000 mask cells and 18,000/18,000
  paired estimand rows reconciled**.
- No benchmark, simulation, or v4 rerun was performed.

The unchanged `tests/test_rubin_study_imputers.py` regression file was also
run against the active scikit-learn 1.5.1 environment: **7 passed, 2 failed**.
The failures are the existing `test_improper_mice_draws_differ` (all
imputations were equal for that fixture/seed/runtime) and the strict
`estimate == 2.0` HC3 test (observed `2.0000000000000004`). No v4 imputer or
analysis implementation was edited in this audit; these baseline failures
remain unresolved and should be checked in the pinned environment before
claiming unchanged benchmark reproducibility.

## Literature and unresolved design work

Crossref metadata verified the bibliographic records for Morris, White, and
Royston, “Tuning multiple imputation by predictive mean matching and local
residual draws” (2014, DOI
[10.1186/1471-2288-14-75](https://doi.org/10.1186/1471-2288-14-75)), and
Bailey, Andridge, and Shoben, “Multiple imputation by predictive mean
matching in cluster-randomized trials” (2020, DOI
[10.1186/s12874-020-00948-6](https://doi.org/10.1186/s12874-020-00948-6)).
The latter's Crossref abstract concerns PMM procedures for clustered trials;
that setting does not establish properties of this single-target candidate.
Publisher full-text retrieval returned HTTP 406 during this audit. A complete
literature review of proper MI theory and the candidate's assumptions remains
a **TODO before protocol freeze**. No novelty or properness claim is made.

Other blocking items remain in the protocol, including frozen DGP parameters,
the exact supported sklearn environment, complete methodologist review,
aggregate weighting and multiplicity decisions, bootstrap procedures for
paired uncertainty, and an outcome-blind runtime benchmark. The current
helpers are not a full Study 2 runner.

## Files changed for this audit

- `experiments/rubin_study/study2_methods.py` — Study 2 ablations and PMM
  candidate; v4 imputer left untouched.
- `experiments/rubin_study/evaluation.py` — separate finite-interval
  coverage, failure, and operational metrics.
- `experiments/rubin_study/workload.py` — config/raw inventory reconciliation.
- `experiments/rubin_study/study2_config.json` — neutral method IDs,
  diagnostic status, stream mapping, donor assumptions, and metric definitions.
- `experiments/tests/test_study2_methods.py`,
  `experiments/tests/test_study2_evaluation.py`, and
  `experiments/tests/test_study2_workload.py` — focused implementation,
  fixture, arithmetic, and metric tests.
- `experiments/RUBIN_STUDY2_PROTOCOL.md` and
  `experiments/proposals/RUBIN_STUDY2_REVIEW_DRAFT.md` — corrected method
  naming, PMM assumptions, ablation scope, workload counts, and separate
  reliability metrics.
