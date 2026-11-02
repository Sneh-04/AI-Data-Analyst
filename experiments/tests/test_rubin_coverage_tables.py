import numpy as np
import pandas as pd

from make_rubin_tables import summarize, write_tables


def test_summary_tables_calculate_coverage_mc_se_width_bias_and_failure_counts(tmp_path):
    rows = []
    for trial, covers in enumerate((True, True, False, True)):
        rows.append({
            "run_key": f"key-{trial}",
            "trial": trial,
            "dataset": "fixture",
            "estimand": "mean",
            "mechanism": "MNAR",
            "method": "mice_improper",
            "mask_rate": 0.1,
            "m": 5,
            "delta_sd": 0.5,
            "status": "success",
            "ci_covers_truth": covers,
            "ci_width": 2.0 + trial,
            "bias": trial / 10,
        })
    pd.DataFrame(rows).to_csv(tmp_path / "raw.csv", index=False)
    pd.DataFrame([{
        "run_key": "failed-key",
        "trial": 4,
        "dataset": "fixture",
        "estimand": "mean",
        "mechanism": "MNAR",
        "method": "mice_improper",
        "mask_rate": 0.1,
        "m": 5,
        "delta_sd": 0.5,
    }]).to_csv(tmp_path / "failures.csv", index=False)

    tables = summarize(tmp_path)
    coverage = tables["coverage"].iloc[0]
    width = tables["width"].iloc[0]
    bias = tables["bias"].iloc[0]

    assert coverage["coverage"] == 0.75
    assert np.isclose(coverage["coverage_mc_se"], 0.21650635094610965)
    assert coverage["successful_runs"] == 4
    assert coverage["failed_runs"] == 1
    assert coverage["attempted_runs"] == 5
    assert width["mean_ci_width"] == 3.5
    assert bias["mean_bias"] == 0.15
    assert len(tables["mnar_delta"]) == 1

    write_tables(tables, tmp_path)
    assert (tmp_path / "rubin_coverage_tables.md").is_file()
    latex = (tmp_path / "rubin_coverage_tables.tex").read_text(encoding="utf-8")
    assert r"\begin{tabular}" in latex
    assert r"mice\_improper" in latex


def test_summary_tables_preserve_a_condition_with_only_failed_runs(tmp_path):
    columns = [
        "run_key",
        "trial",
        "dataset",
        "estimand",
        "mechanism",
        "method",
        "mask_rate",
        "m",
        "delta_sd",
        "status",
        "ci_covers_truth",
        "ci_width",
        "bias",
    ]
    pd.DataFrame(columns=columns).to_csv(tmp_path / "raw.csv", index=False)
    pd.DataFrame([{
        "run_key": "failed-only",
        "trial": 0,
        "dataset": "fixture",
        "estimand": "ols_slope",
        "mechanism": "MCAR",
        "method": "mice_proper",
        "mask_rate": 0.3,
        "m": 5,
        "delta_sd": 0.0,
    }]).to_csv(tmp_path / "failures.csv", index=False)

    tables = summarize(tmp_path)

    assert len(tables["coverage"]) == 1
    row = tables["coverage"].iloc[0]
    assert row["coverage"] != row["coverage"]
    assert row["successful_runs"] == 0
    assert row["failed_runs"] == 1
    assert row["attempted_runs"] == 1


def test_headline_uses_dataset_cluster_bootstrap_and_sanity_status(tmp_path):
    rows = []
    for dataset, excluded_trials in (("a", {9}), ("b", {0, 1})):
        for trial in range(10):
            rows.append({
                "run_key": f"{dataset}-{trial}",
                "trial": trial,
                "dataset": dataset,
                "estimand": "mean",
                "mechanism": "MCAR",
                "method": "mice_improper",
                "mask_rate": 0.1,
                "m": 5,
                "delta_sd": 0.0,
                "status": "success",
                "ci_covers_truth": trial not in excluded_trials,
                "ci_width": 2.0,
                "bias": 0.0,
            })
    for trial in range(20):
        rows.append({
            "run_key": f"sanity-{trial}",
            "dataset": "a",
            "estimand": "mean",
            "trial": trial,
            "mechanism": "NONE",
            "method": "no_missing_sanity",
            "mask_rate": 0.0,
            "m": 1,
            "delta_sd": 0.0,
            "status": "success",
            "ci_covers_truth": trial != 19,
            "ci_width": 2.0,
            "bias": 0.0,
        })
    pd.DataFrame(rows).to_csv(tmp_path / "raw.csv", index=False)
    pd.DataFrame(columns=[
        "dataset", "estimand", "mechanism", "method", "mask_rate",
        "m", "delta_sd",
    ]).to_csv(tmp_path / "failures.csv", index=False)

    tables = summarize(tmp_path)
    headline = tables["headline_coverage"].query(
        "mechanism == 'MCAR'"
    ).iloc[0]
    sanity = tables["no_missing_sanity"].iloc[0]

    assert headline["coverage"] == 0.85
    assert headline["contributing_datasets"] == 2
    assert np.isfinite(headline["dataset_cluster_bootstrap_mc_se"])
    assert headline["dataset_cluster_bootstrap_mc_se"] > 0
    assert headline["cluster_bootstrap_replicates"] == 2_000
    assert sanity["coverage"] == 0.95
    assert sanity["sanity_status"] == "incomplete"


def test_headline_excludes_sanity_failed_dataset_estimand(tmp_path):
    rows = []
    for dataset in ("a", "b"):
        for estimand in ("mean", "ols_slope"):
            for trial in range(10):
                rows.append({
                    "run_key": f"{dataset}-{estimand}-{trial}",
                    "trial": trial,
                    "dataset": dataset,
                    "estimand": estimand,
                    "mechanism": "MCAR",
                    "method": "mice_improper",
                    "mask_rate": 0.1,
                    "m": 5,
                    "delta_sd": 0.0,
                    "status": "success",
                    "ci_covers_truth": trial < (
                        1 if dataset == "a" and estimand == "ols_slope" else 8
                    ),
                    "ci_width": 2.0,
                    "bias": 0.0,
                })
            sanity_coverage = (
                0.90 if dataset == "a" and estimand == "ols_slope" else 0.95
            )
            for trial in range(100):
                rows.append({
                    "run_key": f"sanity-{dataset}-{estimand}-{trial}",
                    "trial": trial,
                    "dataset": dataset,
                    "estimand": estimand,
                    "mechanism": "NONE",
                    "method": "no_missing_sanity",
                    "mask_rate": 0.0,
                    "m": 1,
                    "delta_sd": 0.0,
                    "status": "success",
                    "ci_covers_truth": trial < int(sanity_coverage * 100),
                    "ci_width": 2.0,
                    "bias": 0.0,
                })
    pd.DataFrame(rows).to_csv(tmp_path / "raw.csv", index=False)
    pd.DataFrame(columns=[
        "dataset", "estimand", "mechanism", "method", "mask_rate",
        "m", "delta_sd",
    ]).to_csv(tmp_path / "failures.csv", index=False)

    tables = summarize(tmp_path)
    sanity = tables["no_missing_sanity"].set_index(["dataset", "estimand"])
    headline = tables["headline_coverage"].set_index("estimand")
    per_dataset = tables["coverage"]

    assert sanity.loc[("a", "mean"), "sanity_status"] == "sanity-passed"
    assert sanity.loc[("a", "ols_slope"), "sanity_status"] == "sanity-failed"
    assert sanity.loc[("b", "ols_slope"), "sanity_status"] == "sanity-passed"
    assert headline.loc["mean", "contributing_datasets"] == 2
    assert headline.loc["ols_slope", "contributing_datasets"] == 1
    assert headline.loc["ols_slope", "coverage"] == 0.8
    assert headline.loc["ols_slope", "sanity_failed_datasets_excluded"] == "a"
    assert per_dataset.query(
        "dataset == 'a' and estimand == 'ols_slope'"
    ).shape[0] == 1
