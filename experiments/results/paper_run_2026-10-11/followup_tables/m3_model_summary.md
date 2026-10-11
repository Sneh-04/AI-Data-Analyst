# M3 Model Summary

Means are computed by averaging within-series MASE first, so each of the 20 series receives equal weight. Runtime is mean model-call seconds per forecast window.

| method            |   mean_series_mase |   mean_seconds_per_window |   median_seconds_per_window |   n_series |   evaluation_windows |
|-------------------|--------------------|---------------------------|-----------------------------|------------|----------------------|
| arima             |            1.91572 |                0.0194613  |                  0.0196548  |         20 |                   80 |
| auto              |            1.97263 |                0.215551   |                  0.145218   |         20 |                   80 |
| auto_no_shortlist |            1.95391 |                0.367973   |                  0.381305   |         20 |                   80 |
| ensemble          |            1.80812 |                0.0266643  |                  0.0273887  |         20 |                   80 |
| holt              |            1.95883 |                0.00942398 |                  0.00932418 |         20 |                   80 |
| naive             |            1.98646 |                0.001435   |                  0.00142368 |         20 |                   80 |
| sarima            |            2.13972 |                0.110014   |                  0.116026   |         20 |                   80 |
| seasonal_naive    |            2.3213  |                0.00144422 |                  0.00139572 |         20 |                   80 |
