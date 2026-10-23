from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch
from urllib.error import URLError

import numpy as np
import pandas as pd
import pytest
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer as SklearnIterativeImputer

from datasets.registry import (
    DATASETS,
    DatasetSpec,
    _feature_metadata_cache_path,
    _retry_network_fetch,
    classify_openml_features,
    dataset_frame_sha256,
    fetch_dataset,
    validate_registry,
    write_manifest_record,
)
import datasets.registry as registry
from make_real_dataset_tables import (
    _add_rmse_ratio_vs_mean,
    _effect_size_tables,
    _concat_unique,
    _dataset_level_significance,
    _holm_per_metric_sensitivity,
    _merge_summaries,
    _negligible_missingness_datasets,
    _scoreable_protocol_a_cell_count,
    _select_protocol_b_significance_input,
    _study_labels,
    _summarize_protocol_b,
    _uncertainty_distribution_table,
)
from make_mice_ablation_tables import summarize
import run_stage
from run_stage import is_complete_run
from run_real_datasets import (
    EncodedFrame,
    MASK_RATES,
    MECHANISMS,
    METHODS,
    ObservedScaler,
    _fit_transform_method,
    _metric_rows,
    make_mask,
)
import run_mice_ablation as mice_ablation
import run_real_datasets as real_benchmark
from make_real_dataset_tables import _with_coverage_label


class RegistryAndManifestTests(unittest.TestCase):
    def test_registry_schema_is_valid_and_has_verified_runtime_identifiers(self):
        validate_registry()
        self.assertGreaterEqual(len(DATASETS), 10)
        for key, spec in DATASETS.items():
            with self.subTest(dataset=key):
                self.assertEqual(spec.name, key)
                self.assertGreater(spec.data_id, 0)
                self.assertGreater(spec.version, 0)
                self.assertEqual(spec.n_rows, int(spec.n_rows))
                self.assertIn(spec.task_type, {"classification", "regression"})
                self.assertTrue(spec.license_citation_note)

    def test_manifest_records_shape_types_missing_rates_and_sha256(self):
        table = pd.DataFrame({
            "number": [1.0, np.nan, 3.0],
            "category": ["a", "b", None],
            "target": ["yes", "no", "yes"],
        })
        spec = DATASETS["breast-w"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            cached = path / "fixture.csv"
            table.to_csv(cached, index=False)
            manifest_path = path / "manifest.json"
            record = write_manifest_record(
                spec, table, cached, manifest_path, fetch_date="2026-10-11"
            )
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))[spec.name]
            self.assertEqual(saved["shape"], [3, 3])
            self.assertEqual(saved["per_column_missing_rate"]["number"], 1 / 3)
            self.assertEqual(saved["fetch_date"], "2026-10-11")
            self.assertEqual(record["sha256"], hashlib.sha256(cached.read_bytes()).hexdigest())
            self.assertEqual(saved["sha256"], record["sha256"])

    def test_rmse_ratio_matches_mean_imputer_within_each_trial_cell(self):
        raw = pd.DataFrame({
            "dataset": ["d", "d", "d", "d"],
            "mechanism": ["MCAR"] * 4,
            "mask_rate": [0.1] * 4,
            "trial": [0, 0, 1, 1],
            "method": ["mean", "knn5", "mean", "knn5"],
            "numeric_rmse": [2.0, 1.0, 4.0, 6.0],
            "categorical_error_rate": [0.2, 0.3, 0.2, 0.3],
        })
        result = _add_rmse_ratio_vs_mean(raw)
        np.testing.assert_allclose(result["rmse_ratio_vs_mean"], [1.0, 0.5, 1.0, 1.5])
        np.testing.assert_array_equal(result["numeric_rmse"], raw["numeric_rmse"])
        np.testing.assert_array_equal(result["categorical_error_rate"], raw["categorical_error_rate"])

    def test_cached_dataset_loads_without_network_or_openml_fetch(self):
        spec = DatasetSpec(
            "offline-fixture",
            "OpenML:offline-fixture",
            900001,
            1,
            "target",
            "classification",
            4,
            1,
            1,
            0.0,
            "Synthetic offline test fixture.",
        )
        table = pd.DataFrame({
            "measure": [1.0, 2.0, 3.0, 4.0],
            "kind": ["a", "b", "a", "b"],
            "target": ["yes", "no", "yes", "no"],
        })
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache_dir = root / "cache"
            cache_dir.mkdir()
            cache_file = cache_dir / "offline-fixture.csv"
            table.to_csv(cache_file, index=False)
            feature_types = {"measure": "numeric", "kind": "nominal"}
            write_manifest_record(
                spec,
                table,
                cache_file,
                root / "manifest.json",
                feature_types=feature_types,
            )
            with (
                patch.object(registry, "fetch_openml", side_effect=URLError("blocked")),
                patch.object(registry, "urlopen", side_effect=URLError("blocked")),
            ):
                features, target, metadata = fetch_dataset(spec, cache_dir)
            self.assertTrue(
                _feature_metadata_cache_path(spec, cache_dir).is_file()
            )
        self.assertEqual(metadata["source"], "verified_local_cache")
        self.assertTrue(pd.api.types.is_numeric_dtype(features["measure"]))
        self.assertTrue(isinstance(features["kind"].dtype, pd.CategoricalDtype))
        self.assertEqual(dataset_frame_sha256(features, target), dataset_frame_sha256(
            table.drop(columns="target"), table["target"]
        ))

    def test_missing_metadata_sidecar_is_fetched_written_and_hashed(self):
        spec = DatasetSpec(
            "offline-fixture",
            "OpenML:offline-fixture",
            900002,
            1,
            "target",
            "classification",
            4,
            1,
            1,
            0.0,
            "Synthetic offline test fixture.",
        )
        table = pd.DataFrame({
            "measure": [1.0, 2.0, 3.0, 4.0],
            "kind": ["a", "b", "a", "b"],
            "target": ["yes", "no", "yes", "no"],
        })
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache_dir = root / "cache"
            cache_dir.mkdir()
            cache_file = cache_dir / "offline-fixture.csv"
            table.to_csv(cache_file, index=False)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps({
                spec.name: {
                    "cached_file": cache_file.name,
                    "sha256": hashlib.sha256(cache_file.read_bytes()).hexdigest(),
                }
            }), encoding="utf-8")
            metadata = {"measure": "numeric", "kind": "nominal"}
            with (
                patch.object(registry, "_openml_feature_types", return_value=metadata) as fetch,
                patch.object(registry, "fetch_openml", side_effect=AssertionError("unexpected data fetch")),
            ):
                features, _, _ = fetch_dataset(spec, cache_dir)
            fetch.assert_called_once_with(spec.data_id)
            self.assertTrue(pd.api.types.is_numeric_dtype(features["measure"]))
            sidecar = _feature_metadata_cache_path(spec, cache_dir)
            record = json.loads(manifest_path.read_text(encoding="utf-8"))[spec.name]
            self.assertTrue(sidecar.is_file())
            self.assertEqual(
                record["feature_metadata_cache_file"],
                f"feature_metadata/{sidecar.name}",
            )
            self.assertEqual(
                record["feature_metadata_cache_sha256"],
                hashlib.sha256(sidecar.read_bytes()).hexdigest(),
            )

    def test_metadata_sidecar_hash_mismatch_fails_clearly(self):
        spec = DatasetSpec(
            "offline-fixture",
            "OpenML:offline-fixture",
            900003,
            1,
            "target",
            "classification",
            4,
            1,
            1,
            0.0,
            "Synthetic offline test fixture.",
        )
        with tempfile.TemporaryDirectory() as directory:
            cache_dir = Path(directory) / "cache"
            cache_dir.mkdir()
            sidecar = _feature_metadata_cache_path(spec, cache_dir)
            sidecar.parent.mkdir(parents=True)
            sidecar.write_text(json.dumps({
                "data_id": spec.data_id,
                "version": spec.version,
                "feature_types": {"measure": "numeric"},
            }), encoding="utf-8")
            with patch.object(registry, "_openml_feature_types") as fetch:
                with self.assertRaisesRegex(
                    registry.DatasetLoadError, "feature metadata SHA-256 mismatch"
                ):
                    registry._load_feature_types(
                        spec, cache_dir, {"feature_metadata_cache_sha256": "bad"}
                    )
            fetch.assert_not_called()

    def test_network_fetch_retries_three_times_with_exponential_backoff(self):
        attempts = []

        def fetch():
            attempts.append(len(attempts) + 1)
            if len(attempts) < 3:
                raise URLError("temporarily unavailable")
            return "ok"

        with patch.object(registry.time, "sleep") as sleep:
            self.assertEqual(_retry_network_fetch(fetch, "fixture"), "ok")
        self.assertEqual(len(attempts), 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_non_network_fetch_error_is_not_retried(self):
        attempts = []

        def fetch():
            attempts.append(1)
            raise ValueError("invalid dataset payload")

        with patch.object(registry.time, "sleep") as sleep:
            with self.assertRaisesRegex(ValueError, "invalid dataset payload"):
                _retry_network_fetch(fetch, "fixture")
        self.assertEqual(len(attempts), 1)
        sleep.assert_not_called()

    @pytest.mark.network
    @pytest.mark.skipif(
        __import__("os").environ.get("RUN_OPENML_TESTS") != "1",
        reason="Set RUN_OPENML_TESTS=1 to run OpenML network tests.",
    )
    def test_openml_name_resolves_to_registered_version(self):
        from datasets.registry import fetch_dataset

        features, target, metadata = fetch_dataset(DATASETS["breast-w"])
        self.assertEqual((metadata["data_id"], metadata["version"]), (15, 1))
        self.assertEqual(len(features), len(target))


class MixedTypeEncodingTests(unittest.TestCase):
    def test_encode_decode_round_trip_preserves_numeric_and_categorical_values(self):
        frame = pd.DataFrame({
            "measurement": [1.25, 2.5, 3.75, 5.0],
            "group": pd.Series(["low", "high", "medium", "low"], dtype="category"),
        })
        encoded = EncodedFrame.fit_transformer(frame)
        scaler = ObservedScaler.fit(encoded.values)
        decoded = encoded.decode(scaler.transform(encoded.values), scaler)
        np.testing.assert_allclose(decoded[:, 0], frame["measurement"].to_numpy())
        categories = encoded.categories["group"]
        expected = frame["group"].astype(str).map({value: i for i, value in enumerate(categories)}).to_numpy()
        np.testing.assert_array_equal(decoded[:, 1].astype(int), expected)

    def test_missing_categorical_entries_round_trip_as_missing(self):
        frame = pd.DataFrame({"category": ["b", None, "a"]})
        encoded = EncodedFrame.fit_transformer(frame)
        scaler = ObservedScaler.fit(encoded.values)
        decoded = encoded.decode(scaler.transform(encoded.values), scaler)
        self.assertTrue(np.isnan(encoded.values[1, 0]))
        self.assertTrue(np.isnan(decoded[1, 0]))

    def test_openml_metadata_classifies_numeric_category_and_numeric_string(self):
        raw = pd.DataFrame({
            "numeric_category": pd.Series([1, 2, 3], dtype="category"),
            "numeric_string": ["4.5", "bad", "6.5"],
            "string_coded_numeric": ["1.5", " ", "2.5"],
            "nominal": ["a", "b", "a"],
        })
        features, coercions = classify_openml_features(
            raw,
            {
                "numeric_category": "numeric",
                "numeric_string": "numeric",
                "string_coded_numeric": "string",
                "nominal": "nominal",
            },
            numeric_string_columns=("string_coded_numeric",),
        )
        self.assertTrue(pd.api.types.is_numeric_dtype(features["numeric_category"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(features["numeric_string"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(features["string_coded_numeric"]))
        self.assertEqual(coercions["numeric_category"], 0)
        self.assertEqual(coercions["numeric_string"], 1)
        self.assertTrue(np.isnan(features.loc[1, "numeric_string"]))
        self.assertEqual(coercions["string_coded_numeric"], 1)
        self.assertTrue(np.isnan(features.loc[1, "string_coded_numeric"]))
        self.assertFalse(pd.api.types.is_numeric_dtype(features["nominal"]))


class FoldIsolationTests(unittest.TestCase):
    def test_iterative_imputer_fit_receives_training_fold_only(self):
        train = np.array([[0.0, 10.0], [1.0, 11.0], [np.nan, 12.0], [3.0, 13.0]])
        test = np.array([[100000.0, np.nan], [200000.0, 99.0]])
        fit_inputs = []

        class RecordingImputer:
            def __init__(self, **kwargs):
                self.delegate = SklearnIterativeImputer(**kwargs)

            def fit_transform(self, values):
                fit_inputs.append(np.asarray(values).copy())
                return self.delegate.fit_transform(values)

            def transform(self, values):
                return self.delegate.transform(values)

        for method, expected_fits in (("iterative_single", 1), ("mice_multiple_NEW", 5)):
            fit_inputs.clear()
            with self.subTest(method=method), patch(
                "run_real_datasets.IterativeImputer", RecordingImputer
            ):
                filled_train, filled_test, _ = _fit_transform_method(
                    method, train, test, seed=5
                )
                self.assertEqual(len(fit_inputs), expected_fits)
                for fit_input in fit_inputs:
                    np.testing.assert_array_equal(fit_input, train)
                self.assertEqual(filled_train.shape, train.shape)
                self.assertEqual(filled_test.shape, test.shape)
                self.assertGreater(filled_test[0, 0], 10000)

    def test_project_mice_accepts_a_constant_training_feature(self):
        train = np.column_stack([np.full(30, 4.0), np.linspace(0.0, 1.0, 30)])
        train[[3, 11, 19], 0] = np.nan
        test = np.array([[np.nan, 0.25], [np.nan, 0.75]])
        _, filled_test, _ = _fit_transform_method(
            "mice_multiple_NEW", train, test, seed=17
        )
        self.assertTrue(np.isfinite(filled_test).all())
        np.testing.assert_allclose(filled_test[:, 0], 4.0, atol=1e-6)


class MaskingProtocolTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(7)
        driver = rng.normal(size=1000)
        related = 0.8 * driver + rng.normal(scale=0.5, size=1000)
        self.values = np.column_stack([driver, related, rng.normal(size=1000)])

    def test_mcar_rate_is_close_to_requested_rate(self):
        mask = make_mask(self.values, "MCAR", 0.2, np.random.RandomState(10))
        self.assertAlmostEqual(float(mask.mean()), 0.2, delta=0.02)

    def test_mar_driver_stays_observed_and_missingness_tracks_driver(self):
        mask = make_mask(self.values, "MAR", 0.2, np.random.RandomState(12))
        self.assertFalse(mask[:, 0].any())
        self.assertAlmostEqual(float(mask.mean()), 0.2, delta=0.03)
        self.assertGreater(np.corrcoef(self.values[:, 0], mask[:, 1:].mean(axis=1))[0, 1], 0.3)

    def test_mnar_mask_probability_depends_on_its_own_value(self):
        mask = make_mask(self.values, "MNAR", 0.2, np.random.RandomState(15))
        self.assertAlmostEqual(float(mask.mean()), 0.2, delta=0.03)
        self.assertGreater(np.corrcoef(self.values.ravel(), mask.ravel())[0, 1], 0.2)

    def test_mean_imputation_mcar_rmse_uses_full_data_standard_deviation(self):
        rng = np.random.RandomState(202)
        values = rng.normal(size=(5000, 2))
        encoder = EncodedFrame.fit_transformer(
            pd.DataFrame({"measurement_a": values[:, 0], "measurement_b": values[:, 1]})
        )
        scaler = ObservedScaler.fit(values)
        mask = make_mask(
            scaler.transform(values), "MCAR", 0.10, np.random.RandomState(17)
        )
        self.assertAlmostEqual(float(mask.mean()), 0.10, delta=0.02)
        masked = np.where(mask, np.nan, scaler.transform(values))
        estimate, _, _ = _fit_transform_method("mean", masked, masked, seed=17)
        metrics = _metric_rows(values, estimate, mask, encoder, scaler)
        self.assertGreaterEqual(metrics["numeric_rmse"], 0.8)
        self.assertLessEqual(metrics["numeric_rmse"], 1.3)
        self.assertTrue(np.isnan(metrics["categorical_error_rate"]))


class MiceAblationTests(unittest.TestCase):
    def test_complete_dataset_skip_requires_matching_run_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "run_config.json").write_text(
                json.dumps({
                    "dataset": "fixture",
                    "repeats": 1,
                    "seed": 42,
                    "max_rows": 5000,
                    "mechanisms": list(MECHANISMS),
                    "variants": list(mice_ablation.VARIANTS),
                }),
                encoding="utf-8",
            )
            pd.DataFrame([
                {
                    "dataset": "fixture",
                    "mechanism": mechanism,
                    "trial": 0,
                    "variant": variant,
                }
                for mechanism in MECHANISMS
                for variant in mice_ablation.VARIANTS
            ]).to_csv(run_dir / "ablation.csv", index=False)
            self.assertTrue(mice_ablation._is_complete_dataset(
                run_dir, "fixture", 1, MECHANISMS, 42, 5000
            ))
            self.assertFalse(mice_ablation._is_complete_dataset(
                run_dir, "fixture", 1, MECHANISMS, 42, 1000
            ))

    def test_variant_wiring_uses_expected_draw_counts_and_estimator_paths(self):
        masked = np.array([[np.nan, 2.0], [3.0, 4.0]])
        estimate = np.full((2, 2), 8.0)
        uncertainty = np.full((2, 2), 0.25)
        with (
            patch(
                "run_mice_ablation._project_mice_complete",
                return_value=(estimate, uncertainty),
            ) as project_m5,
            patch(
                "run_mice_ablation._project_mice_train_test",
                return_value=(estimate, estimate.copy(), uncertainty),
            ) as project_train_test,
            patch(
                "run_mice_ablation._project_deterministic",
                return_value=estimate,
            ) as deterministic,
            patch(
                "run_mice_ablation._fit_transform_method",
                return_value=(estimate, estimate, None),
            ) as harness_method,
            patch(
                "run_mice_ablation._iterative_single",
                return_value=(estimate, None),
            ) as iterative,
        ):
            mice_ablation._variant_estimate("project_m5", masked, 17)
            project_m5.assert_called_once_with(masked, 17)
            for variant, expected_draws in (("project_m20", 20), ("project_m50", 50)):
                result, _ = mice_ablation._variant_estimate(variant, masked, 17)
                project_train_test.assert_called_with(
                    masked, masked, 17, n_imputations=expected_draws
                )
                self.assertEqual(result[0, 1], masked[0, 1])
                self.assertTrue(np.isfinite(result[0, 0]))
            mice_ablation._variant_estimate("project_deterministic", masked, 17)
            deterministic.assert_called_once_with(masked, 17)
            mice_ablation._variant_estimate("iterative_single_as_is", masked, 17)
            harness_method.assert_called_once_with(
                "iterative_single", masked, masked, 17
            )
            mice_ablation._variant_estimate(
                "iterative_single_posterior_true", masked, 17
            )
            mice_ablation._variant_estimate(
                "iterative_single_posterior_false", masked, 17
            )
            self.assertEqual(
                [call.kwargs["sample_posterior"] for call in iterative.call_args_list],
                [True, False],
            )

    def test_new_variants_route_to_bounded_or_unbounded_estimators(self):
        masked = np.array([[np.nan, 2.0], [3.0, 4.0]])
        estimate = np.ones((2, 2))
        uncertainty = np.full((2, 2), 0.5)
        with (
            patch(
                "run_mice_ablation._project_deterministic_no_bounds",
                return_value=estimate,
            ) as no_bounds,
            patch(
                "run_mice_ablation._project_multiple_no_bounds",
                return_value=(estimate, uncertainty),
            ) as multiple_no_bounds,
            patch(
                "run_mice_ablation._project_deterministic",
                return_value=estimate,
            ) as deterministic,
            patch(
                "run_mice_ablation._project_mice_train_test",
                return_value=(estimate, estimate.copy(), uncertainty.copy()),
            ) as posterior_draws,
        ):
            mice_ablation._variant_estimate(
                "project_deterministic_no_bounds", masked, 9
            )
            no_bounds.assert_called_once_with(masked, 9)
            mice_ablation._variant_estimate("project_m50_no_bounds", masked, 9)
            multiple_no_bounds.assert_called_once_with(masked, 9, 50)
            hybrid, hybrid_sd = mice_ablation._variant_estimate(
                "project_hybrid_m20", masked, 9
            )
            posterior_draws.assert_called_once_with(
                masked, masked, 9, n_imputations=20
            )
            deterministic.assert_called_once_with(masked, 9)
            self.assertEqual(hybrid[0, 1], masked[0, 1])
            self.assertTrue(np.isnan(hybrid_sd[0, 1]))

    def test_m5_interval_preserves_legacy_quantile_and_df_adapts(self):
        raw = np.array([[0.0], [1.0], [2.0], [3.0], [4.0]])
        encoder = EncodedFrame.fit_transformer(pd.DataFrame({"x": raw[:, 0]}))
        scaler = ObservedScaler.fit(raw)
        estimate = scaler.transform(raw)
        estimate[1, 0] += 0.15
        sd = np.full(raw.shape, 0.2)
        mask = np.array([[False], [True], [True], [False], [True]])
        original_ppf = real_benchmark.stats.t.ppf
        seen_dfs = []

        def ppf(probability, degrees):
            seen_dfs.append(degrees)
            return original_ppf(probability, degrees)

        with patch.object(real_benchmark.stats.t, "ppf", side_effect=ppf):
            actual_m5 = real_benchmark._uncertainty_metrics(
                raw, estimate, sd, mask, encoder, scaler, n_imputations=5
            )[0]
            actual_m20 = real_benchmark._uncertainty_metrics(
                raw, estimate, sd, mask, encoder, scaler, n_imputations=20
            )[0]

        std_raw = sd[mask] * scaler.scale[0]
        half_width = original_ppf(0.95, 4) * std_raw * np.sqrt(1 + 1 / 5)
        expected_m5 = float(np.mean(
            np.abs(raw[mask] - scaler.inverse(estimate)[mask]) <= half_width
        ))
        self.assertEqual(actual_m5, expected_m5)
        self.assertEqual(seen_dfs, [4, 19])
        self.assertIsInstance(actual_m20, float)

    def test_reproduction_gate_requires_exact_keys_and_rmse(self):
        ablation = pd.DataFrame({
            "dataset": ["heart-statlog", "heart-statlog"],
            "mechanism": ["MCAR", "MAR"],
            "mask_rate": [0.2, 0.2],
            "trial": [0, 0],
            "variant": ["project_m5", "iterative_single_as_is"],
            "numeric_rmse": [0.75, 0.8],
        })
        saved = pd.DataFrame({
            "dataset": ["heart-statlog", "heart-statlog"],
            "mechanism": ["MCAR", "MAR"],
            "mask_rate": [0.2, 0.2],
            "trial": [0, 0],
            "method": ["mice_multiple_NEW", "iterative_single"],
            "numeric_rmse": [0.75, 0.8],
        })
        joined, maximum = mice_ablation.compare_reproduction(ablation, saved)
        self.assertEqual(len(joined), 2)
        self.assertEqual(maximum, 0.0)
        changed = ablation.copy()
        changed.loc[0, "numeric_rmse"] += 1e-6
        with self.assertRaisesRegex(AssertionError, "exceeds"):
            mice_ablation.compare_reproduction(changed, saved)
        with self.assertRaisesRegex(ValueError, "keys do not match"):
            mice_ablation.compare_reproduction(ablation.iloc[:1], saved)

    def test_ablation_summary_is_dataset_median_then_aggregate(self):
        rows = []
        ratios = {"project_m5": 1.0, "project_m20": 0.9, "project_m50": 1.1}
        for dataset in ("a", "b"):
            for trial in (0, 1):
                for variant, ratio in ratios.items():
                    rows.append({
                        "dataset": dataset,
                        "mechanism": "MCAR",
                        "trial": trial,
                        "variant": variant,
                        "rmse_ratio_vs_mean": ratio,
                        "uncertainty_spearman_numeric": 0.2,
                        "uncertainty_coverage90_numeric": 0.9,
                    })
        per_dataset, aggregate, uncertainty = summarize(pd.DataFrame(rows))
        m20 = aggregate.loc[aggregate["variant"].eq("project_m20")].iloc[0]
        self.assertEqual(m20["n_datasets"], 2)
        self.assertEqual(m20["datasets_lower_ratio_than_project_m5"], 2)
        self.assertAlmostEqual(m20["median_rmse_ratio_vs_mean"], 0.9)
        self.assertEqual(len(per_dataset), 6)
        coverage = uncertainty.loc[
            uncertainty["uncertainty_metric"].eq("uncertainty_coverage90_numeric")
        ].iloc[0]
        self.assertAlmostEqual(coverage["median"], 0.9)


class ResumableStageAndTableMergeTests(unittest.TestCase):
    def test_complete_dataset_directory_is_skippable_only_at_expected_row_count(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            run_dir = output_dir / "fixture"
            run_dir.mkdir()
            repeats = 2
            (run_dir / "run_config.json").write_text(json.dumps({
                "protocol": "A",
                "repeats": repeats,
                "datasets_requested": ["fixture"],
            }), encoding="utf-8")
            pd.DataFrame([{
                "name": "fixture",
                "load_status": "loaded",
                "protocol_a_status": "completed",
            }]).to_csv(run_dir / "dataset_summary.csv", index=False)
            rows = [
                {
                    "dataset": "fixture",
                    "mechanism": mechanism,
                    "mask_rate": rate,
                    "trial": trial,
                    "method": method,
                }
                for mechanism in MECHANISMS
                for rate in MASK_RATES
                for trial in range(repeats)
                for method in METHODS
            ]
            csv_path = run_dir / "protocol_a_ground_truth.csv"
            pd.DataFrame(rows).to_csv(csv_path, index=False)
            self.assertEqual(len(rows), len(MECHANISMS) * len(MASK_RATES) * repeats * len(METHODS))
            self.assertTrue(is_complete_run(run_dir, "fixture", "A"))
            args = SimpleNamespace(
                datasets=["fixture"],
                protocol="A",
                repeats=repeats,
                attempts=3,
                base_delay=0.0,
                out=output_dir,
                seed=42,
                max_rows=5000,
            )
            with (
                patch.object(run_stage, "DATASETS", {"fixture": object()}),
                patch.object(run_stage.subprocess, "run") as subprocess_run,
            ):
                self.assertEqual(run_stage.run_stage(args), output_dir.resolve())
            subprocess_run.assert_not_called()
            pd.DataFrame(rows[:-1]).to_csv(csv_path, index=False)
            self.assertFalse(is_complete_run(run_dir, "fixture", "A"))

    def test_summary_merge_preserves_protocol_completion_across_stages(self):
        protocol_b = pd.DataFrame([{
            "name": "adult",
            "load_status": "loaded",
            "protocol_a_status": "not_requested",
            "protocol_b_status": "completed",
            "protocol_a_dropped_incomplete_columns": "[]",
        }])
        protocol_a = pd.DataFrame([{
            "name": "adult",
            "load_status": "loaded",
            "protocol_a_status": "completed",
            "protocol_b_status": "not_requested",
            "protocol_a_dropped_incomplete_columns": '["x"]',
        }])
        merged = _merge_summaries([protocol_b, protocol_a]).iloc[0]
        self.assertEqual(merged["protocol_a_status"], "completed")
        self.assertEqual(merged["protocol_b_status"], "completed")

    def test_summary_uses_later_success_and_keeps_earlier_failure_as_attempt(self):
        failed = pd.DataFrame([{
            "name": "fixture",
            "load_status": "failed",
            "load_failure_reason": "temporary OpenML connection reset",
            "protocol_a_status": "not_run",
            "protocol_b_status": "not_run",
            "source_dir": "stage-a",
        }])
        succeeded = pd.DataFrame([{
            "name": "fixture",
            "load_status": "loaded",
            "load_failure_reason": "",
            "protocol_a_status": "completed",
            "protocol_b_status": "not_requested",
            "source_dir": "stage-b",
        }])
        merged = _merge_summaries([failed, succeeded])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged.iloc[0]["load_status"], "loaded")
        self.assertEqual(merged.iloc[0]["source_dir"], "stage-b")
        self.assertIn("stage-a", merged.iloc[0]["attempts_log"])
        self.assertIn("temporary OpenML connection reset", merged.iloc[0]["attempts_log"])

    def test_merge_rejects_duplicate_protocol_keys(self):
        frame = pd.DataFrame({
            "dataset": ["fixture", "fixture"],
            "mechanism": ["MCAR", "MCAR"],
            "mask_rate": [0.1, 0.1],
            "trial": [0, 0],
            "method": ["mean", "mean"],
        })
        with self.assertRaisesRegex(ValueError, "Duplicate Protocol A"):
            _concat_unique(
                [frame.iloc[:1], frame.iloc[1:]],
                ["dataset", "mechanism", "mask_rate", "trial", "method"],
                "Protocol A",
            )

    def test_protocol_b_summary_supports_classification_csv_without_rmse(self):
        raw = pd.DataFrame({
            "dataset": ["mushroom", "mushroom"],
            "task_type": ["classification", "classification"],
            "method": ["mean", "mean"],
            "accuracy": [0.99, 1.0],
            "auc": [0.98, 0.99],
            "heldout_numeric_rmse": [np.nan, np.nan],
            "heldout_categorical_error_rate": [0.1, 0.2],
        })
        result = _summarize_protocol_b(raw)
        self.assertNotIn("rmse", result.columns)
        self.assertAlmostEqual(result.loc[0, "accuracy"], 0.995)
        self.assertAlmostEqual(result.loc[0, "heldout_categorical_error_rate"], 0.15)

    def test_dataset_level_significance_uses_datasets_as_paired_units(self):
        rows = []
        for dataset_index, dataset in enumerate(("a", "b", "c", "d")):
            for mechanism in MECHANISMS:
                for rate in MASK_RATES:
                    for trial in range(2):
                        rows.extend([
                            {
                                "dataset": dataset,
                                "mechanism": mechanism,
                                "mask_rate": rate,
                                "trial": trial,
                                "method": "mice_multiple_NEW",
                                "numeric_rmse": 0.7 + dataset_index * 0.01,
                                "categorical_error_rate": 0.2,
                            },
                            {
                                "dataset": dataset,
                                "mechanism": mechanism,
                                "mask_rate": rate,
                                "trial": trial,
                                "method": "mean",
                                "numeric_rmse": 1.0 + dataset_index * 0.01,
                                "categorical_error_rate": 0.3,
                            },
                        ])
        a_result, b_result = _dataset_level_significance(
            pd.DataFrame(rows), pd.DataFrame()
        )
        numeric = a_result.loc[
            a_result["metric"].eq("numeric_rmse")
            & a_result["mechanism"].eq("MCAR")
            & a_result["vs"].eq("mean")
        ].iloc[0]
        self.assertEqual(int(numeric["n_datasets"]), 4)
        self.assertTrue(bool(numeric["low_power_n_lt_10"]))
        self.assertTrue(np.isfinite(numeric["p_holm"]))
        self.assertTrue((a_result["p_holm"] >= a_result["p_value"]).all())
        self.assertEqual(int(numeric["n_comparisons_in_holm_family"]), len(a_result))
        self.assertEqual(float(numeric["min_attainable_two_sided_exact_p"]), 0.125)
        self.assertFalse(bool(numeric["can_reach_0_05_after_holm"]))
        self.assertIn("cannot reach 0.05", numeric["power_note"])

    def test_effect_size_tables_pair_datasets_and_bootstrap_deterministically(self):
        rows_a = []
        rows_b = []
        for dataset, scale in (("a", 1.0), ("b", 2.0), ("c", 3.0)):
            for method, score in (
                ("mean", scale),
                ("knn5", 0.9 * scale),
                ("mice_multiple_NEW", 0.8 * scale),
            ):
                rows_a.append({
                    "dataset": dataset,
                    "mechanism": "MCAR",
                    "mask_rate": 0.1,
                    "trial": 0,
                    "method": method,
                    "numeric_rmse": score,
                })
                rows_b.append({
                    "dataset": dataset,
                    "method": method,
                    "accuracy": (
                        0.8 if method == "mean"
                        else 0.82 if method == "knn5"
                        else 0.9
                    ),
                })
        a = pd.DataFrame(rows_a)
        b = pd.DataFrame(rows_b)
        first = _effect_size_tables(a, b)
        second = _effect_size_tables(a, b)
        a_effect = first["protocol_a_effect_sizes"]
        a_knn = a_effect.loc[a_effect["vs"].eq("knn5")].iloc[0]
        self.assertEqual(int(a_knn["n_datasets"]), 3)
        self.assertEqual(int(a_knn["datasets_project_better"]), 3)
        self.assertAlmostEqual(float(a_knn["median_project_minus_baseline_ratio"]), -0.1)
        np.testing.assert_allclose(
            a_effect["bootstrap_95_ci_low"],
            second["protocol_a_effect_sizes"]["bootstrap_95_ci_low"],
        )
        b_effect = first["protocol_b_effect_sizes"]
        b_knn = b_effect.loc[
            b_effect["metric"].eq("accuracy") & b_effect["vs"].eq("knn5")
        ].iloc[0]
        self.assertEqual(int(b_knn["datasets_project_better"]), 3)
        self.assertAlmostEqual(float(b_knn["median_project_minus_baseline_metric"]), 0.08)

    def test_study_labels_cover_sentinel_negligible_and_marginal_cases(self):
        self.assertIn(
            "sentinel-coded missingness (zeros treated as missing), not native NaN",
            _study_labels("diabetes", "B"),
        )
        self.assertIn(
            "negligible natural missingness",
            _study_labels("adult", "B"),
        )
        self.assertIn(
            "marginal: 7 retained columns, 2 numeric",
            _study_labels("cylinder-bands", "A"),
        )
        self.assertIn(
            "adult (negligible natural missingness)",
            _negligible_missingness_datasets(["adult", "hepatitis"]),
        )

    def test_protocol_b_primary_filter_preserves_all_heldout_metrics(self):
        raw = pd.DataFrame({
            "dataset": ["adult", "mushroom"],
            "accuracy": [0.8, 1.0],
            "auc": [0.9, 1.0],
            "heldout_numeric_rmse": [0.5, 0.6],
            "heldout_categorical_error_rate": [0.1, 0.2],
        })
        selected = _select_protocol_b_significance_input(raw, {"adult"})
        self.assertTrue(pd.isna(selected.loc[1, "accuracy"]))
        self.assertTrue(pd.isna(selected.loc[1, "auc"]))
        self.assertEqual(selected.loc[1, "heldout_numeric_rmse"], 0.6)
        self.assertEqual(selected.loc[1, "heldout_categorical_error_rate"], 0.2)

    def test_win_tie_loss_cell_counter_counts_scorable_headline_cells(self):
        raw = pd.DataFrame({
            "dataset": ["adult", "adult", "hepatitis"],
            "mechanism": ["MCAR", "MAR", "MCAR"],
            "mask_rate": [0.1, 0.1, 0.1],
            "method": ["mean", "mean", "mean"],
            "numeric_rmse": [1.0, np.nan, 2.0],
        })
        self.assertEqual(_scoreable_protocol_a_cell_count(raw), 2)

    def test_uncertainty_summary_has_mechanism_distributions_and_nominal_mnar(self):
        frame = pd.DataFrame({
            "dataset": ["adult", "bank-marketing", "adult"],
            "mechanism": ["MCAR", "MCAR", "MNAR"],
            "uncertainty_spearman_numeric": [0.1, 0.3, 0.2],
            "uncertainty_coverage90_numeric": [0.8, 0.9, 0.85],
        })
        summary = _uncertainty_distribution_table(frame, {"adult", "bank-marketing"})
        self.assertEqual(len(summary), 4)
        self.assertEqual(set(summary["mechanism"]), {"MCAR", "MNAR"})
        mcar_coverage = summary.loc[
            summary["metric"].eq("uncertainty_coverage90_numeric")
            & summary["mechanism"].eq("MCAR")
        ].iloc[0]
        mnar_coverage = summary.loc[
            summary["metric"].eq("uncertainty_coverage90_numeric")
            & summary["mechanism"].eq("MNAR")
        ].iloc[0]
        self.assertAlmostEqual(float(mcar_coverage["median"]), 0.85)
        self.assertEqual(mcar_coverage["coverage_target"], "nominal 0.90")
        self.assertEqual(mnar_coverage["coverage_target"], "nominal 0.90")

    def test_all_coverage_rows_show_nominal_target(self):
        frame = pd.DataFrame({
            "mechanism": ["MCAR", "MAR", "MNAR"],
            "uncertainty_coverage90_numeric": [0.8, 0.9, 0.7],
        })
        labeled = _with_coverage_label(frame)
        self.assertEqual(
            labeled["coverage_nominal_target"].tolist(),
            ["nominal 0.90"] * 3,
        )

    def test_posthoc_holm_sensitivity_is_separately_labeled(self):
        frame = pd.DataFrame({
            "metric": ["numeric_rmse", "numeric_rmse", "categorical_error_rate"],
            "p_value": [0.01, 0.04, 0.02],
            "n_datasets": [10, 10, 8],
        })
        result = _holm_per_metric_sensitivity(frame)
        self.assertEqual(result.loc[0, "p_holm"], 0.02)
        self.assertEqual(result.loc[1, "p_holm"], 0.04)
        self.assertEqual(
            result.loc[2, "p_holm"],
            0.02,
        )
        self.assertTrue(
            result["holm_sensitivity_label"].str.contains(
                "chosen after seeing results"
            ).all()
        )


if __name__ == "__main__":
    unittest.main()
