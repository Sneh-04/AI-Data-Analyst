# M3 Auto Comparisons

Exploratory paired Wilcoxon tests on per-series mean MASE (n=20 series), Auto minus each alternative. Holm correction is across all seven alternatives; negative differences favor Auto. Series may share M3 domains.

| model             |   mean_series_mase_diff_auto_minus_model |   auto_wins |   pairs |     p_raw |   p_holm | p_holm_lt_0_05   |
|-------------------|------------------------------------------|-------------|---------|-----------|----------|------------------|
| arima             |                                0.0569086 |           9 |      20 | 0.784126  | 1        | False            |
| auto_no_shortlist |                                0.0187198 |           0 |      20 | 0.179712  | 0.898562 | False            |
| ensemble          |                                0.164511  |           7 |      20 | 0.0758514 | 0.53096  | False            |
| holt              |                                0.0137965 |           8 |      20 | 0.647655  | 1        | False            |
| naive             |                               -0.0138308 |           7 |      20 | 0.674223  | 1        | False            |
| sarima            |                               -0.16709   |          12 |      20 | 0.311794  | 1        | False            |
| seasonal_naive    |                               -0.348669  |          13 |      20 | 0.0973072 | 0.583843 | False            |
