# Rubin Study 2 Protocol

**Protocol version:** 5.1  
**Protocol date:** 2026-11-01  
**Status:** Pre-registration draft; diagnostic implementation validation and
outcome-blind performance benchmarking only. **No inferential Study 2
experiments are authorized** while any blocking `TODO` below remains. Resolve
every blocking `TODO`, review and freeze this file, record its SHA-256 and
containing Git commit, and only then write or run the full study. Diagnostic
helpers and the performance benchmark do not authorize an inferential study.  
**Parent protocol:** `experiments/RUBIN_COVERAGE_PROTOCOL.md` (v4)  
**Study outputs:** `experiments/results/rubin_study2_<tag>/`

This protocol adds a synthetic known-data-generating-process study and a
pre-specified PMM real-data extension to v4. It does not amend v4 or authorize
editing or rerunning v4 code or results.

## 1. Motivation (EXPLORATORY observations)

The following are **EXPLORATORY observations**, not established causes,
confirmed findings, or pre-registered results:

1. At 50% missingness under MCAR/MAR, improper MICE has been observed to have
   SE/SD around 0.56–0.88, while bootstrap-then-impute has been around 1.0,
   with intervals about 15–81% wider.
2. Residual proper-MICE undercoverage at 50% missingness under MAR appears
   concentrated in a few datasets (bank-marketing, credit-g, credit-approval,
   breast-w) and appears bias-driven.
3. MNAR failure appears bias-dominated, and the existing ±1 SD delta grid has
   not reached nominal coverage.

These observations motivate Study 2 but do not determine its outcomes. Study 2
will not tune its settings to reproduce or explain them.

## 2. Research questions and estimands

The study will compare interval performance for:

1. The finite-population mean of outcome `x2`.
2. The intercept-including OLS slope of `x2` on `x1`.

The synthetic study uses known analytic population truths. The real-data
extension retains the exact 10 v4 finite populations, eligible columns, truths,
and row-sampling protocol. Only `x2` is made missing; all other eligible
numeric predictors remain observed and available as imputation predictors.

## 3. A. Synthetic known-DGP study

### 3.1 Replicates and DGPs

Each replicate is an independent iid sample of `n = 500` rows from its
specified population. There are three DGP families. DGP parameters marked
`TODO` are blocking: choose and record them before protocol freeze, and do not
change them after observing any study result.

**DGP 1 — bivariate multivariate normal**

Let `(x1, x2)` follow a bivariate normal distribution with mean vector
`(mu1, mu2)` and covariance matrix
`[[sigma1^2, sigma12], [sigma12, sigma2^2]]`.

- Population mean truth for `x2`: `mu2`.
- Population OLS slope truth for `x2 ~ 1 + x1`: `sigma12 / sigma1^2`.
- Parameters: `mu1`, `mu2`, `sigma1`, `sigma2`, and correlation (or
  `sigma12`) are **TODO**; require a positive-definite covariance matrix.

**DGP 2 — skewed outcome with a log-normal `x2`**

Let `x1 ~ Normal(mu1, sigma1^2)`, `epsilon ~ Normal(0, sigma_e^2)`
independently, and
`x2 = exp(alpha + beta*x1 + epsilon)`.

- Population mean truth:
  `E[x2] = exp(alpha + beta*mu1 + 0.5*(beta^2*sigma1^2 + sigma_e^2))`.
- Population OLS slope truth:
  `Cov(x1,x2)/Var(x1) = beta * E[x2]`.
- Parameters `mu1`, `sigma1`, `alpha`, `beta`, and `sigma_e` are **TODO**.
  Require positive scale parameters and a non-degenerate outcome.

**DGP 3 — nonlinear quadratic outcome**

Let `x1 ~ Normal(0, sigma1^2)`, `epsilon ~ Normal(0, sigma_e^2)`
independently, and
`x2 = alpha + beta*x1 + gamma*(x1^2 - sigma1^2) + epsilon`.

- Population mean truth for `x2`: `alpha`.
- Population OLS slope truth for `x2 ~ 1 + x1`: `beta`.
- Parameters `sigma1`, `sigma_e`, `alpha`, `beta`, and `gamma` are **TODO**;
  require positive scales and nonzero `gamma` so the conditional mean is
  nonlinear.

For mechanism-strength standardization in synthetic data, use the analytic
population mean and standard deviation of each DGP variable. In DGP 2,
`Var(x2) = exp(2*alpha + 2*beta*mu1 + 2*beta^2*sigma1^2 +
2*sigma_e^2) - E[x2]^2`. In DGP 3,
`Var(x2) = beta^2*sigma1^2 + 2*gamma^2*sigma1^4 + sigma_e^2`.
DGP 1 uses its specified covariance matrix. No simulated replicate values may
be used to redefine the analytic truths.

### 3.2 Missingness mechanisms, rates, and mechanism strength

Use rates `{0.10, 0.30, 0.50}`. For each replicate, method, and estimand,
methods share the same generated sample and missingness mask.

- **MCAR:** each `x2` value is independently missing with probability `rate`.
- **MAR:** missingness probability is
  `logistic(slope*z1 + intercept)`.
- **MNAR:** missingness probability is
  `logistic(slope*z2 + intercept)`.

Here `z1` and `z2` are standardized by the analytic synthetic population
moments or, for real data, by the v4 full eligible population scaler. For MAR
and MNAR, calibrate `intercept` by bisection over `[-30, 30]` so the mean
missingness probability on the replicate sample equals the target rate. Use
`logistic(a) = 1 / (1 + exp(-clip(a, -35, 35)))`. Draw Bernoulli indicators
from the recorded mask RNG stream. Retain the v4 safeguards: leave at least
five `x2` values observed and, if no value was masked, force one value missing
using that stream. Record the realized missing fraction.

For MAR and MNAR, run slopes `{0.5, 1, 2}`. Slope `2` is the v4-equivalent
primary mechanism strength; slopes `0.5` and `1` are pre-specified
mechanism-strength sensitivity conditions. MCAR has no slope parameter.

### 3.3 Methods and replication count

Run only the following methods, each with `m = 20`:

1. `mice_improper`: the v4 repeated `IterativeImputer` BayesianRidge approach
   with posterior sampling, `max_iter=10`, and `skip_complete=True`.
2. `mice_proper`: v4 bootstrap-then-impute with BayesianRidge, independently
   resampling `n` masked rows with replacement for each draw, fitting the
   chained imputer on that bootstrap sample, and imputing the original masked
   sample; use `sample_posterior=True`, `max_iter=10`, and
   `skip_complete=True`.
3. `bootstrap_pmm_candidate`: bootstrap predictive mean matching,
   as fully specified in Section 4.1.

Use 100 pre-specified replicate indices `0..99` for every DGP and condition.
Do not replace a failed replicate with a new seed.

### 3.4 No-missing sanity gate

For each DGP, draw 100 independent complete-data samples of size 500 using
the pre-specified replicate streams. Compute the mean and OLS slope intervals
directly from the complete data (no imputation), using two-sided nominal 95%
Student-t intervals: sample-variance-over-`n` for the mean with `n-1` degrees
of freedom, and HC3 OLS slope variance with `n-2` degrees of freedom.
Compare each interval to its analytic truth. For each DGP-estimand, report the
exact observed coverage and its two-sided 95% Clopper-Pearson interval. The
gate passes only when nominal coverage `0.95` lies inside that interval.
Report every gate outcome; do not tune a DGP or method in response to a
failure. A failed gate blocks claims about masked-condition calibration for
that DGP-estimand but does not erase or replace its results. With 100
replicates this is a low-power compatibility check, not proof of nominal
coverage.

## 4. B. Real-data PMM extension and validation

### 4.1 PMM algorithm (`bootstrap_pmm_candidate`)

Use the same 10 v4 eligible finite populations, selected columns, truths,
sampled rows, missingness masks, rates, mechanisms, and mechanism strengths.
At slope `2`, use the exact v4 trial and mask seeds and reproduce the v4 mask.
The only new real-data method is `bootstrap_pmm_candidate` with `m=20`; compare it
paired against the existing v4 `mice_proper` rows.

Only one target column is incomplete and predictors must be complete, so this
is one conditional update per imputation, not a multi-column chained-MICE
algorithm. For each of the 20 imputations:

1. Resample `n` incomplete rows with replacement from the replicate's masked
   analysis matrix. Preserve row multiplicity and missingness patterns.
2. Keep bootstrap copies with observed target values as donors. Fail the
   replicate if fewer than `k=5` donor records are available. Duplicate
   bootstrap records remain separate donor candidates.
3. Standardize predictors using their means and population SDs (`ddof=0`) in
   this donor pool. Drop constant predictors for this fit; fail if none remain.
   Apply that same transform to donor and recipient rows.
4. Fit `BayesianRidge(fit_intercept=False)` to a design matrix with a leading
   constant column. Draw the joint coefficient vector from
   `Normal(coef_, sigma_)`. With the explicit constant in `X`, `sigma_` covers
   both the intercept and predictor coefficients. Hold fitted empirical-Bayes
   noise and coefficient precisions fixed; do not add a separate residual
   draw. This samples coefficient uncertainty conditional on fitted
   hyperparameters only.
5. Compute donor and missing-recipient predictions from the same coefficient
   draw. Select uniformly from the five nearest donors by absolute prediction
   distance; randomize exact-distance ties with the donor stream and copy the
   selected observed target value exactly. Do not shift values by delta during
   imputation.
6. Restore observed cells unchanged and analyze the completed original `n`
   rows, not the bootstrap sample.

The explicit intercept receives BayesianRidge's same shared empirical-Bayes
coefficient prior; this changes the model relative to `fit_intercept=True`.
The candidate does not integrate over fitted hyperparameters and is not
classified as statistically proper or fully Bayesian. The fitted
`alpha_`/`lambda_` are plug-in estimates, not draws from a hyperprior.
Randomness uses `SeedSequence([seed, draw_index, stream_id])`, with stream
IDs 1 (bootstrap), 2 (coefficient draw), and 3 (donor choice). Record these
entropy keys with every generated result.

The v4 result metadata records scikit-learn 1.9.1. The current implementation
validation environment and frozen numeric fixture use scikit-learn 1.5.1;
the repository requirements pin 1.7.2. Verify the fixture and behavior under
the exact supported study environment before freeze. See the separate
methodology audit report for versioned source analysis.

Use Rubin pooling and the same estimand-specific within-imputation variances
as v4: sample variance divided by `n` for the mean; HC3 slope variance from
intercept-including OLS for the slope. Supply complete-data degrees of freedom
`n-1` and `n-2`, respectively, to the existing Barnard-Rubin pooling
implementation. Use two-sided 95% t intervals. Retain each completed-data
estimate and variance, pooled estimate, within/between/total variance,
standard error, degrees of freedom, interval endpoints, and failure reason.

### 4.2 Pre-run PMM implementation validation

Before any study run, write and pass deterministic unit tests for the frozen
PMM algorithm. Tests must verify:

- observed values are unchanged and only missing cells are filled;
- every PMM replacement is an actual observed donor value from the permitted
  bootstrap donor pool;
- parameter draws, donor distances, and selected donors follow the frozen
  algorithm on hand-constructed fixtures;
- identical input and seed reproduce identical completed datasets;
- distinct imputation streams are recorded and used, and output has exactly
  `m=20` finite complete datasets;
- `k` boundary behavior, insufficient donor rows, all-missing targets,
  constant predictors, and invalid/non-finite inputs either follow the
  pre-specified rule or fail explicitly;
- the same original mask is applied across methods, and the v4 slope-2 mask
  reproduces the recorded v4 mask for each real-data seed;
- a fixed small analytic/reference case confirms the PMM pooling inputs and
  Rubin interval calculations.

The exact fixtures, reference values, and test files are **TODO** and must be
specified or generated from frozen analytic definitions before the first
study run. A failing PMM test blocks execution; do not weaken tests after
seeing full-study results.

### 4.3 Pairing to v4

For each matching real-data dataset, mechanism, rate, strength-2 mask, trial,
and estimand, pair the new PMM outcome with the corresponding successful v4
`mice_proper`, `m=20`, `delta=0` row. Use exact dataset/trial/mask-seed keys.
Do not compare mismatched or regenerated masks. Report unmatched or failed
rows and their reasons; do not silently drop them from accounting.

### 4.4 Verified workload for the read-only v4 baseline

The configuration-driven, read-only audit in `rubin_study/workload.py`
computed `10 datasets × 3 mechanisms × 3 rates × 100 trials = 9,000`
configured mask replicates. It found 9,000 observed cells, no missing or
unexpected cells, and no inconsistent or missing mask seeds. Both configured
estimands (`mean`, `ols_slope`) were present for every successful
`mice_proper`, `m=20`, delta-zero comparison: 18,000 paired estimand rows and
zero missing pairs. The raw file contains 254,000 successful rows, including
252,000 configured masked-condition rows and 2,000 no-missing sanity rows.
This confirms that 900 is not the full v4 workload; it is an incorrect count
for this run configuration, not a basis for editing or rerunning v4.

The benchmark reuses the same `m=20` completed datasets for both estimands.
Therefore a full PMM extension at the same 9,000 mask cells implies up to
180,000 completed-data draws (9,000 × 20), corresponding to 18,000
estimand-level comparison rows. The audit reads v4 files only; it writes no
files under `experiments/results/`.

### 4.5 Uncertainty ablation (diagnostic only)

Implement and evaluate three separately named variants on otherwise matched
inputs. These are diagnostic ablations, not additional primary method
rankings:

- `posterior_only`: fit the observed target rows without bootstrap and draw
  regression coefficients from the fitted conditional Gaussian posterior.
  Predict missing target values from the sampled coefficients, with no
  residual-noise or donor draw. Randomness is coefficient sampling only.
- `bootstrap_only`: resample rows and refit the BayesianRidge imputer for each
  draw, with posterior predictive sampling disabled. Randomness is bootstrap
  row selection; no posterior coefficient draw is used.
- `bootstrap_pmm_candidate`: combine bootstrap refitting, a conditional
  coefficient draw, and PMM donor selection using the algorithm above.

Use independent `SeedSequence` entropy keys for every named random stream;
the manifest function and configuration define the mapping. Report bias,
estimate variance, finite-interval coverage, finite-interval width, and
failure rate with explicit denominators for each variant. Bootstrap
variation and coefficient-posterior variation are distinct implemented
sources; their combination is not presumed to be better calibrated.

## 5. C. MNAR sensitivity and oracle diagnostic

For MNAR conditions, run the pre-specified delta grid
`{-3, -2, -1, 0, 1, 2, 3}` in observed-`x2` standard-deviation units. After
imputation, add `delta * observed_SD(x2)` to imputed `x2` cells only; leave
observed values unchanged. Define `observed_SD(x2)` as the sample SD among
observed `x2` values for that replicate before imputation. If it is zero or
non-finite, retain a failed scenario and its reason.

Apply every delta to the three synthetic MI methods and to
`bootstrap_pmm_candidate` in the real-data extension. The v4 proper-method rows remain
the paired delta-zero comparator for the real-data extension.

For each MNAR replicate, additionally calculate the **oracle delta diagnostic**

`delta_oracle = (mean(x2_missing_truth) - mean(x2_observed)) / observed_SD(x2)`.

Apply the corresponding raw-unit shift to missing imputed `x2` cells and
report its metrics separately. This diagnostic uses the true values of
masked `x2`, is not available in real use, is not a usable method, is not part
of a primary method comparison, and must be labeled **ORACLE DIAGNOSTIC —
uses masked truth; not deployable** in every relevant output.

The delta grid and oracle diagnostic do not identify the MNAR mechanism and
do not establish that Rubin's Rules are valid under MNAR.

## 6. D. Mechanism-strength comparisons

The MAR and MNAR slope grid `{0.5, 1, 2}` applies to the synthetic study.
Strength `2` reproduces the v4 logistic mechanism at the same population
scaling and target missing rate. MCAR is run once per rate, not replicated
for each slope value. The strength-2 comparison is the primary reference;
slopes `0.5` and `1` are pre-specified sensitivity analyses. The real-data
extension is limited to strength `2` so its masks and paired comparator are
exactly the existing v4 conditions; no new real-data strengths are run under
this protocol.

## 7. E. Metrics, paired comparisons, and decision rules

### 7.1 Metrics

For every dataset/DGP, mechanism, rate, strength where applicable, estimand,
method, and delta where applicable, report:

- finite-interval empirical coverage (`covered valid finite intervals /
  valid finite intervals`), nominal 95%;
- failure rate (`failed runs + invalid intervals + undefined intervals /
  scheduled replicates`), with mutually exclusive failed-run,
  invalid-interval, and undefined-interval categories;
- all-scheduled operational success-adjusted coverage (`covered valid finite
  intervals / scheduled replicates`);
- mean interval width among valid finite intervals and its denominator;
- mean bias and **standardized bias**, defined as mean estimate-minus-truth
  across replicate seeds divided by the empirical SD of estimates across
  those seeds (undefined if that SD is zero);
- empirical SD of the estimate across seeds;
- the median and mean pooled standard error across seeds, each divided by the
  empirical SD of the estimate (`median_SE / empirical_SD` and
  `mean_SE / empirical_SD`);
- Rubin pooling diagnostics per replicate and cell: `W`, `B`, `T`, `SE`,
  Barnard-Rubin degrees of freedom, relative increase in variance
  `RIV = (1 + 1/m) * B / W`, fraction of missing information
  `FMI = (1 + 1/m) * B / T`, finite-imputation relative efficiency
  `RE = 1 / (1 + FMI/m)`, within-variance share `W/T`, and between-variance
  share `((1 + 1/m) * B)/T`. Define zero-variance edge cases explicitly and
  retain undefined values rather than silently substituting zero;
- interval failures, failed seeds, and the denominator used for every metric.

Report both the median and mean SE calibration ratios. Do not select one after
seeing the results. For single-imputation diagnostics, report their
single-completed-data standard errors separately and label them as such; they
are not pooled SEs.

For HC3 OLS slope analyses, `U` is the fitted HC3 sandwich variance from each
completed dataset and the complete-data degrees of freedom are the fitted
residual degrees of freedom. Reference-test the HC3 calculation and its
propagation into Rubin pooling. Barnard-Rubin degrees-of-freedom adjustment
does not by itself establish validity for robust HC3 inference; report this
as an empirical validation target, not a theoretical guarantee.

### 7.2 Primary comparisons (fixed in advance)

1. **Synthetic method contrasts:** at mechanism strength `2`, compare
   `mice_improper` with `mice_proper`, and `bootstrap_pmm_candidate` with
   `mice_proper`, within each DGP × mechanism × rate × estimand. Primary
   outcomes are coverage, interval width, standardized bias, and both SE/SD
   ratios.
2. **Synthetic mechanism-strength sensitivity:** for MAR and MNAR separately,
   report the same metrics at slopes `0.5` and `1` beside slope `2`, within
   each DGP × rate × estimand. These are sensitivity comparisons, not
   additional primary hypotheses.
3. **Real-data PMM contrast:** compare `bootstrap_pmm_candidate` with v4
   `mice_proper` at `m=20`, delta `0`, using the exactly paired
   dataset/trial/mask conditions. Report the same metrics by mechanism × rate
   × estimand.
4. **MNAR sensitivity:** for each MICE method, report coverage, width,
   standardized bias, and SE/SD across the seven fixed deltas, by mechanism
   strength × rate × estimand. Report the oracle diagnostic separately and
   never include it in deployable-method rankings.
5. **No-missing sanity gate:** apply the exact-binomial compatibility rule in
   Section 3.4 before interpreting the corresponding synthetic
   masked-condition comparisons.

For every DGP/dataset × mechanism × rate × estimand × method cell, report its
coverage, exact two-sided 95% Clopper-Pearson Monte Carlo interval, and
denominators. Method contrasts are replicate-paired differences in coverage
indicators on replicate pairs with valid finite intervals for both methods;
report excluded pairs and each method's operational failure rate separately.
For synthetic method contrasts, pair by DGP replicate and shared mask. For
real data, pair by dataset/trial/mask and report discordant paired coverage
counts. The real-data contrast also retains its specified equal-dataset
weighting and dataset-cluster bootstrap; bootstrap replicate count and seed
remain blocking **TODOs**. Do not average across cells unless aggregation
weights and the target population are justified and fixed before freeze.
Without a prespecified margin and multiplicity rule, report descriptive
paired differences only; do not claim a method is superior, equivalent, or
better.

Use nominal 95% intervals throughout. Report estimates and confidence
intervals; do not declare a method superior merely because a point estimate
is larger or a confidence interval excludes zero. No multiplicity-adjusted
confirmatory claim is planned; these are pre-specified comparative estimates.

### 7.3 Failure and interpretation rules

- Retain every scheduled seed, including failures, with failure stage, error,
  and reason. Never replace failed seeds.
- Report the number attempted, successful, failed, and analyzed for every
  cell. Report coverage denominators and missing/invalid intervals.
- Do not silently drop datasets, estimands, or cells. Any exclusions and
  reasons are reported alongside results.
- Do not change DGP parameters, imputation settings, `k`, iteration count,
  delta grid, mask, seed, or analysis rule after inspecting any study result.
- Any analysis not listed as primary above is labeled
  **EXPLORATORY (post-hoc, not pre-registered)**.
- The motivation observations in Section 1 remain exploratory regardless of
  subsequent results; Study 2 may be consistent or inconsistent with them.

## 8. F. Out of scope

The study excludes GAIN and other deep imputers, random-forest imputation,
classifier-accuracy tasks, forecasting, and logistic-regression estimands.
No new estimand, imputation method, primary endpoint, or post-hoc method
ranking may be added to the confirmatory results.

## 9. G. Seeds, output, run configuration, compute, and changelog

### 9.1 Seeds and pairing

**Real-data slope-2 seed schedule:** use the exact v4 `trial_seed`,
`mask_seed`, trial index, sampled rows, and mask for each matching condition.
The existing v4 deterministic schedule is:

`trial_seed = 42 + 100000 * dataset_registry_index + 1000 * trial`

`mask_seed = trial_seed + mechanism_index`, with v4 mechanism order MCAR,
MAR, MNAR. Reproduce v4's mask generation, including its calibrated logistic
intercept and safeguards. Store the actual seed and a stable hash of each
mask in the new run output; verify equality to the corresponding v4 mask
before accepting the paired comparison.

**Synthetic seed schedule:** use master seed `42`, trial indices `0..99`, and
independent deterministic streams for DGP sample generation, masking,
bootstrap resampling, BayesianRidge parameter draws, and PMM donor selection.
The exact stream derivation and condition-to-stream mapping are **TODO**.
Freeze it before implementation. Reuse a replicate's generated sample and
mask across methods; derive different streams for distinct method draws and
conditions without accidental reuse. Record the actual integer seeds or
SeedSequence entropy/spawn keys for every generated sample, mask, imputation,
bootstrap, parameter draw, and donor selection.

### 9.2 Output folders and run configuration

Each execution writes to a new
`experiments/results/rubin_study2_<tag>/` folder; `<tag>` is **TODO** and must
be fixed before execution. Never overwrite or write into v4 or
`rubin_coverage_full_v4_exploratory`.

Every run must save a machine-readable run configuration containing at
minimum:

- protocol version and SHA-256 of the exact frozen protocol file;
- Git commit containing that frozen protocol and Git commit containing the
  executed code;
- run tag, timestamp, environment/dependency versions, and command;
- dataset identifiers, population/source hashes, selected columns, truths,
  all DGP parameters, and analytic truth formulas;
- all rates, mechanisms, strengths, deltas, methods, `m`, PMM `k`, and
  iteration/parameter settings;
- seed schedule/version and all realized sample, mask, bootstrap, imputation,
  posterior-parameter, and PMM-donor seeds or spawn keys;
- planned, attempted, successful, and failed replicate counts and reasons;
- the sanity-gate status, validation-test results, and output file inventory.

Protocol SHA-256 and frozen Git commit are generated and recorded after the
TODOs are resolved and the protocol is frozen, and before the primary study
runner is written.
Executed-code commit is recorded in the run configuration before results are
analyzed.

### 9.3 Compute estimate and performance benchmark

Use the outcome-blind timing benchmark to derive a compute estimate before
the first study run. `experiments/benchmark_rubin_study.py` provides six
synthetic performance fixtures covering each DGP/mechanism family at 10% and
50% missingness. They are not the protocol DGP parameterization and produce
no coverage or method ranking. Each method/scenario is timed in an isolated
process; report seconds per imputation, analysis/pooling time, peak process
RSS, dependency versions, and scenario-level ranges. Any parallel wall-time
projection must state worker-efficiency assumptions and memory multiplication
method; unless actually executed, label it an estimate.

The active v5 design remains 100 replicates and therefore has
`3 DGPs * 7 mechanism settings * 3 rates * 100 = 6,300` sample/mask
replicates. With 3 methods and `m=20`, this implies up to 18,900
method-condition runs and 378,000 completed-data draws. The attachment's
63,000-condition scale corresponds to 1,000 replicates and is shown only as
an illustrative sensitivity projection; it does not change the active
configuration. Before any inferential study run, record the resource estimate
derived from the benchmark, including CPU-hours, wall-clock time, peak memory,
worker count, and storage. Resolve the accelerator decision before freeze.

### 9.4 Diagnostic implementation map

The implementation-validation layer has these bounded entry points:

- `experiments/rubin_study/diagnostics.py`:
  `exact_binomial_interval`, `summarize_no_missing_gate`,
  `variance_decomposition`, `summarize_pmm_donor_draws`,
  `true_conditional_mean`, `conditional_prediction_diagnostics`,
  `dgp_conditional_diagnostic`, and
  `paired_coverage_difference`.
- `experiments/rubin_study/study2_methods.py`:
  `impute_uncertainty_ablation(..., return_diagnostics=True)` records bounded
  per-imputation PMM summaries and optional capped detail rows. Donor distance
  is absolute conditional-prediction difference in target units, after
  predictor scaling fit within that draw's donor pool. Donor-copy and
  source-row reuse are distinct. Large distances are flagged above the
  within-draw `Q3 + 1.5 * IQR` fence. Donor-pool and conditional-model-fit
  failures have distinct exception stages.
- `experiments/rubin_study/evaluation.py`:
  `summarize_replicates` retains operational reliability and emits exact
  coverage intervals plus variance decomposition summaries.
- `experiments/rubin_study/reporting.py`:
  `summarize_by_cell`, `paired_coverage_summaries`, and `write_study_report`
  write cellwise tables, paired replicate records, diagnostic CSVs, and an
  exact-interval coverage plot without implicit cross-cell aggregation.
- `experiments/benchmark_rubin_study.py`:
  `build_performance_fixture`, `run_benchmark`, `estimate_workload`, and
  `write_benchmark_report` generate outcome-blind timing and extrapolation
  reports.
- Focused validation lives in `experiments/tests/test_study2_diagnostics.py`,
  `test_study2_methods.py`, and `test_rubin_study_imputers.py`. The execution
  layer must preserve raw replicate outputs and write summaries to a separate
  report/output location.

### 9.5 Changelog

| Date | Version | Change |
|---|---:|---|
| 2026-11-01 | 5 | Added the synthetic known-DGP study, real-data PMM extension, expanded MNAR delta and oracle diagnostic, mechanism-strength conditions, metrics, comparisons, validation requirements, and freeze/run requirements. No experiment was run and no v4 files, results, or code were changed. |
| 2026-11-01 | 5.1 | Replaced the broad no-missing range with an exact-binomial compatibility gate; specified paired cellwise coverage differences and expanded Rubin variance diagnostics; documented PMM/DGP diagnostics, report outputs, and outcome-blind performance benchmarking. No full study was run and no v4 files or results were changed. |

## 10. Blocking TODO checklist before protocol freeze

Resolve each item below in this file, review the complete specification, then
compute the protocol hash and commit the frozen protocol **before writing the
primary study runner or running any inferential experiment**:

- DGP parameter values and the positive-definiteness/non-degeneracy checks.
- PMM donor count `k`, intercept/prior treatment, feature scaling,
  constant-predictor handling, and chained-update random-stream allocation.
- Exact PMM validation fixtures/reference values and test files.
- Dataset-cluster bootstrap replicate count and seed; synthetic aggregate
  bootstrap procedure if any aggregate interval is planned.
- Synthetic seed-stream derivation and condition mapping.
- Run tag, compute estimate, worker count, memory/storage estimate, and
  accelerator decision.

Until this checklist is resolved and the file is frozen, no inferential Study
2 execution is authorized by this protocol. The diagnostic helpers and
outcome-blind benchmark are not inferential study executions.
