#!/usr/bin/env python3
"""Export the checked-in Rubin coverage summaries for the frontend."""

import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIMARY_CSV = ROOT / "experiments/results/rubin_coverage_full_v4/headline_coverage.csv"
EXPLORATORY_CSV = (
    ROOT / "experiments/results/rubin_coverage_full_v4_exploratory/coverage_summary.csv"
)
OUTPUT_JSON = ROOT / "frontend/public/research/v4_summary.json"

WIDTH_RATIO_COLUMNS = ("width_ratio", "mean_width_ratio", "interval_width_ratio")
INTEGER_COLUMNS = (
    "m",
    "contributing_datasets",
    "successful_runs",
    "failed_runs",
    "attempted_runs",
    "finite_interval_runs",
    "dataset_count",
)

CAVEATS = [
    "simulation-based on 10 OpenML-derived populations with n=500 samples",
    "only one column masked",
    "one strong logistic mechanism",
    "proper (bootstrap-then-impute) improves but does not reach nominal under strong MAR at high missing rates",
    "results are heterogeneous across datasets",
    "MNAR coverage is very low and the pre-specified +-1 SD delta grid did not rescue it",
    "naive single imputation intervals are not valid",
    "post-hoc analyses are labelled exploratory",
]


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Required research input was not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"Research input has no header row: {path}")
        return list(reader), reader.fieldnames


def number(row: dict[str, str], column: str, *, optional: bool = False) -> float | None:
    value = row.get(column, "")
    if value == "" and optional:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Expected a numeric value for {column!r}: {value!r}") from error
    if not math.isfinite(parsed):
        raise ValueError(f"Expected a finite value for {column!r}: {value!r}")
    return parsed


def integer(row: dict[str, str], column: str, *, optional: bool = False) -> int | None:
    value = number(row, column, optional=optional)
    if value is None:
        return None
    if not value.is_integer():
        raise ValueError(f"Expected an integer value for {column!r}: {value!r}")
    return int(value)


def first_present(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    return next((column for column in candidates if column in columns), None)


def export_primary(rows: list[dict[str, str]], columns: list[str]) -> list[dict[str, Any]]:
    required = {
        "estimand",
        "mechanism",
        "method",
        "mask_rate",
        "m",
        "delta_sd",
        "coverage",
        "coverage_mc_se",
    }
    missing = required.difference(columns)
    if missing:
        raise ValueError(f"Primary CSV is missing required columns: {', '.join(sorted(missing))}")

    width_column = first_present(columns, WIDTH_RATIO_COLUMNS)
    output = []
    for row in rows:
        item: dict[str, Any] = {
            "estimand": row["estimand"],
            "mechanism": row["mechanism"],
            "method": row["method"],
            "mask_rate": number(row, "mask_rate"),
            "m": integer(row, "m"),
            "delta_sd": number(row, "delta_sd"),
            "coverage": number(row, "coverage"),
            "mc_se": number(row, "coverage_mc_se", optional=True),
            "width_ratio": number(row, width_column, optional=True) if width_column else None,
        }
        for column in INTEGER_COLUMNS:
            if column in columns:
                item[column] = integer(row, column, optional=True)
        if "dataset_cluster_bootstrap_mc_se" in columns:
            item["dataset_cluster_bootstrap_mc_se"] = number(
                row, "dataset_cluster_bootstrap_mc_se", optional=True
            )
        output.append(item)

    output.sort(
        key=lambda item: (
            item["estimand"],
            item["mechanism"],
            item["method"],
            item["mask_rate"],
            item["m"],
            item["delta_sd"],
        )
    )
    return output


def export_exploratory(
    rows: list[dict[str, str]], columns: list[str]
) -> list[dict[str, Any]]:
    required = {
        "exploratory_label",
        "mechanism",
        "mask_rate",
        "estimand",
        "method",
        "dataset_count",
        "mean_dataset_coverage",
    }
    missing = required.difference(columns)
    if missing:
        raise ValueError(
            f"Exploratory CSV is missing required columns: {', '.join(sorted(missing))}"
        )

    output = [
        {
            "exploratory_label": row["exploratory_label"],
            "mechanism": row["mechanism"],
            "mask_rate": number(row, "mask_rate"),
            "estimand": row["estimand"],
            "method": row["method"],
            "dataset_count": integer(row, "dataset_count"),
            "coverage": number(row, "mean_dataset_coverage"),
            "mc_se": None,
            "m": None,
            "delta_sd": None,
            "width_ratio": None,
        }
        for row in rows
    ]
    output.sort(
        key=lambda item: (
            item["estimand"],
            item["mechanism"],
            item["method"],
            item["mask_rate"],
        )
    )
    return output


def unique_values(rows: list[dict[str, Any]], column: str) -> list[Any]:
    return sorted({row[column] for row in rows if row.get(column) is not None})


def main() -> None:
    primary_rows, primary_columns = read_csv(PRIMARY_CSV)
    exploratory_rows, exploratory_columns = read_csv(EXPLORATORY_CSV)
    primary = export_primary(primary_rows, primary_columns)
    exploratory = export_exploratory(exploratory_rows, exploratory_columns)
    if not primary or not exploratory:
        raise ValueError("Both research summary inputs must contain at least one data row")

    dataset_counts = {row["contributing_datasets"] for row in primary if "contributing_datasets" in row}
    if len(dataset_counts) != 1:
        raise ValueError("Primary CSV must report one consistent contributing-dataset count")
    population_count = dataset_counts.pop()
    per_dataset_trials = []
    for row in primary:
        runs = row.get("successful_runs")
        datasets = row.get("contributing_datasets")
        if runs is None or datasets in (None, 0):
            continue
        if runs % datasets:
            raise ValueError("Primary CSV runs must divide evenly across contributing datasets")
        per_dataset_trials.append(runs // datasets)
    trial_counts = set(per_dataset_trials)
    if not per_dataset_trials:
        raise ValueError("Primary CSV must report successful runs and contributing datasets")
    if len(trial_counts) != 1:
        raise ValueError("Primary CSV must report a consistent number of seeds per dataset cell")

    summary = {
        "schema_version": 1,
        "source_files": {
            "primary": "experiments/results/rubin_coverage_full_v4/headline_coverage.csv",
            "exploratory": "experiments/results/rubin_coverage_full_v4_exploratory/coverage_summary.csv",
        },
        "tags": ["rubin-full-v4", "rubin-sanity-v4-passed"],
        "study": {
            "nominal_coverage": 0.95,
            "coverage_axis_domain": [0.0, 1.0],
            "design": {
                "dataset_count": population_count,
                "sample_size": 500,
                "seeds_per_cell": trial_counts.pop(),
                "masked_columns": 1,
                "mechanisms": unique_values(primary, "mechanism"),
                "missing_rates": unique_values(primary, "mask_rate"),
                "methods": unique_values(primary, "method"),
                "imputation_counts": unique_values(primary, "m"),
                "mnar_delta_grid_sd": unique_values(
                    [row for row in primary if row["mechanism"] == "MNAR"], "delta_sd"
                ),
                "sanity_gate": {"passed": 20, "total": 20},
            },
        },
        "coverage": primary,
        "exploratory": exploratory,
        "caveats": CAVEATS,
        "width_ratio_available": any(row["width_ratio"] is not None for row in primary),
    }

    # Keep generated artifacts outside experiments, even if this script is edited later.
    output_path = OUTPUT_JSON.resolve()
    public_root = (ROOT / "frontend/public").resolve()
    if not output_path.is_relative_to(public_root):
        raise ValueError(f"Research summary output must remain under {public_root}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {output_path.relative_to(ROOT)} "
        f"({len(primary)} primary rows, {len(exploratory)} exploratory rows)"
    )


if __name__ == "__main__":
    main()
