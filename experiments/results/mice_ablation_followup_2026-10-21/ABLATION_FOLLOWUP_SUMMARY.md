# MICE Ablation Follow-up

**POST-HOC EXPLORATORY. Descriptive only; no p-values or new significance claims.**

All follow-up tables are labeled: **5-dataset exploratory subset, not the 10 declared headline datasets.** The m-dependence fit below is intentionally calculated from the saved 10-dataset ablation CSVs as separately requested; it is not a result of the five-dataset follow-up run.

## Corrected uncertainty coverage (nominal target 0.90)

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** Coverage interval quantiles are adaptive to m; every row states the nominal target.

Source CSV: `adult/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv`

| mechanism   | variant            |   minimum |   median |   maximum | nominal_target   |
|-------------|--------------------|-----------|----------|-----------|------------------|
| MAR         | project_hybrid_m20 |     0.678 |    0.755 |     0.898 | nominal 0.90     |
| MAR         | project_m20        |     0.663 |    0.743 |     0.869 | nominal 0.90     |
| MAR         | project_m5         |     0.731 |    0.796 |     0.858 | nominal 0.90     |
| MAR         | project_m50        |     0.630 |    0.744 |     0.885 | nominal 0.90     |
| MCAR        | project_hybrid_m20 |     0.784 |    0.863 |     0.934 | nominal 0.90     |
| MCAR        | project_m20        |     0.727 |    0.892 |     0.934 | nominal 0.90     |
| MCAR        | project_m5         |     0.818 |    0.879 |     0.916 | nominal 0.90     |
| MCAR        | project_m50        |     0.679 |    0.904 |     0.944 | nominal 0.90     |
| MNAR        | project_hybrid_m20 |     0.366 |    0.466 |     0.585 | nominal 0.90     |
| MNAR        | project_m20        |     0.355 |    0.465 |     0.654 | nominal 0.90     |
| MNAR        | project_m5         |     0.410 |    0.599 |     0.670 | nominal 0.90     |
| MNAR        | project_m50        |     0.345 |    0.434 |     0.651 | nominal 0.90     |

## Corrected versus previously saved coverage medians (m20/m50)

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** The saved medians use the old m=5 interval quantile for m20/m50; the follow-up medians use the corrected m-dependent quantile.

Source CSV: `adult/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, adult/ablation.csv, bank-marketing/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, credit-g/ablation.csv, cylinder-bands/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, telco-customer-churn/ablation.csv, wine-quality-red/ablation.csv`

| mechanism   | variant     |   corrected_median |   saved_old_median |
|-------------|-------------|--------------------|--------------------|
| MAR         | project_m20 |              0.743 |              0.901 |
| MAR         | project_m50 |              0.744 |              0.929 |
| MCAR        | project_m20 |              0.892 |              0.958 |
| MCAR        | project_m50 |              0.904 |              0.964 |
| MNAR        | project_m20 |              0.465 |              0.681 |
| MNAR        | project_m50 |              0.434 |              0.696 |

## RMSE-ratio aggregate comparisons

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** Ratios are medians across datasets within mechanism and variant; lower ratios are counted separately against project_m5 and project_deterministic.

Source CSV: `adult/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv`

| mechanism   | variant                          |   median_rmse_ratio_vs_mean |   n_datasets |   datasets_lower_ratio_than_project_m5 |   datasets_lower_ratio_than_deterministic |
|-------------|----------------------------------|-----------------------------|--------------|----------------------------------------|-------------------------------------------|
| MAR         | iterative_single_as_is           |                       0.930 |            5 |                                      4 |                                         2 |
| MAR         | iterative_single_posterior_false |                       0.930 |            5 |                                      4 |                                         2 |
| MAR         | iterative_single_posterior_true  |                       1.090 |            5 |                                      1 |                                         1 |
| MAR         | project_deterministic            |                       0.930 |            5 |                                      4 |                                         0 |
| MAR         | project_deterministic_no_bounds  |                       0.930 |            5 |                                      4 |                                         2 |
| MAR         | project_hybrid_m20               |                       0.930 |            5 |                                      4 |                                         0 |
| MAR         | project_m20                      |                       0.963 |            5 |                                      5 |                                         2 |
| MAR         | project_m5                       |                       0.978 |            5 |                                      0 |                                         1 |
| MAR         | project_m50                      |                       0.957 |            5 |                                      5 |                                         2 |
| MAR         | project_m50_no_bounds            |                       0.941 |            5 |                                      5 |                                         3 |
| MCAR        | iterative_single_as_is           |                       0.913 |            5 |                                      5 |                                         1 |
| MCAR        | iterative_single_posterior_false |                       0.913 |            5 |                                      5 |                                         1 |
| MCAR        | iterative_single_posterior_true  |                       1.221 |            5 |                                      0 |                                         0 |
| MCAR        | project_deterministic            |                       0.905 |            5 |                                      5 |                                         0 |
| MCAR        | project_deterministic_no_bounds  |                       0.913 |            5 |                                      5 |                                         1 |
| MCAR        | project_hybrid_m20               |                       0.905 |            5 |                                      5 |                                         0 |
| MCAR        | project_m20                      |                       0.952 |            5 |                                      5 |                                         0 |
| MCAR        | project_m5                       |                       0.990 |            5 |                                      0 |                                         0 |
| MCAR        | project_m50                      |                       0.945 |            5 |                                      5 |                                         0 |
| MCAR        | project_m50_no_bounds            |                       0.911 |            5 |                                      5 |                                         2 |
| MNAR        | iterative_single_as_is           |                       0.928 |            5 |                                      1 |                                         0 |
| MNAR        | iterative_single_posterior_false |                       0.928 |            5 |                                      1 |                                         0 |
| MNAR        | iterative_single_posterior_true  |                       0.973 |            5 |                                      0 |                                         0 |
| MNAR        | project_deterministic            |                       0.927 |            5 |                                      1 |                                         0 |
| MNAR        | project_deterministic_no_bounds  |                       0.928 |            5 |                                      1 |                                         0 |
| MNAR        | project_hybrid_m20               |                       0.927 |            5 |                                      1 |                                         0 |
| MNAR        | project_m20                      |                       0.903 |            5 |                                      4 |                                         5 |
| MNAR        | project_m5                       |                       0.913 |            5 |                                      0 |                                         4 |
| MNAR        | project_m50                      |                       0.902 |            5 |                                      4 |                                         5 |
| MNAR        | project_m50_no_bounds            |                       0.937 |            5 |                                      0 |                                         1 |

## Numeric RMSE reproduction checks

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** Exact dataset/mechanism/rate/trial/variant keys; tolerance is 1e-9.

Source CSV: `adult/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, adult/ablation.csv, bank-marketing/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, credit-g/ablation.csv, cylinder-bands/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, telco-customer-churn/ablation.csv, wine-quality-red/ablation.csv`

| variant               |   n_keys |   max_abs_difference |
|-----------------------|----------|----------------------|
| project_deterministic |       30 |                0.000 |
| project_m20           |       30 |                0.000 |
| project_m5            |       30 |                0.000 |
| project_m50           |       30 |                0.000 |

## Three-point descriptive m-dependence fit

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** Uses all 10 saved ablation datasets: squared RMSE ratio = a + b/m for m in {5, 20, 50}.

Source CSV: `adult/ablation.csv, bank-marketing/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, credit-g/ablation.csv, cylinder-bands/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, telco-customer-churn/ablation.csv, wine-quality-red/ablation.csv`

| mechanism   |   n_datasets |   median_a_asymptote |   median_b_slope |   median_asymptote_minus_deterministic_squared |
|-------------|--------------|----------------------|------------------|------------------------------------------------|
| MAR         |           10 |                0.918 |            0.412 |                                          0.040 |
| MCAR        |           10 |                0.898 |            0.427 |                                          0.081 |
| MNAR        |           10 |                0.805 |            0.064 |                                         -0.035 |

## Per-dataset three-point fit and single-draw sanity check

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** Uses all 10 saved ablation datasets. iterative_single_posterior_true is a sanity-check point only and is not part of the fit.

Source CSV: `adult/ablation.csv, bank-marketing/ablation.csv, breast-w/ablation.csv, credit-approval/ablation.csv, credit-g/ablation.csv, cylinder-bands/ablation.csv, heart-statlog/ablation.csv, pc1/ablation.csv, telco-customer-churn/ablation.csv, wine-quality-red/ablation.csv`

| dataset              | mechanism   |   a_asymptote |   b_slope |   deterministic_ratio_squared |   asymptote_minus_deterministic_squared |   single_draw_ratio_sanity_check | fit_description                                      |
|----------------------|-------------|---------------|-----------|-------------------------------|-----------------------------------------|----------------------------------|------------------------------------------------------|
| adult                | MAR         |         1.178 |     0.565 |                         1.057 |                                   0.121 |                            1.348 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| adult                | MCAR        |         1.046 |     0.581 |                         0.945 |                                   0.101 |                            1.349 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| adult                | MNAR        |         0.943 |     0.088 |                         0.957 |                                  -0.014 |                            1.038 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| bank-marketing       | MAR         |         1.068 |     0.451 |                         0.925 |                                   0.143 |                            1.363 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| bank-marketing       | MCAR        |         0.969 |     0.434 |                         0.869 |                                   0.100 |                            1.286 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| bank-marketing       | MNAR        |         0.848 |     0.053 |                         0.863 |                                  -0.016 |                            0.967 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| breast-w             | MAR         |         0.475 |     0.063 |                         0.487 |                                  -0.012 |                            0.808 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| breast-w             | MCAR        |         0.505 |     0.294 |                         0.436 |                                   0.069 |                            0.916 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| breast-w             | MNAR        |         0.532 |     0.057 |                         0.561 |                                  -0.029 |                            0.782 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-approval      | MAR         |         0.928 |     0.151 |                         0.892 |                                   0.036 |                            1.090 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-approval      | MCAR        |         1.084 |     0.659 |                         0.819 |                                   0.265 |                            1.317 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-approval      | MNAR        |         0.854 |     0.024 |                         0.899 |                                  -0.044 |                            0.973 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-g             | MAR         |         0.933 |     0.572 |                         0.867 |                                   0.066 |                            1.330 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-g             | MCAR        |         0.913 |     0.420 |                         0.817 |                                   0.096 |                            1.339 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| credit-g             | MNAR        |         0.801 |     0.071 |                         0.841 |                                  -0.040 |                            1.020 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| cylinder-bands       | MAR         |         1.026 |     0.880 |                         1.012 |                                   0.014 |                            1.415 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| cylinder-bands       | MCAR        |         1.010 |     0.853 |                         1.003 |                                   0.007 |                            1.456 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| cylinder-bands       | MNAR        |         0.922 |     0.109 |                         1.009 |                                  -0.087 |                            1.071 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| heart-statlog        | MAR         |         0.908 |     0.383 |                         0.864 |                                   0.043 |                            1.262 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| heart-statlog        | MCAR        |         0.883 |     0.485 |                         0.830 |                                   0.053 |                            1.221 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| heart-statlog        | MNAR        |         0.810 |     0.121 |                         0.860 |                                  -0.050 |                            1.069 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| pc1                  | MAR         |         0.616 |     0.112 |                         0.705 |                                  -0.089 |                            0.659 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| pc1                  | MCAR        |         0.233 |     0.092 |                         0.224 |                                   0.008 |                            0.576 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| pc1                  | MNAR        |         0.773 |    -0.003 |                         0.783 |                                  -0.010 |                            0.888 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| telco-customer-churn | MAR         |         0.622 |     0.247 |                         0.539 |                                   0.083 |                            1.030 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| telco-customer-churn | MCAR        |         0.566 |     0.242 |                         0.474 |                                   0.093 |                            0.990 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| telco-customer-churn | MNAR        |         0.611 |     0.046 |                         0.679 |                                  -0.068 |                            0.867 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| wine-quality-red     | MAR         |         0.540 |     0.440 |                         0.543 |                                  -0.003 |                            1.056 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| wine-quality-red     | MCAR        |         0.546 |     0.395 |                         0.607 |                                  -0.061 |                            1.033 | descriptive 3-point fit of squared RMSE ratio on 1/m |
| wine-quality-red     | MNAR        |         0.654 |     0.081 |                         0.628 |                                   0.025 |                            0.859 | descriptive 3-point fit of squared RMSE ratio on 1/m |

## PC1 per-column diagnostic across mechanisms

**Scope: 5-dataset exploratory subset, not the 10 declared headline datasets.**
**Additional scope note:** RMSE is averaged across trials. Outside-range fraction is pooled as total n_outside / total n_masked using same-mechanism observed training values.

Source CSV: `pc1/pc1_diagnostic.csv`

| mechanism   | column            |   rmse_iterative_single_as_is |   rmse_project_deterministic |   rmse_project_deterministic_no_bounds |   masked_values_outside_observed_range_fraction |   n_masked |   n_outside |
|-------------|-------------------|-------------------------------|------------------------------|----------------------------------------|-------------------------------------------------|------------|-------------|
| MAR         | B                 |                         0.945 |                        1.943 |                                  0.945 |                                           0.083 |        456 |          38 |
| MAR         | D                 |                         1.355 |                        1.250 |                                  1.355 |                                           0.021 |        476 |          10 |
| MAR         | E                 |                         1.907 |                        1.957 |                                  1.907 |                                           0.091 |        483 |          44 |
| MAR         | I                 |                         1.380 |                        1.493 |                                  1.380 |                                           0.019 |        470 |           9 |
| MAR         | L                 |                         0.928 |                        2.235 |                                  0.928 |                                           0.000 |        462 |           0 |
| MAR         | N                 |                         0.797 |                        1.534 |                                  0.797 |                                           0.091 |        452 |          41 |
| MAR         | T                 |                         1.932 |                        2.099 |                                  1.932 |                                           0.085 |        480 |          41 |
| MAR         | V                 |                         1.125 |                        1.501 |                                  1.125 |                                           0.082 |        461 |          38 |
| MAR         | branchCount       |                         1.174 |                        1.773 |                                  1.174 |                                           0.076 |        474 |          36 |
| MAR         | ev(g)             |                         1.532 |                        1.840 |                                  1.532 |                                           0.023 |        477 |          11 |
| MAR         | iv(G)             |                         1.371 |                        1.632 |                                  1.371 |                                           0.026 |        464 |          12 |
| MAR         | lOBlank           |                         1.452 |                        1.676 |                                  1.452 |                                           0.033 |        456 |          15 |
| MAR         | lOCode            |                         0.162 |                        1.278 |                                  0.162 |                                           0.121 |        462 |          56 |
| MAR         | lOComment         |                         1.530 |                        1.769 |                                  1.530 |                                           0.026 |        454 |          12 |
| MAR         | locCodeAndComment |                         1.648 |                        1.902 |                                  1.648 |                                           0.035 |        457 |          16 |
| MAR         | total_Op          |                         0.840 |                        1.379 |                                  0.840 |                                           0.058 |        467 |          27 |
| MAR         | total_Opnd        |                         0.822 |                        1.256 |                                  0.822 |                                           0.084 |        464 |          39 |
| MAR         | uniq_Op           |                         1.019 |                        1.370 |                                  1.019 |                                           0.043 |        469 |          20 |
| MAR         | uniq_Opnd         |                         0.562 |                        1.437 |                                  0.562 |                                           0.034 |        473 |          16 |
| MAR         | v(g)              |                         1.145 |                        1.580 |                                  1.145 |                                           0.081 |        442 |          36 |
| MCAR        | B                 |                         0.105 |                        0.116 |                                  0.105 |                                           0.000 |        438 |           0 |
| MCAR        | D                 |                         0.576 |                        0.700 |                                  0.576 |                                           0.006 |        465 |           3 |
| MCAR        | E                 |                         0.169 |                        0.164 |                                  0.169 |                                           0.000 |        407 |           0 |
| MCAR        | I                 |                         0.510 |                        0.430 |                                  0.510 |                                           0.000 |        441 |           0 |
| MCAR        | L                 |                         0.742 |                        0.741 |                                  0.742 |                                           0.000 |        449 |           0 |
| MCAR        | N                 |                         0.066 |                        0.070 |                                  0.066 |                                           0.000 |        462 |           0 |
| MCAR        | T                 |                         0.171 |                        0.158 |                                  0.171 |                                           0.000 |        438 |           0 |
| MCAR        | V                 |                         0.212 |                        0.212 |                                  0.212 |                                           0.000 |        437 |           0 |
| MCAR        | branchCount       |                         0.187 |                        0.199 |                                  0.187 |                                           0.000 |        441 |           0 |
| MCAR        | ev(g)             |                         0.556 |                        0.500 |                                  0.556 |                                           0.000 |        452 |           0 |
| MCAR        | iv(G)             |                         0.680 |                        0.493 |                                  0.680 |                                           0.000 |        455 |           0 |
| MCAR        | lOBlank           |                         0.796 |                        0.752 |                                  0.796 |                                           0.000 |        423 |           0 |
| MCAR        | lOCode            |                         0.173 |                        0.530 |                                  0.173 |                                           0.005 |        443 |           2 |
| MCAR        | lOComment         |                         0.917 |                        0.872 |                                  0.917 |                                           0.000 |        447 |           0 |
| MCAR        | loc               |                         0.167 |                        0.175 |                                  0.167 |                                           0.000 |        416 |           0 |
| MCAR        | locCodeAndComment |                         0.497 |                        0.580 |                                  0.497 |                                           0.000 |        454 |           0 |
| MCAR        | total_Op          |                         0.083 |                        0.153 |                                  0.083 |                                           0.004 |        446 |           2 |
| MCAR        | total_Opnd        |                         0.136 |                        0.191 |                                  0.136 |                                           0.002 |        440 |           1 |
| MCAR        | uniq_Op           |                         0.424 |                        0.357 |                                  0.424 |                                           0.000 |        433 |           0 |
| MCAR        | uniq_Opnd         |                         0.301 |                        0.299 |                                  0.301 |                                           0.000 |        463 |           0 |
| MCAR        | v(g)              |                         0.129 |                        0.122 |                                  0.129 |                                           0.000 |        468 |           0 |
| MNAR        | B                 |                         1.914 |                        1.917 |                                  1.914 |                                           0.118 |        458 |          54 |
| MNAR        | D                 |                         1.613 |                        1.607 |                                  1.613 |                                           0.141 |        440 |          62 |
| MNAR        | E                 |                         2.185 |                        2.184 |                                  2.185 |                                           0.075 |        451 |          34 |
| MNAR        | I                 |                         1.736 |                        1.742 |                                  1.736 |                                           0.151 |        450 |          68 |
| MNAR        | L                 |                         1.855 |                        1.781 |                                  1.855 |                                           0.097 |        431 |          42 |
| MNAR        | N                 |                         1.846 |                        1.854 |                                  1.846 |                                           0.208 |        442 |          92 |
| MNAR        | T                 |                         2.223 |                        2.222 |                                  2.223 |                                           0.075 |        442 |          33 |
| MNAR        | V                 |                         1.895 |                        1.895 |                                  1.895 |                                           0.117 |        461 |          54 |
| MNAR        | branchCount       |                         1.995 |                        1.992 |                                  1.995 |                                           0.116 |        438 |          51 |
| MNAR        | ev(g)             |                         2.038 |                        2.023 |                                  2.038 |                                           0.107 |        469 |          50 |
| MNAR        | iv(G)             |                         2.070 |                        2.069 |                                  2.070 |                                           0.133 |        459 |          61 |
| MNAR        | lOBlank           |                         1.844 |                        1.848 |                                  1.844 |                                           0.168 |        470 |          79 |
| MNAR        | lOCode            |                         1.938 |                        1.938 |                                  1.938 |                                           0.184 |        418 |          77 |
| MNAR        | lOComment         |                         1.973 |                        1.979 |                                  1.973 |                                           0.145 |        448 |          65 |
| MNAR        | loc               |                         1.918 |                        1.921 |                                  1.918 |                                           0.206 |        431 |          89 |
| MNAR        | locCodeAndComment |                         2.087 |                        2.079 |                                  2.087 |                                           0.095 |        454 |          43 |
| MNAR        | total_Op          |                         1.920 |                        1.928 |                                  1.920 |                                           0.190 |        416 |          79 |
| MNAR        | total_Opnd        |                         1.774 |                        1.779 |                                  1.774 |                                           0.171 |        467 |          80 |
| MNAR        | uniq_Op           |                         1.289 |                        1.240 |                                  1.289 |                                           0.136 |        440 |          60 |
| MNAR        | uniq_Opnd         |                         1.756 |                        1.768 |                                  1.756 |                                           0.124 |        451 |          56 |
| MNAR        | v(g)              |                         2.015 |                        2.010 |                                  2.015 |                                           0.181 |        431 |          78 |

**PC1 MAR gap columns — Source CSV: `pc1/pc1_diagnostic.csv`.** The five largest absolute project_deterministic versus iterative_single_as_is per-column RMSE gaps are: L, lOCode, B, uniq_Opnd, N. This is part of the 5-dataset exploratory subset, not the 10 declared headline datasets.