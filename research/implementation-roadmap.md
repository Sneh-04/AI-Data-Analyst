# Research and implementation roadmap

Priorities are based on verified repository evidence, achievable evaluation,
and risk. “Implemented” describes code changes, not a claim that the research
question is closed.

| Priority | Status | Work | Evidence required to close |
|---|---|---|---|
| 1 | Implemented; evaluation partial | Replace marginal-only numeric `multiple` imputation with feature-aware stochastic iterative imputation while retaining KNN and marginal baselines. | Current MCAR experiment shows lower RMSE than marginal bootstrap at 10%, 20%, and 30%, but not a consistent win over KNN. Regression tests cover feature use, unchanged observed cells, uncertainty log values, and categorical fallback. |
| 2 | Open | Evaluate uncertainty honestly, then decide whether to retain, rename, or remove the uncertainty field. | Multiple datasets and missingness patterns; empirical interval coverage and width at stated nominal levels; separate between- and within-imputation variation if inferential uncertainty is claimed. |
| 3 | Open | Expand imputation beyond one standardized dataset/target and MCAR. | Dataset provenance/version/license; paired seeds; MCAR and explicit MAR/MNAR generators; complete-case ground truth; failure cases and variability. |
| 4 | Open | Test forecasting model selection beyond Mauna Loa CO2. | Several series with documented frequency/seasonality; common horizons and rolling origins; per-series results. Use paired significance tests only where the design supplies enough suitable independent series/origins. |
| 5 | Open | Build offline RAG retrieval evaluation independent of live generation. | Labeled questions with expected tables/columns/evidence; retrieval precision/recall and context budget; a separate live-model generation/groundedness evaluation when credentials are available. |
| 6 | Open | Validate health-score meaning and trend behavior. | Injected known defects or a labeled corpus; report component scores and configurable weights; validate ranking/trends against defect severity rather than arbitrary thresholds. |
| 7 | Open | Expand service-contract and persistence verification. | Tests for Spring Boot ↔ FastAPI request/timeout/error behavior, authorization boundaries, health-score persistence, and relevant frontend response assumptions. |

## Current verification limits

- The ML service had no existing test suite; this change adds focused standard
  library `unittest` regression tests only.
- Existing Maven tests completed successfully earlier in the session, but the
  repository did not contain Java test files.
- Frontend production build previously passed after pinning Vite 4 for the
  available Node 16 runtime; it emitted a large-chunk warning.
- This work does not add a broad architecture rewrite, validate live LLM calls,
  or claim security/authentication correctness.
