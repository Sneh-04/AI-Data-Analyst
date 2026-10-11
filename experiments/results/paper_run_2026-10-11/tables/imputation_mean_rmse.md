# Imputation Mean Rmse

Mean trial-level RMSE from `imputation_raw.csv`, grouped by mechanism and method.

| mechanism   | method                 |   mean_rmse |   datasets |   runs |
|-------------|------------------------|-------------|------------|--------|
| MAR         | iterative_single       |    0.680856 |          4 |     96 |
| MAR         | knn5                   |    0.761192 |          4 |     96 |
| MAR         | marginal_bootstrap_OLD |    1.25515  |          4 |     96 |
| MAR         | mean                   |    1.17079  |          4 |     96 |
| MAR         | median                 |    1.19385  |          4 |     96 |
| MAR         | mice_multiple_NEW      |    0.774713 |          4 |     96 |
| MCAR        | iterative_single       |    0.650886 |          4 |     96 |
| MCAR        | knn5                   |    0.708725 |          4 |     96 |
| MCAR        | marginal_bootstrap_OLD |    1.09664  |          4 |     96 |
| MCAR        | mean                   |    1.00011  |          4 |     96 |
| MCAR        | median                 |    1.02629  |          4 |     96 |
| MCAR        | mice_multiple_NEW      |    0.656957 |          4 |     96 |
| MNAR        | iterative_single       |    1.15994  |          4 |     96 |
| MNAR        | knn5                   |    1.26937  |          4 |     96 |
| MNAR        | marginal_bootstrap_OLD |    1.71676  |          4 |     96 |
| MNAR        | mean                   |    1.67817  |          4 |     96 |
| MNAR        | median                 |    1.71008  |          4 |     96 |
| MNAR        | mice_multiple_NEW      |    1.19105  |          4 |     96 |
