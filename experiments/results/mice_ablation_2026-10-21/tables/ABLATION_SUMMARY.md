# MICE Point-Estimate Ablation Summary

**Post-hoc exploratory; descriptive only. No p-values or new significance claims.**

Coverage uses the existing Protocol A evaluator, whose interval correction is configured for m=5; m20/m50 coverage is descriptive under that unchanged metric.

## Per-dataset median RMSE ratio

Source CSVs: `adult/ablation.csv`, `bank-marketing/ablation.csv`, `breast-w/ablation.csv`, `credit-approval/ablation.csv`, `credit-g/ablation.csv`, `cylinder-bands/ablation.csv`, `heart-statlog/ablation.csv`, `pc1/ablation.csv`, `telco-customer-churn/ablation.csv`, `wine-quality-red/ablation.csv`

Summary CSV: `ablation_ratios_by_dataset.csv`

| dataset              | mechanism   | variant                          |   median_rmse_ratio_vs_mean |
|----------------------|-------------|----------------------------------|-----------------------------|
| adult                | MAR         | iterative_single_as_is           |                    1.02816  |
| adult                | MAR         | iterative_single_posterior_false |                    1.02816  |
| adult                | MAR         | iterative_single_posterior_true  |                    1.34812  |
| adult                | MAR         | project_deterministic            |                    1.02801  |
| adult                | MAR         | project_m20                      |                    1.09755  |
| adult                | MAR         | project_m5                       |                    1.13636  |
| adult                | MAR         | project_m50                      |                    1.09117  |
| bank-marketing       | MAR         | iterative_single_as_is           |                    0.962078 |
| bank-marketing       | MAR         | iterative_single_posterior_false |                    0.962078 |
| bank-marketing       | MAR         | iterative_single_posterior_true  |                    1.36277  |
| bank-marketing       | MAR         | project_deterministic            |                    0.961587 |
| bank-marketing       | MAR         | project_m20                      |                    1.04387  |
| bank-marketing       | MAR         | project_m5                       |                    1.07611  |
| bank-marketing       | MAR         | project_m50                      |                    1.03786  |
| breast-w             | MAR         | iterative_single_as_is           |                    0.6995   |
| breast-w             | MAR         | iterative_single_posterior_false |                    0.6995   |
| breast-w             | MAR         | iterative_single_posterior_true  |                    0.808411 |
| breast-w             | MAR         | project_deterministic            |                    0.69766  |
| breast-w             | MAR         | project_m20                      |                    0.691868 |
| breast-w             | MAR         | project_m5                       |                    0.698018 |
| breast-w             | MAR         | project_m50                      |                    0.689432 |
| credit-approval      | MAR         | iterative_single_as_is           |                    0.94111  |
| credit-approval      | MAR         | iterative_single_posterior_false |                    0.94111  |
| credit-approval      | MAR         | iterative_single_posterior_true  |                    1.09012  |
| credit-approval      | MAR         | project_deterministic            |                    0.944354 |
| credit-approval      | MAR         | project_m20                      |                    0.968192 |
| credit-approval      | MAR         | project_m5                       |                    0.978449 |
| credit-approval      | MAR         | project_m50                      |                    0.963688 |
| credit-g             | MAR         | iterative_single_as_is           |                    0.931471 |
| credit-g             | MAR         | iterative_single_posterior_false |                    0.931471 |
| credit-g             | MAR         | iterative_single_posterior_true  |                    1.32995  |
| credit-g             | MAR         | project_deterministic            |                    0.931053 |
| credit-g             | MAR         | project_m20                      |                    0.981449 |
| credit-g             | MAR         | project_m5                       |                    1.02311  |
| credit-g             | MAR         | project_m50                      |                    0.970824 |
| cylinder-bands       | MAR         | iterative_single_as_is           |                    1.00613  |
| cylinder-bands       | MAR         | iterative_single_posterior_false |                    1.00613  |
| cylinder-bands       | MAR         | iterative_single_posterior_true  |                    1.41467  |
| cylinder-bands       | MAR         | project_deterministic            |                    1.00605  |
| cylinder-bands       | MAR         | project_m20                      |                    1.03965  |
| cylinder-bands       | MAR         | project_m5                       |                    1.09547  |
| cylinder-bands       | MAR         | project_m50                      |                    1.01702  |
| heart-statlog        | MAR         | iterative_single_as_is           |                    0.930492 |
| heart-statlog        | MAR         | iterative_single_posterior_false |                    0.930492 |
| heart-statlog        | MAR         | iterative_single_posterior_true  |                    1.26212  |
| heart-statlog        | MAR         | project_deterministic            |                    0.9297   |
| heart-statlog        | MAR         | project_m20                      |                    0.963067 |
| heart-statlog        | MAR         | project_m5                       |                    0.992112 |
| heart-statlog        | MAR         | project_m50                      |                    0.956514 |
| pc1                  | MAR         | iterative_single_as_is           |                    0.632599 |
| pc1                  | MAR         | iterative_single_posterior_false |                    0.632599 |
| pc1                  | MAR         | iterative_single_posterior_true  |                    0.658781 |
| pc1                  | MAR         | project_deterministic            |                    0.839646 |
| pc1                  | MAR         | project_m20                      |                    0.788455 |
| pc1                  | MAR         | project_m5                       |                    0.798614 |
| pc1                  | MAR         | project_m50                      |                    0.78567  |
| telco-customer-churn | MAR         | iterative_single_as_is           |                    0.739037 |
| telco-customer-churn | MAR         | iterative_single_posterior_false |                    0.739037 |
| telco-customer-churn | MAR         | iterative_single_posterior_true  |                    1.03023  |
| telco-customer-churn | MAR         | project_deterministic            |                    0.734136 |
| telco-customer-churn | MAR         | project_m20                      |                    0.796403 |
| telco-customer-churn | MAR         | project_m5                       |                    0.819352 |
| telco-customer-churn | MAR         | project_m50                      |                    0.791835 |
| wine-quality-red     | MAR         | iterative_single_as_is           |                    0.737523 |
| wine-quality-red     | MAR         | iterative_single_posterior_false |                    0.737523 |
| wine-quality-red     | MAR         | iterative_single_posterior_true  |                    1.05637  |
| wine-quality-red     | MAR         | project_deterministic            |                    0.736757 |
| wine-quality-red     | MAR         | project_m20                      |                    0.749859 |
| wine-quality-red     | MAR         | project_m5                       |                    0.792395 |
| wine-quality-red     | MAR         | project_m50                      |                    0.740602 |
| adult                | MCAR        | iterative_single_as_is           |                    0.973262 |
| adult                | MCAR        | iterative_single_posterior_false |                    0.973262 |
| adult                | MCAR        | iterative_single_posterior_true  |                    1.34893  |
| adult                | MCAR        | project_deterministic            |                    0.972138 |
| adult                | MCAR        | project_m20                      |                    1.03691  |
| adult                | MCAR        | project_m5                       |                    1.0781   |
| adult                | MCAR        | project_m50                      |                    1.0284   |
| bank-marketing       | MCAR        | iterative_single_as_is           |                    0.951673 |
| bank-marketing       | MCAR        | iterative_single_posterior_false |                    0.951673 |
| bank-marketing       | MCAR        | iterative_single_posterior_true  |                    1.28633  |
| bank-marketing       | MCAR        | project_deterministic            |                    0.93246  |
| bank-marketing       | MCAR        | project_m20                      |                    0.995559 |
| bank-marketing       | MCAR        | project_m5                       |                    1.02761  |
| bank-marketing       | MCAR        | project_m50                      |                    0.988828 |
| breast-w             | MCAR        | iterative_single_as_is           |                    0.663301 |
| breast-w             | MCAR        | iterative_single_posterior_false |                    0.663301 |
| breast-w             | MCAR        | iterative_single_posterior_true  |                    0.915858 |
| breast-w             | MCAR        | project_deterministic            |                    0.660371 |
| breast-w             | MCAR        | project_m20                      |                    0.720493 |
| breast-w             | MCAR        | project_m5                       |                    0.75125  |
| breast-w             | MCAR        | project_m50                      |                    0.715549 |
| credit-approval      | MCAR        | iterative_single_as_is           |                    0.920044 |
| credit-approval      | MCAR        | iterative_single_posterior_false |                    0.920044 |
| credit-approval      | MCAR        | iterative_single_posterior_true  |                    1.31744  |
| credit-approval      | MCAR        | project_deterministic            |                    0.905065 |
| credit-approval      | MCAR        | project_m20                      |                    1.05704  |
| credit-approval      | MCAR        | project_m5                       |                    1.10263  |
| credit-approval      | MCAR        | project_m50                      |                    1.04736  |
| credit-g             | MCAR        | iterative_single_as_is           |                    0.9079   |
| credit-g             | MCAR        | iterative_single_posterior_false |                    0.9079   |
| credit-g             | MCAR        | iterative_single_posterior_true  |                    1.3392   |
| credit-g             | MCAR        | project_deterministic            |                    0.904066 |
| credit-g             | MCAR        | project_m20                      |                    0.967997 |
| credit-g             | MCAR        | project_m5                       |                    0.998389 |
| credit-g             | MCAR        | project_m50                      |                    0.958779 |
| cylinder-bands       | MCAR        | iterative_single_as_is           |                    1.00184  |
| cylinder-bands       | MCAR        | iterative_single_posterior_false |                    1.00184  |
| cylinder-bands       | MCAR        | iterative_single_posterior_true  |                    1.45572  |
| cylinder-bands       | MCAR        | project_deterministic            |                    1.0015   |
| cylinder-bands       | MCAR        | project_m20                      |                    1.02175  |
| cylinder-bands       | MCAR        | project_m5                       |                    1.08747  |
| cylinder-bands       | MCAR        | project_m50                      |                    1.01741  |
| heart-statlog        | MCAR        | iterative_single_as_is           |                    0.913056 |
| heart-statlog        | MCAR        | iterative_single_posterior_false |                    0.913056 |
| heart-statlog        | MCAR        | iterative_single_posterior_true  |                    1.22135  |
| heart-statlog        | MCAR        | project_deterministic            |                    0.911136 |
| heart-statlog        | MCAR        | project_m20                      |                    0.951957 |
| heart-statlog        | MCAR        | project_m5                       |                    0.990103 |
| heart-statlog        | MCAR        | project_m50                      |                    0.945392 |
| pc1                  | MCAR        | iterative_single_as_is           |                    0.473639 |
| pc1                  | MCAR        | iterative_single_posterior_false |                    0.473639 |
| pc1                  | MCAR        | iterative_single_posterior_true  |                    0.575892 |
| pc1                  | MCAR        | project_deterministic            |                    0.473813 |
| pc1                  | MCAR        | project_m20                      |                    0.487776 |
| pc1                  | MCAR        | project_m5                       |                    0.501244 |
| pc1                  | MCAR        | project_m50                      |                    0.484088 |
| telco-customer-churn | MCAR        | iterative_single_as_is           |                    0.705097 |
| telco-customer-churn | MCAR        | iterative_single_posterior_false |                    0.705097 |
| telco-customer-churn | MCAR        | iterative_single_posterior_true  |                    0.990288 |
| telco-customer-churn | MCAR        | project_deterministic            |                    0.688121 |
| telco-customer-churn | MCAR        | project_m20                      |                    0.760184 |
| telco-customer-churn | MCAR        | project_m5                       |                    0.784129 |
| telco-customer-churn | MCAR        | project_m50                      |                    0.756126 |
| wine-quality-red     | MCAR        | iterative_single_as_is           |                    0.803122 |
| wine-quality-red     | MCAR        | iterative_single_posterior_false |                    0.803122 |
| wine-quality-red     | MCAR        | iterative_single_posterior_true  |                    1.03318  |
| wine-quality-red     | MCAR        | project_deterministic            |                    0.778872 |
| wine-quality-red     | MCAR        | project_m20                      |                    0.751314 |
| wine-quality-red     | MCAR        | project_m5                       |                    0.790613 |
| wine-quality-red     | MCAR        | project_m50                      |                    0.744804 |
| adult                | MNAR        | iterative_single_as_is           |                    0.978598 |
| adult                | MNAR        | iterative_single_posterior_false |                    0.978598 |
| adult                | MNAR        | iterative_single_posterior_true  |                    1.03751  |
| adult                | MNAR        | project_deterministic            |                    0.978506 |
| adult                | MNAR        | project_m20                      |                    0.973415 |
| adult                | MNAR        | project_m5                       |                    0.98025  |
| adult                | MNAR        | project_m50                      |                    0.97222  |
| bank-marketing       | MNAR        | iterative_single_as_is           |                    0.929023 |
| bank-marketing       | MNAR        | iterative_single_posterior_false |                    0.929023 |
| bank-marketing       | MNAR        | iterative_single_posterior_true  |                    0.96683  |
| bank-marketing       | MNAR        | project_deterministic            |                    0.929053 |
| bank-marketing       | MNAR        | project_m20                      |                    0.921954 |
| bank-marketing       | MNAR        | project_m5                       |                    0.926397 |
| bank-marketing       | MNAR        | project_m50                      |                    0.921324 |
| breast-w             | MNAR        | iterative_single_as_is           |                    0.749127 |
| breast-w             | MNAR        | iterative_single_posterior_false |                    0.749127 |
| breast-w             | MNAR        | iterative_single_posterior_true  |                    0.781989 |
| breast-w             | MNAR        | project_deterministic            |                    0.748668 |
| breast-w             | MNAR        | project_m20                      |                    0.73124  |
| breast-w             | MNAR        | project_m5                       |                    0.736906 |
| breast-w             | MNAR        | project_m50                      |                    0.729855 |
| credit-approval      | MNAR        | iterative_single_as_is           |                    0.949934 |
| credit-approval      | MNAR        | iterative_single_posterior_false |                    0.949934 |
| credit-approval      | MNAR        | iterative_single_posterior_true  |                    0.972667 |
| credit-approval      | MNAR        | project_deterministic            |                    0.947894 |
| credit-approval      | MNAR        | project_m20                      |                    0.924596 |
| credit-approval      | MNAR        | project_m5                       |                    0.926744 |
| credit-approval      | MNAR        | project_m50                      |                    0.924574 |
| credit-g             | MNAR        | iterative_single_as_is           |                    0.918472 |
| credit-g             | MNAR        | iterative_single_posterior_false |                    0.918472 |
| credit-g             | MNAR        | iterative_single_posterior_true  |                    1.01964  |
| credit-g             | MNAR        | project_deterministic            |                    0.917288 |
| credit-g             | MNAR        | project_m20                      |                    0.897578 |
| credit-g             | MNAR        | project_m5                       |                    0.902934 |
| credit-g             | MNAR        | project_m50                      |                    0.895474 |
| cylinder-bands       | MNAR        | iterative_single_as_is           |                    1.0046   |
| cylinder-bands       | MNAR        | iterative_single_posterior_false |                    1.0046   |
| cylinder-bands       | MNAR        | iterative_single_posterior_true  |                    1.07142  |
| cylinder-bands       | MNAR        | project_deterministic            |                    1.00452  |
| cylinder-bands       | MNAR        | project_m20                      |                    0.962723 |
| cylinder-bands       | MNAR        | project_m5                       |                    0.971354 |
| cylinder-bands       | MNAR        | project_m50                      |                    0.961345 |
| heart-statlog        | MNAR        | iterative_single_as_is           |                    0.927508 |
| heart-statlog        | MNAR        | iterative_single_posterior_false |                    0.927508 |
| heart-statlog        | MNAR        | iterative_single_posterior_true  |                    1.06866  |
| heart-statlog        | MNAR        | project_deterministic            |                    0.927195 |
| heart-statlog        | MNAR        | project_m20                      |                    0.902568 |
| heart-statlog        | MNAR        | project_m5                       |                    0.91334  |
| heart-statlog        | MNAR        | project_m50                      |                    0.9018   |
| pc1                  | MNAR        | iterative_single_as_is           |                    0.886773 |
| pc1                  | MNAR        | iterative_single_posterior_false |                    0.886773 |
| pc1                  | MNAR        | iterative_single_posterior_true  |                    0.887954 |
| pc1                  | MNAR        | project_deterministic            |                    0.884873 |
| pc1                  | MNAR        | project_m20                      |                    0.879569 |
| pc1                  | MNAR        | project_m5                       |                    0.878986 |
| pc1                  | MNAR        | project_m50                      |                    0.879105 |
| telco-customer-churn | MNAR        | iterative_single_as_is           |                    0.825132 |
| telco-customer-churn | MNAR        | iterative_single_posterior_false |                    0.825132 |
| telco-customer-churn | MNAR        | iterative_single_posterior_true  |                    0.86746  |
| telco-customer-churn | MNAR        | project_deterministic            |                    0.823997 |
| telco-customer-churn | MNAR        | project_m20                      |                    0.783429 |
| telco-customer-churn | MNAR        | project_m5                       |                    0.787533 |
| telco-customer-churn | MNAR        | project_m50                      |                    0.782082 |
| wine-quality-red     | MNAR        | iterative_single_as_is           |                    0.793954 |
| wine-quality-red     | MNAR        | iterative_single_posterior_false |                    0.793954 |
| wine-quality-red     | MNAR        | iterative_single_posterior_true  |                    0.858697 |
| wine-quality-red     | MNAR        | project_deterministic            |                    0.792696 |
| wine-quality-red     | MNAR        | project_m20                      |                    0.811307 |
| wine-quality-red     | MNAR        | project_m5                       |                    0.818292 |
| wine-quality-red     | MNAR        | project_m50                      |                    0.80906  |

## Aggregate median ratio and datasets below project_m5

Source CSVs: `adult/ablation.csv`, `bank-marketing/ablation.csv`, `breast-w/ablation.csv`, `credit-approval/ablation.csv`, `credit-g/ablation.csv`, `cylinder-bands/ablation.csv`, `heart-statlog/ablation.csv`, `pc1/ablation.csv`, `telco-customer-churn/ablation.csv`, `wine-quality-red/ablation.csv`

Summary CSV: `ablation_ratio_aggregate.csv`

| mechanism   | variant                          |   median_rmse_ratio_vs_mean |   n_datasets |   datasets_lower_ratio_than_project_m5 |
|-------------|----------------------------------|-----------------------------|--------------|----------------------------------------|
| MAR         | iterative_single_as_is           |                    0.930982 |           10 |                                      9 |
| MAR         | iterative_single_posterior_false |                    0.930982 |           10 |                                      9 |
| MAR         | iterative_single_posterior_true  |                    1.17612  |           10 |                                      1 |
| MAR         | project_deterministic            |                    0.930377 |           10 |                                      9 |
| MAR         | project_m20                      |                    0.96563  |           10 |                                     10 |
| MAR         | project_m5                       |                    0.985281 |           10 |                                      0 |
| MAR         | project_m50                      |                    0.960101 |           10 |                                     10 |
| MCAR        | iterative_single_as_is           |                    0.910478 |           10 |                                      9 |
| MCAR        | iterative_single_posterior_false |                    0.910478 |           10 |                                      9 |
| MCAR        | iterative_single_posterior_true  |                    1.25384  |           10 |                                      0 |
| MCAR        | project_deterministic            |                    0.904566 |           10 |                                     10 |
| MCAR        | project_m20                      |                    0.959977 |           10 |                                     10 |
| MCAR        | project_m5                       |                    0.994246 |           10 |                                      0 |
| MCAR        | project_m50                      |                    0.952085 |           10 |                                     10 |
| MNAR        | iterative_single_as_is           |                    0.92299  |           10 |                                      2 |
| MNAR        | iterative_single_posterior_false |                    0.92299  |           10 |                                      2 |
| MNAR        | iterative_single_posterior_true  |                    0.969748 |           10 |                                      0 |
| MNAR        | project_deterministic            |                    0.922242 |           10 |                                      2 |
| MNAR        | project_m20                      |                    0.900073 |           10 |                                      9 |
| MNAR        | project_m5                       |                    0.908137 |           10 |                                      0 |
| MNAR        | project_m50                      |                    0.898637 |           10 |                                      9 |

## Uncertainty metrics across datasets

Source CSVs: `adult/ablation.csv`, `bank-marketing/ablation.csv`, `breast-w/ablation.csv`, `credit-approval/ablation.csv`, `credit-g/ablation.csv`, `cylinder-bands/ablation.csv`, `heart-statlog/ablation.csv`, `pc1/ablation.csv`, `telco-customer-churn/ablation.csv`, `wine-quality-red/ablation.csv`

Summary CSV: `ablation_uncertainty_summary.csv`

| mechanism   | variant     | uncertainty_metric             |   n_datasets |   minimum |   median |   maximum |
|-------------|-------------|--------------------------------|--------------|-----------|----------|-----------|
| MAR         | project_m20 | uncertainty_coverage90_numeric |           10 |  0.807802 | 0.921064 |  0.97518  |
| MAR         | project_m5  | uncertainty_coverage90_numeric |           10 |  0.740462 | 0.834134 |  0.90286  |
| MAR         | project_m50 | uncertainty_coverage90_numeric |           10 |  0.819894 | 0.940064 |  0.987603 |
| MAR         | project_m20 | uncertainty_spearman_numeric   |           10 |  0.395695 | 0.835163 |  0.944127 |
| MAR         | project_m5  | uncertainty_spearman_numeric   |           10 |  0.32229  | 0.810401 |  0.945027 |
| MAR         | project_m50 | uncertainty_spearman_numeric   |           10 |  0.424334 | 0.839953 |  0.944786 |
| MCAR        | project_m20 | uncertainty_coverage90_numeric |           10 |  0.919818 | 0.95822  |  0.96443  |
| MCAR        | project_m5  | uncertainty_coverage90_numeric |           10 |  0.828649 | 0.868592 |  0.908926 |
| MCAR        | project_m50 | uncertainty_coverage90_numeric |           10 |  0.926861 | 0.964715 |  0.986335 |
| MCAR        | project_m20 | uncertainty_spearman_numeric   |           10 |  0.514286 | 0.824202 |  0.918457 |
| MCAR        | project_m5  | uncertainty_spearman_numeric   |           10 |  0.452918 | 0.806933 |  0.922578 |
| MCAR        | project_m50 | uncertainty_spearman_numeric   |           10 |  0.525719 | 0.834626 |  0.915709 |
| MNAR        | project_m20 | uncertainty_coverage90_numeric |           10 |  0.47227  | 0.672159 |  0.734111 |
| MNAR        | project_m5  | uncertainty_coverage90_numeric |           10 |  0.428342 | 0.596441 |  0.656872 |
| MNAR        | project_m50 | uncertainty_coverage90_numeric |           10 |  0.47596  | 0.683104 |  0.769418 |
| MNAR        | project_m20 | uncertainty_spearman_numeric   |           10 |  0.308981 | 0.831781 |  0.911499 |
| MNAR        | project_m5  | uncertainty_spearman_numeric   |           10 |  0.253758 | 0.801053 |  0.900794 |
| MNAR        | project_m50 | uncertainty_spearman_numeric   |           10 |  0.327289 | 0.836637 |  0.912675 |
