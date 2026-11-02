"""Summarize saved Rubin coverage benchmark CSVs without rerunning experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


GROUP_COLUMNS = [
    "dataset",
    "estimand",
    "mechanism",
    "method",
    "mask_rate",
    "m",
    "delta_sd",
]
HEADLINE_COLUMNS = [column for column in GROUP_COLUMNS if column != "dataset"]
CLUSTER_BOOTSTRAPS = 2_000
CLUSTER_BOOTSTRAP_SEED = 42


def _read_results(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_path = input_dir / "raw.csv"
    failures_path = input_dir / "failures.csv"
    if not raw_path.is_file():
        raise FileNotFoundError(f"Missing raw benchmark results: {raw_path}")
    raw = pd.read_csv(raw_path)
    required = {
        *GROUP_COLUMNS,
        "status",
        "ci_covers_truth",
        "ci_width",
        "bias",
    }
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"raw.csv is missing columns: {sorted(missing)}")
    failures = pd.read_csv(failures_path) if failures_path.is_file() else pd.DataFrame()
    return raw, failures


def summarize(input_dir: Path) -> dict[str, pd.DataFrame]:
    """Create per-dataset, dataset-clustered headline, and sanity tables."""
    raw, all_failures = _read_results(input_dir)
    all_successful = raw.loc[raw["status"].eq("success")].copy()
    successful = all_successful.loc[
        ~all_successful["method"].eq("no_missing_sanity")
    ].copy()
    failures = all_failures.loc[
        ~all_failures["method"].eq("no_missing_sanity")
    ].copy() if not all_failures.empty else all_failures
    successful["ci_covers_truth"] = successful["ci_covers_truth"].astype(bool)
    all_successful["ci_covers_truth"] = all_successful["ci_covers_truth"].astype(bool)
    sanity = _no_missing_sanity(all_successful, all_failures)
    sanity_failed_pairs = set(
        sanity.loc[
            sanity["sanity_status"].eq("sanity-failed"),
            ["dataset", "estimand"],
        ].itertuples(index=False, name=None)
    )

    failed = (
        failures.groupby(GROUP_COLUMNS, dropna=False).size()
        if not failures.empty
        else pd.Series(dtype="int64")
    )
    grouped = successful.groupby(GROUP_COLUMNS, dropna=False, as_index=False)
    coverage = grouped.agg(
        coverage=("ci_covers_truth", "mean"),
        coverage_mc_se=("ci_covers_truth", lambda values: float(
            np.sqrt(values.mean() * (1.0 - values.mean()) / len(values))
        )),
        successful_runs=("run_key", "count"),
        noncovering_runs=("ci_covers_truth", lambda values: int((~values).sum())),
        finite_interval_runs=("ci_width", "count"),
    )
    coverage["failed_runs"] = 0
    coverage_indexed = coverage.set_index(GROUP_COLUMNS)
    for key, count in failed.items():
        if key in coverage_indexed.index:
            coverage_indexed.loc[key, "failed_runs"] += int(count)
        else:
            row = dict(zip(GROUP_COLUMNS, key if isinstance(key, tuple) else (key,)))
            row.update({
                "coverage": np.nan,
                "coverage_mc_se": np.nan,
                "successful_runs": 0,
                "noncovering_runs": 0,
                "finite_interval_runs": 0,
                "failed_runs": int(count),
            })
            coverage_indexed.loc[key] = [row[column] for column in coverage_indexed.columns]
    coverage = coverage_indexed.reset_index().sort_values(GROUP_COLUMNS).reset_index(drop=True)
    coverage["attempted_runs"] = coverage["successful_runs"] + coverage["failed_runs"]
    coverage["complete_100_seed_cell"] = coverage["successful_runs"].ge(100)

    headline_successful = _exclude_sanity_failed(successful, sanity_failed_pairs)
    headline_failures = _exclude_sanity_failed(failures, sanity_failed_pairs)
    headline = _headline_coverage(headline_successful, headline_failures)
    excluded_by_estimand = {
        estimand: ", ".join(sorted(
            dataset
            for dataset, failed_estimand in sanity_failed_pairs
            if failed_estimand == estimand
        ))
        for estimand in sanity["estimand"].dropna().unique()
    }
    headline["sanity_failed_datasets_excluded"] = headline["estimand"].map(
        excluded_by_estimand
    ).fillna("")
    width = (
        successful.groupby(GROUP_COLUMNS, dropna=False, as_index=False)
        .agg(
            mean_ci_width=("ci_width", "mean"),
            finite_interval_runs=("ci_width", "count"),
            successful_runs=("run_key", "count"),
        )
        .sort_values(GROUP_COLUMNS)
        .reset_index(drop=True)
    )
    bias = (
        successful.groupby(GROUP_COLUMNS, dropna=False, as_index=False)
        .agg(
            mean_bias=("bias", "mean"),
            successful_runs=("run_key", "count"),
        )
        .sort_values(GROUP_COLUMNS)
        .reset_index(drop=True)
    )
    mnar_delta = coverage.loc[coverage["mechanism"].eq("MNAR")].copy()
    return {
        "coverage": coverage,
        "headline_coverage": headline,
        "width": width,
        "bias": bias,
        "mnar_delta": mnar_delta,
        "no_missing_sanity": sanity,
    }


def _exclude_sanity_failed(
    frame: pd.DataFrame, failed_pairs: set[tuple[object, object]]
) -> pd.DataFrame:
    if frame.empty or not failed_pairs:
        return frame
    keep = [
        (dataset, estimand) not in failed_pairs
        for dataset, estimand in zip(frame["dataset"], frame["estimand"])
    ]
    return frame.loc[keep].copy()


def _headline_coverage(
    successful: pd.DataFrame, failures: pd.DataFrame
) -> pd.DataFrame:
    columns = [
        *HEADLINE_COLUMNS,
        "coverage",
        "coverage_mc_se",
        "dataset_cluster_bootstrap_mc_se",
        "contributing_datasets",
        "successful_runs",
        "failed_runs",
        "attempted_runs",
        "noncovering_runs",
        "finite_interval_runs",
        "cluster_bootstrap_replicates",
        "cluster_bootstrap_seed",
    ]
    failed_counts = (
        failures.groupby(HEADLINE_COLUMNS, dropna=False).size()
        if not failures.empty
        else pd.Series(dtype="int64")
    )
    if successful.empty:
        rows = []
        for key, count in failed_counts.items():
            if not isinstance(key, tuple):
                key = (key,)
            row = dict(zip(HEADLINE_COLUMNS, key))
            row.update({
                "coverage": np.nan,
                "coverage_mc_se": np.nan,
                "dataset_cluster_bootstrap_mc_se": np.nan,
                "contributing_datasets": 0,
                "successful_runs": 0,
                "failed_runs": int(count),
                "attempted_runs": int(count),
                "noncovering_runs": 0,
                "finite_interval_runs": 0,
                "cluster_bootstrap_replicates": CLUSTER_BOOTSTRAPS,
                "cluster_bootstrap_seed": CLUSTER_BOOTSTRAP_SEED,
            })
            rows.append(row)
        return pd.DataFrame(rows, columns=columns)

    rows = []
    successful_keys = set()
    for key, group in successful.groupby(HEADLINE_COLUMNS, dropna=False, sort=True):
        if not isinstance(key, tuple):
            key = (key,)
        successful_keys.add(key)
        dataset_groups = {
            dataset: frame["ci_covers_truth"].to_numpy(dtype=float)
            for dataset, frame in group.groupby("dataset", sort=True)
        }
        coverage = float(group["ci_covers_truth"].mean())
        rng = np.random.RandomState(CLUSTER_BOOTSTRAP_SEED)
        datasets = list(dataset_groups)
        bootstrap_estimates = []
        if len(datasets) > 1:
            for _ in range(CLUSTER_BOOTSTRAPS):
                sampled = rng.choice(datasets, size=len(datasets), replace=True)
                sampled_values = [
                    dataset_groups[name]
                    for name in sampled
                ]
                bootstrap_estimates.append(
                    float(np.concatenate(sampled_values).mean())
                )
            cluster_se = float(np.std(bootstrap_estimates, ddof=1))
        else:
            cluster_se = np.nan
        row = dict(zip(HEADLINE_COLUMNS, key))
        row.update({
            "coverage": coverage,
            "coverage_mc_se": float(
                np.sqrt(coverage * (1.0 - coverage) / len(group))
            ),
            "dataset_cluster_bootstrap_mc_se": cluster_se,
            "contributing_datasets": len(datasets),
            "successful_runs": len(group),
            "failed_runs": 0,
            "attempted_runs": len(group),
            "noncovering_runs": int((~group["ci_covers_truth"]).sum()),
            "finite_interval_runs": int(group["ci_width"].count()),
            "cluster_bootstrap_replicates": CLUSTER_BOOTSTRAPS,
            "cluster_bootstrap_seed": CLUSTER_BOOTSTRAP_SEED,
        })
        if key in failed_counts.index:
            row["failed_runs"] = int(failed_counts.loc[key])
            row["attempted_runs"] += row["failed_runs"]
        rows.append(row)
    if not failures.empty:
        for key, count in failed_counts.items():
            if not isinstance(key, tuple):
                key = (key,)
            if key in successful_keys:
                continue
            row = dict(zip(HEADLINE_COLUMNS, key))
            row.update({
                "coverage": np.nan,
                "coverage_mc_se": np.nan,
                "dataset_cluster_bootstrap_mc_se": np.nan,
                "contributing_datasets": 0,
                "successful_runs": 0,
                "failed_runs": int(count),
                "attempted_runs": int(count),
                "noncovering_runs": 0,
                "finite_interval_runs": 0,
                "cluster_bootstrap_replicates": CLUSTER_BOOTSTRAPS,
                "cluster_bootstrap_seed": CLUSTER_BOOTSTRAP_SEED,
            })
            rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def _no_missing_sanity(
    successful: pd.DataFrame, failures: pd.DataFrame
) -> pd.DataFrame:
    sanity = successful.loc[
        successful["method"].eq("no_missing_sanity")
        & successful["trial"].lt(100)
    ]
    if sanity.empty:
        result = pd.DataFrame(columns=[
            "dataset", "estimand", "expected_runs", "coverage", "coverage_mc_se",
            "successful_runs", "failed_runs", "attempted_runs",
            "sanity_status",
        ])
    else:
        result = (
            sanity.groupby(["dataset", "estimand"], dropna=False, as_index=False)
            .agg(
                coverage=("ci_covers_truth", "mean"),
                coverage_mc_se=("ci_covers_truth", lambda values: float(
                    np.sqrt(values.mean() * (1.0 - values.mean()) / len(values))
                )),
                successful_runs=("run_key", "count"),
            )
        )
        result["expected_runs"] = 100
    if failures.empty:
        failed_counts = pd.Series(dtype="int64")
    else:
        sanity_failures = failures.loc[
            failures["method"].eq("no_missing_sanity")
            & failures["trial"].lt(100)
        ]
        failed_counts = sanity_failures.groupby(
            ["dataset", "estimand"], dropna=False
        ).size()
    result["failed_runs"] = 0
    result = result.set_index(["dataset", "estimand"])
    for key, count in failed_counts.items():
        if key in result.index:
            result.loc[key, "failed_runs"] += int(count)
        else:
            result.loc[key, ["coverage", "coverage_mc_se", "successful_runs"]] = [
                np.nan, np.nan, 0
            ]
            result.loc[key, "expected_runs"] = 100
            result.loc[key, "failed_runs"] = int(count)
    result = result.reset_index()
    result["successful_runs"] = result["successful_runs"].fillna(0).astype(int)
    result["failed_runs"] = result["failed_runs"].fillna(0).astype(int)
    result["attempted_runs"] = result["successful_runs"] + result["failed_runs"]
    result["sanity_status"] = np.select(
        [
            result["coverage"].isna(),
            result["successful_runs"].lt(100),
            ~result["coverage"].between(0.91, 0.99),
        ],
        ["not assessed", "incomplete", "sanity-failed"],
        default="sanity-passed",
    )
    return result.sort_values(["dataset", "estimand"]).reset_index(drop=True)


def write_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    sections = [
        ("Per-dataset coverage by mechanism, method, rate, estimand, m, and delta", "coverage"),
        ("Headline coverage pooled across datasets (dataset-cluster bootstrap SE)", "headline_coverage"),
        ("Mean interval width", "width"),
        ("Mean bias", "bias"),
        ("MNAR coverage by delta", "mnar_delta"),
        ("No-missing sanity coverage (sanity-failed outside 91-99%)", "no_missing_sanity"),
    ]
    markdown = ["# Rubin coverage benchmark tables", ""]
    latex = [
        "% Generated from saved raw.csv; no experiment was run by this table builder.",
        r"\section*{Rubin coverage benchmark tables}",
        "% Headline cluster bootstrap resamples datasets with replacement; 2,000 replicates, seed 42.",
    ]
    for heading, key in sections:
        frame = tables[key]
        markdown.extend([f"## {heading}", "", frame.to_markdown(index=False), ""])
        latex.extend([
            r"\subsection*{" + heading.replace("&", r"\&") + "}",
            _latex_table(frame),
        ])
    (output_dir / "rubin_coverage_tables.md").write_text(
        "\n".join(markdown), encoding="utf-8"
    )
    (output_dir / "rubin_coverage_tables.tex").write_text(
        "\n\n".join(latex) + "\n", encoding="utf-8"
    )


def _latex_escape(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in text)


def _latex_table(frame: pd.DataFrame) -> str:
    columns = len(frame.columns)
    alignment = "l" * columns
    header = " & ".join(_latex_escape(value) for value in frame.columns) + r" \\"
    body = [
        " & ".join(_latex_escape(value) for value in row) + r" \\"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\hline",
        header,
        r"\hline",
        *body,
        r"\hline",
        r"\end{tabular}",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    tables = summarize(args.input_dir)
    write_tables(tables, args.out_dir or args.input_dir)
    print(f"Wrote coverage, width/bias, and MNAR-delta tables to {args.out_dir or args.input_dir}")


if __name__ == "__main__":
    main()
