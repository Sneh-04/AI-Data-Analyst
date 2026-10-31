# Real-Dataset Benchmark Headline Summary


## Rules Summary


Source CSV: `rules_summary.csv`




| protocol            | dataset              | placement                             | exclusion_reason                         | study_labels                                                          |
|---------------------|----------------------|---------------------------------------|------------------------------------------|-----------------------------------------------------------------------|
| A                   | adult                | headline                              | nan                                      | nan                                                                   |
| A                   | bank-marketing       | headline                              | nan                                      | nan                                                                   |
| A                   | breast-w             | headline                              | nan                                      | nan                                                                   |
| A                   | credit-approval      | headline                              | nan                                      | nan                                                                   |
| A                   | credit-g             | headline                              | nan                                      | nan                                                                   |
| A                   | cylinder-bands       | headline                              | nan                                      | marginal: 7 retained columns, 2 numeric                               |
| A                   | dermatology          | supplementary                         | no saved Protocol A result available     | nan                                                                   |
| A                   | diabetes             | supplementary                         | only 3 complete retained columns (<5)    | sentinel-coded missingness (zeros treated as missing), not native NaN |
| A                   | heart-statlog        | headline                              | nan                                      | nan                                                                   |
| A                   | hepatitis            | supplementary                         | only 4 complete retained columns (<5)    | nan                                                                   |
| A                   | mushroom             | supplementary                         | no saved Protocol A result available     | nan                                                                   |
| A                   | pc1                  | headline                              | nan                                      | nan                                                                   |
| A                   | soybean              | supplementary                         | no saved Protocol A result available     | nan                                                                   |
| A                   | telco-customer-churn | headline                              | nan                                      | nan                                                                   |
| A                   | wine-quality-red     | headline                              | nan                                      | nan                                                                   |
| B downstream        | adult                | headline                              | nan                                      | negligible natural missingness                                        |
| B downstream        | heart-statlog        | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | breast-w             | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | hepatitis            | headline                              | nan                                      | nan                                                                   |
| B downstream        | cylinder-bands       | headline                              | nan                                      | nan                                                                   |
| B downstream        | soybean              | headline                              | nan                                      | nan                                                                   |
| B downstream        | credit-approval      | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | dermatology          | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | mushroom             | supplementary                         | mean-imputer accuracy 1 >= 0.999 ceiling | nan                                                                   |
| B downstream        | credit-g             | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | bank-marketing       | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | wine-quality-red     | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | diabetes             | headline                              | nan                                      | sentinel-coded missingness (zeros treated as missing), not native NaN |
| B downstream        | telco-customer-churn | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B downstream        | pc1                  | supplementary                         | no saved Protocol B result available     | negligible natural missingness                                        |
| B held-out recovery | nan                  | include all saved Protocol B datasets | nan                                      | nan                                                                   |



## Dataset Summary


Source CSV: `dataset_summary.csv`




| name                 |   n_rows |   n_numeric |   n_categorical |   natural_missing_fraction | load_status   | protocol_a_status   | protocol_b_status   | source_dir                        | study_labels                                                          |
|----------------------|----------|-------------|-----------------|----------------------------|---------------|---------------------|---------------------|-----------------------------------|-----------------------------------------------------------------------|
| adult                |    48842 |           6 |               8 |                     0.0095 | loaded        | completed           | completed           | stage2                            | negligible natural missingness                                        |
| bank-marketing       |    45211 |           7 |               9 |                     0      | loaded        | completed           | not_requested       | stage2_rerun/bank-marketing       | negligible natural missingness                                        |
| breast-w             |      699 |           9 |               0 |                     0.0025 | loaded        | completed           | not_requested       | stage2_rerun/breast-w             | negligible natural missingness                                        |
| credit-approval      |      690 |           6 |               9 |                     0.0065 | loaded        | completed           | not_requested       | stage2_rerun/credit-approval      | negligible natural missingness                                        |
| credit-g             |     1000 |           7 |              13 |                     0      | loaded        | completed           | not_requested       | stage2_rerun/credit-g             | negligible natural missingness                                        |
| cylinder-bands       |      540 |          18 |              19 |                     0.05   | loaded        | completed           | completed           | stage2_rerun/cylinder-bands       | nan                                                                   |
| dermatology          |      366 |           1 |              33 |                     0.0006 | not_run       | not_run             | not_run             | nan                               | negligible natural missingness                                        |
| diabetes             |      768 |           8 |               0 |                     0.1061 | loaded        | completed           | completed           | stage2_rerun/diabetes             | sentinel-coded missingness (zeros treated as missing), not native NaN |
| heart-statlog        |      270 |          13 |               0 |                     0      | loaded        | completed           | not_requested       | stage2_rerun/heart-statlog        | negligible natural missingness                                        |
| hepatitis            |      155 |           6 |              13 |                     0.0567 | loaded        | completed           | completed           | stage2_rerun/hepatitis            | nan                                                                   |
| mushroom             |     8124 |           0 |              22 |                     0.0139 | loaded        | not_requested       | completed           | stage1                            | nan                                                                   |
| pc1                  |     1109 |          21 |               0 |                     0      | loaded        | completed           | not_requested       | stage2_rerun/pc1                  | negligible natural missingness                                        |
| soybean              |      683 |           0 |              35 |                     0.0978 | loaded        | not_requested       | completed           | stage1                            | nan                                                                   |
| telco-customer-churn |     7043 |           4 |              15 |                     0.0008 | loaded        | completed           | not_requested       | stage2_rerun/telco-customer-churn | negligible natural missingness                                        |
| wine-quality-red     |     1599 |          11 |               0 |                     0      | loaded        | completed           | not_requested       | stage2_rerun/wine-quality-red     | negligible natural missingness                                        |



## Protocol A Win Tie Loss Vs Best Baseline


Source CSV: `protocol_a_win_tie_loss_vs_best_baseline.csv`




| method            |   win |   tie |   loss |
|-------------------|-------|-------|--------|
| iterative_single  |     0 |    72 |     18 |
| knn5              |     0 |    20 |     70 |
| mean              |     0 |    14 |     76 |
| median            |     0 |     3 |     87 |
| mice_multiple_NEW |    18 |    12 |     60 |



## Protocol A Effect Sizes


Source CSV: `protocol_a_effect_sizes.csv`




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



## Protocol A Dataset Level Significance


Source CSV: `protocol_a_dataset_level_significance.csv`


Categorical metrics: harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.


| metric                 | mechanism   | vs               |   n_datasets | low_power_n_lt_10   |   mean_loss_diff |    p_value |   p_holm |   n_comparisons_in_holm_family |   min_attainable_two_sided_exact_p | can_reach_0_05_after_holm   | power_note                                                       |
|------------------------|-------------|------------------|--------------|---------------------|------------------|------------|----------|--------------------------------|------------------------------------|-----------------------------|------------------------------------------------------------------|
| numeric_rmse           | MAR         | mean             |           10 | False               |      -0.103118   | 0.322266   | 1        |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MAR         | median           |           10 | False               |      -0.201314   | 0.0195312  | 0.371094 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MAR         | knn5             |           10 | False               |       0.00526968 | 0.695312   | 1        |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MAR         | iterative_single |           10 | False               |       0.0977599  | 0.00195312 | 0.046875 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MCAR        | mean             |           10 | False               |      -0.0870562  | 0.375      | 1        |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MCAR        | median           |           10 | False               |      -0.157119   | 0.0371094  | 0.5625   |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MCAR        | knn5             |           10 | False               |       0.0186131  | 0.0839844  | 0.923828 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MCAR        | iterative_single |           10 | False               |       0.0523204  | 0.00195312 | 0.046875 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MNAR        | mean             |           10 | False               |      -0.239011   | 0.00195312 | 0.046875 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MNAR        | median           |           10 | False               |      -0.360178   | 0.00195312 | 0.046875 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MNAR        | knn5             |           10 | False               |      -0.0814421  | 0.00195312 | 0.046875 |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| numeric_rmse           | MNAR        | iterative_single |           10 | False               |      -0.0327748  | 0.0371094  | 0.5625   |                             24 |                         0.00195312 | True                        | n=10; p_min=0.00195312; Holm m=24; p_min*m=0.046875; attainable. |
| categorical_error_rate | MAR         | mean             |            6 | True                |      -0.0141784  | 0.84375    | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MAR         | median           |            6 | True                |       0.0897011  | 0.3125     | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MAR         | knn5             |            6 | True                |       0.135142   | 0.0625     | 0.75     |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MAR         | iterative_single |            6 | True                |       0.102083   | 0.03125    | 0.5625   |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MCAR        | mean             |            6 | True                |      -0.0078001  | 1          | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MCAR        | median           |            6 | True                |       0.0839459  | 0.3125     | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MCAR        | knn5             |            6 | True                |       0.117244   | 0.03125    | 0.5625   |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MCAR        | iterative_single |            6 | True                |       0.0974286  | 0.03125    | 0.5625   |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MNAR        | mean             |            6 | True                |      -0.0964848  | 0.21875    | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MNAR        | median           |            6 | True                |      -0.0673458  | 0.4375     | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MNAR        | knn5             |            6 | True                |       0.0846641  | 0.03125    | 0.5625   |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |
| categorical_error_rate | MNAR        | iterative_single |            6 | True                |       0.0419089  | 0.3125     | 1        |                             24 |                         0.03125    | False                       | n=6; p_min=0.03125; Holm m=24; p_min*m=0.75; cannot reach 0.05.  |



## Protocol A Project Mice Uncertainty Summary


Source CSV: `protocol_a_project_mice_uncertainty_summary.csv`


Coverage target: nominal 0.90.


| mechanism   | metric                         |   n_headline_datasets |   minimum |   median |   maximum | coverage_target   |
|-------------|--------------------------------|-----------------------|-----------|----------|-----------|-------------------|
| MAR         | uncertainty_spearman_numeric   |                    10 |  0.309068 | 0.797994 |  0.945903 | nan               |
| MAR         | uncertainty_coverage90_numeric |                    10 |  0.743799 | 0.832531 |  0.899923 | nominal 0.90      |
| MCAR        | uncertainty_spearman_numeric   |                    10 |  0.467402 | 0.821234 |  0.922666 | nan               |
| MCAR        | uncertainty_coverage90_numeric |                    10 |  0.818163 | 0.877492 |  0.907406 | nominal 0.90      |
| MNAR        | uncertainty_spearman_numeric   |                    10 |  0.237128 | 0.806935 |  0.898539 | nan               |
| MNAR        | uncertainty_coverage90_numeric |                    10 |  0.459746 | 0.596877 |  0.641079 | nominal 0.90      |



## Protocol A Project Mice Uncertainty


Source CSV: `protocol_a_project_mice_uncertainty.csv`


Coverage target: nominal 0.90.


| dataset              | mechanism   |   uncertainty_spearman_numeric |   uncertainty_coverage90_numeric | coverage_nominal_target   |
|----------------------|-------------|--------------------------------|----------------------------------|---------------------------|
| adult                | MAR         |                       0.945903 |                         0.856699 | nominal 0.90              |
| adult                | MCAR        |                       0.922666 |                         0.889354 | nominal 0.90              |
| adult                | MNAR        |                       0.818843 |                         0.635325 | nominal 0.90              |
| bank-marketing       | MAR         |                       0.920177 |                         0.894381 | nominal 0.90              |
| bank-marketing       | MCAR        |                       0.901829 |                         0.899774 | nominal 0.90              |
| bank-marketing       | MNAR        |                       0.898539 |                         0.530681 | nominal 0.90              |
| breast-w             | MAR         |                       0.309068 |                         0.743799 | nominal 0.90              |
| breast-w             | MCAR        |                       0.467402 |                         0.844745 | nominal 0.90              |
| breast-w             | MNAR        |                       0.237128 |                         0.464314 | nominal 0.90              |
| credit-approval      | MAR         |                       0.768541 |                         0.807261 | nominal 0.90              |
| credit-approval      | MCAR        |                       0.764618 |                         0.877562 | nominal 0.90              |
| credit-approval      | MNAR        |                       0.676303 |                         0.459746 | nominal 0.90              |
| credit-g             | MAR         |                       0.835927 |                         0.848124 | nominal 0.90              |
| credit-g             | MCAR        |                       0.836883 |                         0.844196 | nominal 0.90              |
| credit-g             | MNAR        |                       0.854615 |                         0.508706 | nominal 0.90              |
| cylinder-bands       | MAR         |                       0.754319 |                         0.860521 | nominal 0.90              |
| cylinder-bands       | MCAR        |                       0.750824 |                         0.877422 | nominal 0.90              |
| cylinder-bands       | MNAR        |                       0.732114 |                         0.633538 | nominal 0.90              |
| heart-statlog        | MAR         |                       0.758479 |                         0.791046 | nominal 0.90              |
| heart-statlog        | MCAR        |                       0.798473 |                         0.818163 | nominal 0.90              |
| heart-statlog        | MNAR        |                       0.794311 |                         0.594179 | nominal 0.90              |
| pc1                  | MAR         |                       0.800691 |                         0.749737 | nominal 0.90              |
| pc1                  | MCAR        |                       0.837454 |                         0.907406 | nominal 0.90              |
| pc1                  | MNAR        |                       0.81892  |                         0.641079 | nominal 0.90              |
| telco-customer-churn | MAR         |                       0.795297 |                         0.816938 | nominal 0.90              |
| telco-customer-churn | MCAR        |                       0.805585 |                         0.821217 | nominal 0.90              |
| telco-customer-churn | MNAR        |                       0.795027 |                         0.599575 | nominal 0.90              |
| wine-quality-red     | MAR         |                       0.865936 |                         0.899923 | nominal 0.90              |
| wine-quality-red     | MCAR        |                       0.86752  |                         0.901417 | nominal 0.90              |
| wine-quality-red     | MNAR        |                       0.857693 |                         0.613644 | nominal 0.90              |



## Protocol B Downstream Headline


Source CSV: `protocol_b_downstream_headline.csv`


Note: Datasets with <1% natural missingness (negligible natural missingness): adult, bank-marketing, breast-w, credit-approval, credit-g, dermatology, heart-statlog, pc1, telco-customer-churn, wine-quality-red.
Categorical metrics: harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.


| dataset        | task_type      | method            |   accuracy |        auc |   heldout_numeric_rmse |   heldout_categorical_accuracy |   heldout_categorical_error_rate | study_labels                                                          |   exclusion_reason |
|----------------|----------------|-------------------|------------|------------|------------------------|--------------------------------|----------------------------------|-----------------------------------------------------------------------|--------------------|
| adult          | classification | iterative_single  |   0.832767 |   0.903043 |               1.01817  |                       0.330733 |                         0.669267 | negligible natural missingness                                        |                nan |
| adult          | classification | knn5              |   0.833433 |   0.903269 |               0.964436 |                       0.506724 |                         0.493276 | negligible natural missingness                                        |                nan |
| adult          | classification | mean              |   0.832683 |   0.902813 |               1.0216   |                       0.326151 |                         0.673849 | negligible natural missingness                                        |                nan |
| adult          | classification | median            |   0.832117 |   0.902874 |               1.00935  |                       0.532444 |                         0.467556 | negligible natural missingness                                        |                nan |
| adult          | classification | mice_multiple_NEW |   0.833667 |   0.902517 |               0.982236 |                       0.300903 |                         0.699097 | negligible natural missingness                                        |                nan |
| cylinder-bands | classification | iterative_single  |   0.818056 |   0.897375 |               0.912191 |                       0.612719 |                         0.387281 | nan                                                                   |                nan |
| cylinder-bands | classification | knn5              |   0.8125   |   0.885204 |               0.906089 |                       0.721591 |                         0.278409 | nan                                                                   |                nan |
| cylinder-bands | classification | mean              |   0.817284 |   0.896476 |               0.99784  |                       0.569688 |                         0.430312 | nan                                                                   |                nan |
| cylinder-bands | classification | median            |   0.811111 |   0.888999 |               1.02534  |                       0.671494 |                         0.328506 | nan                                                                   |                nan |
| cylinder-bands | classification | mice_multiple_NEW |   0.820679 |   0.897772 |               0.978866 |                       0.573682 |                         0.426318 | nan                                                                   |                nan |
| diabetes       | classification | iterative_single  |   0.752718 |   0.82633  |               0.926323 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | knn5              |   0.751188 |   0.824651 |               0.948917 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | mean              |   0.754671 |   0.827938 |               0.999158 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | median            |   0.757374 |   0.829386 |               1.02521  |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | mice_multiple_NEW |   0.755975 |   0.827444 |               0.981732 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| hepatitis      | classification | iterative_single  |   0.856452 |   0.881647 |               0.866708 |                       0.755715 |                         0.244285 | nan                                                                   |                nan |
| hepatitis      | classification | knn5              |   0.862366 |   0.891165 |               0.934253 |                       0.757384 |                         0.242616 | nan                                                                   |                nan |
| hepatitis      | classification | mean              |   0.842473 |   0.875706 |               1.00256  |                       0.718156 |                         0.281844 | nan                                                                   |                nan |
| hepatitis      | classification | median            |   0.839785 |   0.871177 |               1.07557  |                       0.724097 |                         0.275903 | nan                                                                   |                nan |
| hepatitis      | classification | mice_multiple_NEW |   0.846774 |   0.88397  |               1.02246  |                       0.715782 |                         0.284218 | nan                                                                   |                nan |
| soybean        | classification | iterative_single  |   0.933752 | nan        |             nan        |                       0.790361 |                         0.209639 | nan                                                                   |                nan |
| soybean        | classification | knn5              |   0.930217 | nan        |             nan        |                       0.830455 |                         0.169545 | nan                                                                   |                nan |
| soybean        | classification | mean              |   0.932411 | nan        |             nan        |                       0.610995 |                         0.389005 | nan                                                                   |                nan |
| soybean        | classification | median            |   0.92875  | nan        |             nan        |                       0.685584 |                         0.314416 | nan                                                                   |                nan |
| soybean        | classification | mice_multiple_NEW |   0.930461 | nan        |             nan        |                       0.749611 |                         0.250389 | nan                                                                   |                nan |



## Protocol B Heldout Recovery All


Source CSV: `protocol_b_heldout_recovery_all.csv`


Note: Datasets with <1% natural missingness (negligible natural missingness): adult, bank-marketing, breast-w, credit-approval, credit-g, dermatology, heart-statlog, pc1, telco-customer-churn, wine-quality-red.
Categorical metrics: harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.


| dataset        | task_type      | method            |   accuracy |        auc |   heldout_numeric_rmse |   heldout_categorical_accuracy |   heldout_categorical_error_rate | study_labels                                                          |   exclusion_reason |
|----------------|----------------|-------------------|------------|------------|------------------------|--------------------------------|----------------------------------|-----------------------------------------------------------------------|--------------------|
| adult          | classification | iterative_single  |   0.832767 |   0.903043 |               1.01817  |                       0.330733 |                         0.669267 | negligible natural missingness                                        |                nan |
| adult          | classification | knn5              |   0.833433 |   0.903269 |               0.964436 |                       0.506724 |                         0.493276 | negligible natural missingness                                        |                nan |
| adult          | classification | mean              |   0.832683 |   0.902813 |               1.0216   |                       0.326151 |                         0.673849 | negligible natural missingness                                        |                nan |
| adult          | classification | median            |   0.832117 |   0.902874 |               1.00935  |                       0.532444 |                         0.467556 | negligible natural missingness                                        |                nan |
| adult          | classification | mice_multiple_NEW |   0.833667 |   0.902517 |               0.982236 |                       0.300903 |                         0.699097 | negligible natural missingness                                        |                nan |
| cylinder-bands | classification | iterative_single  |   0.818056 |   0.897375 |               0.912191 |                       0.612719 |                         0.387281 | nan                                                                   |                nan |
| cylinder-bands | classification | knn5              |   0.8125   |   0.885204 |               0.906089 |                       0.721591 |                         0.278409 | nan                                                                   |                nan |
| cylinder-bands | classification | mean              |   0.817284 |   0.896476 |               0.99784  |                       0.569688 |                         0.430312 | nan                                                                   |                nan |
| cylinder-bands | classification | median            |   0.811111 |   0.888999 |               1.02534  |                       0.671494 |                         0.328506 | nan                                                                   |                nan |
| cylinder-bands | classification | mice_multiple_NEW |   0.820679 |   0.897772 |               0.978866 |                       0.573682 |                         0.426318 | nan                                                                   |                nan |
| diabetes       | classification | iterative_single  |   0.752718 |   0.82633  |               0.926323 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | knn5              |   0.751188 |   0.824651 |               0.948917 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | mean              |   0.754671 |   0.827938 |               0.999158 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | median            |   0.757374 |   0.829386 |               1.02521  |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| diabetes       | classification | mice_multiple_NEW |   0.755975 |   0.827444 |               0.981732 |                     nan        |                       nan        | sentinel-coded missingness (zeros treated as missing), not native NaN |                nan |
| hepatitis      | classification | iterative_single  |   0.856452 |   0.881647 |               0.866708 |                       0.755715 |                         0.244285 | nan                                                                   |                nan |
| hepatitis      | classification | knn5              |   0.862366 |   0.891165 |               0.934253 |                       0.757384 |                         0.242616 | nan                                                                   |                nan |
| hepatitis      | classification | mean              |   0.842473 |   0.875706 |               1.00256  |                       0.718156 |                         0.281844 | nan                                                                   |                nan |
| hepatitis      | classification | median            |   0.839785 |   0.871177 |               1.07557  |                       0.724097 |                         0.275903 | nan                                                                   |                nan |
| hepatitis      | classification | mice_multiple_NEW |   0.846774 |   0.88397  |               1.02246  |                       0.715782 |                         0.284218 | nan                                                                   |                nan |
| mushroom       | classification | iterative_single  |   1        |   1        |             nan        |                       0.473426 |                         0.526574 | nan                                                                   |                nan |
| mushroom       | classification | knn5              |   1        |   1        |             nan        |                       0.706491 |                         0.293509 | nan                                                                   |                nan |
| mushroom       | classification | mean              |   1        |   1        |             nan        |                       0.455008 |                         0.544992 | nan                                                                   |                nan |
| mushroom       | classification | median            |   1        |   1        |             nan        |                       0.54358  |                         0.45642  | nan                                                                   |                nan |
| mushroom       | classification | mice_multiple_NEW |   1        |   1        |             nan        |                       0.471603 |                         0.528397 | nan                                                                   |                nan |
| soybean        | classification | iterative_single  |   0.933752 | nan        |             nan        |                       0.790361 |                         0.209639 | nan                                                                   |                nan |
| soybean        | classification | knn5              |   0.930217 | nan        |             nan        |                       0.830455 |                         0.169545 | nan                                                                   |                nan |
| soybean        | classification | mean              |   0.932411 | nan        |             nan        |                       0.610995 |                         0.389005 | nan                                                                   |                nan |
| soybean        | classification | median            |   0.92875  | nan        |             nan        |                       0.685584 |                         0.314416 | nan                                                                   |                nan |
| soybean        | classification | mice_multiple_NEW |   0.930461 | nan        |             nan        |                       0.749611 |                         0.250389 | nan                                                                   |                nan |



## Protocol B Effect Sizes


Source CSV: `protocol_b_effect_sizes.csv`


Note: Datasets with <1% natural missingness (negligible natural missingness): adult, bank-marketing, breast-w, credit-approval, credit-g, dermatology, heart-statlog, pc1, telco-customer-churn, wine-quality-red.
Categorical metrics: harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.


| metric                         | metric_direction   | vs               |   n_datasets |   median_project_minus_baseline_metric |   bootstrap_95_ci_low |   bootstrap_95_ci_high |   datasets_project_better |   datasets_project_worse |   datasets_tied_within_1_percent |
|--------------------------------|--------------------|------------------|--------------|----------------------------------------|-----------------------|------------------------|---------------------------|--------------------------|----------------------------------|
| accuracy                       | higher             | mean             |            5 |                            0.00130436  |          -0.00195005  |             0.00430108 |                         0 |                        0 |                                5 |
| accuracy                       | higher             | median           |            5 |                            0.00171121  |          -0.00139915  |             0.0095679  |                         1 |                        0 |                                4 |
| accuracy                       | higher             | knn5             |            5 |                            0.000244204 |          -0.0155914   |             0.00817901 |                         1 |                        1 |                                3 |
| accuracy                       | higher             | iterative_single |            5 |                            0.0009      |          -0.00967742  |             0.00325736 |                         0 |                        1 |                                4 |
| auc                            | higher             | mean             |            4 |                            0.00050013  |          -0.000494235 |             0.00826389 |                         0 |                        0 |                                4 |
| auc                            | higher             | median           |            4 |                            0.00420818  |          -0.00194249  |             0.0127937  |                         1 |                        0 |                                3 |
| auc                            | higher             | knn5             |            4 |                            0.00102016  |          -0.00719444  |             0.0125682  |                         1 |                        0 |                                3 |
| auc                            | higher             | iterative_single |            4 |                            0.000755297 |          -0.000525553 |             0.00232341 |                         0 |                        0 |                                4 |
| heldout_numeric_rmse           | lower              | mean             |            4 |                           -0.0182001   |          -0.03936     |             0.0198925  |                         3 |                        1 |                                0 |
| heldout_numeric_rmse           | lower              | median           |            4 |                           -0.0449742   |          -0.0531131   |            -0.0271178  |                         4 |                        0 |                                0 |
| heldout_numeric_rmse           | lower              | knn5             |            4 |                            0.0527956   |           0.0178001   |             0.0882026  |                         0 |                        4 |                                0 |
| heldout_numeric_rmse           | lower              | iterative_single |            4 |                            0.0610423   |          -0.0359374   |             0.155749   |                         1 |                        3 |                                0 |
| heldout_categorical_accuracy   | higher             | mean             |            5 |                            0.00399433  |          -0.0252485   |             0.138617   |                         2 |                        1 |                                2 |
| heldout_categorical_accuracy   | higher             | median           |            5 |                           -0.0719768   |          -0.231541    |             0.0640277  |                         1 |                        4 |                                0 |
| heldout_categorical_accuracy   | higher             | knn5             |            5 |                           -0.147909    |          -0.234888    |            -0.0416021  |                         0 |                        5 |                                0 |
| heldout_categorical_accuracy   | higher             | iterative_single |            5 |                           -0.0390368   |          -0.0407498   |            -0.00182252 |                         0 |                        4 |                                1 |
| heldout_categorical_error_rate | lower              | mean             |            5 |                           -0.00399433  |          -0.138617    |             0.0252485  |                         2 |                        1 |                                2 |
| heldout_categorical_error_rate | lower              | median           |            5 |                            0.0719768   |          -0.0640277   |             0.231541   |                         1 |                        4 |                                0 |
| heldout_categorical_error_rate | lower              | knn5             |            5 |                            0.147909    |           0.0416021   |             0.234888   |                         0 |                        5 |                                0 |
| heldout_categorical_error_rate | lower              | iterative_single |            5 |                            0.0390368   |           0.00182252  |             0.0407498  |                         0 |                        4 |                                1 |



## Protocol B Dataset Level Significance


Source CSV: `protocol_b_dataset_level_significance.csv`


Note: Datasets with <1% natural missingness (negligible natural missingness): adult, bank-marketing, breast-w, credit-approval, credit-g, dermatology, heart-statlog, pc1, telco-customer-churn, wine-quality-red.
Categorical metrics: harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.


| metric                         | vs               |   n_datasets | low_power_n_lt_10   |   mean_loss_diff |   p_value |   p_holm |   n_comparisons_in_holm_family |   min_attainable_two_sided_exact_p | can_reach_0_05_after_holm   | power_note                                                     |
|--------------------------------|------------------|--------------|---------------------|------------------|-----------|----------|--------------------------------|------------------------------------|-----------------------------|----------------------------------------------------------------|
| accuracy                       | mean             |            5 | True                |     -0.00160676  |    0.3125 |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| accuracy                       | median           |            5 | True                |     -0.00368384  |    0.125  |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| accuracy                       | knn5             |            5 | True                |      0.000429637 |    0.625  |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| accuracy                       | iterative_single |            5 | True                |      0.00123751  |    0.8125 |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| heldout_numeric_rmse           | mean             |            4 | True                |     -0.013967    |    0.625  |     1    |                             12 |                             0.125  | False                       | n=4; p_min=0.125; Holm m=12; p_min*m=1.5; cannot reach 0.05.   |
| heldout_numeric_rmse           | median           |            4 | True                |     -0.0425448   |    0.125  |     1    |                             12 |                             0.125  | False                       | n=4; p_min=0.125; Holm m=12; p_min*m=1.5; cannot reach 0.05.   |
| heldout_numeric_rmse           | knn5             |            4 | True                |      0.0528985   |    0.125  |     1    |                             12 |                             0.125  | False                       | n=4; p_min=0.125; Holm m=12; p_min*m=1.5; cannot reach 0.05.   |
| heldout_numeric_rmse           | iterative_single |            4 | True                |      0.0604739   |    0.25   |     1    |                             12 |                             0.125  | False                       | n=4; p_min=0.125; Holm m=12; p_min*m=1.5; cannot reach 0.05.   |
| heldout_categorical_error_rate | mean             |            5 | True                |     -0.0263168   |    0.625  |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| heldout_categorical_error_rate | median           |            5 | True                |      0.0691234   |    0.1875 |     1    |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| heldout_categorical_error_rate | knn5             |            5 | True                |      0.142213    |    0.0625 |     0.75 |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |
| heldout_categorical_error_rate | iterative_single |            5 | True                |      0.0302743   |    0.0625 |     0.75 |                             12 |                             0.0625 | False                       | n=5; p_min=0.0625; Holm m=12; p_min*m=0.75; cannot reach 0.05. |


