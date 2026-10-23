"""Create descriptive tables from saved post-hoc MICE ablation CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
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
    deterministic = (
        per_dataset.loc[
            per_dataset["variant"].eq("project_deterministic"),
            ["dataset", "mechanism", "median_rmse_ratio_vs_mean"],
        ]
        .rename(columns={"median_rmse_ratio_vs_mean": "deterministic_ratio"})
    )
    comparisons = per_dataset.merge(
        project, on=["dataset", "mechanism"], how="left", validate="many_to_one"
    ).merge(
        deterministic, on=["dataset", "mechanism"], how="left", validate="many_to_one"
    )
    comparisons["lower_ratio_than_project_m5"] = (
        comparisons["variant"].ne("project_m5")
        & comparisons["median_rmse_ratio_vs_mean"].lt(comparisons["project_m5_ratio"])
    )
    comparisons["lower_ratio_than_deterministic"] = (
        comparisons["variant"].ne("project_deterministic")
        & comparisons["median_rmse_ratio_vs_mean"].lt(comparisons["deterministic_ratio"])
    )
    aggregate = (
        comparisons.groupby(["mechanism", "variant"], as_index=False)
        .agg(
            median_rmse_ratio_vs_mean=("median_rmse_ratio_vs_mean", "median"),
            n_datasets=("dataset", "nunique"),
            datasets_lower_ratio_than_project_m5=(
                "lower_ratio_than_project_m5", "sum"
            ),
            datasets_lower_ratio_than_deterministic=(
                "lower_ratio_than_deterministic", "sum"
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


def fit_m_dependence(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {"dataset", "mechanism", "trial", "variant", "rmse_ratio_vs_mean"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Ablation CSVs are missing columns: {sorted(missing)}")
    medians = (
        frame.groupby(["dataset", "mechanism", "variant"], as_index=False)
        ["rmse_ratio_vs_mean"].median()
    )
    pivot = medians.pivot(
        index=["dataset", "mechanism"],
        columns="variant",
        values="rmse_ratio_vs_mean",
    )
    fit_rows = []
    for (dataset, mechanism), values in pivot.iterrows():
        fit_variants = ("project_m5", "project_m20", "project_m50")
        if any(variant not in values or pd.isna(values[variant]) for variant in fit_variants):
            continue
        x = np.array([1 / 5, 1 / 20, 1 / 50], dtype=float)
        y = np.square([float(values[variant]) for variant in fit_variants])
        slope, intercept = np.polyfit(x, y, deg=1)
        deterministic_ratio = float(values.get("project_deterministic", np.nan))
        single_draw_ratio = float(values.get("iterative_single_posterior_true", np.nan))
        fit_rows.append({
            "dataset": dataset,
            "mechanism": mechanism,
            "a_asymptote": float(intercept),
            "b_slope": float(slope),
            "deterministic_ratio_squared": deterministic_ratio**2,
            "asymptote_minus_deterministic_squared": (
                float(intercept - deterministic_ratio**2)
                if np.isfinite(deterministic_ratio) else np.nan
            ),
            "single_draw_ratio_sanity_check": single_draw_ratio,
            "fit_description": "descriptive 3-point fit of squared RMSE ratio on 1/m",
        })
    detail = pd.DataFrame(fit_rows)
    aggregate = (
        detail.groupby("mechanism", as_index=False)
        .agg(
            n_datasets=("dataset", "nunique"),
            median_a_asymptote=("a_asymptote", "median"),
            median_b_slope=("b_slope", "median"),
            median_asymptote_minus_deterministic_squared=(
                "asymptote_minus_deterministic_squared", "median"
            ),
        )
    )
    return detail, aggregate


def coverage_summary(frame: pd.DataFrame) -> pd.DataFrame:
    coverage = frame.loc[
        frame["variant"].isin(
            ("project_m5", "project_m20", "project_m50", "project_hybrid_m20")
        )
    ]
    return (
        coverage.groupby(["mechanism", "variant"], as_index=False)
        ["uncertainty_coverage90_numeric"]
        .agg(minimum="min", median="median", maximum="max")
        .assign(nominal_target="nominal 0.90")
    )


def diagnostic_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    return (
        frame.groupby(["mechanism", "column", "variant"], as_index=False)
        .agg(
            per_column_rmse=("per_column_rmse", "mean"),
            masked_values_outside_observed_range_fraction=(
                "masked_values_outside_observed_range_fraction", "mean"
            ),
            n_masked=("n_masked", "sum"),
            n_outside=("n_outside", "sum"),
        )
        .sort_values(["mechanism", "column", "variant"])
    )


def write_summary(input_dir: Path, output_dir: Path) -> Path:
    frame, source_names = load_ablation(input_dir)
    per_dataset, aggregate, uncertainty = summarize(frame)
    fit_detail, fit_aggregate = fit_m_dependence(frame)
    coverage = coverage_summary(frame)
    diagnostic_path = input_dir / "pc1" / "pc1_diagnostic.csv"
    diagnostic = (
        diagnostic_summary(pd.read_csv(diagnostic_path))
        if diagnostic_path.is_file() else pd.DataFrame()
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = (
        ("ablation_ratios_by_dataset.csv", per_dataset),
        ("ablation_ratio_aggregate.csv", aggregate),
        ("ablation_uncertainty_summary.csv", uncertainty),
        ("ablation_m_dependence_by_dataset.csv", fit_detail),
        ("ablation_m_dependence_aggregate.csv", fit_aggregate),
        ("ablation_coverage_corrected.csv", coverage),
    )
    for filename, table in tables:
        table.to_csv(output_dir / filename, index=False)
    if not diagnostic.empty:
        diagnostic.to_csv(output_dir / "pc1_column_diagnostic_summary.csv", index=False)

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
        "## Corrected 90% interval coverage",
        "",
        f"Source CSVs: {source_list}",
        "",
        "Summary CSV: `ablation_coverage_corrected.csv`",
        "",
        coverage.to_markdown(index=False, tablefmt="github"),
        "",
        "## Descriptive m-dependence fit",
        "",
        f"Source CSVs: {source_list}",
        "",
        "Descriptive three-point fit: squared RMSE ratio = a + b/m for m in {5, 20, 50}; the iterative single posterior draw is reported only as a sanity check.",
        "",
        "Aggregate CSV: `ablation_m_dependence_aggregate.csv`; per-dataset CSV: `ablation_m_dependence_by_dataset.csv`",
        "",
        fit_aggregate.to_markdown(index=False, tablefmt="github"),
        "",
        "## PC1 per-column MAR diagnostic",
        "",
        "Source CSV: `pc1/pc1_diagnostic.csv`",
        "",
        "Per-column RMSE is in full-data-standardized units. The range diagnostic reports the fraction of masked truths outside the min/max of observed entries in that column for the same mechanism/trial.",
        "",
        (
            diagnostic.to_markdown(index=False, tablefmt="github")
            if not diagnostic.empty else "Not run."
        ),
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
