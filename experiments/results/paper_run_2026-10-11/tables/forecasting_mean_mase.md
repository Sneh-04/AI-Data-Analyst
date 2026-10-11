# Forecasting Mean Mase

Mean MASE and scored series/window counts from the saved `forecasting_raw.csv`. The oracle-best-fixed row is a reference bound, not a deployable model.

| method             |   mean_mase |   n_series |   evaluation_windows |
|--------------------|-------------|------------|----------------------|
| arima              |     1.66975 |          6 |                   48 |
| auto               |     1.46741 |          6 |                   48 |
| auto_legacy        |     1.6088  |          6 |                   48 |
| auto_no_shortlist  |     1.51894 |          6 |                   48 |
| auto_with_ensemble |     1.52309 |          6 |                   48 |
| ensemble           |     2.19965 |          6 |                   48 |
| holt               |     3.33811 |          6 |                   48 |
| naive              |     2.46051 |          6 |                   48 |
| oracle_best_fixed  |     1.05735 |          6 |                   48 |
| sarima             |     1.81128 |          4 |                   32 |
| seasonal_naive     |     3.96773 |          4 |                   32 |
