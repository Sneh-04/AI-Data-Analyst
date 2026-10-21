"""Create descriptive tables from saved post-hoc MICE ablation CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


KEYS = ["dataset", "mechanism", "trial", "variant"]
DRAW_VARIANTS = ("project_m5", "project_m20", "project_m50")
UNCERTAINTY_METRICS = (
    "uncertainty_spearman_numeric",
    "uncertainty_coverage90_numeric",
)


def load_ablation(input_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    paths = sorted(input_dir.glob("*/ablation.csv"))
    if not paths:
        raise FileNotFoundError(f"No per-dataset ablation CSVs found in {input_dir}.")
    frames = [pd.read_csv(path) for path in paths]
    frame = pd.concat(frames, ignore_index=True)
    if frame.duplicated(KEYS).any():
        duplicates = frame.loc[frame.duplicated(KEYS, keep=False), KEYS]
        raise ValueError(f"Duplicate saved ablation trial keys:\n{duplicates}")
    return frame, [path.relative_to(input_dir).as_posix() for path in paths]


def summarize(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = {*KEYS, "rmse_ratio_vs_mean", *UNCERTAINTY_METRICS}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Ablation CSVs are missing columns: {sorted(missing)}")
    per_dataset = (
        frame.groupby(["dataset", "mechanism", "variant"], as_index=False)
        .agg(
            median_rmse_ratio_vs_mean=("rmse_ratio_vs_mean", "median"),
        )
        .sort_values(["mechanism", "dataset", "variant"])
        .reset_index(drop=True)
    )
    project = (
        per_dataset.loc[
            per_dataset["variant"].eq("project_m5"),
            ["dataset", "mechanism", "median_rmse_ratio_vs_mean"],
        ]
        .rename(columns={"median_rmse_ratio_vs_mean": "project_m5_ratio"})
    )
    comparisons = per_dataset.merge(
        project, on=["dataset", "mechanism"], how="left", validate="many_to_one"
    )
    comparisons["lower_ratio_than_project_m5"] = (
        comparisons["variant"].ne("project_m5")
        & comparisons["median_rmse_ratio_vs_mean"].lt(comparisons["project_m5_ratio"])
    )
    aggregate = (
        comparisons.groupby(["mechanism", "variant"], as_index=False)
        .agg(
            median_rmse_ratio_vs_mean=("median_rmse_ratio_vs_mean", "median"),
            n_datasets=("dataset", "nunique"),
            datasets_lower_ratio_than_project_m5=(
                "lower_ratio_than_project_m5", "sum"
            ),
        )
        .sort_values(["mechanism", "variant"])
        .reset_index(drop=True)
    )
    uncertainty_by_dataset = (
        frame.loc[frame["variant"].isin(DRAW_VARIANTS)]
        .groupby(["dataset", "mechanism", "variant"], as_index=False)[
            list(UNCERTAINTY_METRICS)
        ]
        .median()
    )
    uncertainty = (
        uncertainty_by_dataset.melt(
            id_vars=["dataset", "mechanism", "variant"],
            value_vars=list(UNCERTAINTY_METRICS),
            var_name="uncertainty_metric",
            value_name="value",
        )
        .groupby(["mechanism", "variant", "uncertainty_metric"], as_index=False)
        .agg(
            n_datasets=("dataset", "nunique"),
            minimum=("value", "min"),
            median=("value", "median"),
            maximum=("value", "max"),
        )
        .sort_values(["mechanism", "uncertainty_metric", "variant"])
        .reset_index(drop=True)
    )
    return per_dataset, aggregate, uncertainty


def write_summary(input_dir: Path, output_dir: Path) -> Path:
    frame, source_names = load_ablation(input_dir)
    per_dataset, aggregate, uncertainty = summarize(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = (
        ("ablation_ratios_by_dataset.csv", per_dataset),
        ("ablation_ratio_aggregate.csv", aggregate),
        ("ablation_uncertainty_summary.csv", uncertainty),
    )
    for filename, table in tables:
        table.to_csv(output_dir / filename, index=False)

    source_list = ", ".join(f"`{name}`" for name in source_names)
    sections = [
        "# MICE Point-Estimate Ablation Summary",
        "",
        "**Post-hoc exploratory; descriptive only. No p-values or new significance claims.**",
        "",
        "Coverage uses the existing Protocol A evaluator, whose interval correction is configured for m=5; m20/m50 coverage is descriptive under that unchanged metric.",
        "",
        "## Per-dataset median RMSE ratio",
        "",
        f"Source CSVs: {source_list}",
        "",
        f"Summary CSV: `ablation_ratios_by_dataset.csv`",
        "",
        per_dataset.to_markdown(index=False, tablefmt="github"),
        "",
        "## Aggregate median ratio and datasets below project_m5",
        "",
        f"Source CSVs: {source_list}",
        "",
        f"Summary CSV: `ablation_ratio_aggregate.csv`",
        "",
        aggregate.to_markdown(index=False, tablefmt="github"),
        "",
        "## Uncertainty metrics across datasets",
        "",
        f"Source CSVs: {source_list}",
        "",
        f"Summary CSV: `ablation_uncertainty_summary.csv`",
        "",
        uncertainty.to_markdown(index=False, tablefmt="github"),
        "",
    ]
    path = output_dir / "ABLATION_SUMMARY.md"
    path.write_text("\n".join(sections), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    output_dir = args.out or args.input_dir / "tables"
    print(write_summary(args.input_dir, output_dir))


if __name__ == "__main__":
    main()
