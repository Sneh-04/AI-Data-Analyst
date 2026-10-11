"""Build paper tables from the frozen benchmark CSV files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


EXPERIMENTS_DIR = Path(__file__).resolve().parent
RUN_DIR = EXPERIMENTS_DIR / "results" / "paper_run_2026-10-11"
TABLES_DIR = RUN_DIR / "tables"
IMPUTATION_DIR = RUN_DIR / "imputation"
FORECASTING_DIR = RUN_DIR / "forecasting"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required saved CSV is missing: {path}")
    return pd.read_csv(path)


def write_table(name: str, frame: pd.DataFrame, note: str) -> None:
    csv_path = TABLES_DIR / f"{name}.csv"
    markdown_path = TABLES_DIR / f"{name}.md"
    frame.to_csv(csv_path, index=False)
    markdown_path.write_text(
        f"# {name.replace('_', ' ').title()}\n\n{note}\n\n"
        f"{frame.to_markdown(index=False, tablefmt='github')}\n",
        encoding="utf-8",
    )


def holm_adjust(pvalues: list[float]) -> np.ndarray:
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p) - rank) * p[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def weighted_calibration_rows(raw: pd.DataFrame) -> pd.DataFrame:
    measured = raw.loc[raw["coverage90"].notna()].copy()
    if measured.empty:
        raise ValueError("Imputation CSV contains no measured coverage90 values.")

    def aggregate(group: pd.DataFrame, scope: str, dataset: str) -> dict:
        valid_coverage = group.loc[group["coverage90"].notna()]
        weights = valid_coverage["n_masked"].astype(float)
        coverage = np.average(valid_coverage["coverage90"], weights=weights)
        return {
            "scope": scope,
            "dataset": dataset,
            "mechanism": group["mechanism"].iloc[0],
            "method": group["method"].iloc[0],
            "coverage90": coverage,
            "uncertainty_spearman": group["uncertainty_spearman"].mean(),
            "masked_cells": int(weights.sum()),
            "run_count": int(len(valid_coverage)),
        }

    rows = []
    for (dataset, mechanism, method), group in measured.groupby(
        ["dataset", "mechanism", "method"], sort=True
    ):
        rows.append(aggregate(group, "dataset_mechanism", dataset))
    for (mechanism, method), group in measured.groupby(
        ["mechanism", "method"], sort=True
    ):
        rows.append(aggregate(group, "pooled_mechanism", "ALL"))
    return pd.DataFrame(rows).round(
        {"coverage90": 8, "uncertainty_spearman": 8}
    )


def build_imputation_tables() -> None:
    raw = read_csv(IMPUTATION_DIR / "imputation_raw.csv")
    rmse = (
        raw.groupby(["mechanism", "method"], as_index=False, sort=True)
        .agg(mean_rmse=("rmse", "mean"), datasets=("dataset", "nunique"), runs=("rmse", "count"))
        .round({"mean_rmse": 8})
    )
    write_table(
        "imputation_mean_rmse",
        rmse,
        "Mean trial-level RMSE from `imputation_raw.csv`, grouped by mechanism and method.",
    )

    significance = read_csv(IMPUTATION_DIR / "imputation_significance.csv")
    comparisons = significance.rename(columns={"vs": "method", "p_value": "p_raw"})[
        [
            "dataset",
            "mechanism",
            "method",
            "mean_rmse_diff",
            "new_wins",
            "pairs",
            "p_raw",
            "p_holm",
        ]
    ].copy()
    comparisons = comparisons.sort_values(
        ["dataset", "mechanism", "method"], kind="stable"
    ).round({"mean_rmse_diff": 8, "p_raw": 12, "p_holm": 12})
    write_table(
        "imputation_mice_comparisons",
        comparisons,
        "Paired MICE (`mice_multiple_NEW`) versus each baseline, taken from the saved "
        "`imputation_significance.csv`; negative `mean_rmse_diff` favors MICE.",
    )

    calibration = weighted_calibration_rows(raw)
    write_table(
        "imputation_uncertainty",
        calibration,
        "Dataset/mechanism rows summarize trials; pooled rows combine all datasets "
        "within each mechanism. `coverage90` is weighted by masked-cell count: "
        "sum(coverage90 × n_masked) / sum(n_masked). `uncertainty_spearman` is the "
        "unweighted mean across runs with a measured value. Coverage and uncertainty "
        "are reported for methods whose source rows contain those metrics.",
    )


def build_forecasting_tables() -> None:
    raw = read_csv(FORECASTING_DIR / "forecasting_raw.csv")
    scored = raw.loc[raw["mase"].notna()].copy()

    def model_row(method: str, group: pd.DataFrame) -> dict:
        return {
            "method": method,
            "mean_mase": group["mase"].mean(),
            "n_series": int(group["series"].nunique()),
            "evaluation_windows": int(len(group)),
        }

    summary = pd.DataFrame(
        [
            model_row(method, group)
            for method, group in scored.groupby("method", sort=False)
        ]
    ).sort_values("method", kind="stable")
    summary["mean_mase"] = summary["mean_mase"].round(8)
    write_table(
        "forecasting_mean_mase",
        summary,
        "Mean MASE and scored series/window counts from the saved `forecasting_raw.csv`. "
        "The oracle-best-fixed row is a reference bound, not a deployable model.",
    )

    pivot = scored.pivot(index=["series", "window"], columns="method", values="mase")
    alternatives = [
        method
        for method in pivot.columns
        if method not in {"auto", "oracle_best_fixed"}
    ]
    preferred_order = [
        "naive",
        "seasonal_naive",
        "holt",
        "arima",
        "sarima",
        "ensemble",
        "auto_legacy",
        "auto_no_shortlist",
        "auto_with_ensemble",
    ]
    alternatives.sort(
        key=lambda method: (
            preferred_order.index(method)
            if method in preferred_order
            else len(preferred_order),
            method,
        )
    )

    rows = []
    for method in alternatives:
        pair = pivot[["auto", method]].dropna()
        if pair.empty:
            raise ValueError(f"No paired Auto-versus-{method} MASE values in input CSV.")
        difference = pair["auto"] - pair[method]
        p_raw = (
            float(stats.wilcoxon(difference).pvalue)
            if (difference != 0).any()
            else 1.0
        )
        rows.append(
            {
                "model": method,
                "mean_mase_diff_auto_minus_model": float(difference.mean()),
                "auto_wins": int((difference < 0).sum()),
                "pairs": int(len(pair)),
                "n_series": int(pair.index.get_level_values("series").nunique()),
                "evaluation_windows": int(len(pair)),
                "p_raw": p_raw,
            }
        )
    comparisons = pd.DataFrame(rows)
    comparisons["p_holm"] = holm_adjust(comparisons["p_raw"].tolist())
    comparisons["p_holm_lt_0_05"] = comparisons["p_holm"] < 0.05
    comparisons = comparisons.round(
        {
            "mean_mase_diff_auto_minus_model": 8,
            "p_raw": 12,
            "p_holm": 12,
        }
    )
    write_table(
        "forecasting_auto_comparisons",
        comparisons,
        "Paired Wilcoxon signed-rank tests on series/window MASE differences "
        "(Auto minus model); negative differences favor Auto. Holm correction is "
        "applied across every scored non-oracle alternative method in this table. "
        "`p_holm_lt_0_05` marks the strict p_holm < 0.05 rule.",
    )


def compare_prior_imputation_run() -> None:
    current_path = IMPUTATION_DIR / "imputation_raw.csv"
    prior_path = EXPERIMENTS_DIR / "results" / "imputation_raw.csv"
    if not prior_path.is_file():
        (RUN_DIR / "imputation_prior_run_comparison.txt").write_text(
            "Prior raw imputation CSV not found; no numeric comparison was possible.\n",
            encoding="utf-8",
        )
        return

    current = read_csv(current_path)
    prior = read_csv(prior_path)
    keys = ["dataset", "mechanism", "rate", "trial", "method"]
    metrics = [
        column
        for column in ["rmse", "n_masked", "coverage90", "interval_width", "uncertainty_spearman"]
        if column in current.columns and column in prior.columns
    ]
    joined = current[keys + metrics].merge(
        prior[keys + metrics],
        on=keys,
        how="outer",
        suffixes=("_frozen", "_prior"),
        indicator=True,
        validate="one_to_one",
    )
    lines = [
        f"Frozen raw rows: {len(current)}",
        f"Prior raw rows: {len(prior)}",
        f"Rows with keys only in frozen run: {int((joined['_merge'] == 'left_only').sum())}",
        f"Rows with keys only in prior run: {int((joined['_merge'] == 'right_only').sum())}",
    ]
    both = joined.loc[joined["_merge"] == "both"]
    for metric in metrics:
        frozen = pd.to_numeric(both[f"{metric}_frozen"], errors="coerce").to_numpy()
        old = pd.to_numeric(both[f"{metric}_prior"], errors="coerce").to_numpy()
        equal = np.isclose(frozen, old, rtol=1e-12, atol=1e-15, equal_nan=True)
        finite = np.isfinite(frozen) & np.isfinite(old)
        max_abs_diff = (
            float(np.max(np.abs(frozen[finite] - old[finite]))) if finite.any() else 0.0
        )
        lines.append(
            f"{metric}: {int((~equal).sum())} differing matched rows; "
            f"maximum absolute finite difference={max_abs_diff:.12g}"
        )
    (RUN_DIR / "imputation_prior_run_comparison.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def audit_tables() -> None:
    problems = []
    for path in sorted(TABLES_DIR.glob("*.csv")):
        frame = pd.read_csv(path, keep_default_na=False)
        for row_index, row in frame.iterrows():
            for column, value in row.items():
                if value == "" or (
                    isinstance(value, str) and value.strip().lower() in {"nan", "na", "null"}
                ):
                    problems.append(f"{path.name}: row {row_index + 2}, column {column}")
    if problems:
        print("Blank/NaN cells in generated table CSVs:")
        print("\n".join(problems))
        raise ValueError("Generated tables contain blank/NaN cells.")
    print("Blank/NaN cells in generated table CSVs: none.")


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    build_imputation_tables()
    build_forecasting_tables()
    compare_prior_imputation_run()
    audit_tables()
    print(f"Tables written to {TABLES_DIR}")
    print((RUN_DIR / "imputation_prior_run_comparison.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
