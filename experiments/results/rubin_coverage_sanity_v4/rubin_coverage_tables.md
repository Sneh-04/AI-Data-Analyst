# Rubin coverage benchmark tables

## Per-dataset coverage by mechanism, method, rate, estimand, m, and delta

| dataset   | estimand   | mechanism   | method   | mask_rate   | m   | delta_sd   | coverage   | coverage_mc_se   | successful_runs   | noncovering_runs   | finite_interval_runs   | failed_runs   | attempted_runs   | complete_100_seed_cell   |
|-----------|------------|-------------|----------|-------------|-----|------------|------------|------------------|-------------------|--------------------|------------------------|---------------|------------------|--------------------------|

## Headline coverage pooled across datasets (dataset-cluster bootstrap SE)

| estimand   | mechanism   | method   | mask_rate   | m   | delta_sd   | coverage   | coverage_mc_se   | dataset_cluster_bootstrap_mc_se   | contributing_datasets   | successful_runs   | failed_runs   | attempted_runs   | noncovering_runs   | finite_interval_runs   | cluster_bootstrap_replicates   | cluster_bootstrap_seed   | sanity_failed_datasets_excluded   |
|------------|-------------|----------|-------------|-----|------------|------------|------------------|-----------------------------------|-------------------------|-------------------|---------------|------------------|--------------------|------------------------|--------------------------------|--------------------------|-----------------------------------|

## Mean interval width

| dataset   | estimand   | mechanism   | method   | mask_rate   | m   | delta_sd   | mean_ci_width   | finite_interval_runs   | successful_runs   |
|-----------|------------|-------------|----------|-------------|-----|------------|-----------------|------------------------|-------------------|

## Mean bias

| dataset   | estimand   | mechanism   | method   | mask_rate   | m   | delta_sd   | mean_bias   | successful_runs   |
|-----------|------------|-------------|----------|-------------|-----|------------|-------------|-------------------|

## MNAR coverage by delta

| dataset   | estimand   | mechanism   | method   | mask_rate   | m   | delta_sd   | coverage   | coverage_mc_se   | successful_runs   | noncovering_runs   | finite_interval_runs   | failed_runs   | attempted_runs   | complete_100_seed_cell   |
|-----------|------------|-------------|----------|-------------|-----|------------|------------|------------------|-------------------|--------------------|------------------------|---------------|------------------|--------------------------|

## No-missing sanity coverage (sanity-failed outside 91-99%)

| dataset              | estimand   |   coverage |   coverage_mc_se |   successful_runs |   expected_runs |   failed_runs |   attempted_runs | sanity_status   |
|:---------------------|:-----------|-----------:|-----------------:|------------------:|----------------:|--------------:|-----------------:|:----------------|
| adult                | mean       |       0.97 |        0.0170587 |               100 |             100 |             0 |              100 | sanity-passed   |
| adult                | ols_slope  |       0.94 |        0.0237487 |               100 |             100 |             0 |              100 | sanity-passed   |
| bank-marketing       | mean       |       0.92 |        0.0271293 |               100 |             100 |             0 |              100 | sanity-passed   |
| bank-marketing       | ols_slope  |       0.94 |        0.0237487 |               100 |             100 |             0 |              100 | sanity-passed   |
| breast-w             | mean       |       0.96 |        0.0195959 |               100 |             100 |             0 |              100 | sanity-passed   |
| breast-w             | ols_slope  |       0.95 |        0.0217945 |               100 |             100 |             0 |              100 | sanity-passed   |
| credit-approval      | mean       |       0.92 |        0.0271293 |               100 |             100 |             0 |              100 | sanity-passed   |
| credit-approval      | ols_slope  |       0.95 |        0.0217945 |               100 |             100 |             0 |              100 | sanity-passed   |
| credit-g             | mean       |       0.95 |        0.0217945 |               100 |             100 |             0 |              100 | sanity-passed   |
| credit-g             | ols_slope  |       0.93 |        0.0255147 |               100 |             100 |             0 |              100 | sanity-passed   |
| diabetes             | mean       |       0.95 |        0.0217945 |               100 |             100 |             0 |              100 | sanity-passed   |
| diabetes             | ols_slope  |       0.96 |        0.0195959 |               100 |             100 |             0 |              100 | sanity-passed   |
| heart-statlog        | mean       |       0.93 |        0.0255147 |               100 |             100 |             0 |              100 | sanity-passed   |
| heart-statlog        | ols_slope  |       0.96 |        0.0195959 |               100 |             100 |             0 |              100 | sanity-passed   |
| pc1                  | mean       |       0.93 |        0.0255147 |               100 |             100 |             0 |              100 | sanity-passed   |
| pc1                  | ols_slope  |       0.93 |        0.0255147 |               100 |             100 |             0 |              100 | sanity-passed   |
| telco-customer-churn | mean       |       0.97 |        0.0170587 |               100 |             100 |             0 |              100 | sanity-passed   |
| telco-customer-churn | ols_slope  |       0.98 |        0.014     |               100 |             100 |             0 |              100 | sanity-passed   |
| wine-quality-red     | mean       |       0.97 |        0.0170587 |               100 |             100 |             0 |              100 | sanity-passed   |
| wine-quality-red     | ols_slope  |       0.91 |        0.0286182 |               100 |             100 |             0 |              100 | sanity-passed   |
