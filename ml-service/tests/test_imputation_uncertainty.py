import unittest
import math

import numpy as np

from app.services.imputation_uncertainty import pool_rubins_rules


class RubinPoolingTests(unittest.TestCase):
    def test_pools_manual_example_with_barnard_rubin_interval(self):
        estimates = [2.0, 4.0, 6.0]
        within_variances = [1.0, 1.0, 1.0]

        pooled = pool_rubins_rules(estimates, within_variances, complete_data_df=20)

        self.assertAlmostEqual(pooled.estimate, 4.0)
        self.assertAlmostEqual(pooled.within_imputation_variance, 1.0)
        self.assertAlmostEqual(pooled.between_imputation_variance, 4.0)
        self.assertAlmostEqual(pooled.total_variance, 19 / 3)
        self.assertAlmostEqual(pooled.standard_error, 2.516611478423583)
        self.assertAlmostEqual(pooled.missing_information_fraction, 0.8421052631578947)
        self.assertAlmostEqual(pooled.degrees_of_freedom, 1.425728050351527)
        self.assertAlmostEqual(pooled.confidence_interval[0], -12.297192921016105)
        self.assertAlmostEqual(pooled.confidence_interval[1], 20.297192921016105)

    def test_zero_within_and_between_variance_produces_degenerate_interval(self):
        pooled = pool_rubins_rules([3.0, 3.0], [0.0, 0.0], complete_data_df=10)

        self.assertEqual(pooled.total_variance, 0.0)
        self.assertEqual(pooled.standard_error, 0.0)
        self.assertEqual(pooled.confidence_interval, (3.0, 3.0))

    def test_positive_between_variance_without_within_variance_has_no_finite_interval(self):
        pooled = pool_rubins_rules([1.0, 3.0], [0.0, 0.0], complete_data_df=10)

        self.assertEqual(pooled.within_imputation_variance, 0.0)
        self.assertGreater(pooled.between_imputation_variance, 0.0)
        self.assertGreater(pooled.total_variance, 0.0)
        self.assertEqual(pooled.degrees_of_freedom, 0.0)
        self.assertIsNone(pooled.confidence_interval)

    def test_zero_between_variance_has_finite_barnard_rubin_degrees_of_freedom(self):
        pooled = pool_rubins_rules([2.0, 2.0, 2.0], [1.0, 1.0, 1.0], complete_data_df=20)

        self.assertEqual(pooled.between_imputation_variance, 0.0)
        self.assertGreater(pooled.degrees_of_freedom, 0.0)
        self.assertLessEqual(pooled.degrees_of_freedom, 20.0)
        self.assertIsNotNone(pooled.confidence_interval)

    def test_pooling_is_numerically_stable_for_large_estimates(self):
        pooled = pool_rubins_rules(
            [1e12, 1e12 + 1, 1e12 + 2],
            [1e-4, 1e-4, 1e-4],
            complete_data_df=100,
        )

        self.assertTrue(math.isfinite(pooled.estimate))
        self.assertTrue(math.isfinite(pooled.between_imputation_variance))
        self.assertTrue(math.isfinite(pooled.total_variance))
        self.assertTrue(math.isfinite(pooled.standard_error))

    def test_rejects_invalid_inputs(self):
        invalid_cases = [
            (([1.0], [1.0], 10), "at least two"),
            (([1.0, 2.0], [1.0], 10), "equal-length"),
            (([[1.0, 2.0], [2.0, 3.0]], [[1.0, 1.0], [1.0, 1.0]], 10), "1D"),
            (([1.0, np.nan], [1.0, 1.0], 10), "estimates"),
            (([1.0, 2.0], [-1.0, 1.0], 10), "non-negative"),
            (([1.0, 2.0], [1.0, np.inf], 10), "finite"),
            (([1.0, 2.0], [1.0, 1.0], 0), "complete_data_df"),
            (([1.0, 2.0], [1.0, 1.0], None), "complete_data_df"),
            (([1.0, 2.0], [1.0, 1.0], "10"), "complete_data_df"),
            (([1.0, 2.0], [1.0, 1.0], 10, 1.0), "confidence_level"),
            (([1.0, 2.0], [1.0, 1.0], 10, None), "confidence_level"),
            (([1.0, 2.0], [1.0, 1.0], 10, float("nan")), "confidence_level"),
        ]
        for arguments, expected_message in invalid_cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, expected_message):
                    pool_rubins_rules(*arguments)

    def test_rejects_unrepresentable_between_imputation_variance(self):
        with self.assertRaisesRegex(ValueError, "between-imputation variance"):
            pool_rubins_rules(
                [-1e308, 1e308],
                [0.0, 0.0],
                complete_data_df=10,
            )

    def test_rejects_unrepresentable_total_variance(self):
        estimate_magnitude = math.sqrt(6.5e307)
        with self.assertRaisesRegex(ValueError, "total variance"):
            pool_rubins_rules(
                [-estimate_magnitude, estimate_magnitude],
                [0.0, 0.0],
                complete_data_df=10,
            )


if __name__ == "__main__":
    unittest.main()
