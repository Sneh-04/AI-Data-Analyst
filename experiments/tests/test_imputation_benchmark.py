import unittest

import numpy as np
import pandas as pd

from imputation_benchmark import (
    evaluate_methods,
    missingness_probabilities,
    reconstruction_metrics,
    simulate_missingness,
    summarize_paired_comparisons,
    summarize,
)


class MissingnessSimulationTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(10)
        source = rng.normal(size=5000)
        self.frame = pd.DataFrame({
            "source": source,
            "target": 2.5 * source + rng.normal(scale=0.5, size=len(source)),
        })

    def test_mar_propensity_depends_on_observed_predictor_and_hits_expected_rate(self):
        for rate in (0.1, 0.2, 0.3, 0.4):
            with self.subTest(rate=rate):
                probabilities = missingness_probabilities(
                    self.frame, "target", rate, "mar", mar_column="source"
                )
                self.assertAlmostEqual(probabilities.mean(), rate, places=8)
                self.assertGreater(
                    np.corrcoef(probabilities, self.frame["source"])[0, 1],
                    0.5,
                )

    def test_mnar_propensity_depends_on_target_value(self):
        probabilities = missingness_probabilities(
            self.frame, "target", 0.3, "mnar"
        )
        self.assertAlmostEqual(probabilities.mean(), 0.3, places=8)
        self.assertGreater(
            np.corrcoef(probabilities, self.frame["target"])[0, 1],
            0.5,
        )

    def test_simulation_preserves_truth_and_repeats_exactly_for_seed(self):
        for rate in (0.1, 0.2, 0.3, 0.4):
            with self.subTest(rate=rate):
                first = simulate_missingness(
                    self.frame, "target", rate, "mar", seed=11, mar_column="source"
                )
                second = simulate_missingness(
                    self.frame, "target", rate, "mar", seed=11, mar_column="source"
                )
                pd.testing.assert_series_equal(first.mask, second.mask)
                pd.testing.assert_series_equal(first.ground_truth, self.frame["target"])
                pd.testing.assert_series_equal(first.ground_truth, second.ground_truth)
                self.assertTrue(first.masked_data.loc[first.mask, "target"].isna().all())
                self.assertTrue(
                    first.masked_data.loc[~first.mask, "target"].equals(
                        self.frame.loc[~first.mask, "target"]
                    )
                )
                self.assertAlmostEqual(first.mask.mean(), rate, delta=0.03)

    def test_preexisting_missing_targets_are_not_evaluated_or_remasked(self):
        frame = self.frame.copy()
        frame.loc[0:9, "target"] = np.nan

        sample = simulate_missingness(
            frame, "target", 0.2, "mar", seed=19, mar_column="source"
        )

        self.assertFalse(sample.mask.loc[0:9].any())
        self.assertTrue(sample.ground_truth.loc[0:9].isna().all())
        self.assertTrue(np.isfinite(sample.ground_truth.loc[sample.mask]).all())

    def test_invalid_missing_rates_and_unsupported_targets_are_rejected(self):
        for rate in (0, 1, -0.1, 1.1):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                missingness_probabilities(
                    self.frame, "target", rate, "mar", mar_column="source"
                )
        with self.assertRaises(TypeError):
            missingness_probabilities(
                self.frame.assign(label=["a"] * len(self.frame)),
                "label",
                0.2,
                "mnar",
            )
        with self.assertRaises(ValueError):
            missingness_probabilities(self.frame, "target", 0.2, "mar")


class EvaluationTests(unittest.TestCase):
    def test_metrics_are_computed_only_on_masked_cells(self):
        truth = pd.Series([1.0, 3.0, 5000.0])
        mask = pd.Series([True, True, False], dtype=bool)

        metrics = reconstruction_metrics(truth, [2.0, 1.0, -9000.0], mask)

        self.assertAlmostEqual(metrics["rmse"], np.sqrt(2.5))
        self.assertAlmostEqual(metrics["mae"], 1.5)

    def test_metrics_reject_empty_or_missing_truth_evaluation_masks(self):
        truth = pd.Series([1.0, np.nan])
        with self.assertRaises(ValueError):
            reconstruction_metrics(truth, [1.0, 2.0], pd.Series([False, False]))
        with self.assertRaises(ValueError):
            reconstruction_metrics(truth, [1.0, 2.0], pd.Series([False, True]))

    def test_all_methods_share_same_mask_and_ignore_categorical_predictors(self):
        rng = np.random.RandomState(5)
        source = rng.normal(size=120)
        frame = pd.DataFrame({
            "source": source,
            "target": 1.7 * source + rng.normal(scale=0.2, size=len(source)),
            "category": np.where(source > 0, "high", "low"),
        })
        sample = simulate_missingness(
            frame, "target", 0.2, "mnar", seed=7
        )
        original_masked_data = sample.masked_data.copy(deep=True)

        results = evaluate_methods(sample, "target", seed=7)

        self.assertEqual(
            {result["method"] for result in results},
            {
                "mean",
                "median",
                "knn_k5",
                "iterative_bayesian_ridge",
                "proposed_iterative_multiple",
            },
        )
        self.assertTrue(
            all(np.isfinite(result["rmse"]) and np.isfinite(result["mae"]) for result in results)
        )
        self.assertTrue(all(result["runtime_seconds"] >= 0 for result in results))
        pd.testing.assert_frame_equal(sample.masked_data, original_masked_data)

    def test_methods_are_reproducible_and_do_not_score_originally_missing_values(self):
        rng = np.random.RandomState(8)
        source = rng.normal(size=100)
        frame = pd.DataFrame({
            "source": source,
            "target": source + rng.normal(scale=0.3, size=len(source)),
        })
        frame.loc[[0, 1, 2], "target"] = np.nan
        first = simulate_missingness(frame, "target", 0.25, "mar", 31, "source")
        second = simulate_missingness(frame, "target", 0.25, "mar", 31, "source")

        first_results = evaluate_methods(first, "target", seed=31)
        second_results = evaluate_methods(second, "target", seed=31)

        pd.testing.assert_series_equal(first.mask, second.mask)
        for first_result, second_result in zip(first_results, second_results):
            self.assertEqual(first_result["method"], second_result["method"])
            self.assertAlmostEqual(first_result["rmse"], second_result["rmse"], places=12)
            self.assertAlmostEqual(first_result["mae"], second_result["mae"], places=12)

    def test_summary_reports_trial_variability_and_95_percent_intervals(self):
        rows = pd.DataFrame({
            "dataset": ["sample"] * 3,
            "mechanism": ["mar"] * 3,
            "mask_rate": [0.2] * 3,
            "method": ["mean"] * 3,
            "trial": [0, 1, 2],
            "realized_missing_rate": [0.18, 0.2, 0.22],
            "rmse": [1.0, 2.0, 3.0],
            "mae": [0.5, 1.0, 1.5],
            "runtime_seconds": [0.01, 0.02, 0.03],
        })

        summary = summarize(rows).iloc[0]

        self.assertEqual(summary["n_trials"], 3)
        self.assertAlmostEqual(summary["mean_rmse"], 2.0)
        self.assertAlmostEqual(summary["std_rmse"], 1.0)
        self.assertLess(summary["rmse_ci95_low"], summary["mean_rmse"])
        self.assertGreater(summary["rmse_ci95_high"], summary["mean_rmse"])
        self.assertNotIn("runtime_seconds_ci95_low", summary.index)
        self.assertNotIn("runtime_seconds_ci95_high", summary.index)

    def test_paired_comparisons_use_same_trial_masks_and_report_difference_intervals(self):
        methods = [
            "mean",
            "median",
            "knn_k5",
            "iterative_bayesian_ridge",
            "proposed_iterative_multiple",
        ]
        rows = []
        proposed_rmse = [1.0, 2.0, 3.0]
        mean_rmse = [2.0, 4.0, 6.0]
        for trial in range(3):
            for method in methods:
                rmse = (
                    proposed_rmse[trial]
                    if method == "proposed_iterative_multiple"
                    else mean_rmse[trial]
                    if method == "mean"
                    else mean_rmse[trial] + 10
                )
                rows.append({
                    "dataset": "sample",
                    "mechanism": "mar",
                    "mask_rate": 0.2,
                    "trial": trial,
                    "method": method,
                    "rmse": rmse,
                    "mae": rmse / 2,
                })

        comparisons = summarize_paired_comparisons(pd.DataFrame(rows))
        rmse_mean_comparison = comparisons.query(
            "metric == 'rmse' and baseline == 'mean'"
        ).iloc[0]
        self.assertEqual(len(comparisons), 8)
        self.assertEqual(rmse_mean_comparison["n_trials"], 3)
        self.assertAlmostEqual(rmse_mean_comparison["mean_proposed_minus_baseline"], -2.0)
        self.assertAlmostEqual(rmse_mean_comparison["std_paired_difference"], 1.0)
        self.assertLess(rmse_mean_comparison["paired_difference_ci95_low"], -2.0)
        self.assertGreater(rmse_mean_comparison["paired_difference_ci95_high"], -2.0)


if __name__ == "__main__":
    unittest.main()
