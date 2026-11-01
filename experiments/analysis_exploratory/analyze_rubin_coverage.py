"""Post-hoc analysis of the existing v4 Rubin coverage results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


EXPLORATORY_LABEL = "EXPLORATORY (post-hoc, not pre-registered)"
EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = EXPERIMENTS_DIR / "results/rubin_coverage_full_v4/raw.csv.gz"
OUTPUT_DIR = EXPERIMENTS_DIR / "results/rubin_coverage_full_v4_exploratory"
SENSITIVITY_GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)
METHODS = ("mice_improper", "mice_proper")
PAIR_KEYS = (
    "dataset",
    "mechanism",
    "mask_rate",
    "estimand",
    "trial",
    "mask_seed",
    "trial_seed",
)
NUMERIC_COLUMNS = (
    "mask_rate",
    "delta_sd",
    "delta_raw",
    "m",
    "trial",
    "mask_seed",
    "trial_seed",
    "truth",
    "estimate",
    "bias",
    "standard_error",
    "ci_lower",
    "ci_upper",
)
INPUT_COLUMNS = (
    "dataset",
    "estimand",
    "mechanism",
    "mask_rate",
    "delta_sd",
    "delta_raw",
    "method",
    "m",
    "trial",
    "mask_seed",
    "trial_seed",
    "truth",
    "estimate",
    "standard_error",
    "ci_lower",
    "ci_upper",
    "bias",
    "status",
)


def _valid_intervals(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "truth",
        "estimate",
        "ci_lower",
        "ci_upper",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing interval columns: {sorted(missing)}")
    valid = frame.copy()
    if "status" in valid:
        valid = valid.loc[valid["status"].eq("success")].copy()
    numeric = ["truth", "estimate", "ci_lower", "ci_upper"]
    for column in numeric:
        valid[column] = pd.to_numeric(valid[column], errors="coerce")
    finite = np.isfinite(valid[numeric].to_numpy(dtype=float)).all(axis=1)
    valid = valid.loc[finite & valid["ci_lower"].le(valid["ci_upper"])].copy()
    valid["_covers_truth"] = (
        valid["ci_lower"].le(valid["truth"])
        & valid["ci_upper"].ge(valid["truth"])
    )
    return valid


def undercoverage_decomposition(frame: pd.DataFrame) -> dict[str, Any]:
    """Summarize bias, empirical variability, SE calibration, and miss direction."""
    required = {"bias", "standard_error"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing decomposition columns: {sorted(missing)}")
    valid = _valid_intervals(frame)
    valid["bias"] = pd.to_numeric(valid["bias"], errors="coerce")
    valid["standard_error"] = pd.to_numeric(
        valid["standard_error"], errors="coerce"
    )
    valid = valid.loc[
        np.isfinite(valid[["bias", "standard_error"]].to_numpy(dtype=float)).all(
            axis=1
        )
    ]
    estimates = valid["estimate"].to_numpy(dtype=float)
    empirical_sd = float(np.std(estimates, ddof=1)) if len(estimates) > 1 else np.nan
    mean_se = float(valid["standard_error"].mean()) if len(valid) else np.nan
    noncovering = valid.loc[~valid["_covers_truth"]]
    n_noncovering = len(noncovering)
    n_above = int(noncovering["ci_lower"].gt(noncovering["truth"]).sum())
    n_below = int(noncovering["ci_upper"].lt(noncovering["truth"]).sum())
    return {
        "n_intervals": len(valid),
        "mean_bias": float(valid["bias"].mean()) if len(valid) else np.nan,
        "empirical_sd_estimate": empirical_sd,
        "mean_pooled_se": mean_se,
        "mean_se_to_empirical_sd": (
            mean_se / empirical_sd
            if np.isfinite(empirical_sd) and empirical_sd > 0
            else np.nan
        ),
        "n_noncovering": n_noncovering,
        "n_noncovering_above_truth": n_above,
        "share_noncovering_above_truth": (
            n_above / n_noncovering if n_noncovering else np.nan
        ),
        "n_noncovering_below_truth": n_below,
        "share_noncovering_below_truth": (
            n_below / n_noncovering if n_noncovering else np.nan
        ),
    }


def paired_difference(
    frame: pd.DataFrame, n_bootstrap: int = 2_000, seed: int = 42
) -> dict[str, Any]:
    """Compare coverage on matching masks, bootstrapping whole datasets."""
    missing = set(PAIR_KEYS + ("method",)).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing paired-comparison columns: {sorted(missing)}")
    valid = _valid_intervals(frame)
    valid = valid.loc[valid["method"].isin(METHODS)].copy()
    paired_parts = []
    for method, output_column in (
        ("mice_improper", "improper_covers"),
        ("mice_proper", "proper_covers"),
    ):
        subset = valid.loc[valid["method"].eq(method), list(PAIR_KEYS) + [
            "_covers_truth"
        ]].copy()
        subset = subset.dropna(subset=list(PAIR_KEYS))
        subset = subset.rename(columns={"_covers_truth": output_column})
        paired_parts.append(subset)
    improper, proper = paired_parts
    paired = improper.merge(
        proper,
        on=list(PAIR_KEYS),
        how="inner",
        validate="one_to_one",
    )
    if paired.empty:
        return {
            "n_pairs": 0,
            "n_datasets": 0,
            "improper_covers_proper_does_not": 0,
            "proper_covers_improper_does_not": 0,
            "coverage_difference_improper_minus_proper": np.nan,
            "bootstrap_ci_lower": np.nan,
            "bootstrap_ci_upper": np.nan,
            "bootstrap_reps": n_bootstrap,
            "bootstrap_seed": seed,
        }

    differences = (
        paired["improper_covers"].astype(bool).astype(int)
        - paired["proper_covers"].astype(bool).astype(int)
    )
    dataset_values = paired["dataset"].drop_duplicates().to_numpy()
    dataset_summaries = (
        paired.assign(_difference=differences)
        .groupby("dataset", sort=True)["_difference"]
        .agg(["sum", "count"])
    )
    rng = np.random.RandomState(seed)
    bootstrapped = np.empty(n_bootstrap, dtype=float)
    cluster_names = dataset_summaries.index.to_numpy()
    for replicate in range(n_bootstrap):
        sampled = rng.choice(cluster_names, size=len(cluster_names), replace=True)
        sampled_sums = dataset_summaries.loc[sampled, "sum"].to_numpy(dtype=float)
        sampled_counts = dataset_summaries.loc[sampled, "count"].to_numpy(dtype=float)
        bootstrapped[replicate] = sampled_sums.sum() / sampled_counts.sum()
    lower, upper = np.quantile(bootstrapped, [0.025, 0.975])
    return {
        "n_pairs": len(paired),
        "n_datasets": len(dataset_values),
        "improper_covers_proper_does_not": int(
            (paired["improper_covers"] & ~paired["proper_covers"]).sum()
        ),
        "proper_covers_improper_does_not": int(
            (paired["proper_covers"] & ~paired["improper_covers"]).sum()
        ),
        "coverage_difference_improper_minus_proper": float(differences.mean()),
        "bootstrap_ci_lower": float(lower),
        "bootstrap_ci_upper": float(upper),
        "bootstrap_reps": n_bootstrap,
        "bootstrap_seed": seed,
    }


def _coverage_table(
    frame: pd.DataFrame, group_columns: list[str]
) -> pd.DataFrame:
    valid = _valid_intervals(frame)
    if valid.empty:
        return pd.DataFrame(columns=group_columns + [
            "n_intervals",
            "coverage",
            "binomial_mc_se",
        ])
    summary = (
        valid.groupby(group_columns, dropna=False, sort=True)["_covers_truth"]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(
            columns={
                "sum": "n_covering",
                "count": "n_intervals",
                "mean": "coverage",
            }
        )
    )
    summary["binomial_mc_se"] = np.sqrt(
        summary["coverage"] * (1.0 - summary["coverage"])
        / summary["n_intervals"]
    )
    return summary


def _decomposition_table(frame: pd.DataFrame) -> pd.DataFrame:
    groups = ["dataset", "mechanism", "mask_rate", "estimand", "method"]
    rows = []
    for keys, group in frame.groupby(groups, dropna=False, sort=True):
        values = dict(zip(groups, keys))
        values.update(undercoverage_decomposition(group))
        rows.append(values)
    return pd.DataFrame(rows)


def _paired_table(frame: pd.DataFrame) -> pd.DataFrame:
    groups = ["mechanism", "mask_rate", "estimand"]
    rows = []
    for keys, group in frame.groupby(groups, dropna=False, sort=True):
        values = dict(zip(groups, keys))
        values.update(paired_difference(group))
        rows.append(values)
    return pd.DataFrame(rows)


def _mnar_envelopes(frame: pd.DataFrame) -> pd.DataFrame:
    selected = frame.loc[
        frame["mechanism"].eq("MNAR")
        & frame["method"].eq("mice_proper")
        & frame["m"].eq(20)
        & frame["delta_sd"].map(
            lambda value: any(np.isclose(value, target) for target in SENSITIVITY_GRID)
        )
    ].copy()
    group_columns = [
        "dataset",
        "mask_rate",
        "estimand",
        "trial",
        "trial_seed",
        "mask_seed",
    ]
    rows = []
    for keys, group in selected.groupby(group_columns, dropna=False, sort=True):
        values = dict(zip(group_columns, keys))
        present_levels = set(group["delta_sd"].dropna().astype(float))
        valid = _valid_intervals(group)
        valid_levels = valid["delta_sd"].dropna().astype(float)
        if valid_levels.duplicated().any():
            raise ValueError(f"Duplicate MNAR sensitivity rows for mask {keys}")
        complete = (
            len(present_levels) == len(SENSITIVITY_GRID)
            and len(valid_levels) == len(SENSITIVITY_GRID)
        )
        if complete:
            lower = float(valid["ci_lower"].min())
            upper = float(valid["ci_upper"].max())
            truth_values = valid["truth"].unique()
            if len(truth_values) != 1:
                raise ValueError(f"Truth differs across MNAR sensitivity rows: {keys}")
            truth = float(truth_values[0])
            covers = lower <= truth <= upper
        else:
            lower = upper = truth = np.nan
            covers = np.nan
        values.update({
            "n_delta_levels_present": len(present_levels),
            "n_valid_delta_levels": len(valid_levels),
            "complete_envelope": bool(complete),
            "union_ci_lower": lower,
            "union_ci_upper": upper,
            "truth": truth,
            "union_covers_truth": covers,
        })
        rows.append(values)
    return pd.DataFrame(rows)


def _add_label(frame: pd.DataFrame) -> pd.DataFrame:
    labeled = frame.copy()
    labeled.insert(0, "exploratory_label", EXPLORATORY_LABEL)
    return labeled


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    _add_label(frame).to_csv(path, index=False)


def _save_figure(fig: plt.Figure, stem: str) -> None:
    fig.text(
        0.5,
        0.005,
        EXPLORATORY_LABEL,
        ha="center",
        va="bottom",
        fontsize=5.5,
    )
    fig.savefig(OUTPUT_DIR / f"{stem}.png", dpi=300)
    fig.savefig(OUTPUT_DIR / f"{stem}.pdf")
    plt.close(fig)


def _plot_coverage(coverage: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(3.5, 4.6), sharey=True)
    mechanisms = ("MCAR", "MAR", "MNAR")
    estimands = ("mean", "ols_slope")
    method_labels = {
        "mice_improper": "Improper",
        "mice_proper": "Proper",
    }
    for row_index, mechanism in enumerate(mechanisms):
        for column_index, estimand in enumerate(estimands):
            axis = axes[row_index, column_index]
            subset = coverage.loc[
                coverage["mechanism"].eq(mechanism)
                & coverage["estimand"].eq(estimand)
            ]
            for method in METHODS:
                line = subset.loc[subset["method"].eq(method)].sort_values("mask_rate")
                axis.plot(
                    line["mask_rate"],
                    line["mean_dataset_coverage"],
                    marker="o",
                    markersize=2.5,
                    linewidth=0.9,
                    label=method_labels[method],
                )
            axis.axhline(0.95, color="0.35", linestyle="--", linewidth=0.6)
            axis.set_title(f"{mechanism} / {estimand}", fontsize=6)
            axis.set_ylim(0, 1.02)
            axis.set_xticks(sorted(coverage["mask_rate"].dropna().unique()))
            axis.tick_params(labelsize=5, length=2)
            if row_index == 2:
                axis.set_xlabel("Missing rate", fontsize=5.5)
            if column_index == 0:
                axis.set_ylabel("Mean dataset coverage", fontsize=5.5)
            if row_index == 0 and column_index == 0:
                axis.legend(fontsize=5, frameon=False, loc="lower left")
    fig.suptitle(EXPLORATORY_LABEL, fontsize=7)
    fig.tight_layout(rect=(0, 0.025, 1, 0.96), h_pad=1.2, w_pad=0.6)
    _save_figure(fig, "coverage_vs_missing_rate_by_mechanism")


def _plot_mnar_coverage(coverage: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.25), sharey=True)
    for axis, estimand in zip(axes, ("mean", "ols_slope")):
        subset = coverage.loc[coverage["estimand"].eq(estimand)]
        for rate in sorted(subset["mask_rate"].dropna().unique()):
            line = subset.loc[subset["mask_rate"].eq(rate)].sort_values("delta_sd")
            axis.plot(
                line["delta_sd"],
                line["coverage"],
                marker="o",
                markersize=2.5,
                linewidth=0.9,
                label=f"rate {rate:g}",
            )
        axis.axhline(0.95, color="0.35", linestyle="--", linewidth=0.6)
        axis.set_title(estimand, fontsize=6)
        axis.set_xticks(SENSITIVITY_GRID)
        axis.set_ylim(0, 1.02)
        axis.tick_params(labelsize=5, length=2)
        axis.set_xlabel("MNAR delta (SD units)", fontsize=5.5)
        axis.legend(fontsize=5, frameon=False)
    axes[0].set_ylabel("Coverage (proper method)", fontsize=5.5)
    fig.suptitle(EXPLORATORY_LABEL, fontsize=7)
    fig.tight_layout(rect=(0, 0.025, 1, 0.91), w_pad=0.7)
    _save_figure(fig, "mnar_coverage_vs_delta")


def _plot_se_calibration(decomposition: pd.DataFrame) -> None:
    ratio = (
        decomposition.groupby(
            ["mechanism", "mask_rate", "estimand", "method"], sort=True
        )["mean_se_to_empirical_sd"]
        .mean()
        .reset_index(name="mean_dataset_ratio")
    )
    fig, axes = plt.subplots(3, 2, figsize=(3.5, 4.6), sharey=True)
    for row_index, mechanism in enumerate(("MCAR", "MAR", "MNAR")):
        for column_index, estimand in enumerate(("mean", "ols_slope")):
            axis = axes[row_index, column_index]
            subset = ratio.loc[
                ratio["mechanism"].eq(mechanism)
                & ratio["estimand"].eq(estimand)
            ]
            for method in METHODS:
                line = subset.loc[subset["method"].eq(method)].sort_values("mask_rate")
                axis.plot(
                    line["mask_rate"],
                    line["mean_dataset_ratio"],
                    marker="o",
                    markersize=2.5,
                    linewidth=0.9,
                    label={"mice_improper": "Improper", "mice_proper": "Proper"}[
                        method
                    ],
                )
            axis.axhline(1.0, color="0.35", linestyle="--", linewidth=0.6)
            axis.set_title(f"{mechanism} / {estimand}", fontsize=6)
            axis.tick_params(labelsize=5, length=2)
            if row_index == 2:
                axis.set_xlabel("Missing rate", fontsize=5.5)
            if column_index == 0:
                axis.set_ylabel("Mean dataset SE / SD", fontsize=5.5)
            if row_index == 0 and column_index == 0:
                axis.legend(fontsize=5, frameon=False, loc="best")
    fig.suptitle(EXPLORATORY_LABEL, fontsize=7)
    fig.tight_layout(rect=(0, 0.025, 1, 0.96), h_pad=1.2, w_pad=0.6)
    _save_figure(fig, "se_calibration_ratio_vs_missing_rate")


def run_analysis() -> dict[str, int]:
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Existing v4 input not found: {INPUT_PATH}")
    if INPUT_PATH.resolve() == OUTPUT_DIR.resolve():
        raise ValueError("Output directory must not overwrite the input file")
    raw = pd.read_csv(
        INPUT_PATH,
        compression="gzip",
        usecols=list(INPUT_COLUMNS),
    )
    for column in NUMERIC_COLUMNS:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    primary = raw.loc[
        raw["method"].isin(METHODS)
        & raw["m"].eq(20)
        & raw["delta_sd"].eq(0)
        & raw["delta_raw"].eq(0)
        & raw["mechanism"].isin(("MCAR", "MAR", "MNAR"))
    ].copy()
    primary_valid = _valid_intervals(primary)
    coverage_by_dataset = _coverage_table(
        primary_valid,
        ["dataset", "mechanism", "mask_rate", "estimand", "method"],
    )
    _write_csv(
        coverage_by_dataset,
        OUTPUT_DIR / "coverage_by_dataset.csv",
    )
    coverage_summary = (
        coverage_by_dataset.groupby(
            ["mechanism", "mask_rate", "estimand", "method"], sort=True
        )
        .agg(
            dataset_count=("dataset", "nunique"),
            mean_dataset_coverage=("coverage", "mean"),
        )
        .reset_index()
    )
    _write_csv(coverage_summary, OUTPUT_DIR / "coverage_summary.csv")

    decomposition = _decomposition_table(primary_valid)
    _write_csv(
        decomposition,
        OUTPUT_DIR / "undercoverage_decomposition_by_dataset.csv",
    )
    paired = _paired_table(primary_valid)
    _write_csv(paired, OUTPUT_DIR / "paired_method_comparison.csv")

    mnar_delta_rows = raw.loc[
        raw["mechanism"].eq("MNAR")
        & raw["method"].eq("mice_proper")
        & raw["m"].eq(20)
        & raw["delta_sd"].map(
            lambda value: any(np.isclose(value, target) for target in SENSITIVITY_GRID)
        )
    ]
    mnar_delta_coverage = _coverage_table(
        mnar_delta_rows,
        ["mask_rate", "estimand", "delta_sd"],
    )
    _write_csv(
        mnar_delta_coverage,
        OUTPUT_DIR / "mnar_proper_coverage_by_delta.csv",
    )
    envelopes = _mnar_envelopes(raw)
    _write_csv(envelopes, OUTPUT_DIR / "mnar_proper_union_envelopes_by_dataset.csv")
    complete_envelopes = envelopes.loc[envelopes["complete_envelope"]].copy()
    envelope_summary = (
        complete_envelopes.groupby(["mask_rate", "estimand"], sort=True)
        ["union_covers_truth"]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(
            columns={
                "sum": "n_envelopes_covering",
                "count": "n_complete_envelopes",
                "mean": "coverage",
            }
        )
    )
    envelope_summary["n_incomplete_envelopes"] = (
        envelopes.groupby(["mask_rate", "estimand"], sort=True)
        .size()
        .reindex(
            pd.MultiIndex.from_frame(envelope_summary[["mask_rate", "estimand"]]),
            fill_value=0,
        )
        .to_numpy()
        - envelope_summary["n_complete_envelopes"].to_numpy()
    )
    envelope_summary["binomial_mc_se"] = np.sqrt(
        envelope_summary["coverage"]
        * (1.0 - envelope_summary["coverage"])
        / envelope_summary["n_complete_envelopes"]
    )
    _write_csv(
        envelope_summary,
        OUTPUT_DIR / "mnar_proper_union_coverage_by_rate_estimand.csv",
    )

    _plot_coverage(coverage_summary)
    _plot_mnar_coverage(mnar_delta_coverage)
    _plot_se_calibration(decomposition)

    metadata = {
        "exploratory_label": EXPLORATORY_LABEL,
        "input_file": str(INPUT_PATH.relative_to(EXPERIMENTS_DIR.parent)),
        "output_directory": str(OUTPUT_DIR.relative_to(EXPERIMENTS_DIR.parent)),
        "source_rows_read": int(len(raw)),
        "primary_rows_selected": int(len(primary)),
        "primary_valid_intervals": int(len(primary_valid)),
        "bootstrap_reps": 2_000,
        "bootstrap_seed": 42,
        "sensitivity_delta_sd_grid": list(SENSITIVITY_GRID),
        "figure_width_inches": 3.5,
        "figure_width_description": "single-column IEEE",
        "analysis_only": True,
        "simulation_rerun": False,
    }
    (OUTPUT_DIR / "analysis_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    readme = (
        f"{EXPLORATORY_LABEL}\n\n"
        "This folder contains post-hoc analyses of the existing "
        "experiments/results/rubin_coverage_full_v4/raw.csv.gz. "
        "No simulation or experiment was rerun. The source v4 results were "
        "read only; all generated artifacts are in this folder.\n\n"
        "CSV outputs contain an exploratory_label column. Each figure carries "
        "the same label. The paired comparison uses matching dataset/trial/"
        "mask seeds and resamples whole datasets (2,000 bootstrap replicates, "
        "seed 42). MNAR union coverage requires all five recorded delta-SD "
        "levels {-1, -0.5, 0, 0.5, 1} to have valid intervals.\n"
    )
    (OUTPUT_DIR / "README.txt").write_text(readme, encoding="utf-8")
    return {
        "source_rows": len(raw),
        "primary_valid_intervals": len(primary_valid),
        "coverage_rows": len(coverage_by_dataset),
        "decomposition_rows": len(decomposition),
        "paired_cells": len(paired),
        "complete_mnar_envelopes": len(complete_envelopes),
        "outputs": len(list(OUTPUT_DIR.iterdir())),
    }


def main() -> None:
    summary = run_analysis()
    print(EXPLORATORY_LABEL)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
