# Forecasting benchmark results

Dataset: statsmodels Mauna Loa CO2, monthly-resampled, n=526.
Walk-forward origins: 6; horizon: 12 months.

## Aggregate metrics

| method_group   |   mean_mase |   std_mase |   mean_mape |   windows |
|:---------------|------------:|-----------:|------------:|----------:|
| auto           |      2.1364 |     0.4586 |      0.6235 |         6 |
| naive          |      2.2895 |     0.4800 |      0.6669 |         6 |
| arima          |      2.6847 |     1.0523 |      0.7833 |         6 |
| sarima         |      3.1746 |     1.1420 |      0.9267 |         6 |
| seasonal_naive |      3.2748 |     0.4766 |      0.9514 |         6 |
| holt           |      7.4092 |     3.9162 |      2.1601 |         6 |

## Automatic model selections by origin

|   window | method                        |   mase |
|---------:|:------------------------------|-------:|
|        0 | auto (picked: naive)          | 1.8592 |
|        1 | auto (picked: naive)          | 2.5241 |
|        2 | auto (picked: seasonal_naive) | 2.5746 |
|        3 | auto (picked: arima)          | 1.8007 |
|        4 | auto (picked: naive)          | 1.5315 |
|        5 | auto (picked: naive)          | 2.5284 |
