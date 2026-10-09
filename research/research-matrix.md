# Research matrix

References below were checked for bibliographic identity and the claims listed
are deliberately narrower than their general subject area. They guide an
experiment; they do not establish that an algorithm is valid for this dataset.

| Reference | Supported limitation or methodological point | Project mapping |
|---|---|---|
| Jäger, Sebastian; Allhorn, Arndt; Biessmann, Felix (2021). “A Benchmark for Data Imputation Methods.” *Frontiers in Big Data*, 4, 693674. [DOI: 10.3389/fdata.2021.693674](https://doi.org/10.3389/fdata.2021.693674) | Their benchmark compares point-estimate imputation quality and downstream-task effects; it does not establish calibration of an imputer's reported uncertainty. Therefore, a standard deviation across sampled imputations is not, by itself, evidence of calibrated uncertainty. | [`cleaning_service.py`](../ml-service/app/services/cleaning_service.py) reports between-imputation standard deviation; [`imputation_benchmark.py`](../experiments/imputation_benchmark.py) now measures its rank association with absolute error, which remains near zero in the current experiment. |
| White, Ian R.; Royston, Patrick; Wood, Angela M. (2011). “Multiple imputation using chained equations: Issues and guidance for practice.” *Statistics in Medicine*, 30(4), 377–399. [DOI: 10.1002/sim.4067](https://doi.org/10.1002/sim.4067) | Chained-equation imputation requires suitable imputation-model specification and checking; the method name alone does not ensure valid imputations. | The new iterative `multiple` strategy uses BayesianRidge conditional models, but this repository has not yet validated model compatibility, convergence sensitivity, or inferential properties. |
| Bartlett, Jonathan W.; Seaman, Shaun R.; White, Ian R.; Carpenter, James R.; et al. (2015; published online 2014). “Multiple imputation of covariates by fully conditional specification: Accommodating the substantive model.” *Statistical Methods in Medical Research*, 24(4), 462–487. [DOI: 10.1177/0962280214521348](https://doi.org/10.1177/0962280214521348) | Standard fully conditional specification can be incompatible with a nonlinear or interaction-containing substantive model; the paper's stated consistency conditions include MAR and correctly specified, mutually compatible models. | The current linear-conditional imputer is evaluated only for point reconstruction under MCAR. It has not been validated for downstream models with nonlinearities/interactions or for MAR/MNAR. |

## Limitation-to-code mapping

| Observed limitation | Evidence in this repository | Scope of current response |
|---|---|---|
| Previous numeric `multiple` strategy resampled only the target's marginal observed values. | `_multiple_impute_column()` in [`cleaning_service.py`](../ml-service/app/services/cleaning_service.py); the prior saved results show higher RMSE than KNN on the tested target. | Replaced the table-level production path with repeated BayesianRidge iterative imputation when at least two numeric columns contain observed values. Retained the marginal method as a comparison and one-column fallback. |
| The previous standard deviation was not validated as uncertainty. | Existing experiment computed Spearman correlation against absolute error; the prior correlations were near zero. | The updated experiment reports trial-level uncertainty/error rank association. Values remain near zero; no calibration claim is made. |
| Current imputation evaluation covers one dataset, one target, and MCAR only. | [`imputation_benchmark.py`](../experiments/imputation_benchmark.py) masks `bmi` at three rates. | Not resolved by the algorithm change. Multi-dataset and MAR/MNAR studies remain roadmap items. |
| Forecasting evidence is one series with six walk-forward origins. | [`forecasting_benchmark.py`](../experiments/forecasting_benchmark.py) evaluates one Mauna Loa series. | Results are now clearly described as dataset-specific, descriptive evidence; no significance or generalization claim is made. |

## Bibliographic caveat

The scikit-learn diabetes loader description identifies its source URL and
Efron et al. (2004), but does not name a separate dataset license. The benchmark
does not redistribute the dataset; users should verify source terms before
redistribution.
