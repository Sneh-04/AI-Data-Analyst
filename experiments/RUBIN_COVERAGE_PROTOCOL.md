# Pre-registered Rubin's Rules coverage study

**Protocol version:** 4  
**Status:** version 4 pre-specification; no masked-condition study results exist.  
**Protocol date:** 2026-10-31  
**Research question:** Under MCAR, MAR, and MNAR, do nominal 95% confidence
intervals pooled with Rubin's Rules attain 95% repeated-mask coverage, and does
bootstrap-then-impute multiple imputation differ from the current repeated
`IterativeImputer(sample_posterior=True)` approach?

This protocol must be frozen before implementation or execution of the full
coverage study. The v3 no-missing sanity gate was run; its results remain on
record in `experiments/results/rubin_coverage_20261031T162217Z`. No
masked-condition results exist. Version 4 pre-specifies HC3 heteroskedasticity-
robust variance for OLS slopes and a new sanity-only rerun. Do not replace
failed seeds without retaining their failure records.

## 1. Scope and dataset eligibility

Consider only datasets in `experiments/datasets/registry.py`, with metadata
checked against `experiments/datasets/manifest.json` and cached-file SHA-256
verified by the registry loader. First omit rows with a missing registry
target. Eligible predictors are registry-metadata numeric, naturally complete
in that full target-observed cohort, and nonconstant. Preserve original feature
order. Count distinct values on this full eligible population before replicate
sampling or masking. Select `x1` and `x2` as the first two eligible columns,
in original order, that each have at least 10 distinct values. Exclude a
dataset without two such columns and record its reason. Keep all eligible
numeric columns as complete imputation predictors.

The >=10-distinct-value rule is an operational screen only; it does not prove
that a variable is continuous or interval-scaled. Numeric ordinal/category
codes may pass this threshold.

### Selected datasets and v3 analysis pairs

Counts and pair selection below use the full target-observed eligible
population and original feature order.

| Registry name | Eligible numeric predictors | Predictors with >=10 values | v3 x1 (distinct values) | v3 x2 (distinct values) |
|---|---:|---:|---|---|
| `adult` | 6 | 6 | `age` (74) | `fnlwgt` (28,523) |
| `bank-marketing` | 7 | 7 | `V1` (77) | `V6` (7,168) |
| `breast-w` | 8 | 7 | `Clump_Thickness` (10) | `Cell_Size_Uniformity` (10) |
| `credit-approval` | 4 | 4 | `A3` (215) | `A8` (132) |
| `credit-g` | 7 | 3 | `duration` (33) | `credit_amount` (921) |
| `diabetes` | 3 | 3 | `preg` (17) | `pedi` (517) |
| `heart-statlog` | 13 | 5 | `age` (41) | `resting_blood_pressure` (47) |
| `pc1` | 21 | 21 | `loc` (111) | `v(g)` (48) |
| `telco-customer-churn` | 3 | 2 | `tenure` (73) | `MonthlyCharges` (1,585) |
| `wine-quality-red` | 11 | 11 | `fixed_acidity` (96) | `volatile_acidity` (143) |

### Excluded datasets

| Registry name | Reason |
|---|---|
| `cylinder-bands` | Only `job_number` qualifies (262 distinct values); `unit_number` has 7, leaving fewer than two qualifying predictors. |
| `dermatology` | Zero naturally complete numeric predictors: its only numeric feature, `Age`, has 8 missing values in the cache. |
| `hepatitis` | Only one naturally complete numeric predictor qualifies (`AGE`, 49 distinct values). |
| `mushroom` | No numeric predictors in the registry metadata. |
| `soybean` | No numeric predictors in the registry metadata. |

These counts are from the currently tracked manifest and cache. Before running, verify
each selected cached dataset against its manifest hash and reapply the stated
eligibility rule to the loaded frame. If the manifest, cached data, actual
column order, or eligibility counts disagree, record the discrepancy and mark
the affected dataset as not run; do not silently substitute columns or datasets.
Use every eligible numeric predictor as an imputation predictor; no additional
column cap is applied. The only replication-row limit is the pre-specified
sample of `min(500, N)` rows with replacement.
The actual loaded complete-target row counts and final column lists are
**TODO: record in the run configuration before unmasking or analyzing results**.
The existing Protocol A minimum of 100 complete-target rows applies; if a
selected dataset falls below it, log and report the exclusion rather than
replacing it.

## 2. Population, replication sample, truth, and estimands

For each selected dataset, define the full eligible cohort as rows with a
nonmissing registry target and the naturally complete, nonconstant numeric
predictor columns identified above. Drop the registry target from the analysis
matrix. Treat this entire eligible cohort as the finite study population.
Compute and save the truths below from the full population before any sampling
or masking.

Let `x1` and `x2` be the first two eligible numeric predictor columns in
original dataset feature order that each have at least 10 distinct values in
the full eligible population. The primary estimands are:

1. **Column mean:** the arithmetic mean of `x2` over every row in the
   full eligible population. This full-population finite-population mean is
   the simulation truth.
2. **OLS coefficient:** the slope for `x1` in the intercept-including
   ordinary least squares model `x2 = beta0 + beta1*x1 + error`, fit to every
   row in the full eligible population. The full-population `beta1` is the
   simulation truth.

For every replicate, draw `n = min(500, N)` rows with replacement from the
full eligible population of size `N`, using that replicate's recorded
`trial_seed`. Reset the sampled frame's row index but retain duplicate sampled
rows: these are part of the bootstrap sample. Apply the mask only after
sampling. Inference targets the full-population truth, not the sampled-row
estimate. Save `x1`, `x2`, full-population truths, `N`, replicate `n`, and
column order in run metadata before masking. If full-population `x1` is
constant and the OLS slope is undefined, record that estimand as failed; do
not select another predictor based on results.

### Sanity-only gate

The benchmark must support `--sanity-only`, which runs only this condition:
all 10 selected datasets, exactly 100 pre-specified trials (indices 0..99),
the same `n = min(500, N)` with-replacement row sampling, no mask, `m=1`, and
the complete-data two-sided 95% Student-t interval for each estimand. For the
OLS slope use the HC3 robust variance with residual degrees of freedom `n - 2`;
for the mean retain the sample-variance-over-`n` variance. Compare each interval
with its full-population truth. For every dataset-estimand, report coverage
separately and label it `sanity-failed` if coverage is below 91% or above 99%.
Report sanity failures separately from masked-condition results. Do not tune
settings or select another column in response to a failure.

Under v4, rerun this same gate (all 10 datasets, 100 trials) in a new results
folder using `--tag sanity_v4`. Any dataset-estimand still outside 91–99% is
`sanity-failed`; report it in the sanity table, retain it in per-dataset
tables, and exclude that dataset-estimand from pooled headline tables. Make no
further estimator changes in response to the v4 gate.

## 3. Missingness mechanisms and rates

Only `x2` is masked. All other eligible numeric columns, including `x1`, stay
fully observed and serve as imputation predictors. The rate is the missing
fraction of `x2`, not a matrix-wide cell fraction. Standardize `x1` and `x2`
using `ObservedScaler` fit on the full population; use standardized values
only to form simulation probabilities. The sampled rows are masked only after
sampling. Complete values used by simulation to define truth or generate a
mask must not be passed as missing entries to the imputer or analysis.

Reuse `_calibrate_intercept` from `experiments/run_real_datasets.py` where
possible. For each sampled row `i`, with standardized values `z1[i]` and
`z2[i]`, define the probability that `x2` is missing as:

- **MCAR:** `p[i] = rate`.
- **MAR:** `p[i] = logistic(2 * z1[i] + b)`. Calibrate `b` by bisection on
  `[-30, 30]` so the mean probability is `rate`. `x1` is the fully observed
  driver distinct from `x2`.
- **MNAR (self-masking):** `p[i] = logistic(2 * z2[i] + b)`. Calibrate
  `b` by bisection on `[-30, 30]` so the mean probability is `rate`. The
  complete `x2` value is used only by the simulator to make this mask.

Here `logistic(a) = 1 / (1 + exp(-clip(a, -35, 35)))`, matching the current
calibration helper. Draw independent Bernoulli indicators with the recorded
mask seed. If fewer than five `x2` observations would remain, unmask seeded
random rows until five remain. If the draw masks no `x2` values, force one at
a seeded randomly selected row. Record realized `x2` missing fraction.
All non-`x2` predictors remain complete.

Use nominal missing rates **10%, 30%, and 50%**. Each dataset × mechanism ×
rate × seed receives one mask shared by all methods. There are at least 100
pre-specified seeds per cell. Use the fixed master seed `42`, trial indices
`0..99`, and the existing deterministic seed schedule:

`trial_seed = 42 + 100000 * dataset_registry_index + 1000 * trial`

where `dataset_registry_index` is the zero-based position in `DATASETS`
insertion order. Thus the same replicate's resampled rows are shared across
rates and mechanisms. The mask RNG seed is `trial_seed + mechanism_index`, with
mechanism order `MCAR`, `MAR`, `MNAR` (indices 0, 1, 2). Record every resulting
mask seed and every method-specific random seed in the raw results. For MICE
imputation draw `d` (zero-based), use `trial_seed + 100 + d` as the improper
variant's imputer seed. For bootstrap-then-impute draw `d`, use
`trial_seed + 100 + d` for row resampling and `trial_seed + 200 + d` for the
imputer. Median and KNN are deterministic and have no method random seed.
Additional seeds may be run only as a pre-declared extension applied to all
methods and conditions; they must not replace original failed seeds.

## 4. Imputation and inference methods

All methods use the same masked matrix for a given dataset, mechanism, rate,
and seed. Analyze the `x2` mean and the `x2 ~ x1` OLS slope from each
method's completed data. The implementation must preserve each completed
dataset for the analysis; averaging imputed cell values first and analyzing
one averaged frame is not multiple-imputation inference.

1. **Median fill:** single deterministic imputation using each column's
   observed-cell median.
2. **KNN:** single deterministic imputation using `KNNImputer(n_neighbors=5)`,
   matching the service's current KNN default.
3. **MICE improper (current approach):** produce `m` imputations by repeatedly
   fitting the existing BayesianRidge `IterativeImputer` with
   `sample_posterior=True`, `max_iter=10`, and `skip_complete=True` to the same
   masked sample, with distinct recorded draw seeds. This is the present
   `IterativeImputer` sampling approach under study; do not presume it captures
   between-imputation parameter uncertainty adequately.
4. **MICE proper candidate (bootstrap-then-impute):** independently resample
   `n` rows with replacement from the masked sample for each imputation, using
   a distinct recorded bootstrap seed. Fit the BayesianRidge chained imputer
   to that bootstrap sample, then use the fitted imputer to impute the
   **original masked sample**. Analyze the completed original `n` rows, not
   the bootstrap sample. Use `sample_posterior=True`, `max_iter=10`, and
   `skip_complete=True` to retain residual/imputation draws. This is the
   pre-specified bootstrap-then-impute candidate, not an assertion that this
   implementation is universally proper or valid.

For both MICE variants, use `m = 5` and `m = 20`. For each completed dataset
`j`, record the scalar estimate `Q[j]` and its complete-data model variance
`U[j]`:

- For the mean of `x2`, `U[j] = sample_variance(x2) / n` on that completed
  dataset.
- For the OLS slope, `U[j]` is the HC3 heteroskedasticity-robust covariance
  estimate for the `x1` slope, computed from intercept-including OLS. Retain
  residual degrees of freedom `n - 2` for Student-t critical values and as the
  complete-data degrees of freedom supplied to Barnard-Rubin pooling.

Pool each estimand with Rubin's Rules:

`Q_bar = mean(Q[j])`

`W = mean(U[j])`

`B = sample_variance(Q[j], ddof=1)`

`T = W + (1 + 1/m) * B`

`SE = sqrt(T)`

Use the implementation's Barnard-Rubin degrees-of-freedom adjustment and a
two-sided Student-t 95% interval. Keep `Q[j]`, `U[j]`, `Q_bar`, `W`, `B`, `T`,
degrees of freedom, interval endpoints, and any undefined-interval reason in
the raw output. No imputed-cell draw standard deviation may be substituted for
`U[j]`.

Median and KNN are single-imputation point-estimate baselines; they do not
support Rubin pooling. For the requested method comparison, report their
completed-data mean and OLS point estimates and **naive, single-completed-data
model-based 95% intervals** using the same mean and OLS variance formulas
above and the corresponding Student-t degrees of freedom (`n - 1` for the
mean, `n - 2` for the slope). Thus, use HC3 for the OLS slope variance in
MICE-pooled intervals, naive median/KNN intervals, and the no-missing sanity
interval; the mean variance is unchanged. Label single-imputation intervals
explicitly as naive, not Rubin-pooled or valid multiple-imputation intervals.
Do not claim that a difference in their coverage establishes validity of the
interval procedure.

The existing production `fill_missing_values(..., strategy="multiple")` returns
an averaged DataFrame and predictive draw spread, not the individual completed
datasets or estimand-specific `U[j]`. The experiment uses separate
per-imputation analysis and calls the shared `pool_rubins_rules` function
without changing the cleaning API. Its Barnard-Rubin calculation follows the
`mice::pool` definitions:

`lambda = (1 + 1/m) * B / T`

`df_old = (m - 1) / lambda^2`

`df_obs = (df_com + 1) / (df_com + 3) * df_com * (1 - lambda)`

Combine `df_old` and `df_obs` by their harmonic sum. For zero `lambda`,
`df_old` is infinite and the combined degrees of freedom equal `df_obs`; for
zero `df_obs`, the combined degrees of freedom are zero and no finite t-based
interval is defined unless total variance is also zero. Validate the result
against fixed reference values before running the coverage study.

## 5. MNAR pattern-mixture sensitivity analysis

For MNAR only, run five pre-specified delta scenarios for the primary outcome
`x2`: `delta in {-1.0, -0.5, 0, +0.5, +1.0}` standard deviations. Define the
scale for each mask as the sample standard deviation of observed `x2` values
after masking, before imputation. Add `delta * observed_SD(x2)` to the
imputed/missing `x2` cells only; leave observed cells unchanged. Apply each
delta to median, KNN, and both MICE methods so the sensitivity comparison is
paired. The zero-delta scenario is the unadjusted MNAR result. Record the
observed SD, delta in standardized units, and raw-unit shift.

If observed `x2` has zero or non-finite standard deviation, mark that scenario
failed with its reason. Delta adjustment is an explicit pattern-mixture
sensitivity assumption; it does not identify the MNAR mechanism, remove MNAR
bias, or make Rubin's Rules alone sufficient.

## 6. Repetitions, outcomes, and metrics

For each dataset × mechanism × rate × imputation count (where applicable) ×
method × estimand, schedule the 100 pre-specified seeds above. The five MNAR
delta settings form additional reported conditions. Methods share masks and
seeds. Report per-dataset coverage, and also a headline coverage pooled across
datasets for each mechanism × rate × method × estimand × applicable `m` and
delta. The headline proportion weights successful replications equally; report
the number of contributing datasets and a dataset-cluster bootstrap Monte
Carlo SE (resampling datasets as clusters, not treating every replication as
independent). Use 2,000 bootstrap replicates with replacement and seed 42. For
each replicate, resample the contributing dataset names, retain all successful
runs from each sampled dataset (including repeats when a dataset is drawn more
than once), and compute the replication-weighted coverage proportion. Report
the standard deviation of these bootstrap proportions; report it as undefined
when fewer than two datasets contribute. Also report the conventional
replication-level binomial Monte Carlo SE separately. Do not pool records across
datasets when computing a per-dataset coverage estimate. If failures leave
fewer than 100 successful analysis runs, report the cell as incomplete; do not
replace failed seeds.

Report, for each condition and estimand:

- **95% interval coverage:** fraction of successful seeds whose interval
  contains the full-population truth. An interval with non-finite endpoints or
  undefined degrees of freedom is not a covering interval; count it as a
  non-covering run and report its count separately. The coverage denominator
  is all successful analysis runs in that condition, including these
  non-covering runs.
- **Mean interval width:** arithmetic mean of upper minus lower endpoint for
  finite intervals; report interval availability/count alongside it.
- **Bias:** mean of the per-seed method estimate minus the full-population truth.
- **Monte Carlo SE of coverage:** `sqrt(phat * (1 - phat) / R)`, where `R`
  is the coverage denominator above for that exact condition. Also report
  attempted and failed seed counts so this denominator is unambiguous. If
  there are fewer than 100 successful analysis runs, mark the cell
  underpowered/incomplete; do not silently describe it as a 100-seed result.

Keep mean and OLS-slope metrics in their natural units. Also retain raw per-seed
records and full interval endpoints so summaries can be independently
recomputed. Report the no-missing sanity coverage by dataset and estimand,
including the pre-specified 91–99% `sanity-failed` flag in a separate
`sanity_summary.csv`. Do not report simulated results,
coverage estimates, or nominal coverage success until the protocol
implementation has actually been run.

## 7. Failure handling, reproducibility, and freeze rules

- Write a run configuration before execution containing protocol version/hash,
  dataset registry names and manifest hashes, loaded row/column counts,
  selected feature names, estimands/truths, all rates/mechanisms, `m` values,
  method parameters, deltas, software versions, master seed, and the complete
  deterministic seed schedule.
- Persist one raw status record per attempted dataset-condition-method-seed,
  including failures, exception type/message, stage, attempt number, elapsed
  time, mask seed, imputation/bootstrap seeds, observed `x2` standard
  deviation, and realized mask rate. Failed runs must also appear in
  `failures.csv` and the final report with their denominator consequences.
  Failed raw rows are not considered completed when resuming; a later successful
  rerun remains a separate append-only row. Do not discard failed records.
- Do not retry a failed seed as a replacement. A diagnostic rerun may use the
  same seed after a documented code fix, but retain the original failed record
  and link the rerun to it. Do not alter methods or thresholds in response to
  observed coverage.
- Do not use benchmark outcomes to change this protocol. Any change required
  before execution must increment the protocol version and be documented before
  the revised experiment is run. Exploratory deviations must be labeled as
  such, separate from the pre-registered analysis.
- Output directories use `experiments/results/rubin_coverage_<tag>/`; the
  benchmark writes a run configuration, environment snapshot, append-only
  `raw.csv`, separate `failures.csv`, and `sanity_summary.csv`. Results can
  resume by skipping completed run keys; never edit prior raw rows.
- The raw schema stores population/sample sizes, chosen columns, seeds, realized
  missing rate, truth, estimate, per-imputation variances, pooled quantities,
  interval endpoints, status, and runtime.
- The table generator writes per-dataset, pooled headline, width, bias, MNAR
  delta, and no-missing sanity tables in CSV, Markdown, and LaTeX.

## 8. Changelog

- **Version 4 (v3 -> v4):** the trigger was the v3 `--sanity-only` gate in
  `experiments/results/rubin_coverage_20261031T162217Z`: 4 of 20
  dataset-estimands were outside 91–99%, all OLS slopes (`pc1` 0.59,
  `credit-approval` 0.79, `credit-g` 0.86, and `bank-marketing` 0.90);
  all 10 mean estimands passed, with coverage from 0.92 to 0.97. These v3
  results remain on record. No masked-condition results exist or were used.
- **Version 4:** as a post-hoc analytic decision made after observing the v3
  gate, replaced the classical homoskedastic OLS slope variance with the HC3
  heteroskedasticity-robust variance. Apply it uniformly across all 10
  datasets and all methods that report OLS intervals: Rubin-pooled MICE,
  naive median/KNN, and no-missing sanity. Retain `n - 2` residual df for
  Student-t critical values and Barnard-Rubin complete-data df; the mean
  variance is unchanged. No dataset, column, threshold, seed, or imputation
  method changed.
- **Version 4:** pre-specified rerunning the same 100-trial, 10-dataset
  `--sanity-only` gate in the new `rubin_coverage_sanity_v4` output folder.
  Any dataset-estimand still outside 91–99% remains `sanity-failed`, is
  reported separately, stays in per-dataset tables, and is excluded from
  pooled headline tables using the no-missing status from that same `raw.csv`.
  No further estimator changes will be made in response to the v4 gate.
- **Version 3 (v2 -> v3):** imposed the >=10-distinct-value rule on `x1` and
  `x2`, selecting the first two qualifying eligible columns in original
  order. The trigger was the pilot observation during variable-type
  inspection that heart-statlog's prior `x2` (`sex`) is binary-coded; no
  masked-condition coverage results were used to choose the rule. No
  full-study results exist.
- **Version 3:** changed the cohort from 11 to 10 datasets: dropped
  `cylinder-bands` because only one predictor qualifies; changed heart-statlog
  `x2` to `resting_blood_pressure`; changed the telco pair to `tenure` and
  `MonthlyCharges`; the other eight pairs remain unchanged.
- **Version 3:** added the `--sanity-only` 100-trial, all-selected-dataset,
  no-mask, `m=1` gate and the separate `sanity-failed` label for coverage
  outside 91–99%; settings and columns may not be tuned in response.
- **Version 3:** the pilot's no-missing sanity coverage was observed, but it
  was not used to choose or tune the 91–99% sanity rule.
- **Version 3:** removed the `int(100*rate)` term from the replicate seed
  formula so replicate sample selection remains consistent across missingness
  rates. The resulting implementation formula is
  `trial_seed = 42 + 100000 * dataset_registry_index + 1000 * trial`.
- **Version 3:** corrected dermatology eligibility to zero naturally complete
  numeric predictors because cached `Age` has 8 missing values.
- **Version 3:** documented that the cardinality threshold is operational,
  breast-w's ordinal 1–10 inputs are still treated as numeric, and the
  10-dataset cluster bootstrap SE is unstable with only 10 dataset clusters.

- **Version 2:** changed truth from a fixed analyzed cohort to the full eligible
  dataset population; each replicate now samples `min(500, N)` population rows
  with replacement before masking.
- **Version 2:** added a no-missing `m=1` complete-data Student-t sanity
  condition with per-dataset/estimand coverage and a 91–99% flag.
- **Version 2:** specified bootstrap-then-impute as fitting on a bootstrap of
  the masked data but imputing and analyzing the original masked rows.
- **Version 2:** restricted masking to `x2`; defined rates as x2's missing
  fraction, MAR's driver as fully observed `x1`, MNAR as self-masking on `x2`,
  and retained other eligible numeric columns as complete predictors.
- **Version 2:** added a replication-weighted headline coverage table across
  datasets and required dataset-cluster uncertainty alongside per-dataset
  summaries; the cluster bootstrap uses 2,000 replicates with seed 42, resamples
  datasets with replacement, and retains all runs from each sampled dataset.
- **Version 2:** replaced the previous pooling degrees-of-freedom adjustment
  with `mice::pool`'s lambda, old/observed df, and harmonic-combination
  formulas; tests use hardcoded reference values.
- **Version 2:** removed row subsampling/capping of the eligible population;
  the fixed replicate sample size is now `min(500, N)` and no extra eligible
  feature-column cap is applied.
- **Version 2:** specified raw failure rows plus a separate `failures.csv`,
  retaining attempt details and observed `x2` standard deviation; failed raw
  rows do not count as completed keys when resuming.
- **Version 2:** corrected the section numbering after consolidating the run
  outputs and failure-handling rules.
- **Version 2:** clarified the v1 pilot as superseded and excluded from v2
  analysis. No full v2 study has been run.

## 9. Interpretation boundary

MCAR, MAR, and MNAR labels describe the simulated mask-generation process;
they are not inferred from real-world data. MAR results depend on the stated
fully observed driver and calibrated logistic rule. MNAR results depend on the
self-masking rule and delta assumptions. A 95% interval's empirical coverage
must be measured over the pre-specified repeated masks; it cannot be claimed
from the formula or from successful code execution alone. Predictive
uncertainty for missing cell values and inferential uncertainty for the mean
or OLS coefficient are distinct and must not be conflated. The >=10-distinct-
value rule is only an operational cardinality screen: breast-w's ordinal 1–10
variables qualify and are treated as numeric in these analyses. The selected
cohort has 10 datasets, so dataset-cluster bootstrap standard errors are
unstable with only 10 clusters.
