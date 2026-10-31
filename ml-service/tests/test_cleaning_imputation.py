import unittest

import numpy as np
import pandas as pd

from app.services.cleaning_service import fill_missing_values


class MultipleImputationTests(unittest.TestCase):
    def test_multiple_strategy_uses_feature_relationships_and_reports_uncertainty(self):
        rng = np.random.RandomState(17)
        feature = np.linspace(-2, 2, 160)
        target = 3 * feature + rng.normal(0, 0.04, size=len(feature))
        frame = pd.DataFrame({"feature": feature, "target": target})
        hidden = rng.rand(len(frame)) < 0.25
        expected = frame.loc[hidden, "target"].to_numpy()
        frame.loc[hidden, "target"] = np.nan

        imputed, repairs = fill_missing_values(frame, strategy="multiple")
        actual = imputed.loc[hidden, "target"].to_numpy()
        marginal = frame["target"].median()

        self.assertLess(np.sqrt(np.mean((actual - expected) ** 2)), 0.3)
        self.assertLess(
            np.sqrt(np.mean((actual - expected) ** 2)),
            np.sqrt(np.mean((np.full_like(expected, marginal) - expected) ** 2)),
        )
        np.testing.assert_array_equal(
            imputed.loc[~hidden, "target"].to_numpy(),
            target[~hidden],
        )

        target_repairs = [repair for repair in repairs if repair["column"] == "target"]
        self.assertEqual(len(target_repairs), int(hidden.sum()))
        self.assertTrue(
            all(repair["strategy_used"] == "multiple_imputation" for repair in target_repairs)
        )
        self.assertTrue(
            all(
                np.isfinite(repair["imputation_uncertainty"])
                and repair["imputation_uncertainty"] >= 0
                for repair in target_repairs
            )
        )

    def test_multiple_strategy_retains_categorical_mode_fallback(self):
        frame = pd.DataFrame({
            "feature": [1.0, 2.0, 3.0, 4.0],
            "category": ["a", "a", None, "b"],
        })

        imputed, repairs = fill_missing_values(frame, strategy="multiple")

        self.assertEqual(imputed.loc[2, "category"], "a")
        self.assertTrue(
            any(
                repair["column"] == "category" and repair["strategy_used"] == "mode"
                for repair in repairs
            )
        )

    def test_multiple_strategy_uses_marginal_fallback_without_predictors(self):
        frame = pd.DataFrame({"target": [1.0, np.nan, 3.0, 4.0]})

        imputed, repairs = fill_missing_values(frame, strategy="multiple")

        self.assertTrue(np.isfinite(imputed.loc[1, "target"]))
        self.assertEqual(len(repairs), 1)
        self.assertGreaterEqual(repairs[0]["imputation_uncertainty"], 0)

    def test_multiple_strategy_is_reproducible_for_a_fixed_seed(self):
        frame = pd.DataFrame({
            "feature": np.linspace(-2, 2, 30),
            "target": np.linspace(1, 4, 30),
        })
        frame.loc[[2, 8, 15], "target"] = np.nan

        first, first_repairs = fill_missing_values(
            frame, strategy="multiple", random_state=23
        )
        second, second_repairs = fill_missing_values(
            frame, strategy="multiple", random_state=23
        )

        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(first_repairs, second_repairs)

    def test_mnar_delta_adjusts_missing_values_without_changing_observed_values(self):
        frame = pd.DataFrame({"target": [1.0, np.nan, 3.0, np.nan, 5.0]})

        baseline, _ = fill_missing_values(frame, strategy="multiple", random_state=23)
        adjusted, repairs = fill_missing_values(
            frame,
            strategy="multiple",
            random_state=23,
            mnar_deltas={"target": 2.5},
        )

        np.testing.assert_array_equal(adjusted.loc[frame["target"].notna(), "target"], frame.loc[
            frame["target"].notna(), "target"
        ])
        np.testing.assert_allclose(
            adjusted.loc[frame["target"].isna(), "target"],
            baseline.loc[frame["target"].isna(), "target"] + 2.5,
        )
        self.assertTrue(all(repair["mnar_delta"] == 2.5 for repair in repairs))
        self.assertTrue(
            all(
                repair["imputation_uncertainty_type"] == "predictive_draw_spread"
                for repair in repairs
            )
        )

    def test_mnar_delta_applies_to_feature_aware_imputations(self):
        frame = pd.DataFrame({
            "feature": np.linspace(-2, 2, 40),
            "target": np.linspace(-4, 4, 40),
        })
        frame.loc[[3, 10, 21], "target"] = np.nan

        baseline, _ = fill_missing_values(frame, strategy="multiple", random_state=11)
        adjusted, _ = fill_missing_values(
            frame,
            strategy="multiple",
            random_state=11,
            mnar_deltas={"target": -1.25},
        )

        missing = frame["target"].isna()
        np.testing.assert_allclose(
            adjusted.loc[missing, "target"],
            baseline.loc[missing, "target"] - 1.25,
        )

    def test_mnar_delta_rejects_unknown_non_numeric_and_non_multiple_inputs(self):
        frame = pd.DataFrame({"target": [1.0, np.nan], "category": ["a", None]})
        invalid_cases = [
            ({"unknown": 1.0}, "unknown column"),
            ({"category": 1.0}, "numeric column"),
            ({"target": float("nan")}, "finite number"),
        ]
        for deltas, expected_message in invalid_cases:
            with self.subTest(deltas=deltas):
                with self.assertRaisesRegex(ValueError, expected_message):
                    fill_missing_values(frame, strategy="multiple", mnar_deltas=deltas)
        with self.assertRaisesRegex(ValueError, "only be used"):
            fill_missing_values(frame, strategy="median", mnar_deltas={"target": 1.0})


if __name__ == "__main__":
    unittest.main()
