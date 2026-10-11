# Imputation Uncertainty

Dataset/mechanism rows summarize trials; pooled rows combine all datasets within each mechanism. `coverage90` is weighted by masked-cell count: sum(coverage90 × n_masked) / sum(n_masked). `uncertainty_spearman` is the unweighted mean across runs with a measured value. Coverage and uncertainty are reported for methods whose source rows contain those metrics.

| scope             | dataset       | mechanism   | method                 |   coverage90 |   uncertainty_spearman |   masked_cells |   run_count |
|-------------------|---------------|-------------|------------------------|--------------|------------------------|----------------|-------------|
| dataset_mechanism | breast_cancer | MAR         | marginal_bootstrap_OLD |     0.679674 |             -0.165018  |          24422 |          24 |
| dataset_mechanism | breast_cancer | MAR         | mice_multiple_NEW      |     0.780526 |              0.384492  |          24422 |          24 |
| dataset_mechanism | breast_cancer | MCAR        | marginal_bootstrap_OLD |     0.872545 |              0.113106  |          27288 |          24 |
| dataset_mechanism | breast_cancer | MCAR        | mice_multiple_NEW      |     0.901312 |              0.648277  |          27288 |          24 |
| dataset_mechanism | breast_cancer | MNAR        | marginal_bootstrap_OLD |     0.471165 |             -0.107649  |          27328 |          24 |
| dataset_mechanism | breast_cancer | MNAR        | mice_multiple_NEW      |     0.598617 |              0.548347  |          27328 |          24 |
| dataset_mechanism | diabetes      | MAR         | marginal_bootstrap_OLD |     0.871692 |              0.0207531 |          19157 |          24 |
| dataset_mechanism | diabetes      | MAR         | mice_multiple_NEW      |     0.860156 |              0.327669  |          19157 |          24 |
| dataset_mechanism | diabetes      | MCAR        | marginal_bootstrap_OLD |     0.881965 |              0.0235988 |          21248 |          24 |
| dataset_mechanism | diabetes      | MCAR        | mice_multiple_NEW      |     0.886436 |              0.424215  |          21248 |          24 |
| dataset_mechanism | diabetes      | MNAR        | marginal_bootstrap_OLD |     0.59531  |             -0.0980231 |          21236 |          24 |
| dataset_mechanism | diabetes      | MNAR        | mice_multiple_NEW      |     0.678565 |              0.430302  |          21236 |          24 |
| dataset_mechanism | iris          | MAR         | marginal_bootstrap_OLD |     0.846119 |             -0.0173665 |           2216 |          24 |
| dataset_mechanism | iris          | MAR         | mice_multiple_NEW      |     0.84296  |              0.422939  |           2216 |          24 |
| dataset_mechanism | iris          | MCAR        | marginal_bootstrap_OLD |     0.883264 |             -0.013504  |           2904 |          24 |
| dataset_mechanism | iris          | MCAR        | mice_multiple_NEW      |     0.883609 |              0.394758  |           2904 |          24 |
| dataset_mechanism | iris          | MNAR        | marginal_bootstrap_OLD |     0.700938 |             -0.0318006 |           2879 |          24 |
| dataset_mechanism | iris          | MNAR        | mice_multiple_NEW      |     0.733241 |              0.494762  |           2879 |          24 |
| dataset_mechanism | wine          | MAR         | marginal_bootstrap_OLD |     0.83647  |             -0.0238685 |          10255 |          24 |
| dataset_mechanism | wine          | MAR         | mice_multiple_NEW      |     0.901219 |              0.105347  |          10255 |          24 |
| dataset_mechanism | wine          | MCAR        | marginal_bootstrap_OLD |     0.871595 |              0.0146518 |          11160 |          24 |
| dataset_mechanism | wine          | MCAR        | mice_multiple_NEW      |     0.885394 |              0.104817  |          11160 |          24 |
| dataset_mechanism | wine          | MNAR        | marginal_bootstrap_OLD |     0.582937 |             -0.0770954 |          11135 |          24 |
| dataset_mechanism | wine          | MNAR        | mice_multiple_NEW      |     0.657027 |              0.147543  |          11135 |          24 |
| pooled_mechanism  | ALL           | MAR         | marginal_bootstrap_OLD |     0.780571 |             -0.046375  |          56050 |          96 |
| pooled_mechanism  | ALL           | MAR         | mice_multiple_NEW      |     0.832293 |              0.310112  |          56050 |          96 |
| pooled_mechanism  | ALL           | MCAR        | marginal_bootstrap_OLD |     0.87607  |              0.0344632 |          62600 |          96 |
| pooled_mechanism  | ALL           | MCAR        | mice_multiple_NEW      |     0.892604 |              0.393017  |          62600 |          96 |
| pooled_mechanism  | ALL           | MNAR        | marginal_bootstrap_OLD |     0.543753 |             -0.0786421 |          62578 |          96 |
| pooled_mechanism  | ALL           | MNAR        | mice_multiple_NEW      |     0.642334 |              0.405238  |          62578 |          96 |
