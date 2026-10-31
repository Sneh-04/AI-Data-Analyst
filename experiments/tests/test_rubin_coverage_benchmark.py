import numpy as np
import pandas as pd

from rubin_coverage_benchmark import (
    RAW_COLUMNS,
    _failure_as_raw_row,
    _prepare_args,
    _read_completed_keys,
    _run_sanity_task,
    run,
    _sample_population,
    _write_sanity_summary,
    _x2_mask,
)
from run_real_datasets import ObservedScaler


def _dataset() -> dict:
    rng = np.random.RandomState(17)
    x1 = rng.normal(size=120)
    x2 = 1.2 + 0.8 * x1 + rng.normal(scale=0.4, size=120)
    auxiliary = 0.5 * x1 + rng.normal(size=120)
    features = pd.DataFrame({
        "x1": x1,
        "x2": x2,
        "auxiliary": auxiliary,
    })
    values = features.to_numpy()
    return {
        "name": "adult",
        "features": features,
        "numeric_columns": list(features.columns),
        "x1": "x1",
        "x2": "x2",
        "scaler": ObservedScaler.fit(values),
        "truths": {
            "mean": float(features["x2"].mean()),
            "ols_slope": float(np.polyfit(features["x1"], features["x2"], 1)[0]),
        },
        "n_rows": len(features),
        "population_n": len(features),
        "n_columns": features.shape[1],
    }


def test_population_sampling_is_seeded_and_uses_replacement():
    dataset = _dataset()

    sample = _sample_population(dataset, trial_seed=431)
    repeated = _sample_population(dataset, trial_seed=431)

    pd.testing.assert_frame_equal(sample, repeated)
    assert len(sample) == min(500, dataset["population_n"])
    expected_indices = np.random.RandomState(431).choice(
        dataset["population_n"], size=len(sample), replace=True
    )
    pd.testing.assert_frame_equal(
        sample,
        dataset["features"].iloc[expected_indices].reset_index(drop=True),
    )


def test_missingness_mask_only_masks_x2():
    dataset = _dataset()
    mask = _x2_mask(
        dataset["features"],
        dataset,
        mechanism="MAR",
        rate=0.3,
        seed=912,
    )

    x2_position = dataset["numeric_columns"].index("x2")
    assert mask[:, x2_position].any()
    assert mask[:, [0, 2]].sum() == 0


def test_no_missing_sanity_records_complete_data_intervals():
    records, failures = _run_sanity_task(_dataset(), trial=0)

    assert failures == []
    assert {record["estimand"] for record in records} == {"mean", "ols_slope"}
    assert all(record["method"] == "no_missing_sanity" for record in records)
    assert all(record["m"] == 1 for record in records)
    assert all(record["mechanism"] == "NONE" for record in records)
    assert all(record["realized_mask_rate"] == 0.0 for record in records)
    assert all("complete-data t interval" in record["interval_type"] for record in records)


def test_failed_raw_rows_are_auditable_but_not_marked_complete(tmp_path):
    failure = {
        "run_key": "failed-run",
        "dataset": "adult",
        "mechanism": "MNAR",
        "mask_rate": 0.3,
        "delta_sd": 0.5,
        "method": "mice_proper",
        "m": 5,
        "trial": 2,
        "estimand": "mean",
        "stage": "imputation",
        "attempt": 1,
        "error_type": "ValueError",
        "error_message": "test failure",
        "traceback": "trace",
        "trial_seed": 123,
        "mask_seed": 124,
        "imputation_seeds": "[323,324,325,326,327]",
        "bootstrap_seeds": "[223,224,225,226,227]",
    }
    raw_path = tmp_path / "raw.csv"
    pd.DataFrame([_failure_as_raw_row(failure)], columns=RAW_COLUMNS).to_csv(
        raw_path, index=False
    )

    raw_row = pd.read_csv(raw_path).iloc[0]
    assert raw_row["status"] == "failed"
    assert raw_row["failure_stage"] == "imputation"
    assert raw_row["error_message"] == "test failure"
    assert _read_completed_keys(raw_path) == set()


def test_sanity_only_flag_is_available():
    args = _prepare_args().parse_args(["--sanity-only"])

    assert args.sanity_only


def test_sanity_only_run_creates_summary_with_protocol_columns(tmp_path, monkeypatch):
    dataset = _dataset()
    dataset.update({
        "x1_nunique": int(dataset["features"]["x1"].nunique()),
        "x2_nunique": int(dataset["features"]["x2"].nunique()),
        "data_id": 1,
        "version": 1,
        "source": "test fixture",
    })
    monkeypatch.setattr("rubin_coverage_benchmark.RESULTS_ROOT", tmp_path)
    monkeypatch.setattr(
        "rubin_coverage_benchmark.ELIGIBLE_DATASETS",
        ("adult",),
    )
    monkeypatch.setattr(
        "rubin_coverage_benchmark._feature_cohort",
        lambda name: dataset,
    )

    args = _prepare_args().parse_args([
        "--sanity-only",
        "--tag",
        "sanity-only-test",
        "--n-jobs",
        "1",
    ])
    output_dir = run(args)

    summary_path = output_dir / "sanity_summary.csv"
    assert summary_path.is_file()
    summary = pd.read_csv(summary_path)
    assert summary.columns.tolist() == [
        "dataset",
        "estimand",
        "expected_trials",
        "successful_runs",
        "failed_runs",
        "attempted_runs",
        "coverage",
        "sanity_status",
    ]
    assert len(summary) == 2
    assert summary["expected_trials"].eq(100).all()


def test_sanity_summary_marks_out_of_range_coverage_after_100_trials(tmp_path):
    rows = []
    for trial in range(100):
        for estimand, covers in (("mean", True), ("ols_slope", trial < 95)):
            rows.append({
                "dataset": "adult",
                "estimand": estimand,
                "trial": trial,
                "method": "no_missing_sanity",
                "status": "success",
                "ci_covers_truth": covers,
            })
    raw_path = tmp_path / "raw.csv"
    failures_path = tmp_path / "failures.csv"
    summary_path = tmp_path / "sanity_summary.csv"
    pd.DataFrame(rows).to_csv(raw_path, index=False)
    pd.DataFrame(columns=["dataset", "estimand", "method"]).to_csv(
        failures_path, index=False
    )

    _write_sanity_summary(
        raw_path,
        failures_path,
        summary_path,
        [{"name": "adult"}],
    )
    summary = pd.read_csv(summary_path).set_index("estimand")

    assert summary.loc["mean", "sanity_status"] == "sanity-failed"
    assert summary.loc["ols_slope", "sanity_status"] == "sanity-passed"
