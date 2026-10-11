# Research notes (honest status)

This file separates what is **implemented**, what is **measured**, and what could be **claimed**.

## 1. Status

| Component | Implemented | Measured on real data | Result |
|---|---|---|---|
| Feature-aware multiple imputation (MICE-style, with per-cell uncertainty) | yes | yes (12 dataset x mechanism cells) | Much better than the previous method and than mean/median; on par with KNN, slightly worse than single iterative imputation; calibrated under MCAR only |
| MNAR/non-random-missingness detector | yes | yes | Separates random from non-random; cannot separate MAR from MNAR |
| Seasonal-period inference + backtest-based model selection | yes | yes (6 series, 48 windows) | Beats naive; **not** significantly better than fixed ARIMA; big win on strongly seasonal data; large selection regret |
| Hand-set meta-feature shortlisting | yes | yes (ablation) | No accuracy cost, small speed gain |
| Equal-weight forecast ensemble | yes (opt-in) | yes | No benefit; off by default |
| Data-quality score (completeness/uniqueness/consistency/outliers, sentinels, weights, trend) | yes | yes (corruption study) | Monotone; one blind spot fixed; weakly sensitive to duplicates/outliers |
| Schema-budgeted RAG context, retrieval merge | yes | **no** | Unknown |
| Drift trend via stored previous score | yes | **no** | Unknown |
| Repair log / explainability | yes | no (qualitative feature) | - |
| Refresh tokens, persistence, timeouts | yes | not research claims | engineering |

## 2. Contributions that can honestly be claimed

Engineering / systems:
* An auditable analysis pipeline in which every automated repair is logged with its method and, for imputed
  cells, an uncertainty, exposed in the UI.
* A reproducible, open evaluation harness (`experiments/`) that exercises the shipped code, not a re-implementation.

Empirical (these are evaluation findings, which is what the data support):
* A controlled study showing that a naive "multiple imputation by resampling" is uncalibrated and no better than
  mean imputation, while chained-equations imputation is informative and calibrated under MCAR but over-confident
  under MAR/MNAR.
* A concrete failure analysis of an automated forecasting selector: a hard-coded seasonal period silently degraded
  seasonal data 3x; backtest selection beats naive but not a fixed ARIMA; combination did not help.
* A corruption-based validity test for a composite quality score, with a found blind spot.

## 3. What is **not** novel (do not claim)

* Multiple imputation / chained equations: Rubin (1987); van Buuren & Groothuis-Oudshoorn (2011, `mice`); scikit-learn's
  `IterativeImputer` is used here.
* Feature-based forecast model selection and combination is an established, stronger line of work: FFORMS
  (Talagala, Hyndman & Athanasopoulos) and FFORMA (Montero-Manso, Athanasopoulos, Hyndman & Talagala, International
  Journal of Forecasting, 2020; second place in the M4 competition). The hand-set shortlist here is a heuristic and
  is not a contribution; a learned selector would be, but would need training data across many series.
* MASE (Hyndman & Koehler, 2006), rolling-origin evaluation, forecast combination, composite data-quality scores.

## 4. Candidate research question that the current evidence supports

"Do the default behaviours of an automated analytics pipeline - imputation with uncertainty, seasonal-period
handling, automatic model selection, composite quality scoring - hold up under controlled evaluation, and where do
they fail?" This is a **negative-results / evaluation** paper or a **system + evaluation** workshop paper. It is not,
on current evidence, a paper proposing a new method that beats the state of the art.

## 5. Gaps before a submission (in priority order)

1. **RAG evaluation**: a labelled question/answer set over the bundled datasets, retrieval precision/recall of the
   selected columns, answer correctness, tokens used; compare against "no retrieval" and "full schema". Needs an LLM key.
2. **More data**: more and larger series (e.g. M3/M4 subsets) and tables; today it is 6 series and 4 small tables.
   Re-test the "auto vs fixed ARIMA" and "KNN parity" results there before generalising.
3. **Close the MNAR gap**: either add a sensitivity analysis (delta-adjusted / pattern-mixture imputation) or
   report the interval as optimistic when the detector fires; measure whether that restores coverage.
4. **Reduce selection regret**: a learned or weighted combination in the spirit of FFORMA, evaluated against the
   oracle gap (0.42 MASE).
5. **Quality-score weights**: tune/validate against the effect of each corruption on a downstream model, instead
   of hand-set weights; address the weak response to duplicates/outliers.
6. **Held-out discipline**: the ensemble-off decision was taken after seeing the benchmark; confirm on new series.
7. **Statistics**: windows/trials are dependent; add block bootstrap or Diebold-Mariano style tests with proper
   dependence handling.

## 6. References (check every bibliographic detail before submission)

Verified in this work through a literature search: Montero-Manso, Athanasopoulos, Hyndman, Talagala (2020), "FFORMA:
Feature-based forecast model averaging", International Journal of Forecasting; Talagala, Hyndman, Athanasopoulos
(2018), "Meta-learning how to forecast time series" / FFORMS (Monash working paper; `seer` R package).

Cited from the earlier literature survey or standard references, **not re-verified here**: Rubin (1987) *Multiple
Imputation for Nonresponse in Surveys*; van Buuren & Groothuis-Oudshoorn (2011) "mice", J. Statistical Software;
Jäger et al. (2021) "A Benchmark for Data Imputation Methods"; Hyndman & Koehler (2006) "Another look at measures of
forecast accuracy", IJF; Hewamalage et al. (2022) "Forecast evaluation for data scientists: common pitfalls and best
practices"; Mohammed et al. (2024) "Data Quality Assessment: Challenges and Opportunities" (arXiv:2403.00526);
Chen et al. (2024) "TableRAG" (arXiv:2410.04739).
