import csv
import json
from pathlib import Path

from rubin_study.workload import audit_v4_workload, expected_mask_cells


EXPERIMENTS = Path(__file__).resolve().parents[1]


def test_actual_v4_config_defines_nine_thousand_mask_replicates():
    config = json.loads(
        (EXPERIMENTS / "results/rubin_coverage_full_v4/run_config.json").read_text()
    )
    assert len(expected_mask_cells(config)) == (
        len(config["datasets"])
        * len(config["mechanisms"])
        * len(config["mask_rates"])
        * len(config["trials"])
    )
    assert len(expected_mask_cells(config)) == 9000


def test_workload_audit_reconciles_configured_cells_to_raw_rows(tmp_path):
    config = {
        "datasets": [{"name": "d1"}],
        "mechanisms": ["MCAR"],
        "mask_rates": [0.1],
        "trials": [0, 1],
        "m_values": [5, 20],
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    raw_path = tmp_path / "raw.csv"
    headers = [
        "dataset", "mechanism", "mask_rate", "trial", "estimand", "method",
        "m", "delta_sd", "status", "mask_seed",
    ]
    rows = []
    for trial in config["trials"]:
        for estimand in ("mean", "ols_slope"):
            rows.append([
                "d1", "MCAR", "0.1", trial, estimand, "mice_proper",
                "20", "0.0", "success", str(trial + 42),
            ])
    rows.append([
        "unexpected", "MCAR", "0.1", 0, "mean", "mice_proper",
        "20", "0.0", "success", "42",
    ])
    with raw_path.open("w", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(headers)
        writer.writerows(rows)

    report = audit_v4_workload(config_path, raw_path, comparison_m=20)

    assert report["expected_mask_replicates"] == 2
    assert report["observed_mask_replicates"] == 3
    assert report["missing_mask_replicates"] == 0
    assert report["unexpected_mask_replicates"] == 1
    assert report["expected_paired_estimand_cells"] == 4
    assert report["observed_successful_paired_estimand_cells"] == 4
    assert report["missing_paired_estimand_cells"] == 0
    assert report["mask_seed_mismatched_cells"] == 0
    assert report["mask_seed_records_missing"] == 0
    assert report["records_for_configured_mask_cells"] == 4
    assert report["records_outside_configured_mask_cells"] == 1
    assert report["candidate_mi_completed_datasets_if_full_extension"] == 40
