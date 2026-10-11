# Research matrix

References below were checked for bibliographic identity and the claims listed
are deliberately narrower than their general subject area. They guide an
experiment; they do not establish that an algorithm is valid for this dataset.

| Reference | Supported limitation or methodological point | Project mapping |
|---|---|---|
| Jäger, Sebastian; Allhorn, Arndt; Biessmann, Felix (2021). “A Benchmark for Data Imputation Methods.” *Frontiers in Big Data*, 4, 693674. [DOI: 10.3389/fdata.2021.693674](https://doi.org/10.3389/fdata.2021.693674) | Their benchmark compares point-estimate imputation quality and downstream-task effects; it does not establish calibration of an imputer's reported uncertainty. Therefore, a standard deviation across sampled imputations is not, by itself, evidence of calibrated uncertainty. | [`cleaning_service.py`](../ml-service/app/services/cleaning_service.py) reports between-imputation standard deviation; [`imputation_benchmark.py`](../experiments/imputation_benchmark.py) now measures its rank association with absolute error, which remains near zero in the current experiment. |
| White, Ian R.; Royston, Patrick; Wood, Angela M. (2011). “Multiple imputation using chained equations: Issues and guidance for practice.” *Statistics in Medicine*, 30(4), 377–399. [DOI: 10.1002/sim.4067](https://doi.org/10.1002/sim.4067) | Chained-equation imputation requires suitable imputation-model specification and checking; the method name alone does not ensure valid imputations. | The production `multiple` strategy uses BayesianRidge conditional models and is now scored under simulated MAR/MNAR point reconstruction, but model compatibility, convergence sensitivity, interval calibration, and inferential properties remain unvalidated. |
| Bartlett, Jonathan W.; Seaman, Shaun R.; White, Ian R.; Carpenter, James R.; et al. (2015; published online 2014). “Multiple imputation of covariates by fully conditional specification: Accommodating the substantive model.” *Statistical Methods in Medical Research*, 24(4), 462–487. [DOI: 10.1177/0962280214521348](https://doi.org/10.1177/0962280214521348) | Standard fully conditional specification can be incompatible with a nonlinear or interaction-containing substantive model; the paper's stated consistency conditions include MAR and correctly specified, mutually compatible models. | The benchmark masks a target using a single logistic predictor (MAR) or the target value (MNAR), and evaluates only point reconstruction. It does not validate downstream nonlinear/interaction models, compatibility, convergence, or inferential validity. |

## Limitation-to-code mapping

| Observed limitation | Evidence in this repository | Scope of current response |
|---|---|---|
| Previous numeric `multiple` strategy resampled only the target's marginal observed values. | `_multiple_impute_column()` in [`cleaning_service.py`](../ml-service/app/services/cleaning_service.py); the prior saved results show higher RMSE than KNN on the tested target. | Replaced the table-level production path with repeated BayesianRidge iterative imputation when at least two numeric columns contain observed values. Retained the marginal method as a comparison and one-column fallback. |
| The previous between-imputation standard deviation was not validated as predictive uncertainty. | The earlier MCAR experiment's uncertainty/error rank correlations were near zero. | The MAR/MNAR benchmark does not treat between-imputation spread as a predictive interval; coverage and width remain unmeasured. |
| Imputation evaluation remains a controlled numeric benchmark and does not cover MCAR, categorical targets/predictors, or general real-world missingness. | [`imputation_benchmark.py`](../experiments/imputation_benchmark.py) evaluates three bundled datasets/targets under calibrated logistic MAR and MNAR propensities, with a separate observed MAR predictor. | The benchmark covers these simulated MAR/MNAR cases at four expected rates; it does not establish validity for arbitrary missingness processes or mixed-type data. Add MCAR and additional data/missingness settings before broader claims. |
| The original bundled forecasting benchmark uses one series with six walk-forward origins; the supplementary M3 evidence is a deterministic 20-series subset from one dataset, whose series may share domains. | [`forecasting_benchmark.py`](../experiments/forecasting_benchmark.py) evaluates one Mauna Loa series; the frozen M3 raw series-level results and Holm-adjusted Auto comparisons are in [`m3_series_results.csv`](../experiments/results/paper_run_2026-10-11/followup_tables/m3_series_results.csv) and [`m3_auto_comparisons.csv`](../experiments/results/paper_run_2026-10-11/followup_tables/m3_auto_comparisons.csv). | The original six-origin results remain dataset-specific. On the M3 subset, Auto was not significantly different from fixed ARIMA after Holm correction; neither analysis supports generalization beyond the evaluated data. |

## Bibliographic caveat

The scikit-learn diabetes loader description identifies its source URL and
Efron et al. (2004), but does not name a separate dataset license. The benchmark
does not redistribute the dataset; users should verify source terms before
redistribution.
