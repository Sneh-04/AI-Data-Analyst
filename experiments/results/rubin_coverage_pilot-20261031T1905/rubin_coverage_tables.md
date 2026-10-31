# Rubin coverage benchmark tables

## Coverage by mechanism, method, rate, dataset, estimand, m, and delta

| dataset        | estimand   | mechanism   | method        |   mask_rate |   m |   delta_sd |   coverage |   coverage_mc_se |   successful_runs |   failed_runs |   attempted_runs | complete_100_seed_cell   |
|:---------------|:-----------|:------------|:--------------|------------:|----:|-----------:|-----------:|-----------------:|------------------:|--------------:|-----------------:|:-------------------------|
| cylinder-bands | mean       | MAR         | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | knn           |         0.3 |   1 |        0   |       0.7  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | knn           |         0.5 |   1 |        0   |       0.1  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | median        |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | median        |         0.3 |   1 |        0   |       0.3  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_improper |         0.3 |   5 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_improper |         0.5 |   5 |        0   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | knn           |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | knn           |         0.5 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | median        |         0.1 |   1 |        0   |       0.5  |        0.111803  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | median        |         0.3 |   1 |        0   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |       0.1  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   |       0.1  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | median        |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | median        |         0.3 |   1 |        0   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   |       0.7  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |       0.5  |        0.111803  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0.3  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |       0.3  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |       0.4  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |       0.7  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0.65 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | knn           |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | knn           |         0.5 |   1 |        0   |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | median        |         0.1 |   1 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | median        |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_improper |         0.5 |   5 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | knn           |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | knn           |         0.5 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | median        |         0.1 |   1 |        0   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | median        |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0.25 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.25 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        1   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | median        |         0.1 |   1 |        0   |       0.5  |        0.111803  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | median        |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |       0.7  |        0.10247   |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |

## Mean interval width

| dataset        | estimand   | mechanism   | method        |   mask_rate |   m |   delta_sd |   mean_ci_width |   finite_interval_runs |   successful_runs |
|:---------------|:-----------|:------------|:--------------|------------:|----:|-----------:|----------------:|-----------------------:|------------------:|
| cylinder-bands | mean       | MAR         | knn           |         0.1 |   1 |        0   |     0.501998    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | knn           |         0.3 |   1 |        0   |     0.382401    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | knn           |         0.5 |   1 |        0   |     0.197994    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.1 |   1 |        0   |     0.529647    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.3 |   1 |        0   |     0.381205    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.5 |   1 |        0   |     0.126722    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |     0.624776    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.3 |   5 |        0   |     0.885117    |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.5 |   5 |        0   |     1.3968      |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |     0.7611      |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   |     1.54268     |                     20 |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   |     6.62676     |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.1 |   1 |        0   |     0.527919    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.3 |   1 |        0   |     0.48881     |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.5 |   1 |        0   |     0.456202    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.1 |   1 |        0   |     0.542679    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.3 |   1 |        0   |     0.512708    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.5 |   1 |        0   |     0.48347     |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |     0.586388    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   |     0.62612     |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   |     0.714402    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |     0.587413    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   |     0.663344    |                     20 |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |     0.741424    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |     0.538339    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |     0.519482    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0   |     0.511713    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |     0.515539    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        1   |     0.530702    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |     0.490203    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |     0.448623    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0   |     0.429878    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |     0.436914    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        1   |     0.468575    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |     0.485707    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |     0.424262    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0   |     0.387062    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |     0.381272    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        1   |     0.408238    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -1   |     0.578583    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |     0.545803    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0   |     0.522456    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |     0.509855    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        1   |     0.508809    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -1   |     0.538468    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |     0.478135    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0   |     0.435727    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |     0.416758    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        1   |     0.424381    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -1   |     0.506843    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |     0.437171    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0   |     0.388701    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |     0.36987     |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        1   |     0.38505     |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |     0.589051    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |     0.573407    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |     0.567836    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |     0.572626    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |     0.587534    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |     0.632787    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |     0.605087    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |     0.594641    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |     0.602135    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |     0.627044    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |     0.658044    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |     0.628513    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |     0.617857    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |     0.626835    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |     0.654802    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |     0.599367    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |     0.584329    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |     0.57918     |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |     0.584172    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |     0.599056    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |     0.651761    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |     0.625526    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |     0.615844    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |     0.623273    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |     0.647384    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |     0.755792    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |     0.731831    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |     0.722732    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |     0.728387    |                     20 |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |     0.748894    |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |     5.75468e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   |     4.33967e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   |     2.15721e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.1 |   1 |        0   |     5.9734e-05  |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.3 |   1 |        0   |     4.30759e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |     1.44789e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |     9.7645e-05  |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   |     0.000129987 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   |     0.000218743 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |     0.000178754 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   |     0.000258915 |                     20 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   |     0.00069971  |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |     6.27883e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |     6.29126e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |     6.44779e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |     6.4799e-05  |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   |     6.75889e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |     7.11484e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |     7.32391e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |     9.68036e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |     0.000128851 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |     7.26138e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |     0.000108503 |                     20 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |     0.000172925 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |     0.000107035 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |     0.000103337 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |     0.000101849 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |     0.000102667 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |     0.000105738 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |     0.000100301 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |     9.19056e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |     8.8249e-05  |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |     8.99113e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |     9.66188e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |     9.24802e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |     8.09101e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |     7.41924e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |     7.36637e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |     7.94474e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |     0.000116517 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |     0.000109959 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |     0.000105305 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |     0.000102815 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |     0.000102651 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |     0.000114789 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |     0.000102028 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |     9.31151e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |     8.92113e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |     9.0964e-05  |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |     0.000103801 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |     8.95653e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |     7.96711e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |     7.58382e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |     7.89542e-05 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |     0.000125206 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |     0.00012256  |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |     0.000121645 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |     0.000122496 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |     0.000125082 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |     0.000177903 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |     0.000173936 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |     0.000171822 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |     0.000171607 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |     0.000173475 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |     0.000467614 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |     0.000464018 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |     0.000453355 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |     0.000434381 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |     0.000412717 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |     0.000129174 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |     0.000126512 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |     0.000125536 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |     0.000126282 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |     0.000128723 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |     0.000217734 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |     0.000213855 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |     0.000211137 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |     0.000209518 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |     0.000209208 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |     0.000785763 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |     0.000775183 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |     0.00074933  |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |     0.000706949 |                     20 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |     0.000658383 |                     20 |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.1 |   1 |        0   |     0.106865    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.3 |   1 |        0   |     0.095612    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.5 |   1 |        0   |     0.0841564   |                     20 |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.1 |   1 |        0   |     0.107858    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.3 |   1 |        0   |     0.0964542   |                     20 |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.5 |   1 |        0   |     0.0818228   |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |     0.126765    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.3 |   5 |        0   |     0.161229    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.5 |   5 |        0   |     0.169786    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |     0.131008    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   |     0.182489    |                     20 |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   |     0.244673    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.1 |   1 |        0   |     0.10719     |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.3 |   1 |        0   |     0.0987725   |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.5 |   1 |        0   |     0.0871936   |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.1 |   1 |        0   |     0.108411    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.3 |   1 |        0   |     0.101157    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.5 |   1 |        0   |     0.0881867   |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |     0.126608    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   |     0.153678    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   |     0.162767    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |     0.131568    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   |     0.162289    |                     20 |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |     0.204358    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |     0.117468    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |     0.112788    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0   |     0.110666    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |     0.111248    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        1   |     0.114493    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |     0.123708    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |     0.111587    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0   |     0.105351    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |     0.106018    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        1   |     0.113475    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |     0.111716    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |     0.0972431   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0   |     0.0901781   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |     0.0922313   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        1   |     0.102862    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -1   |     0.109365    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |     0.109335    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0   |     0.112042    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |     0.117292    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        1   |     0.12476     |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -1   |     0.100829    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |     0.102476    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0   |     0.111013    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |     0.125069    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        1   |     0.143066    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -1   |     0.132942    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |     0.11162     |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0   |     0.0945864   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |     0.0844795   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        1   |     0.0838361   |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |     0.132575    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |     0.129713    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |     0.129125    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |     0.13084     |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |     0.134775    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |     0.169208    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |     0.162624    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |     0.160308    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |     0.162397    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |     0.16877     |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |     0.181751    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |     0.175249    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |     0.173114    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |     0.175433    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |     0.182113    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |     0.137045    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |     0.134021    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |     0.133167    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |     0.134521    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |     0.138025    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |     0.183762    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |     0.178272    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |     0.176555    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |     0.178663    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |     0.18454     |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |     0.208791    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |     0.203459    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |     0.201687    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |     0.203439    |                     20 |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |     0.208725    |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |     0.0117282   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   |     0.0104125   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   |     0.00908969  |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.1 |   1 |        0   |     0.0118785   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.3 |   1 |        0   |     0.0104593   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |     0.00867222  |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |     0.0151836   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   |     0.0198573   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   |     0.0192688   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |     0.0159271   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   |     0.0212133   |                     20 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   |     0.0221799   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |     0.0122164   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |     0.0123524   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |     0.0124302   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |     0.0125027   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   |     0.0132192   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |     0.0138127   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |     0.0147708   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |     0.0183347   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |     0.0192561   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |     0.0149492   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |     0.0189472   |                     20 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |     0.0195009   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |     0.0141217   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |     0.013555    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |     0.0132946   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |     0.0133582   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |     0.0137415   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |     0.0176882   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |     0.0159551   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |     0.0150655   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |     0.0151649   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |     0.0162363   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |     0.0190992   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |     0.0166194   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |     0.0154093   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |     0.0157626   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |     0.0175857   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |     0.013328    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |     0.0133191   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |     0.013643    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |     0.0142767   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |     0.0151807   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |     0.0151312   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |     0.0153815   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |     0.0166638   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |     0.0187726   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |     0.0214715   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |     0.025129    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |     0.0210999   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |     0.0178843   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |     0.0159814   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |     0.0158695   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |     0.0159894   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |     0.0157237   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |     0.0157354   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |     0.0160233   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |     0.0165723   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |     0.0217602   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |     0.0206197   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |     0.0201799   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |     0.0204827   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |     0.0214925   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |     0.0286559   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |     0.0278102   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |     0.0277263   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |     0.0283963   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |     0.0297724   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |     0.0165874   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |     0.0161962   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |     0.0160636   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |     0.0161958   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |     0.0165869   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |     0.021972    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |     0.0211467   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |     0.0209962   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |     0.0215251   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |     0.0226889   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |     0.0279342   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |     0.0265526   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |     0.026007    |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |     0.0263535   |                     20 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |     0.0275689   |                     20 |                20 |

## Mean bias

| dataset        | estimand   | mechanism   | method        |   mask_rate |   m |   delta_sd |    mean_bias |   successful_runs |
|:---------------|:-----------|:------------|:--------------|------------:|----:|-----------:|-------------:|------------------:|
| cylinder-bands | mean       | MAR         | knn           |         0.1 |   1 |        0   |  0.0650926   |                20 |
| cylinder-bands | mean       | MAR         | knn           |         0.3 |   1 |        0   | -0.0615556   |                20 |
| cylinder-bands | mean       | MAR         | knn           |         0.5 |   1 |        0   | -0.164481    |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.1 |   1 |        0   | -0.52537     |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.3 |   1 |        0   | -0.679907    |                20 |
| cylinder-bands | mean       | MAR         | median        |         0.5 |   1 |        0   |  0.717037    |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |  0.0186821   |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.3 |   5 |        0   | -0.104835    |                20 |
| cylinder-bands | mean       | MAR         | mice_improper |         0.5 |   5 |        0   | -0.249237    |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |  0.0182499   |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   | -0.152411    |                20 |
| cylinder-bands | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   | -0.183832    |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.1 |   1 |        0   |  0.0113333   |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.3 |   1 |        0   |  0.00168519  |                20 |
| cylinder-bands | mean       | MCAR        | knn           |         0.5 |   1 |        0   | -0.00192593  |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.1 |   1 |        0   | -0.255926    |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.3 |   1 |        0   | -0.596667    |                20 |
| cylinder-bands | mean       | MCAR        | median        |         0.5 |   1 |        0   | -0.958241    |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |  0.0182856   |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   |  0.0201204   |                20 |
| cylinder-bands | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   | -0.00372991  |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |  0.024023    |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   |  0.0128348   |                20 |
| cylinder-bands | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |  0.0171423   |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -1   | -0.684498    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 | -0.538601    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0   | -0.392704    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 | -0.246807    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        1   | -0.10091     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -1   | -1.96675     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 | -1.5942      |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0   | -1.22165     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 | -0.849098    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        1   | -0.476548    |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -1   | -2.80652     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 | -2.28626     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0   | -1.766       |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 | -1.24574     |                20 |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        1   | -0.725478    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -1   | -0.891424    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 | -0.745527    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0   | -0.59963     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0.5 | -0.453733    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        1   | -0.307835    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -1   | -2.33417     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 | -1.96162     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0   | -1.58907     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0.5 | -1.21652     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        1   | -0.843974    |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -1   | -3.00515     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 | -2.48489     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0   | -1.96463     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0.5 | -1.44437     |                20 |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        1   | -0.924108    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   | -0.664656    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 | -0.518759    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   | -0.372862    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 | -0.226965    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   | -0.0810677   |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   | -1.91378     |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 | -1.54123     |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   | -1.16868     |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 | -0.796127    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   | -0.423577    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   | -2.47756     |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 | -1.9573      |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   | -1.43704     |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 | -0.916775    |                20 |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   | -0.396514    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   | -0.660857    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 | -0.51496     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   | -0.369063    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 | -0.223166    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   | -0.077269    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   | -1.90618     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 | -1.53363     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   | -1.16108     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 | -0.78853     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   | -0.41598     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   | -2.5158      |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 | -1.99554     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   | -1.47528     |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 | -0.955019    |                20 |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   | -0.434758    |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |  1.37835e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   |  7.2251e-07  |                20 |
| cylinder-bands | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   | -4.07929e-06 |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.1 |   1 |        0   | -5.0266e-05  |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.3 |   1 |        0   | -1.47424e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |  1.77519e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |  5.54878e-06 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   | -2.95331e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   | -4.22052e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |  5.17261e-06 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   | -3.39314e-05 |                20 |
| cylinder-bands | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   | -3.18394e-05 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |  2.25187e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |  7.02167e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |  9.69729e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |  2.4719e-06  |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   | -1.18028e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |  5.20633e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |  3.11109e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |  6.26761e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |  1.15835e-05 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |  3.29428e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |  6.32367e-06 |                20 |
| cylinder-bands | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |  6.62054e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   | -2.50808e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 | -1.97852e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   | -1.44896e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 | -9.194e-06   |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   | -3.8984e-06  |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   | -7.53047e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 | -6.17021e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   | -4.80995e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 | -3.4497e-05  |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   | -2.08944e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   | -0.000105705 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 | -8.53009e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   | -6.48967e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 | -4.44924e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   | -2.40881e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   | -2.65358e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 | -2.09191e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   | -1.53024e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 | -9.68574e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   | -4.06905e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   | -5.95635e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 | -4.69594e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   | -3.43552e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 | -2.17511e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   | -9.14699e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   | -1.06375e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 | -3.03107e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |  4.57541e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |  1.21819e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |  1.97884e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   | -1.91345e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 | -1.40235e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   | -8.91242e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 | -3.80137e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |  1.30969e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   | -9.02703e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 | -7.84737e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   | -6.6677e-05  |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 | -5.48804e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   | -4.30838e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   | -3.87903e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 | -3.09756e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   | -2.3161e-05  |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 | -1.53463e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   | -7.53158e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   | -1.97748e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 | -1.46909e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   | -9.60697e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 | -4.52306e-06 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |  5.60852e-07 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   | -8.59931e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 | -7.4795e-05  |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   | -6.35969e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 | -5.23988e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   | -4.12007e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   | -5.78663e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 | -4.9507e-05  |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   | -4.11478e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 | -3.27886e-05 |                20 |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   | -2.44293e-05 |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.1 |   1 |        0   |  0.00514815  |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.3 |   1 |        0   | -0.00392593  |                20 |
| heart-statlog  | mean       | MAR         | knn           |         0.5 |   1 |        0   | -0.00655556  |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.1 |   1 |        0   |  0.0414815   |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.3 |   1 |        0   |  0.11963     |                20 |
| heart-statlog  | mean       | MAR         | median        |         0.5 |   1 |        0   |  0.187593    |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.1 |   5 |        0   |  0.00470511  |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.3 |   5 |        0   |  0.0217893   |                20 |
| heart-statlog  | mean       | MAR         | mice_improper |         0.5 |   5 |        0   |  0.0334767   |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.1 |   5 |        0   |  0.00493774  |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.3 |   5 |        0   |  0.0206348   |                20 |
| heart-statlog  | mean       | MAR         | mice_proper   |         0.5 |   5 |        0   |  0.0290203   |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.1 |   1 |        0   |  0.00507407  |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.3 |   1 |        0   | -0.00992593  |                20 |
| heart-statlog  | mean       | MCAR        | knn           |         0.5 |   1 |        0   | -0.0128889   |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.1 |   1 |        0   |  0.0364815   |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.3 |   1 |        0   |  0.0907407   |                20 |
| heart-statlog  | mean       | MCAR        | median        |         0.5 |   1 |        0   |  0.160556    |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.1 |   5 |        0   |  0.00331313  |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.3 |   5 |        0   | -0.00430564  |                20 |
| heart-statlog  | mean       | MCAR        | mice_improper |         0.5 |   5 |        0   | -0.00389379  |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.1 |   5 |        0   |  0.000520873 |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.3 |   5 |        0   | -0.00518889  |                20 |
| heart-statlog  | mean       | MCAR        | mice_proper   |         0.5 |   5 |        0   |  0.000726942 |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -1   | -0.0905319   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 | -0.0661178   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0   | -0.0417037   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 | -0.0172896   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        1   |  0.00712451  |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -1   | -0.31411     |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 | -0.239       |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0   | -0.163889    |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 | -0.0887783   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        1   | -0.0136677   |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -1   | -0.57045     |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 | -0.450484    |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0   | -0.330519    |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 | -0.210553    |                20 |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        1   | -0.0905871   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -1   | -0.0471616   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 | -0.0227474   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0   |  0.00166667  |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |  0.0260808   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        1   |  0.0504949   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -1   | -0.155221    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 | -0.0801106   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0   | -0.005       |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |  0.0701106   |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        1   |  0.145221    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -1   | -0.724191    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 | -0.604225    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0   | -0.484259    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0.5 | -0.364294    |                20 |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        1   | -0.244328    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   | -0.0774811   |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 | -0.053067    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   | -0.0286529   |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 | -0.00423878  |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |  0.0201753   |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   | -0.285364    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 | -0.210254    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   | -0.135143    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 | -0.0600326   |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |  0.015078    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   | -0.534208    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 | -0.414242    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   | -0.294276    |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 | -0.17431     |                20 |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   | -0.0543447   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   | -0.0806609   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 | -0.0562468   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   | -0.0318327   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 | -0.0074186   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |  0.0169955   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   | -0.279352    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 | -0.204241    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   | -0.129131    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 | -0.05402     |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |  0.0210907   |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   | -0.538953    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 | -0.418987    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   | -0.299022    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 | -0.179056    |                20 |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   | -0.0590901   |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.1 |   1 |        0   |  0.00100391  |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.3 |   1 |        0   | -0.000297069 |                20 |
| heart-statlog  | ols_slope  | MAR         | knn           |         0.5 |   1 |        0   |  8.27498e-05 |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.1 |   1 |        0   |  0.00567406  |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.3 |   1 |        0   |  0.0126344   |                20 |
| heart-statlog  | ols_slope  | MAR         | median        |         0.5 |   1 |        0   |  0.0150559   |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.1 |   5 |        0   |  0.000908634 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.3 |   5 |        0   |  0.0035011   |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_improper |         0.5 |   5 |        0   |  0.00500161  |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.1 |   5 |        0   |  0.000817942 |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.3 |   5 |        0   |  0.00317866  |                20 |
| heart-statlog  | ols_slope  | MAR         | mice_proper   |         0.5 |   5 |        0   |  0.0050753   |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.1 |   1 |        0   |  0.00104331  |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.3 |   1 |        0   |  0.00232524  |                20 |
| heart-statlog  | ols_slope  | MCAR        | knn           |         0.5 |   1 |        0   |  0.00343241  |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.1 |   1 |        0   |  0.000705636 |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.3 |   1 |        0   |  0.000298957 |                20 |
| heart-statlog  | ols_slope  | MCAR        | median        |         0.5 |   1 |        0   |  0.00200834  |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.1 |   5 |        0   |  0.00087918  |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.3 |   5 |        0   |  0.00193881  |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_improper |         0.5 |   5 |        0   |  0.0031886   |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.1 |   5 |        0   |  0.000719003 |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.3 |   5 |        0   |  0.00171652  |                20 |
| heart-statlog  | ols_slope  | MCAR        | mice_proper   |         0.5 |   5 |        0   |  0.00315722  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |  0.00213812  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |  0.00166482  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |  0.00119153  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |  0.000718237 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |  0.000244943 |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |  0.00455335  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |  0.00435978  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |  0.00416621  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |  0.00397265  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |  0.00377908  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |  0.00243554  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |  0.00221586  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |  0.00199617  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |  0.00177648  |                20 |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |  0.0015568   |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |  0.00146033  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |  0.001025    |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |  0.000589664 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |  0.000154331 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   | -0.000281002 |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |  0.00339564  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |  0.00308046  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |  0.00276529  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |  0.00245012  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |  0.00213495  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |  0.0044967   |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |  0.00447961  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |  0.00446252  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |  0.00444544  |                20 |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |  0.00442835  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |  0.00237794  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |  0.00205369  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |  0.00172943  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |  0.00140517  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |  0.00108092  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |  0.0048034   |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |  0.00458985  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |  0.00437629  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |  0.00416274  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |  0.00394919  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |  0.00499164  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |  0.00517619  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |  0.00536074  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |  0.00554529  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |  0.00572984  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |  0.00227842  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |  0.00189678  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |  0.00151514  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |  0.00113349  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |  0.000751852 |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |  0.00484583  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |  0.00471759  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |  0.00458934  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |  0.0044611   |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |  0.00433285  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |  0.00431037  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |  0.00442164  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |  0.00453292  |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |  0.0046442   |                20 |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |  0.00475547  |                20 |

## MNAR coverage by delta

| dataset        | estimand   | mechanism   | method        |   mask_rate |   m |   delta_sd |   coverage |   coverage_mc_se |   successful_runs |   failed_runs |   attempted_runs | complete_100_seed_cell   |
|:---------------|:-----------|:------------|:--------------|------------:|----:|-----------:|-----------:|-----------------:|------------------:|--------------:|-----------------:|:-------------------------|
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.3 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | knn           |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.1 |   1 |        1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.3 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | median        |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |       0.1  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0.3  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |       0.3  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |       0.35 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |       0.4  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0.45 |        0.111243  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0.6  |        0.109545  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |       0.7  |        0.10247   |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0.65 |        0.106654  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| cylinder-bands | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |       -0.5 |       0.25 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.25 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.3 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | knn           |         0.5 |   1 |        1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.1 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.3 |   1 |        1   |       0.05 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | median        |         0.5 |   1 |        1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -1   |       0.2  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_improper |         0.5 |   5 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       0.15 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0   |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       0    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | mean       | MNAR        | mice_proper   |         0.5 |   5 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -1   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |       -0.5 |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0   |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.3 |   1 |        1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -1   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |       -0.5 |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0   |       0.9  |        0.067082  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        0.5 |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | knn           |         0.5 |   1 |        1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.1 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.3 |   1 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -1   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |       -0.5 |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0   |       0.75 |        0.0968246 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        0.5 |       0.8  |        0.0894427 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | median        |         0.5 |   1 |        1   |       0.85 |        0.0798436 |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -1   |       0.95 |        0.048734  |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_improper |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.1 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.3 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -1   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |       -0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0   |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        0.5 |       1    |        0         |                20 |             0 |               20 | False                    |
| heart-statlog  | ols_slope  | MNAR        | mice_proper   |         0.5 |   5 |        1   |       1    |        0         |                20 |             0 |               20 | False                    |
