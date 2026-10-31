# Protocol A Win Tie Loss Vs Best Baseline

Primary headline-dataset outcomes. For each dataset × mechanism × mask-rate cell, the best conventional baseline is the lowest mean-imputer-relative numeric RMSE among mean, median, KNN5, and single IterativeImputer. Each listed method is compared with that best baseline: win means >1% lower RMSE, tie means within 1%, and loss means >1% higher RMSE.

| method            |   win |   tie |   loss |
|-------------------|-------|-------|--------|
| iterative_single  |     0 |    72 |     18 |
| knn5              |     0 |    20 |     70 |
| mean              |     0 |    14 |     76 |
| median            |     0 |     3 |     87 |
| mice_multiple_NEW |    18 |    12 |     60 |
