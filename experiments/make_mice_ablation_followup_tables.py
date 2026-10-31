"""Build the post-hoc exploratory MICE follow-up report from saved CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from make_mice_ablation_tables import (
    coverage_summary,
    diagnostic_summary,
    fit_m_dependence,
    load_ablation,
    summarize,
)


SUBSET_LABEL = "5-dataset exploratory subset, not the 10 declared headline datasets"
REPRO_VARIANTS = (
    "project_m5",
    "project_m20",
    "project_m50",
    "project_deterministic",
)
UNCERTAINTY_VARIANTS = (
    "project_m5",
    "project_m20",
    "project_m50",
    "project_hybrid_m20",
)
KEYS = ["dataset", "mechanism", "mask_rate", "trial", "variant"]


def reproduction_check(
    followup: pd.DataFrame, baseline: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare saved numeric RMSE values on identical dataset/trial cells."""
    left = followup.loc[followup["variant"].isin(REPRO_VARIANTS), KEYS + ["numeric_rmse"]]
    selected_datasets = set(left["dataset"])
    right = baseline.loc[
        baseline["dataset"].isin(selected_datasets)
        & baseline["variant"].isin(REPRO_VARIANTS),
        KEYS + ["numeric_rmse"],
    ]
    joined = left.merge(
        right,
        on=KEYS,
        how="outer",
        suffixes=("_followup", "_saved"),
        indicator=True,
        validate="one_to_one",
    )
    if not joined["_merge"].eq("both").all():
        counts = joined["_merge"].value_counts().to_dict()
        raise ValueError(f"Reproduction keys differ: {counts}")
    joined["absolute_difference"] = (
        joined["numeric_rmse_followup"] - joined["numeric_rmse_saved"]
    ).abs()
    summary = (
        joined.groupby("variant", as_index=False)
        .agg(
            n_keys=("absolute_difference", "size"),
            max_abs_difference=("absolute_difference", "max"),
        )
        .sort_values("variant")
        .reset_index(drop=True)
    )
    if summary.empty or (summary["max_abs_difference"] > 1e-9).any():
        raise AssertionError("A variant failed its saved numeric-RMSE reproduction check.")
    return joined.drop(columns="_merge"), summary


def compare_coverage_medians(
    followup: pd.DataFrame, baseline: pd.DataFrame
) -> pd.DataFrame:
    """Compare corrected follow-up coverage against the original saved intervals."""
    variants = ("project_m20", "project_m50")
    selected_datasets = set(followup["dataset"])
    new = (
        followup.loc[followup["variant"].isin(variants)]
        .groupby(["mechanism", "variant"], as_index=False)
        ["uncertainty_coverage90_numeric"]
        .median()
        .rename(columns={"uncertainty_coverage90_numeric": "corrected_median"})
    )
    old = (
        baseline.loc[
            baseline["dataset"].isin(selected_datasets)
            & baseline["variant"].isin(variants)
        ]
        .groupby(["mechanism", "variant"], as_index=False)
        ["uncertainty_coverage90_numeric"]
        .median()
        .rename(columns={"uncertainty_coverage90_numeric": "saved_old_median"})
    )
    return new.merge(old, on=["mechanism", "variant"], validate="one_to_one")


def pc1_diagnostic_table(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize per-column RMSE and pool outside-range counts across trials."""
    if raw.empty:
        raise ValueError("PC1 diagnostic CSV is empty.")
    required = {
        "mechanism",
        "column",
        "variant",
        "per_column_rmse",
        "n_masked",
        "n_outside",
    }
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"PC1 diagnostic CSV missing columns: {sorted(missing)}")
    grouped = (
        raw.groupby(["mechanism", "column", "variant"], as_index=False)
        .agg(
            per_column_rmse=("per_column_rmse", "mean"),
            n_masked=("n_masked", "sum"),
            n_outside=("n_outside", "sum"),
        )
    )
    grouped["masked_values_outside_observed_range_fraction"] = (
        grouped["n_outside"] / grouped["n_masked"]
    )
    mar = grouped.loc[grouped["mechanism"].eq("MAR")]
    wide = mar.pivot(
        index="column", columns="variant", values="per_column_rmse"
    )
    for variant in (
        "project_deterministic",
        "project_deterministic_no_bounds",
        "iterative_single_as_is",
    ):
        if variant not in wide:
            raise ValueError(f"PC1 MAR diagnostic lacks {variant}.")
    wide["abs_det_vs_iterative_gap"] = (
        wide["project_deterministic"] - wide["iterative_single_as_is"]
    ).abs()
    wide["abs_bounds_vs_no_bounds_gap"] = (
        wide["project_deterministic"] - wide["project_deterministic_no_bounds"]
    ).abs()
    gaps = (
        wide.reset_index()
        .sort_values(
            ["abs_det_vs_iterative_gap", "abs_bounds_vs_no_bounds_gap"],
            ascending=False,
        )
        .reset_index(drop=True)
    )
    return grouped.sort_values(["mechanism", "column", "variant"]), gaps


def pc1_diagnostic_wide_table(long_table: pd.DataFrame) -> pd.DataFrame:
    rmse = long_table.pivot(
        index=["mechanism", "column"],
        columns="variant",
        values="per_column_rmse",
    ).reset_index()
    names = {
        "project_deterministic": "rmse_project_deterministic",
        "project_deterministic_no_bounds": "rmse_project_deterministic_no_bounds",
        "iterative_single_as_is": "rmse_iterative_single_as_is",
    }
    rmse = rmse.rename(columns=names)
    range_stats = (
        long_table.groupby(["mechanism", "column"], as_index=False)
        .agg(
            masked_values_outside_observed_range_fraction=(
                "masked_values_outside_observed_range_fraction", "first"
            ),
            n_masked=("n_masked", "first"),
            n_outside=("n_outside", "first"),
        )
    )
    return (
        rmse.merge(range_stats, on=["mechanism", "column"], validate="one_to_one")
        .sort_values(["mechanism", "column"])
        .reset_index(drop=True)
    )


def _table_section(title: str, source: str, table: pd.DataFrame, scope_note: str | None = None) -> str:
    lines = [
        f"## {title}",
        "",
        f"**Scope: {SUBSET_LABEL}.**",
    ]
    if scope_note:
        lines.append(f"**Additional scope note:** {scope_note}")
    lines.extend([
        "",
        f"Source CSV: `{source}`",
        "",
        table.to_markdown(index=False, tablefmt="github", floatfmt=".3f"),
        "",
    ])
    return "\n".join(lines)


def write_followup_summary(
    followup_dir: Path,
    baseline_dir: Path,
    output_path: Path | None = None,
) -> Path:
    followup, followup_sources = load_ablation(followup_dir)
    baseline, baseline_sources = load_ablation(baseline_dir)
    followup_datasets = sorted(followup["dataset"].unique())
    if len(followup_datasets) != 5:
        raise ValueError(
            f"Expected a five-dataset follow-up subset, found {followup_datasets}."
        )
    if not set(followup_datasets).issubset(set(baseline["dataset"])):
        raise ValueError("Follow-up datasets are missing from the saved baseline ablation.")

    _, ratio_aggregate, _ = summarize(followup)
    coverage = coverage_summary(followup)
    if not set(UNCERTAINTY_VARIANTS).issubset(set(coverage["variant"])):
        raise ValueError("Corrected coverage table does not contain every requested variant.")
    repro_detail, repro_summary = reproduction_check(followup, baseline)
    coverage_comparison = compare_coverage_medians(followup, baseline)

    fit_detail, fit_aggregate = fit_m_dependence(baseline)
    if fit_detail["dataset"].nunique() != 10:
        raise ValueError(
            "The descriptive m-fit must use the 10-dataset saved baseline CSVs."
        )
    diagnostic_path = followup_dir / "pc1" / "pc1_diagnostic.csv"
    diagnostic_long, mar_gaps = pc1_diagnostic_table(pd.read_csv(diagnostic_path))
    diagnostic = pc1_diagnostic_wide_table(diagnostic_long)
    top_mar_columns = ", ".join(
        str(column) for column in mar_gaps["column"].head(5).tolist()
    )

    output_path = output_path or followup_dir / "ABLATION_FOLLOWUP_SUMMARY.md"
    sections = [
        "# MICE Ablation Follow-up",
        "",
        "**POST-HOC EXPLORATORY. Descriptive only; no p-values or new significance claims.**",
        "",
        f"All follow-up tables are labeled: **{SUBSET_LABEL}.** The m-dependence fit below is intentionally calculated from the saved 10-dataset ablation CSVs as separately requested; it is not a result of the five-dataset follow-up run.",
        "",
        _table_section(
            "Corrected uncertainty coverage (nominal target 0.90)",
            ", ".join(followup_sources),
            coverage,
            "Coverage interval quantiles are adaptive to m; every row states the nominal target.",
        ),
        _table_section(
            "Corrected versus previously saved coverage medians (m20/m50)",
            ", ".join(followup_sources + baseline_sources),
            coverage_comparison,
            "The saved medians use the old m=5 interval quantile for m20/m50; the follow-up medians use the corrected m-dependent quantile.",
        ),
        _table_section(
            "RMSE-ratio aggregate comparisons",
            ", ".join(followup_sources),
            ratio_aggregate,
            "Ratios are medians across datasets within mechanism and variant; lower ratios are counted separately against project_m5 and project_deterministic.",
        ),
        _table_section(
            "Numeric RMSE reproduction checks",
            ", ".join(followup_sources + baseline_sources),
            repro_summary,
            "Exact dataset/mechanism/rate/trial/variant keys; tolerance is 1e-9.",
        ),
        _table_section(
            "Three-point descriptive m-dependence fit",
            ", ".join(baseline_sources),
            fit_aggregate,
            "Uses all 10 saved ablation datasets: squared RMSE ratio = a + b/m for m in {5, 20, 50}.",
        ),
        _table_section(
            "Per-dataset three-point fit and single-draw sanity check",
            ", ".join(baseline_sources),
            fit_detail,
            "Uses all 10 saved ablation datasets. iterative_single_posterior_true is a sanity-check point only and is not part of the fit.",
        ),
        _table_section(
            "PC1 per-column diagnostic across mechanisms",
            "pc1/pc1_diagnostic.csv",
            diagnostic,
            "RMSE is averaged across trials. Outside-range fraction is pooled as total n_outside / total n_masked using same-mechanism observed training values.",
        ),
        f"**PC1 MAR gap columns — Source CSV: `pc1/pc1_diagnostic.csv`.** The five largest absolute project_deterministic versus iterative_single_as_is per-column RMSE gaps are: {top_mar_columns}. This is part of the {SUBSET_LABEL}.",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sections), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--followup-dir", required=True, type=Path)
    parser.add_argument("--baseline-dir", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    path = write_followup_summary(args.followup_dir, args.baseline_dir, args.out)
    print(path)
    print(f"size_bytes={path.stat().st_size}")


if __name__ == "__main__":
    main()
