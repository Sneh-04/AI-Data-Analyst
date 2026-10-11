# M3 Shortlisting Noninferiority

Frozen M3 evidence; one paired observation per series is Auto minus auto_no_shortlist MASE averaged over that series' four saved rolling windows. The +0.05 MASE margin was fixed before M3 results existed. As in the six-series analysis, both the one-sided t upper bound (df=19) and nonparametric percentile-bootstrap upper bound must be below the margin to establish non-inferiority. Non-inferiority not established.

|   series_count | paired_difference_definition      |   mean_paired_mase_difference |   one_sided_95pct_t_upper_df19 |   one_sided_95pct_bootstrap_upper | bootstrap_method                                                                                   |   noninferiority_margin | noninferiority_established   |
|----------------|-----------------------------------|-------------------------------|--------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------|-------------------------|------------------------------|
|             20 | Auto minus auto_no_shortlist MASE |                     0.0187198 |                      0.0480264 |                         0.0526187 | Nonparametric percentile bootstrap resampling series differences; 200000 replicates; seed 20261011 |                    0.05 | False                        |
