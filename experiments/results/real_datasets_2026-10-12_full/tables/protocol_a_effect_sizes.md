# Protocol A Effect Sizes

Primary headline-set effect sizes from saved CSVs. Held-out recovery includes all Protocol B datasets. Percentile bootstrap intervals use 10,000 dataset-level resamples with seed 42. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.

| mechanism   | vs               |   n_datasets |   median_project_minus_baseline_ratio |   bootstrap_95_ci_low |   bootstrap_95_ci_high |   datasets_project_better |   datasets_project_worse |   datasets_tied_within_1_percent |
|-------------|------------------|--------------|---------------------------------------|-----------------------|------------------------|---------------------------|--------------------------|----------------------------------|
| MAR         | mean             |           10 |                           -0.0179966  |            -0.218334  |             0.0787513  |                         5 |                        4 |                                1 |
| MAR         | median           |           10 |                           -0.14613    |            -0.235499  |            -0.0221173  |                         8 |                        2 |                                0 |
| MAR         | knn5             |           10 |                           -0.00265875 |            -0.0246448 |             0.0444916  |                         5 |                        5 |                                0 |
| MAR         | iterative_single |           10 |                            0.0748874  |             0.0414645 |             0.11075    |                         0 |                       10 |                                0 |
| MCAR        | mean             |           10 |                           -0.00207498 |            -0.209939  |             0.0676971  |                         4 |                        4 |                                2 |
| MCAR        | median           |           10 |                           -0.129757   |            -0.26357   |             0.0120008  |                         7 |                        3 |                                0 |
| MCAR        | knn5             |           10 |                            0.0307931  |             0.0120656 |             0.0460423  |                         1 |                        8 |                                1 |
| MCAR        | iterative_single |           10 |                            0.0786223  |             0.0480611 |             0.103505   |                         0 |                       10 |                                0 |
| MNAR        | mean             |           10 |                           -0.0958293  |            -0.180222  |            -0.0571147  |                        10 |                        0 |                                0 |
| MNAR        | median           |           10 |                           -0.171868   |            -0.235531  |            -0.126761   |                        10 |                        0 |                                0 |
| MNAR        | knn5             |           10 |                           -0.0498826  |            -0.0589746 |            -0.0197922  |                         8 |                        0 |                                2 |
| MNAR        | iterative_single |           10 |                           -0.0136356  |            -0.0246353 |            -0.00114025 |                         7 |                        1 |                                2 |
