# Forecasting Auto Comparisons

Paired Wilcoxon signed-rank tests on series/window MASE differences (Auto minus model); negative differences favor Auto. Holm correction is applied across every scored non-oracle alternative method in this table. `p_holm_lt_0_05` marks the strict p_holm < 0.05 rule.

| model              |   mean_mase_diff_auto_minus_model |   auto_wins |   pairs |   n_series |   evaluation_windows |       p_raw |      p_holm | p_holm_lt_0_05   |
|--------------------|-----------------------------------|-------------|---------|------------|----------------------|-------------|-------------|------------------|
| naive              |                        -0.993107  |          36 |      48 |          6 |                   48 | 7.90886e-05 | 0.00055362  | True             |
| seasonal_naive     |                        -2.32484   |          30 |      32 |          4 |                   32 | 2.31294e-06 | 2.08165e-05 | True             |
| holt               |                        -1.8707    |          24 |      48 |          6 |                   48 | 0.000562684 | 0.0033761   | True             |
| arima              |                        -0.202345  |          16 |      48 |          6 |                   48 | 0.110936    | 0.443744    | False            |
| sarima             |                        -0.168392  |          14 |      32 |          4 |                   32 | 0.157875    | 0.473624    | False            |
| ensemble           |                        -0.732248  |          38 |      48 |          6 |                   48 | 1.85516e-05 | 0.000148413 | True             |
| auto_legacy        |                        -0.141396  |           9 |      48 |          6 |                   48 | 0.0843794   | 0.421897    | False            |
| auto_no_shortlist  |                        -0.0515281 |           2 |      48 |          6 |                   48 | 0.179712    | 0.473624    | False            |
| auto_with_ensemble |                        -0.0556832 |           1 |      48 |          6 |                   48 | 0.317311    | 0.473624    | False            |
