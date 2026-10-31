# Protocol A Win Tie Loss Vs Best Baseline All Datasets Supplementary

Supplementary all-dataset outcomes. For each dataset × mechanism × mask-rate cell, the best conventional baseline is the lowest mean-imputer-relative numeric RMSE among mean, median, KNN5, and single IterativeImputer. Each listed method is compared with that best baseline: win means >1% lower RMSE, tie means within 1%, and loss means >1% higher RMSE.

| method            |   win |   tie |   loss |
|-------------------|-------|-------|--------|
| iterative_single  |     0 |    85 |     20 |
| knn5              |     0 |    21 |     84 |
| mean              |     0 |    19 |     86 |
| median            |     0 |     3 |    102 |
| mice_multiple_NEW |    21 |    12 |     72 |
