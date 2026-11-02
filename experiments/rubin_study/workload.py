"""Read-only workload audit for a Rubin v4 run configuration and raw CSV."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any


def expected_mask_cells(config: dict[str, Any]) -> set[tuple[str, str, float, int]]:
    datasets = [item["name"] for item in config["datasets"]]
    return {
        (dataset, mechanism, float(rate), int(trial))
        for dataset, mechanism, rate, trial in product(
            datasets,
            config["mechanisms"],
            config["mask_rates"],
            config["trials"],
        )
    }


def audit_v4_workload(
    config_path: Path,
    raw_csv_path: Path,
    *,
    comparison_method: str = "mice_proper",
    comparison_m: int | None = None,
) -> dict[str, Any]:
    """Derive configured cells and reconcile them with saved raw records."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    masks_expected = expected_mask_cells(config)
    if comparison_m is None:
        comparison_m = max(int(value) for value in config["m_values"])

    observed_masks: set[tuple[str, str, float, int]] = set()
    observed_pair_cells: set[tuple[str, str, float, int, str]] = set()
    estimands: set[str] = set()
    mask_seed_values: dict[tuple[str, str, float, int], set[str]] = {}
    missing_mask_seed_records = 0
    statuses: Counter[str] = Counter()
    raw_rows = 0
    configured_mask_records = 0
    with raw_csv_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {
            "dataset",
            "mechanism",
            "mask_rate",
            "trial",
            "estimand",
            "method",
            "m",
            "delta_sd",
            "status",
            "mask_seed",
        }
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"raw results lack required columns: {sorted(missing)}")
        for row in reader:
            raw_rows += 1
            statuses[row["status"]] += 1
            if row["mechanism"] not in config["mechanisms"]:
                continue
            mask_key = (
                row["dataset"],
                row["mechanism"],
                float(row["mask_rate"]),
                int(row["trial"]),
            )
            observed_masks.add(mask_key)
            if mask_key in masks_expected:
                configured_mask_records += 1
                estimands.add(row["estimand"])
                mask_seed = row["mask_seed"].strip()
                if mask_seed:
                    mask_seed_values.setdefault(mask_key, set()).add(mask_seed)
                else:
                    missing_mask_seed_records += 1
            if (
                row["method"] == comparison_method
                and int(row["m"]) == comparison_m
                and float(row["delta_sd"]) == 0.0
                and row["status"] == "success"
                and mask_key in masks_expected
            ):
                observed_pair_cells.add((*mask_key, row["estimand"]))

    expected_pair_cells = {
        (*mask_key, estimand)
        for mask_key in masks_expected
        for estimand in estimands
    }
    return {
        "config_path": str(config_path),
        "raw_csv_path": str(raw_csv_path),
        "configured_dimensions": {
            "datasets": len(config["datasets"]),
            "mechanisms": len(config["mechanisms"]),
            "missing_rates": len(config["mask_rates"]),
            "trials": len(config["trials"]),
            "estimands_observed": sorted(estimands),
            "comparison_method": comparison_method,
            "comparison_m": comparison_m,
        },
        "expected_mask_replicates": len(masks_expected),
        "observed_mask_replicates": len(observed_masks),
        "missing_mask_replicates": len(masks_expected - observed_masks),
        "unexpected_mask_replicates": len(observed_masks - masks_expected),
        "mask_seed_mismatched_cells": sum(
            len(seeds) > 1 for seeds in mask_seed_values.values()
        ),
        "mask_seed_records_missing": missing_mask_seed_records,
        "expected_paired_estimand_cells": len(expected_pair_cells),
        "observed_successful_paired_estimand_cells": len(observed_pair_cells),
        "missing_paired_estimand_cells": len(expected_pair_cells - observed_pair_cells),
        "raw_record_count": raw_rows,
        "records_for_configured_mask_cells": configured_mask_records,
        "records_outside_configured_mask_cells": raw_rows - configured_mask_records,
        "raw_records_by_status": dict(sorted(statuses.items())),
        "candidate_mi_completed_datasets_if_full_extension": (
            len(masks_expected) * comparison_m
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "results/rubin_coverage_full_v4/run_config.json",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "results/rubin_coverage_full_v4/raw.csv",
    )
    parser.add_argument("--method", default="mice_proper")
    parser.add_argument("--m", type=int, default=None)
    args = parser.parse_args()
    print(json.dumps(
        audit_v4_workload(
            args.config,
            args.raw,
            comparison_method=args.method,
            comparison_m=args.m,
        ),
        indent=2,
    ))


if __name__ == "__main__":
    main()
