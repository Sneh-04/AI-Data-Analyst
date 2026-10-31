# Protocol B Natural Missingness Significance

Natural-missingness paired fold-level tests versus project MICE, with Holm-adjusted p-values.

|   protocol |   label | metric                         | dataset         | vs               |   mean_loss_diff |   project_mice_wins |   pairs |   p_value |   p_holm | project_mice_won   |
|------------|---------|--------------------------------|-----------------|------------------|------------------|---------------------|---------|-----------|----------|--------------------|
|        nan |     nan | accuracy                       | breast-w        | mean             |     -1.02775e-05 |                   1 |       5 |    1      |        1 | True               |
|        nan |     nan | accuracy                       | breast-w        | median           |     -0.00286742  |                   2 |       5 |    0.5    |        1 | True               |
|        nan |     nan | accuracy                       | breast-w        | knn5             |      0.00142857  |                   0 |       5 |    1      |        1 | False              |
|        nan |     nan | accuracy                       | breast-w        | iterative_single |      0.00142857  |                   0 |       5 |    1      |        1 | False              |
|        nan |     nan | accuracy                       | credit-approval | mean             |     -0.00434783  |                   3 |       5 |    0.6875 |        1 | True               |
|        nan |     nan | accuracy                       | credit-approval | median           |     -0.00289855  |                   1 |       5 |    1      |        1 | True               |
|        nan |     nan | accuracy                       | credit-approval | knn5             |      0           |                   2 |       5 |    1      |        1 | False              |
|        nan |     nan | accuracy                       | credit-approval | iterative_single |     -0.00144928  |                   1 |       5 |    1      |        1 | True               |
|        nan |     nan | accuracy                       | hepatitis       | mean             |      4.44089e-17 |                   2 |       5 |    0.875  |        1 | False              |
|        nan |     nan | accuracy                       | hepatitis       | median           |      0.0129032   |                   2 |       5 |    0.625  |        1 | False              |
|        nan |     nan | accuracy                       | hepatitis       | knn5             |      0.0322581   |                   1 |       5 |    0.5    |        1 | False              |
|        nan |     nan | accuracy                       | hepatitis       | iterative_single |      0.0129032   |                   0 |       5 |    0.5    |        1 | False              |
|        nan |     nan | heldout_numeric_rmse           | breast-w        | mean             |     -0.0305421   |                   2 |       5 |    0.8125 |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | breast-w        | median           |     -0.207209    |                   5 |       5 |    0.0625 |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | breast-w        | knn5             |      0.285669    |                   0 |       5 |    0.0625 |        1 | False              |
|        nan |     nan | heldout_numeric_rmse           | breast-w        | iterative_single |      0.0220556   |                   3 |       5 |    0.8125 |        1 | False              |
|        nan |     nan | heldout_numeric_rmse           | credit-approval | mean             |     -0.494719    |                   4 |       5 |    0.4375 |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | credit-approval | median           |     -0.182729    |                   4 |       5 |    0.125  |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | credit-approval | knn5             |     -0.400911    |                   2 |       5 |    1      |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | credit-approval | iterative_single |     -0.257574    |                   4 |       5 |    0.125  |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | hepatitis       | mean             |     -0.132563    |                   3 |       5 |    0.625  |        1 | True               |
|        nan |     nan | heldout_numeric_rmse           | hepatitis       | median           |      0.084845    |                   1 |       5 |    0.625  |        1 | False              |
|        nan |     nan | heldout_numeric_rmse           | hepatitis       | knn5             |      0.235808    |                   1 |       5 |    0.3125 |        1 | False              |
|        nan |     nan | heldout_numeric_rmse           | hepatitis       | iterative_single |      0.340183    |                   1 |       5 |    0.125  |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | credit-approval | mean             |      0.0308282   |                   1 |       5 |    0.4375 |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | credit-approval | median           |      0.108129    |                   0 |       5 |    0.0625 |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | credit-approval | knn5             |      0.0988706   |                   0 |       5 |    0.0625 |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | credit-approval | iterative_single |      0.0393205   |                   1 |       5 |    0.4375 |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | hepatitis       | mean             |     -0.00231795  |                   2 |       5 |    1      |        1 | True               |
|        nan |     nan | heldout_categorical_error_rate | hepatitis       | median           |     -0.0683076   |                   4 |       5 |    0.1875 |        1 | True               |
|        nan |     nan | heldout_categorical_error_rate | hepatitis       | knn5             |      0.0673879   |                   0 |       5 |    0.125  |        1 | False              |
|        nan |     nan | heldout_categorical_error_rate | hepatitis       | iterative_single |      0.00884087  |                   3 |       5 |    1      |        1 | False              |
