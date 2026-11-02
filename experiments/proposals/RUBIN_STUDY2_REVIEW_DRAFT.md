# Study 2: proposed protocol for review

**Status:** Review draft; superseded by `experiments/RUBIN_STUDY2_PROTOCOL.md`
and its methodology audit. The current validation helpers are not a full
study implementation; no experiment is authorized.  
**Protocol scope:** New synthetic known-DGP study and a paired real-data PMM
extension.  
**Protected baseline:** Rubin coverage v4 and its exploratory analysis,
including commit `e2c46187cdb4087ed725bd431e8e84a833a624c0`.  
**Primary question:** Under MCAR, MAR, and MNAR, do multiple-imputation
confidence intervals attain nominal 95% coverage, and how does proper versus
improper imputation affect coverage?

This is a new review draft. It does not amend v4 or the existing Study 2 draft.
No v4 source, protocol, result, or figure is to be edited or overwritten.
Study 2 code may be written only after this proposal is reviewed, all blocking
TODOs are resolved, and a final protocol is frozen and committed. No
experiment is authorized by this draft.

## 1. Research hypotheses and questions

### Confirmatory questions

1. For a known population estimand, does nominal 95% Rubin-pooled interval
   coverage differ from 95% under each missingness mechanism, missing rate,
   and DGP?
2. At the v4-equivalent logistic strength, does bootstrap-then-impute
   BayesianRidge MICE (`mice_proper`) have coverage closer to 95% than repeated
   posterior-sampling BayesianRidge MICE without bootstrap
   (`mice_improper`)?
3. Does the proposed bootstrap PMM candidate (`bootstrap_pmm_candidate`) change coverage,
   width, bias, or SE calibration relative to `mice_proper`?
4. How do mechanism strength and the prespecified MNAR delta shifts change
   these metrics?

### Directional hypotheses (not assumed results)

- **H1:** At mechanism strength 2, compare `mice_proper` and
  `mice_improper` separately in every prespecified cell. No direction or
  average effect across cells is assumed.
- **H2:** `bootstrap_pmm_candidate` may improve robustness to skewness or model
  misspecification versus `mice_proper`, but its coverage advantage is not
  assumed; any differences will be reported with uncertainty.
- **H3:** Increasing MAR/MNAR selection strength and missing rate may degrade
  coverage. MNAR delta shifts may move estimates and coverage but cannot, by
  themselves, identify the mechanism or guarantee nominal coverage.

The primary analysis is cellwise: report every prespecified
DGP × mechanism × missing-rate × estimand cell separately. No aggregate
“closer to 0.95 on average” contrast is specified. Any aggregate summary is
optional and may be added only through a protocol amendment made before
outcomes are inspected, with its weighting rule and interpretation fixed in
advance. Do not select weights or decision rules after seeing results.

No novelty claim is made. A literature review of MI properness, bootstrap MI,
PMM, MNAR sensitivity analysis, and coverage evaluation is required before
making any novelty or priority claim.

## 2. Protected v4 baseline and study scope

### v4 reproducibility baseline

Treat v4 as a read-only reference. It contains 10 OpenML-derived populations,
100 seeds per condition, MCAR/MAR/MNAR, missing rates 10%, 30%, and 50%,
median/KNN/improper MICE/proper bootstrap-then-impute MICE, mean and OLS-slope
estimands, and coverage, CI width, bias, and Monte Carlo uncertainty. The
exploratory analysis at commit `e2c4618` is committed and remains labelled
exploratory.

Study 2 must not rerun v4 or write to any v4 code, protocol, result, or figure
path. For the real-data PMM extension, consume the existing v4 records
read-only and pair only against exact matching v4 `m=20`, delta-zero,
strength-2 `mice_proper` results. Do not regenerate v4 masks or substitute
seeds. The original v4 `m=5` and `m=20` results remain part of the baseline;
the new PMM contrast is scoped to `m=20`.

### Study 2 scope

1. A synthetic study with known analytical truths, three DGP families, three
   missingness mechanisms, missing rates 10%, 30%, and 50%, and MAR/MNAR
   logistic slopes 0.5, 1, and 2.
2. Three MI methods: `mice_improper`, `mice_proper`, and the proposed
   `bootstrap_pmm_candidate`. The principal comparison uses `m=20`.
3. An MNAR pattern-mixture delta grid of `{-3, -2, -1, 0, 1, 2, 3}` observed-SD
   units, plus a clearly separated oracle simulation diagnostic.
4. A real-data PMM extension on the 10 v4 populations, using exact v4 sampling,
   masks, and seeds at strength 2, paired against existing v4
   `mice_proper` at `m=20`, delta 0.

Only the designated target variable is masked; auxiliary predictors remain
complete. This preserves comparability with v4 but does not assess settings
where multiple columns are simultaneously incomplete.

## 3. Synthetic DGPs, population truths, and what they test

Each synthetic row is independently sampled from one frozen population. Let
`X1` be the complete analysis predictor, `X2` the partially observed target,
and (where applicable) `X3` a complete auxiliary predictor. The two estimands
are the population mean `mu2 = E[X2]` and the population linear-projection
slope `beta_OLS = Cov(X1, X2) / Var(X1)` from an intercept-including
regression of `X2` on `X1`.

Analytical truths are computed from the generating parameters, never from a
finite simulated replicate. DGP parameter values are deliberately not fixed in
this review draft.

### DGP 1 — multivariate normal

Draw `(X1, X2, X3)` from a trivariate normal distribution with mean vector
`mu` and positive-definite covariance matrix `Sigma`.

- Mean truth: `mu2`.
- OLS slope truth: `Sigma_X1_X2 / Sigma_X1_X1`.
- Purpose: a regular, correctly specified linear-Gaussian reference case.
  Under MAR driven by complete `X1`/`X3`, the conditional distribution used by
  BayesianRidge is intended to be relatively well aligned. Differences here
  help identify uncertainty-estimation or finite-imputation issues separate
  from skewness and nonlinear outcome shape.

**TODO:** Freeze `mu`, `Sigma`, variable ordering, and positive-definiteness
and non-degeneracy tests.

### DGP 2 — skewed log-normal target

Draw independent `X1 ~ Normal(mu1, sigma1^2)`,
`X3 ~ Normal(mu3, sigma3^2)`, and `epsilon ~ Normal(0, sigma_e^2)`. Set
`X2 = exp(alpha + beta*X1 + gamma*X3 + epsilon)`.

Let
`M2 = exp(alpha + beta*mu1 + gamma*mu3 + 0.5*(beta^2*sigma1^2 +
gamma^2*sigma3^2 + sigma_e^2))`.

- Mean truth: `M2`.
- OLS slope truth: `beta * M2` (by independence and the normal moment
  generating function).
- Purpose: isolates positive skew and non-Gaussian conditional residual shape,
  testing whether normal conditional imputation and Rubin pooling are robust
  when the target is skewed. `X3` supplies an observed auxiliary predictor.

**TODO:** Freeze `mu1`, `mu3`, `sigma1`, `sigma3`, `alpha`, `beta`, `gamma`,
and `sigma_e`; require positive scales and finite, non-degenerate truths.

### DGP 3 — nonlinear quadratic relationship

Draw independent `X1 ~ Normal(0, sigma1^2)`,
`X3 ~ Normal(0, sigma3^2)`, and independent mean-zero errors
`epsilon ~ Normal(0, sigma_e^2)`. Set
`X2 = alpha + beta*X1 + gamma*(X1^2 - sigma1^2) + eta*X3 + epsilon`.

- Mean truth: `alpha`.
- OLS slope truth: `beta`, since the centered quadratic term is orthogonal to
  `X1` under the symmetric normal distribution and `X3` is independent.
- Purpose: isolates misspecification of a linear conditional imputation model
  when the true conditional mean contains curvature. `X3` is an observed
  auxiliary covariate.

**TODO:** Freeze `sigma1`, `sigma3`, `alpha`, `beta`, `gamma`, `eta`, and
`sigma_e`; require positive scales and nonzero `gamma`.

For DGP 1–3, retain `n=500`, matching the v4 study's nominal sample size.
Synthetic truths are superpopulation analytical truths; real-data extension
truths remain the v4 finite-population truths. Do not combine these targets
without labelling the distinction.

## 4. Samples, masks, and mechanism strength

### Replicates and pairing

Proposed synthetic sample size is **1,000 independent replicate indices
`0..999` per DGP and condition**, each with `n=500`. The first 100 indices are
the v4-scale reference subset, not an interim analysis. No optional stopping,
replacement seeds, or result-dependent extensions are permitted.

Use the same generated complete sample and same realized mask for every method
within a replicate-condition. For a given DGP and replicate, use independent
deterministic streams for sample generation, masking, bootstrap row draws,
BayesianRidge imputer draws, PMM coefficient draws, and PMM donor choices.
Record all seeds or `SeedSequence` entropy/spawn keys.

**TODO (blocking):** Freeze the exact stream derivation, whether common uniform
variates will be used to nest mask rates, and the condition-to-stream mapping.
Avoid accidental stream reuse. Real-data extension must use exact v4
`trial_seed`, `mask_seed`, sampled rows, and realized masks.

### Missingness

Mask only `X2`; keep `X1` and `X3` complete. Use target missing rates
`r in {0.10, 0.30, 0.50}`. Let `logistic(a) = 1/(1+exp(-clip(a,-35,35)))`.

- MCAR: `P(R_i=1) = r`, where `R_i=1` means `X2_i` is missing.
- MAR: `P(R_i=1) = logistic(s*z1_i + b)`.
- MNAR self-masking: `P(R_i=1) = logistic(s*z2_i + b)`.

For synthetic data, standardize the driver using the DGP's analytical
population mean and SD. For the v4 real-data extension, reuse the v4
full-eligible-population scaler. Calibrate `b` by deterministic bisection on
`[-30,30]` so the mean probability in the replicate equals the target rate;
then draw Bernoulli indicators from the recorded mask stream. Keep `X2` truth
available only to the simulator for MNAR mask generation and the oracle
diagnostic; never pass masked truth to an imputer or analysis.

MAR and MNAR strength values are `s in {0.5, 1, 2}`. Strength 2 is the
v4-equivalent baseline; 0.5 and 1 are sensitivity conditions. MCAR has no
slope-strength dimension. Preserve v4 safeguards for at least five observed
target values and at least one masked value; record any forced adjustment and
the realized rate.

**TODO:** Confirm v4 safeguard behavior is applicable to every proposed
synthetic condition and specify exact deterministic behavior when a safeguard
is triggered.

## 5. Imputation methods and exact PMM proposal

For each completed dataset, analyze the original `n=500` rows, not a bootstrap
sample. Do not average imputed cells before analyzing. Preserve observed cells
exactly.

### Existing methods

1. **`mice_improper`:** repeated BayesianRidge `IterativeImputer` with
   `sample_posterior=True`, `max_iter=10`, and `skip_complete=True`, fit to the
   same masked data for each draw with a distinct imputer seed and no
   bootstrap-resampled fit sample.
2. **`mice_proper`:** for each imputation independently resample `n` masked
   rows with replacement, fit the existing BayesianRidge iterative imputer to
   the bootstrap sample using `sample_posterior=True`, `max_iter=10`, and
   `skip_complete=True`, then impute the original masked rows. This is the v4
   bootstrap-then-impute candidate, not an assumption of universal validity.

Use `m=20` for the primary synthetic method comparison and real-data PMM
extension. Keep the existing v4 `m=5` and `m=20` outputs intact and available
as read-only baseline; do not rerun v4.

### `bootstrap_pmm_candidate` — proposed bootstrap PMM

The only incomplete column is `X2`; therefore, this design performs one
conditional update per imputation. It does not evaluate multi-column chained
convergence.

For each of `m=20` imputations:

1. Bootstrap `n` rows with replacement from the original masked dataset.
   Preserve row multiplicity; each duplicate bootstrap record is a separate
   donor candidate.
2. Let the donor/training pool be bootstrap rows with observed `X2`. Fail the
   replicate explicitly if it has fewer than `k=5` donor records. `X1` and
   `X3` are the predictors; include an explicit intercept column.
3. Standardize predictors using means and SDs computed on the bootstrap
   training rows for this draw. Drop exactly constant predictors for this fit;
   fail if no nonconstant predictor remains. Use the same frozen transform for
   original recipients and donor rows.
4. Fit `BayesianRidge(fit_intercept=False)` to the observed bootstrap `X2`
   using the explicit intercept column. Draw the joint coefficient vector
   from `Normal(coef_, sigma_)` per imputation using a distinct recorded RNG
   stream. The explicit intercept is part of `sigma_`; however, it receives
   the same shared empirical-Bayes coefficient prior as the other columns.
   Hold fitted empirical-Bayes hyperparameters fixed. This is coefficient
   uncertainty conditional on plug-in hyperparameters, not full Bayesian
   uncertainty propagation.
5. Compute predicted means for each original recipient with missing `X2` and
   each observed bootstrap donor using the same sampled coefficients. Select
   the `k=5` bootstrap donor records with smallest absolute distance between
   donor and recipient predicted means. Resolve exact distance ties by the
   recorded donor RNG. Select uniformly among the five and copy that donor's
   observed `X2` value exactly. Do not add residual noise or a delta during
   this step.
6. Restore all originally observed cells unchanged and retain the completed
   original `n` rows for analysis. Use a separate deterministic stream for
   bootstrap selection, coefficient draw, and donor selection.

Do not call this method statistically proper or fully Bayesian. The fixed
empirical-Bayes noise and coefficient precisions are not sampled from
hyperpriors. Interpret it as a prespecified candidate and report empirical
calibration, without assuming superiority.

The v4 metadata records scikit-learn 1.9.1; the current validation runtime is
1.5.1 and the repository requirements pin 1.7.2. Verify this exact algorithm
under the frozen environment before study execution. See the methodology
audit for the version-specific intercept analysis.

### Diagnostic uncertainty ablation (not a primary ranking)

Evaluate these independently identifiable variants on matched inputs:

1. `posterior_only`: fit the observed rows without bootstrap; sample
   coefficients and predict missing values, without residual or donor draws.
   Randomness enters only through the coefficient draw.
2. `bootstrap_only`: resample rows and refit the BayesianRidge imputer with
   posterior sampling disabled. Randomness enters through bootstrap rows.
3. `bootstrap_pmm_candidate`: combine bootstrap fitting, a coefficient draw,
   and PMM donor selection.

Use independent `SeedSequence([seed, draw, stream_id])` streams. Report bias,
estimate variance, finite-interval coverage and width, and failure rate with
denominators. Combining bootstrap and coefficient sampling is a diagnostic
whose calibration must be measured, not presumed.

## 6. MNAR sensitivity and oracle diagnostic

For MNAR conditions, apply deltas `{-3,-2,-1,0,1,2,3}` SD to imputed `X2`
values only. Define the scale as the sample SD of observed `X2` in the
replicate after masking and before imputation. Shift each missing-cell
imputation by `delta * observed_SD`; leave observed cells unchanged. Use the
same completed imputations for every delta. If the observed SD is zero or
non-finite, record the scenario failure; do not substitute a scale.

Report the seven prespecified deltas separately for all three MI methods,
with coverage, width, bias, and SE diagnostics. Delta zero is the
unadjusted reference.

Additionally compute an **ORACLE DIAGNOSTIC — uses masked truth; not
deployable** for synthetic MNAR only:

`delta_oracle = (mean(X2_missing_truth) - mean(X2_observed)) / observed_SD(X2)`.

Shift missing-cell imputations by this replicate-specific oracle amount and
report as a separate diagnostic table/plot. It uses unavailable truth, is not
a real-world method, is not included in method rankings or primary tests, and
does not identify the missingness mechanism.

## 7. Outcomes and mathematical definitions

For each method/replicate/estimand, retain every completed-data estimate
`Q_j` and its complete-data variance `U_j`.

- Mean: `Q_j = mean(X2)` and `U_j = sample_var(X2, ddof=1)/n`.
- OLS slope: `Q_j` is the intercept-including HC3 OLS slope of `X2 ~ X1`;
  `U_j` is the HC3 robust variance for that slope. Use complete-data degrees
  of freedom `df_com=n-1` for the mean and `df_com=n-2` for the slope.

Pool with Rubin's rules:

```
Q_bar = mean_j(Q_j)
W     = mean_j(U_j)
B     = sample_var_j(Q_j, ddof=1)
T     = W + (1 + 1/m) * B
SE    = sqrt(T)
RIV   = (1 + 1/m) * B / W       # relative increase in variance
FMI   = (1 + 1/m) * B / T       # fraction of missing information
RE_m  = 1 / (1 + FMI / m)       # approximate relative efficiency
Wfrac = W / T                   # within-imputation share of total variance
Bfrac = (1 + 1/m) * B / T       # between-imputation share of total variance
```

Use the Barnard-Rubin degrees-of-freedom adjustment and a two-sided 95%
Student-t interval. Here `Bfrac` equals `FMI`; report both the named diagnostic
and its variance contribution for clarity. If `W=0`, define `RIV` as infinity
when `B>0`, and as zero when `B=0`. If `T=0`, report `FMI`, `RE_m`,
`Wfrac`, and `Bfrac` as undefined and state the zero-variance condition;
retain the existing zero-width interval convention only if its coverage
behavior is explicitly tested. Freeze the exact pooling implementation and
independent fixed-reference values before execution. Unit tests must check
`W`, `B`, `T`, `SE`, `RIV`, `FMI`, `RE_m`, variance shares, and
Barnard-Rubin degrees of freedom against independently calculated expected
values, including zero and boundary cases.

The complete-data degrees of freedom and within-imputation variance form a
pair: validate the mean's `n-1` and OLS slope's `n-2` choices with fixed
reference tests. For HC3 slope variances, treat Barnard-Rubin pooling and
the `n-2` reference df as an approximation to be evaluated, not as a
theoretical guarantee. The no-missing slope sanity gate and the prespecified
coverage study must report whether this robust-variance/df combination is
calibrated in the tested conditions.

### Metrics (report per cell and per dataset/DGP)

1. Empirical coverage among valid finite intervals at nominal 95%
   (`covered finite intervals / valid finite intervals`), with a two-sided
   95% Clopper-Pearson exact binomial interval.
2. Mean CI width among finite intervals, and interval width distribution.
3. Mean bias `mean(Q_bar - truth)` and standardized bias
   `mean(Q_bar - truth) / SD(Q_bar)` across replicates; report undefined if
   the denominator is zero.
4. Empirical SD of `Q_bar`.
5. Mean and median pooled SE divided by empirical SD (`mean_SE/empirical_SD`,
   `median_SE/empirical_SD`); undefined if empirical SD is zero.
6. Failure rate over all scheduled replicates, with mutually exclusive
   failed-run, invalid-interval, and undefined-interval counts; report runtime
   and the denominator for every metric.
7. Relative increase in variance (`RIV`), fraction of missing information
   (`FMI`), approximate finite-`m` relative efficiency (`RE_m`), and the
   within- and between-imputation shares of total variance, as defined above.
8. Monte Carlo uncertainty for coverage and paired differences.

Report three separate quantities: coverage among valid finite intervals with
its exact binomial interval; failure rate (`failed + invalid + undefined /
all scheduled`); and all-scheduled operational success-adjusted coverage
(`covered finite / all scheduled`) with its exact binomial interval. Never
conceal failures by conditioning alone. State each denominator beside every
metric. Report width only for finite intervals and show its denominator.

## 8. Primary/secondary comparisons and statistical analysis plan

### Primary comparisons

At strength 2, for each DGP × mechanism × missing rate × estimand:

1. `mice_proper` versus `mice_improper`.
2. `bootstrap_pmm_candidate` versus `mice_proper`.

Coverage is the primary outcome. CI width, standardized bias, empirical SD,
mean/median SE calibration ratios, runtime, and failures are prespecified
secondary outcomes. Report all cell-level estimates; do not suppress a cell
because it is heterogeneous or unexpected.

For each method and cell, report exact binomial intervals for coverage as
specified above. For each method pair, retain replicate-level paired coverage
indicators and report the paired difference in all-scheduled
success-adjusted coverage, `mean(d_i)` where
`d_i = C_candidate,i - C_reference,i` and each `C` is 1 only for a covered
finite interval (failures, invalid intervals, and undefined intervals count
as 0). For `N` scheduled pairs, compute
`paired_MC_SE = sqrt(sum((d_i - mean(d))^2) / (N * (N - 1)))`.
Report both discordance directions and their counts, plus the descriptive
95% normal Monte Carlo interval (`mean(d) ± 1.96 × paired_MC_SE`) and label
it approximate.
Failures, invalid intervals, and undefined intervals count as uncovered for
this all-scheduled contrast; also report finite-interval conditional
comparisons separately with their denominators.

No absolute coverage-difference margin or multiplicity-controlled
superiority test is specified. Therefore, contrasts are descriptive: do not
claim a method is “superior,” “equivalent,” “better,” or more calibrated based
only on these differences or interval overlap. Any such confirmatory claim
would require an outcome-blind protocol amendment fixing the margin,
multiplicity procedure, and decision rule before outcomes are inspected.
Do not compute a weighted aggregate comparison unless that same amendment
prespecifies a scientifically justified weighting rule.

### Secondary and sensitivity comparisons

- MAR and MNAR slopes 0.5 and 1 versus strength 2, stratified by DGP, rate,
  and estimand.
- All seven MNAR deltas and the separate oracle diagnostic.
- Dataset-level heterogeneity and the paired real-data PMM extension.
- v4 context tables are read-only and explicitly labelled baseline; no new
  v4 analysis or rerun is authorized here.
- Any additional subgroup, tuning, or alternative estimator analysis is
  labelled **EXPLORATORY (post-hoc, not pre-registered)**.

### Uncertainty and pairing

- For each coverage proportion, report the exact two-sided 95%
  Clopper-Pearson interval and its numerator and denominator. For paired
  coverage differences, use the replicate-level paired outcomes, report both
  discordance directions and their counts, and calculate the paired MC SE and
  approximate interval defined above. These intervals describe Monte Carlo
  uncertainty; they are not hypothesis tests or evidence of equivalence.
- Real-data comparison: pair `bootstrap_pmm_candidate` to v4 `mice_proper` using
  dataset/trial/estimand/mechanism/rate/mask identity; compute within-dataset
  paired differences first and resample whole datasets as clusters for
  95% percentile bootstrap intervals. With 10 datasets, report the coarse
  cluster resolution and per-dataset results.
- Report per-DGP synthetic results. Do not treat the three intentionally
  selected DGP families as a random sample of all possible DGPs.
- Report dataset-specific results for all 10 real-data populations; headline
  summaries must state whether weighting is by replicate or equally by
  dataset.

**TODO (blocking):** Freeze real-data cluster bootstrap replicate count and
seed, the small-cluster interval method, the synthetic paired-difference
interval method, and any aggregate weighting before analysis.

### Interpretation rules

Coverage outside a prespecified tolerance is evidence of miscalibration in
that simulated condition, not proof of a universal MI failure. Coverage near
95% is not proof of validity outside the tested DGP/missingness conditions.
Use confidence intervals and failures, not point-estimate ranking alone.
Oracle results never support deployable recommendations.

## 9. Unit tests, validation gates, and implementation checks

No study run may begin until all pre-run gates pass and are committed.

### Unit tests

- Analytical DGP moments and truth formulas match independent symbolic or
  high-precision reference calculations.
- DGP covariance/scale constraints and finite truths are validated.
- Identical seed/configuration reproduces identical samples, masks, MI
  datasets, PMM parameter draws, and donor choices.
- Same sample/mask is used by all methods; mask hashes match across method
  arms; observed values are unchanged.
- Each PMM replacement is exactly one observed target value in the permitted
  bootstrap donor pool; donor multiplicities are respected.
- PMM selects the nearest `k=5` donor pool under frozen distances, resolves
  ties deterministically, produces finite completed data, and uses distinct
  recorded random streams.
- PMM failures for insufficient donors, all-missing targets, constants,
  invalid values, and singular/unstable fits are explicit and deterministic.
- Mean and HC3 slope estimates/variances match hand-calculated reference
  fixtures; Rubin pooling and Barnard-Rubin df/interval match fixed reference
  values, including zero-variance and undefined-interval edge cases.
- Delta shifts alter only missing target values by the expected raw-unit
  amount; oracle calculations use masked truth only in the simulator.
- Real-data PMM pairing verifies exact v4 sample/mask hashes and rejects
  mismatches rather than silently pairing them.

**TODO (blocking):** Name the test files and freeze deterministic fixtures,
expected values, tolerances, and supported dependency versions before
implementation.

### Validation gates

1. **Protocol freeze gate:** TODOs resolved; protocol SHA-256 and commit
   recorded before study code.
2. **Code/unit gate:** all tests pass, seeds and data schema validated, no
   changes to v4 files.
3. **No-missing sanity gate:** for each DGP × estimand, use all 1,000
   prespecified complete samples; use complete-data mean and HC3 slope
   intervals. Report exact coverage (`covered / valid finite intervals`),
   its two-sided 95% Clopper-Pearson interval, all-scheduled
   success-adjusted coverage, and failed/invalid/undefined counts. The gate
   passes only when all 1,000 scheduled intervals are finite and valid and
   the exact binomial interval contains 0.95. This interval is a diagnostic,
   not proof of calibrated coverage. A failed gate blocks calibrated-coverage
   claims for that DGP-estimand but does not erase results or trigger tuning.
   Do not modify a method, change seeds, or otherwise tune it to pass the gate;
   investigate changes only through a documented, outcome-blind protocol
   amendment and a separately identified run.
4. **Dry-run gate:** one small, prespecified smoke condition checks output
   schemas, runtime logging, and deterministic replay. It is not included as
   coverage evidence and cannot be used to tune parameters.
5. **Full-run gate:** run only after independent protocol/code review; record
   all scheduled, attempted, successful, failed, and analyzed replicates.

## 10. Confounders, limitations, and alternative explanations

Potential confounders and interpretive limits include:

- The three synthetic DGPs vary in distributional shape and conditional
  structure; differences cannot be attributed to one feature unless parameter
  contrasts isolate it.
- The target is the only masked column, predictors are complete, and all
  synthetic samples have `n=500`; results do not generalize automatically to
  multivariate missingness, small samples, or high-dimensional settings.
- Logistic intercept calibration targets expected rate within a replicate;
  realized rates vary and safeguards may perturb them.
- Proper bootstrap-then-impute and PMM differ in both imputation model and
  uncertainty procedure; PMM donor discreteness, bootstrap variation, and
  fixed empirical-Bayes hyperparameters are alternative explanations for
  differences.
- BayesianRidge conditional-model misspecification, finite `m`, HC3
  small-sample behavior, and the Barnard-Rubin approximation may each affect
  coverage.
- For MNAR, observed-data methods cannot identify the missingness mechanism;
  delta analysis depends on assumptions and oracle diagnostics use unavailable
  truth.
- Ten real datasets provide limited cluster-bootstrap resolution and are not
  a random sample of all populations. Report all per-dataset heterogeneity.
- Simulation coverage is conditional on the frozen populations, parameters,
  mechanisms, sample size, implementation, and failure rules.
- PMM coefficient draws condition on fitted empirical-Bayes hyperparameters;
  that may understate uncertainty. Its “proper” designation requires
  methodological review.
- Changing DGP parameter values after seeing results, selective failure
  exclusion, or comparisons with mismatched masks would invalidate
  confirmatory interpretation.

Alternative explanations for undercoverage include bias from model
misspecification or selection, underestimated within-imputation variance,
insufficient between-imputation variance, finite-imputation error, small
effective sample size, interval degrees-of-freedom approximation, or
informative method failures. Diagnostics should report bias, SE calibration,
width, and failures together rather than attributing coverage differences to
one cause.

## 11. Sample size, computational feasibility, and runtime estimate

With 1,000 independent replicates and true coverage 0.95, the binomial
Monte Carlo standard error is approximately
`sqrt(0.95*0.05/1000) = 0.0069` (about 0.0135 for a normal-approximation
95% half-width). At 100 replicates it is approximately 0.0218 (about 0.0427
half-width). These are planning calculations, not observed results. Paired
method differences may be more precise depending on discordance.

Proposed synthetic workload at `m=20`:

- 3 DGPs × (1 MCAR + 3 MAR strengths + 3 MNAR strengths) × 3 rates × 1,000
  replicates = 63,000 sample-mask conditions.
- 3 methods per condition = 189,000 method-condition runs.
- 20 imputations per run = 3,780,000 completed-data draws before MNAR
  sensitivity re-analysis.
- MNAR deltas reuse completed imputations; do not refit imputers for each
  delta. The read-only v4 run configuration defines 10 × 3 × 3 × 100 = 9,000
  mask cells. Raw inventory confirms all 9,000, no missing cells or
  inconsistent mask seeds, and 18,000 successful `mice_proper`, `m=20`,
  delta-zero estimand pairs. This is not a 900-cell full workload. With
  v4-style reuse of imputations across both estimands, the full real-data PMM
  extension requires up to 180,000 completed-data draws at `m=20`; paired
  summaries contain 18,000 estimand rows.

The total analysis fits and sensitivity outputs must be counted by the
implementation before execution. This workload may be computationally large.

**TODO (blocking):** Run only a separate, outcome-blind implementation
benchmark after the protocol is frozen and unit gates pass. Record expected
CPU-hours, wall time, worker count, peak memory, storage, hardware, and
benchmark condition. If infeasible, return to protocol review and freeze a
reduced design before any full experiment; never reduce conditions or seeds
mid-run or based on observed coverage. Runtime is not estimated here because
no benchmark has been run.

## 12. Reproducibility, outputs, and implementation sequence

All new outputs go to a new unique directory such as
`experiments/results/rubin_study2_<frozen-tag>/`. Never write under v4 or
`rubin_coverage_full_v4_exploratory`; never overwrite an existing run. Preserve
raw replicate-level records, including failed rows and reasons.

Before any run, save a machine-readable configuration with protocol version,
protocol SHA-256 and commit, code commit, run tag, timestamp, command,
dependency/hardware versions, DGP parameters and analytical truths, data
identifiers/hashes, condition counts, all methods/settings, seeds/spawn keys,
mask hashes, validation status, and planned output inventory. Record runtime,
memory, failures, and output hashes after execution. Keep v4 inputs read-only.

### Ordered implementation sequence

1. Methodological/literature review: assess PMM properness, DGP choices, and
   estimand/truth definitions; resolve all TODOs.
2. Review and freeze this protocol; record hash and commit before coding.
3. Implement analytical DGP generators, truth functions, deterministic seed
   streams, and mask generation in new Study 2 code only.
4. Implement PMM behind a separate method identifier; preserve v4 algorithms
   and interfaces.
5. Add unit tests and pass code/unit validation gates.
6. Validate read-only v4 pairing and exact mask/sample hashes for the real-data
   extension.
7. Perform dry-run and outcome-blind runtime benchmark; review feasibility.
8. Freeze code/configuration and run the complete prespecified study once;
   retain failures without replacement.
9. Analyze with the frozen plan; separate confirmatory results,
   sensitivity analyses, and exploratory follow-ups.
10. Archive raw data, environment/configuration, test evidence, scripts, and
    result checksums in the new Study 2 output directory. Any deviation
    requires a documented protocol amendment before affected results are
    inspected.

## 13. Blocking decisions for review

- **TODO 1:** Freeze each synthetic DGP's numerical parameters and verify
  positive-definite covariance, positive scales, nonzero curvature, and
  non-degenerate truths.
- **TODO 2:** Approve 1,000 synthetic replicates or choose another fixed
  count after considering the stated Monte Carlo precision and benchmark.
- **TODO 3:** Freeze all synthetic RNG stream derivations and rate-pairing
  strategy.
- **TODO 4:** Methodologist review of PMM posterior draw and whether the
  proposed method may be called “proper”; freeze BayesianRidge priors and
  implementation details.
- **TODO 5:** Confirm PMM donor `k=5`, scaling, constants, donor ties, and
  failure behavior.
- **TODO 6:** The primary analysis is cellwise and paired as specified in
  Sections 7–8; no aggregate weights, coverage-difference margin, or
  multiplicity-controlled claim are authorized. Any proposed confirmatory
  superiority/equivalence claim requires an outcome-blind amendment before
  results are inspected.
- **TODO 7:** Freeze dataset-cluster bootstrap repetitions/seed and small
  cluster interval method.
- **TODO 8:** Freeze sanity-gate sample streams, exact pooling reference
  fixtures and tolerances (including HC3 slope variance/df cases), test file
  locations, run tag, runtime budget, and resource limits.
- **TODO 9:** Complete literature review before any novelty or
  general-method claim.

Until these decisions are resolved, reviewed, and frozen, this document is a
proposal only: do not implement or execute Study 2 experiments.
