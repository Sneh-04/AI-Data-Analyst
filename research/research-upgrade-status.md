# Research notes (honest status)

This file separates what is **implemented**, what is **measured**, and what could be **claimed**.

## 1. Status

| Component | Implemented | Measured on real data | Result |
|---|---|---|---|
| Feature-aware multiple imputation (MICE-style, with per-cell uncertainty) | yes | yes (12 dataset x mechanism cells) | Much better than the previous method and than mean/median; on par with KNN, slightly worse than single iterative imputation; calibrated under MCAR only |
| MNAR/non-random-missingness detector | yes | yes | Separates random from non-random; cannot separate MAR from MNAR |
| Seasonal-period inference + backtest-based model selection | yes | yes (6-series study plus 20 M3 Monthly series) | On M3, Auto was not significantly different from fixed ARIMA after Holm correction; see frozen series-level results and limitations below |
| Hand-set meta-feature shortlisting | yes | yes (six-series and M3 comparisons) | Runtime was lower in the M3 subset, but non-inferiority at the fixed +0.05 MASE margin was not established in either series set |
| Equal-weight forecast ensemble | yes (opt-in) | yes | No benefit; off by default |
| Data-quality score (completeness/uniqueness/consistency/outliers, sentinels, weights, trend) | yes | yes (corruption study) | Monotone; one blind spot fixed; weakly sensitive to duplicates/outliers |
| Schema-budgeted RAG context, retrieval merge | yes | **no** | Unknown |
| Drift trend via stored previous score | yes | **no** | Unknown |
| Repair log / explainability | yes | no (qualitative feature) | - |
| Refresh tokens, persistence, timeouts | yes | not research claims | engineering |

<!-- BEGIN GENERATED FROZEN PAPER RESULTS -->
### Frozen forecasting evidence

The supplementary frozen run evaluates 20 M3 Monthly series over 80 scored windows.
Auto's mean series-level MASE was 1.97262782; fixed ARIMA's was 1.91571923. For the
paired Auto-minus-ARIMA comparison, the mean difference was 0.05690859 over 20 series,
with 9 Auto wins; raw p=0.784126281738 and Holm-adjusted p=1. It was not significant
after Holm correction. Across the seven Auto-versus-alternative comparisons, 0 were
significant after Holm correction. See the full [model
summary](../experiments/results/paper_run_2026-10-11/followup_tables/m3_model_summary.csv),
[Auto
comparisons](../experiments/results/paper_run_2026-10-11/followup_tables/m3_auto_comparisons.csv),
and [series-level
results](../experiments/results/paper_run_2026-10-11/followup_tables/m3_series_results.csv).

For shortlisting, differences are per-series mean MASE (Auto minus auto_no_shortlist),
with the series as the paired unit and four rolling windows averaged within each series.
The +0.05 MASE margin was fixed before the M3 results existed. On M3 (n=20), the mean
difference was 0.01871981; the one-sided 95% t upper bound (df=19) was 0.04802643, and
the percentile-bootstrap upper bound was 0.05261873. Non-inferiority was **not
established**: the percentile-bootstrap bound exceeds the margin, although the t upper
bound is below it. The earlier six-series test also **not established** (mean difference
-0.05152810; t upper bound, df=5, 0.05230352; bootstrap upper bound 0.00000000), because
the t upper bound narrowly exceeds the margin. Neither result establishes accuracy
equivalence. See the [M3 non-inferiority
calculation](../experiments/results/paper_run_2026-10-11/followup_tables/m3_shortlisting_noninferiority.csv)
and the [six-series per-series
results](../experiments/results/paper_run_2026-10-11/followup_tables/six_series_shortlisting_by_series.csv).

The M3 shortlisting comparison measured mean runtime of 0.21555068 seconds per window
with shortlisting and 0.36797288 without; the mean per-series runtime reduction was
43.64884549% (paired runtime Wilcoxon p=2.6702881e-05). This is evidence about measured
runtime on this subset, not an accuracy-equivalence result. The fixed-model and
per-series comparison tables are linked above.

Series were selected before model evaluation: 1043 source-order M3 Monthly series met
the length threshold of 102 observations, then 20 evenly spaced indices from first to
last were selected with integer `numpy.linspace` indices. Selection used series length
and source order only, not model scores or runtime. The full rule, selected IDs, and
pre-evaluation flag are recorded in [M3 environment
metadata](../experiments/results/paper_run_2026-10-11/forecasting_m3/m3_environment.json).
M3 series may share domains, so these results do not remove all dependence or establish
generalization beyond this dataset. Canonical environment pins are listed
[here](../experiments/results/paper_run_2026-10-11/environment_pins.txt).
<!-- END GENERATED FROZEN PAPER RESULTS -->

## 2. Contributions that can honestly be claimed

Engineering / systems:
* An auditable analysis pipeline in which every automated repair is logged with its method and, for imputed
  cells, an uncertainty, exposed in the UI.
* A reproducible, open evaluation harness (`experiments/`) that exercises the shipped code, not a re-implementation.

Empirical (these are evaluation findings, which is what the data support):
* A controlled study showing that a naive "multiple imputation by resampling" is uncalibrated and no better than
  mean imputation, while chained-equations imputation is informative and calibrated under MCAR but over-confident
  under MAR/MNAR.
* A concrete failure analysis of an automated forecasting selector in the original Mauna Loa case: a hard-coded
  seasonal period silently degraded seasonal data 3x; backtest selection beat naive but not fixed ARIMA; combination
  did not help. The separate M3 findings are summarized above and in the frozen evidence tables.
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
2. **More data**: the frozen evidence now adds a deterministic 20-series M3 Monthly subset to the original six-series
   study. Evaluate additional datasets and series domains before generalising; M3 series may share domains.
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
