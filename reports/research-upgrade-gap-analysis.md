# Research Upgrade Integration-Gap Analysis

## Scope and evidence limits

Compared all 19 relative paths classified as “present in both but different” in
[`research-upgrade-comparison.md`](./research-upgrade-comparison.md), using read-only unified diffs and source inspection of both trees:

- Original: `/Users/pawankumar/Downloads/ai-data-analyst-platform`
- Research copy: `/Users/pawankumar/Downloads/research-upgrade-files`

No application files were edited, copied, moved, or overwritten. No service was
started, database accessed, migration run, or benchmark/test command executed
for this comparison. The findings below are based on static source and test
inspection only; runtime behavior and the reproducibility/statistical validity
of previously saved benchmark results are not newly verified.

## Executive summary

The research versions are not safe wholesale replacements. In particular:

1. The research `DatasetController` removes ownership checks from dataset
   routes, removes the health-score-history route and its history persistence,
   and suppresses persistence errors.
2. Research versions of the three frontend pages remove dataset-persistence
   guards. `Overview.jsx` additionally removes score-history retrieval/display
   and custom-weight/debounce/error protections; `Forecasting.jsx` hardcodes a
   selection-metric claim that the service can no longer guarantee.
3. Research `ForecastRequest` weakens model and horizon validation. Research
   forecasting also removes input/metric guards and rounds MASE before using it
   to select a model; its frequency inference has less sub-daily coverage.
4. Research health scoring removes custom-weight validation and stops handling
   pandas `string` dtype columns in sentinel and consistency checks.
5. Research cleaning retains the broad feature-aware imputation idea already
   implemented in the original, but changes the private
   `_multiple_impute_dataframe` return shape and silently catches any error.
   Copying it would conflict with current experiments/tests expecting the
   original return contract.
6. Research `experiments/common.py` writes benchmark outputs directly into
   `experiments/results/`; the original's supplementary suite defaults to a
   unique temporary output directory and honors `AI_DATA_ANALYST_RESULTS_DIR`.
7. Several useful v2 research experiment ideas are already in the original
   under `*_research_benchmark.py` names, with the original's safer result
   handling. The upgrade's MNAR script also imports a helper interface that
   does not match the original's legacy `imputation_benchmark.py`.
8. Research tests remove regression coverage present in the original test
   files, and its pytest config broadly suppresses warnings.

## File-by-file review

### 1. `backend/src/main/java/com/aidataanalyst/controller/DatasetController.java`

**Recommendation: KEEP ORIGINAL. Highest priority; do not copy the research version.**

- **Research change:** Replaces the injected `DatasetAccessService`,
  `DatasetHealthScoreRepository`, and `DatasetHealthScorePersistenceService`
  dependencies with `DatasetRepository`; removes `Authentication` parameters
  on several handlers; deletes `GET /{id}/health-score/history`; changes
  health-score persistence to update `Dataset.healthScore` only; and wraps
  forecast/chat persistence in broad catches that return success despite
  failed persistence. Research comments also describe some behavior as TODO or
  “real implementation would also” be required.
- **Already present in original:** Original
  [`DatasetController.java`](../backend/src/main/java/com/aidataanalyst/controller/DatasetController.java)
  uses `DatasetAccessService.requireOwnedDataset(...)` for cleaning, health,
  history, forecast, insights, chat, records, versions, restore, and reports.
  It validates health response score/grade before calling
  `DatasetHealthScorePersistenceService.recordAssessment(...)`, serves the
  history endpoint from `DatasetHealthScoreRepository`, and records versions,
  forecasts, and chats through existing persistence services.
- **Missing from original:** No useful research feature identified that is
  missing from the original controller. Research score-trend input is already
  supplied from the latest persisted health history (falling back to the
  dataset's score) in the original handler.
- **Wholesale-copy risk:** **Critical.** It bypasses per-dataset ownership
  checks on multiple routes (including data reads and mutations), removes the
  history route expected by
  [`datasetApi.healthScoreHistory`](../frontend/src/api/client.js), no longer
  records each health assessment, may silently fail persistence, and changes
  handler constructor dependencies. Authentication may still be required at
  the Spring Security layer, but that is not a substitute for checking that
  the authenticated user owns this specific dataset.
- **Evidence references:** Original `clean`, `healthScore`,
  `healthScoreHistory`, `forecast`, `records`, `versions`, `restore`, and
  `generateReport`; `DatasetAccessService.requireOwnedDataset`;
  `DatasetHealthScorePersistenceService.recordAssessment`. The research class
  removes or alters those call paths.

### 2. `frontend/src/pages/Cleaning.jsx`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Removes the early guard that prevents cleaning a
  browser-only dataset without a persisted `datasetId`; changes the multiple
  imputation label and describes uncertainty as a direct reliability
  indicator.
- **Already present in original:** The original page already renders the
  repair log, truncation indicator, summary, versions, and restore controls.
  It sends `{ records, strategy, remove_duplicates, outlier_method }` using
  `datasetApi.clean`, matching the existing ML cleaning request shape. It also
  explicitly explains that between-imputation spread is not a calibrated
  prediction interval.
- **Missing from original:** No functional research change identified. The
  research wording that treats larger spread as direct reliability is more
  assertive than the original's caution and is not justified by a UI-only
  change.
- **Wholesale-copy risk:** The missing `datasetId` guard permits a request
  such as `/datasets/null/clean` for an unpersisted dataset; it can never use
  the backend ownership/versioning path successfully. Research's uncertainty
  text also risks implying calibration the UI cannot establish.
- **Evidence references:** Original `Cleaning`, `runCleaning`, `loadVersions`,
  `datasetApi.clean`, and `setRecords`; repair-log rendering reads
  `repair_log` and `repair_log_truncated`.

### 3. `frontend/src/pages/Forecasting.jsx`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Removes the persisted-dataset guard, changes the
  “auto” label, and replaces conditional selection-metric handling with a
  fixed “lowest average MASE wins” statement.
- **Already present in original:** The original page already submits the
  selected model/date/value/horizon, renders `forecast`, model comparisons,
  metadata, and displays the backend-provided `selection_metric` or
  `selection_message`.
- **Missing from original:** No useful UI capability identified as missing.
- **Wholesale-copy risk:** Without the guard, an unpersisted dataset attempts
  a backend forecast with a missing ID. The hardcoded MASE statement is
  incompatible with cases where the backend reports no valid selection
  metric/message; it could state model selection occurred when it did not.
- **Evidence references:** Original `Forecasting`, `run`, `datasetApi.forecast`,
  and conditional `result.selection_metric` / `result.selection_message`
  rendering.

### 4. `frontend/src/pages/Overview.jsx`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Removes `scoreHistory`, stops fetching and displaying
  history, removes the dataset-ID guard, recomputes immediately without the
  300ms debounce or custom-weight-sum guard, does not clear prior errors at
  request start, simplifies error extraction, replaces `Number.isFinite`
  guarding with `parseFloat(value) || 0`, and accesses `health.issues` without
  the original fallback.
- **Already present in original:** Original `recomputeHealth` calls
  `datasetApi.healthScore`, then `datasetApi.healthScoreHistory`; the
  controller supports both. It validates weights before requesting and
  displays score history. Health payload and display fields already include
  sentinel counts, trend, MNAR signals, and issues.
- **Missing from original:** No feature-level improvement identified. The
  original's stricter finite-number handling, weight check, debouncing,
  request error handling, and history display are useful protections.
- **Wholesale-copy risk:** Removes a feature wired to the existing backend
  history route; may issue invalid/unowned-dataset requests; can send invalid
  custom weights; can create repeated score-history rows through rapid
  requests; and loses defensive handling of absent `issues` and structured
  error messages.
- **Evidence references:** Original `Overview`, `recomputeHealth`,
  `useEffect`, `handleWeightChange`, `scoreHistory`, and the client methods
  `healthScore` / `healthScoreHistory`.

### 5. `ml-service/app/models/schemas.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Changes `ForecastRequest.model` from a `Literal` enum to
  unrestricted `str` and removes `ge=1, le=365` validation from `periods`.
  Its description lists a different, incomplete model set (including
  `prophet`, which is not a supported candidate in the current service).
- **Already present in original:** Original supports the UI's `auto`, `naive`,
  `seasonal_naive`, `holt`, `arima`, `sarima`, and `ensemble` values and bounds
  periods to 1–365. `DatasetPayload.records`, `CleaningRequest`, and the other
  request models already match the original frontend/backend contract.
- **Missing from original:** No validated new model support: the research
  schema's `prophet` description does not itself add a Prophet implementation.
- **Wholesale-copy risk:** Invalid model strings and excessive/zero/negative
  horizons pass request validation into service execution, where errors or
  unbounded resource use can occur. The model description can advertise an
  unsupported value to callers.
- **Evidence references:** Original `ForecastRequest`, `periods`,
  `model: Literal[...]`; research `ForecastRequest` accepts `model: str`.

### 6. `ml-service/app/services/cleaning_service.py`

**Recommendation: KEEP ORIGINAL; consider only explicitly reviewed, tested algorithm changes later.**

- **Research change:** Changes `_multiple_impute_dataframe` to accept only a
  numeric frame plus `max_iter`, and return uncertainty as a DataFrame rather
  than a per-column/index dictionary. Its `fill_missing_values` adds a
  broad `except Exception` around feature-aware imputation and silently falls
  back to marginal imputation. It also changes some fallback and record-log
  implementation details.
- **Already present in original:** Original already implements feature-aware
  stochastic `IterativeImputer` with posterior sampling, observed-value
  preservation, finite-output validation, an input-size cap, a marginal
  fallback when feature-aware imputation is unsuitable, categorical mode
  imputation, KNN handling that excludes all-missing columns, and per-cell
  repair logs with uncertainty. The public
  `fill_missing_values(df, strategy, custom_strategies, random_state)` still
  returns `(cleaned_df, repair_log)` in both versions, which is what the
  cleaning router consumes.
- **Missing from original:** The research copy exposes `max_iter` on its
  private DataFrame helper and changes that helper's uncertainty result to a
  DataFrame. That is not an app API improvement; it conflicts with current
  callers. Its explanatory docstring is not a code feature.
- **Wholesale-copy risk:** The public endpoint contract may appear unchanged,
  but replacing the implementation changes a private helper used directly by
  the original's `experiments/imputation_research_benchmark.py` and tests:
  those expect the dict-style uncertainty result. The broad catch can hide
  programming/data errors as a successful fallback. Research tests also omit
  an original regression test for all-missing numeric columns and pandas
  string-category imputation.
- **Evidence references:** Original `_multiple_impute_dataframe`,
  `fill_missing_values`, `_MICE_MAX_CELLS`, KNN `usable_cols`, and
  `test_knn_preserves_unfillable_numeric_column_and_imputes_string_dtype`;
  research `_multiple_impute_dataframe(...)->tuple[pd.DataFrame,pd.DataFrame]`
  and broad fallback in `fill_missing_values`.

### 7. `ml-service/app/services/forecasting_service.py`

**Recommendation: KEEP ORIGINAL. Do not cherry-pick the research file wholesale.**

- **Research change:** Adds/clarifies spacing-based period inference and
  first-difference seasonality features, changes the auto-selection
  implementation, removes validation in `_prep_series`, `_mase`, and
  `run_forecast`, no longer errors when automatic backtest splits are absent,
  and drops `selection_metric` / `selection_message` from its response.
- **Already present in original:** Original already infers daily, weekly,
  monthly, quarterly, annual, hourly, and regular sub-daily cycles; binds the
  inferred period into seasonal candidates; includes rolling-origin
  backtesting, candidate shortlisting, MASE-based selection, constant-series
  handling, metadata, and response fields used by the frontend.
- **Useful research change missing from original:** Its comments identify the
  reason to evaluate seasonality on first differences rather than raw levels
  (trend can produce spurious autocorrelation). The original's current
  `_compute_meta_features` path should be retained unless a focused test
  demonstrates a missed case and the change is reconciled with its scoring
  logic. The research period implementation itself is less complete for
  high-frequency data: it returns 24 for all spacing below 0.1 days, rather
  than deriving 12 for 2-hour data, 48 for 30-minute, and 96 for 15-minute
  data.
- **Wholesale-copy risk:** Research `_prep_series` silently drops invalid
  dates/values and duplicate timestamps rather than rejecting invalid
  nonblank input; `_mase` loses shape/finiteness checks; it rounds candidate
  MASE to four decimals before selection, so close candidates can tie or be
  mis-ranked; if no backtest split/scorable candidate exists, it can still
  return a naive forecast without an explicit “no selection” marker. The
  research output removes fields the original UI explicitly handles. Model
  schema validation would also be weakened if its paired schemas file were
  copied.
- **Evidence references:** Original `_prep_series`, `_mase`,
  `_infer_seasonal_period`, `_rolling_origin_splits`, `_compute_meta_features`,
  `_shortlist_candidates`, `_bind_period`, and `run_forecast`; original
  tests `test_mase_rejects_unscorable_or_misaligned_inputs`,
  `test_auto_forecast_does_not_claim_selection_without_backtest_splits`,
  `test_constant_series_uses_naive_without_claiming_an_unscorable_mase_selection`,
  `test_model_selection_uses_unrounded_mase_scores`, and
  `test_forecast_rejects_invalid_values_and_duplicate_timestamps`.

### 8. `ml-service/app/services/health_service.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Clarifies numeric sentinel range handling, changes
  prior-score docstring to refer to a prior dataset version, and removes
  explicit checks that custom weights contain exactly the expected keys and
  are finite/non-negative. Its missingness and consistency loops select only
  `object` columns rather than `object` and pandas `string` columns.
- **Already present in original:** Numeric sentinels are already counted only
  when outside the surrounding value range. Original also detects string
  sentinels, supports `previous_score` trend output, and accepts the weights
  payload used by the frontend.
- **Useful research change missing from original:** None established by the
  code delta. The explanatory comments mostly document logic already in the
  original.
- **Wholesale-copy risk:** Negative, non-finite, unexpected-key, or malformed
  weights may evade the intended validation (depending on values/operations);
  pandas `StringDtype` columns can be omitted from sentinel and consistency
  checks. This regresses coverage explicitly present in
  `test_string_dtype_sentinels_are_included_in_missingness` and
  `test_invalid_health_weight_shapes_and_values_are_rejected`.
- **Evidence references:** Original `_numeric_sentinel_count`,
  `calculate_health_score`, `select_dtypes(include=["object", "string"])`,
  and weight validation; corresponding research loops use only `object`.

### 9. `.gitignore`

**Recommendation: MERGE SPECIFIC CHANGES (ignore patterns only, not a wholesale file replacement).**

- **Research change:** Adds general Python exclusions for
  `**/__pycache__/`, `.venv/`, and `.pytest_cache/`.
- **Already present in original:** The original ignores `ml-service` Python
  caches/venvs and existing application build outputs, as well as `.env`.
- **Missing from original:** A repository-wide `__pycache__` exclusion is
  missing; the current Git status has an untracked `experiments/__pycache__/`
  directory. General pytest-cache coverage may also help outside
  `ml-service`.
- **Wholesale-copy risk:** Low if only patterns are incorporated, but replacing
  the file wholesale risks losing original-specific `.env`, Maven, Node, IDE,
  and service exclusions.
- **Evidence references:** Original `.gitignore` has a Python section limited
  to `ml-service`; research `.gitignore` adds general cache patterns.

### 10. `README.md`

**Recommendation: KEEP ORIGINAL; selectively reconcile factual run/setup documentation only if needed.**

- **Research change:** Replaces the restrained project/research overview with
  an architecture table and quick-start instructions; claims there are no
  backend tests and gives a count of ML tests.
- **Already present in original:** Original gives the architecture summary,
  benchmark reproduction command, and limitations for imputation uncertainty
  and forecasting generalization/statistical significance. The original tree
  contains backend test sources, so the research README's “no tests yet” is
  stale/incorrect for this project state.
- **Missing from original:** A concise all-layers role table and quick-start
  overview may be useful documentation, but no verified application feature
  is missing.
- **Wholesale-copy risk:** The suggested commands start the Compose Postgres
  service with the project configuration and start Spring Boot without
  warning about `ddl-auto: update`; this could connect to or alter a user's
  configured database. The doc also points readers to research claims that
  have not been independently reproduced in this comparison.
- **Evidence references:** Original README research limitations; original
  `backend/src/test/...` test files; `docker-compose.yml` and
  `backend/src/main/resources/application.yml` are project-level configuration
  not supplied by the research folder.

### 11. `experiments/README.md`

**Recommendation: KEEP ORIGINAL; selectively merge only evidence-backed protocol details.**

- **Research change:** Replaces the original's cautious methodology and
  limitations with detailed benchmark tables and stronger claims about
  statistical improvement, calibration, and method ranking.
- **Already present in original:** The original documents supplementary
  MCAR/MAR/MNAR imputation, MNAR-detector, multi-series forecasting, and DQ
  sensitivity experiments, while explicitly distinguishing historical
  outputs from results produced during integration and describing limits.
- **Missing from original:** Some result tables/protocol detail may be
  informative if their exact source run and environment are validated; this
  comparison did not rerun or independently verify them.
- **Wholesale-copy risk:** Documentation could overstate evidence, and the
  upgrade's `run_all.sh` is not part of the original project-level run
  instructions. Its claims should not be adopted without reproducing the
  specified environment and reviewing how trials/windows are treated.
- **Evidence references:** Original sections “Supplementary research-upgrade
  experiments” and “Research basis and open gaps”; research README reports
  result numbers and significance claims.

### 12. `experiments/common.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Sets `RESULTS_DIR` directly to
  `experiments/results/`; original uses `AI_DATA_ANALYST_RESULTS_DIR` if
  supplied, otherwise a newly created temporary directory.
- **Already present in original:** Environment capture and Holm adjustment
  helpers are already present with the same roles.
- **Missing from original:** No useful helper capability is missing. The
  original adds output isolation and explicit user override.
- **Wholesale-copy risk:** **High data-integrity risk for generated results.**
  All scripts writing through research `RESULTS_DIR` can overwrite existing
  benchmark artifacts/environment snapshots in the original project.
- **Evidence references:** Original `RESULTS_DIR` in `common.py`; research
  `RESULTS_DIR`; callers in `forecasting_benchmark.py`,
  `imputation_benchmark.py`, and `mnar_detector_benchmark.py`.

### 13. `experiments/forecasting_benchmark.py`

**Recommendation: NO ACTION on this path; use/review the original's separate v2 research benchmark.**

- **Research change:** Expands a single CO2 series/six origins into six
  bundled series/eight windows, adds fixed-model and ablation arms, an
  oracle comparison, runtime, and paired significance tests.
- **Already present in original:** The original has
  `experiments/forecasting_research_benchmark.py`, a separate expanded
  multi-series benchmark using the current `forecasting_service` API and
  writing through the safe `common.RESULTS_DIR`. Original README already
  explains the supplementary suite.
- **Missing from original:** No confirmed missing capability from the
  research script. The original's expanded script differs in implementation
  details (for example, quarterly date construction); this static audit does
  not establish which benchmark result set is more reproducible.
- **Wholesale-copy risk:** It would replace the focused legacy benchmark at
  this path and, paired with research `common.py`, write/overwrite fixed
  result names. Any benchmark code importing or depending on one version's
  result columns could also be affected.
- **Evidence references:** Original `run_benchmark`, `walk_forward_windows`,
  and separate `forecasting_research_benchmark.py` (`load_series`,
  `run_series`, `main`); research `load_series`, `run_series`, `main`.

### 14. `experiments/imputation_benchmark.py`

**Recommendation: NO ACTION on this path; keep the original configurable benchmark and separate v2 research script.**

- **Research change:** Replaces the original configurable target-column
  experiment (CLI controls for seed, rates, mechanisms, datasets, output)
  with a fixed cell-wise MCAR/MAR/MNAR study over four bundled datasets,
  adding uncertainty coverage/correlation calculations and paired
  comparisons.
- **Already present in original:** The original has
  `experiments/imputation_research_benchmark.py` with the broader
  MCAR/MAR/MNAR, four-dataset, uncertainty and significance design; its
  `experiments/common.py` isolates outputs. The legacy benchmark remains
  useful for configurable target-specific experiments and reports its
  limitations.
- **Missing from original:** No clear capability missing from the original
  project as a whole. The same-path research script's cell-wise masking is a
  distinct experimental protocol, not a direct replacement for the original's
  target-column protocol.
- **Wholesale-copy risk:** Changes semantics and CLI/output contract of the
  existing script. With the research `common.py`, it writes into
  `experiments/results/`. Its imports/calls to private imputation helpers
  must match the current implementation; in particular the research
  service's DataFrame uncertainty return shape is incompatible with the
  original's dict-returning `imputation_research_benchmark.py`.
- **Evidence references:** Original `imputation_benchmark.py`
  (`_parse_args`, `run_benchmark`, `summarize_paired_comparisons`) and
  `imputation_research_benchmark.py` (`make_mask`, `run_one`, `main`); research
  `load_datasets`, `make_mask`, `run_one`, `main`.

### 15. `experiments/mnar_detector_benchmark.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Changes its import from
  `imputation_research_benchmark` to `imputation_benchmark`; rest of the
  detector evaluation is materially the same.
- **Already present in original:** Original `mnar_detector_benchmark.py`
  uses the original's compatible `imputation_research_benchmark` constants,
  `load_datasets`, and `make_mask` helpers.
- **Missing from original:** None identified.
- **Wholesale-copy risk:** The research import target exists in the separate
  research folder but not with that API in the original: original
  `experiments/imputation_benchmark.py` exposes a different target-column
  protocol and does not provide the same `MECHANISMS`, `RATES`, `SEED`,
  `load_datasets`, and `make_mask` interface. Copying the research script
  alone would make imports fail.
- **Evidence references:** Original and research `main` in
  `mnar_detector_benchmark.py`; helper imports from original
  `imputation_research_benchmark.py` versus research `imputation_benchmark.py`.

### 16. `ml-service/pytest.ini`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Adds blanket filters ignoring all
  `DeprecationWarning`, `FutureWarning`, and `UserWarning`.
- **Already present in original:** `pythonpath = .` and `testpaths = tests`
  are already present, providing package/test discovery configuration.
- **Missing from original:** No discovery feature is missing. Warning
  suppression may reduce noise, but broad categories can hide useful
  compatibility or behavior warnings.
- **Wholesale-copy risk:** Suppresses warnings across the entire ML test suite
  and could conceal regressions/deprecations; no warning audit was performed
  here to justify that.
- **Evidence references:** Both `pytest.ini` files; research adds
  `filterwarnings`.

### 17. `ml-service/tests/test_cleaning_service.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Changes uncertainty assertions to expect a DataFrame
  and removes `test_knn_preserves_unfillable_numeric_column_and_imputes_string_dtype`.
- **Already present in original:** Original tests assert uncertainty keys and
  positive per-imputed-cell values under the dict helper contract; it also
  retains the KNN/string-dtype regression test.
- **Missing from original:** No test behavior shown as missing. The research
  assertion that observed cells have no uncertainty is conceptually useful,
  but can be expressed against the original dict contract without changing
  production behavior if desired.
- **Wholesale-copy risk:** Tests would fail against the original
  `_multiple_impute_dataframe` return type and remove a regression case for
  all-missing numeric columns and pandas string categoricals. Tests should
  not be weakened or switched to fit an incompatible implementation.
- **Evidence references:** `test_multiple_imputation_fills_everything_and_reports_uncertainty`,
  `test_uncertainty_is_informative_in_the_right_direction`, and
  `test_knn_preserves_unfillable_numeric_column_and_imputes_string_dtype`.

### 18. `ml-service/tests/test_forecasting_service.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Retains period checks only for daily, weekly, monthly,
  quarterly, annual, and hourly inputs, dropping 2-hour/30-minute/15-minute
  frequencies; removes tests for invalid MASE inputs, absent backtest splits,
  constant-series no-selection behavior, unrounded model ranking, invalid
  values/duplicate dates, and dropped blank/missing cells.
- **Already present in original:** Original has the broader period parameter
  set and the removed validation/edge-case tests. It also tests frontend
  response keys/shapes, leakage-free rolling splits, candidate ablation, and
  ensemble behavior.
- **Missing from original:** No important correctness test identified as
  missing. Some research comments/explanations are not test coverage.
- **Wholesale-copy risk:** Would delete high-value regression coverage that
  specifically guards against the weaker research service behavior described
  above.
- **Evidence references:** Original
  `test_seasonal_period_inferred_from_date_spacing`,
  `test_mase_rejects_unscorable_or_misaligned_inputs`,
  `test_auto_forecast_does_not_claim_selection_without_backtest_splits`,
  `test_model_selection_uses_unrounded_mase_scores`, and
  `test_forecast_rejects_invalid_values_and_duplicate_timestamps`.

### 19. `ml-service/tests/test_health_service.py`

**Recommendation: KEEP ORIGINAL.**

- **Research change:** Removes tests verifying sentinel recognition for
  pandas `string` dtype and rejection of malformed custom weights.
- **Already present in original:** The original retains both tests and its
  `calculate_health_score` implementation supports those cases.
- **Missing from original:** No behavior/test capability identified as
  missing.
- **Wholesale-copy risk:** Drops regression coverage for behaviors the
  research `health_service.py` itself no longer handles correctly.
- **Evidence references:** Original
  `test_string_dtype_sentinels_are_included_in_missingness` and
  `test_invalid_health_weight_shapes_and_values_are_rejected`.

## Prioritized recommendations

1. **Do not copy the research `DatasetController` or replace the original
   controller's auth, ownership, history, or persistence paths.** The original
   integration is materially safer and more complete.
2. **Keep the original ML request schema, forecasting service, and tests.**
   Consider a narrowly scoped seasonality change only after reconciling
   frequency coverage and preserving strict validation, unrounded MASE
   selection, and explicit no-selection responses.
3. **Keep the original frontend pages.** They preserve persisted-dataset
   guards, history, and conditional result/error behavior that research
   versions remove.
4. **Keep the original cleaning implementation and private helper contract.**
   Do not introduce research's broad silent fallback or DataFrame uncertainty
   return without updating and validating every experiment/test caller.
5. **Retain the original safe experiment output helper.** Never use the
   research `RESULTS_DIR=experiments/results` behavior to reproduce runs
   without first redirecting output, because it can overwrite saved results.
6. **Keep the original test files and avoid blanket warning suppression.**
   They include regression cases removed from the research copies.
7. **Optional documentation/housekeeping only:** selectively add general
   Python cache ignore patterns; do not replace original README or experiment
   documentation with stronger research claims without independent
   reproducibility evidence.
8. **No action needed for duplicate v2 experiment coverage:** the original
   already contains separate `imputation_research_benchmark.py` and
   `forecasting_research_benchmark.py`, along with the supplementary research
   suite and isolated result handling.

## Overall assessment

Static inspection indicates the original project has already incorporated
most useful application-level changes while retaining integration safeguards
that the separate research snapshot lacks. The largest “gaps” are not missing
research code: they are differences where the upgrade copy is older, less
integrated, weakens validation/ownership/persistence, or uses incompatible
helper contracts. The only low-risk improvement clearly worth considering is
general Python cache-ignore coverage. No runtime pass/fail conclusion is made
by this report.
