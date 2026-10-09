# Imputation benchmark results

Dataset: scikit-learn diabetes, target `bmi`, n=442.
Trials per mask rate: 10; rates: 10%, 20%, 30%.

|   mask_rate | method                        |   mean_rmse |   std_rmse |   mean_uncertainty_spearman |
|------------:|:------------------------------|------------:|-----------:|----------------------------:|
|      0.1000 | knn_k5                        |      0.0436 |     0.0048 |                    nan      |
|      0.1000 | mean                          |      0.0483 |     0.0040 |                    nan      |
|      0.1000 | median                        |      0.0487 |     0.0040 |                    nan      |
|      0.1000 | multiple_imputation_iterative |      0.0432 |     0.0048 |                     -0.0616 |
|      0.1000 | multiple_imputation_marginal  |      0.0504 |     0.0057 |                     -0.0313 |
|      0.2000 | knn_k5                        |      0.0426 |     0.0020 |                    nan      |
|      0.2000 | mean                          |      0.0471 |     0.0038 |                    nan      |
|      0.2000 | median                        |      0.0475 |     0.0041 |                    nan      |
|      0.2000 | multiple_imputation_iterative |      0.0435 |     0.0041 |                     -0.0214 |
|      0.2000 | multiple_imputation_marginal  |      0.0527 |     0.0046 |                      0.0488 |
|      0.3000 | knn_k5                        |      0.0420 |     0.0029 |                    nan      |
|      0.3000 | mean                          |      0.0468 |     0.0023 |                    nan      |
|      0.3000 | median                        |      0.0474 |     0.0023 |                    nan      |
|      0.3000 | multiple_imputation_iterative |      0.0436 |     0.0031 |                     -0.0273 |
|      0.3000 | multiple_imputation_marginal  |      0.0524 |     0.0021 |                      0.0197 |
