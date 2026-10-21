"""Create reproducible real-dataset tables from one or more saved benchmark runs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from tabulate import tabulate

from common import holm_adjust
from datasets.registry import DATASETS, MANIFEST_PATH, NUMERIC_STRING_COLUMNS
from run_real_datasets import METHODS, _significance_a, _significance_b


PROTECTED_RUN_NAME = "paper_run_2026-10-11"
PROJECT_METHOD = "mice_multiple_NEW"
BASELINE_METHODS = tuple(method for method in METHODS if method != PROJECT_METHOD)
CATEGORICAL_METRIC_CAVEAT = (
    "harness ordinal-encoding adapter; not production behavior "
    "(production uses mode fallback); not for headline claims"
)
MNAR_COVERAGE_LABEL = "nominal 0.90"


def _read_saved(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Saved benchmark CSV is missing: {path}")
    return pd.read_csv(path)


def _write_tables(frame: pd.DataFrame, name: str, output_dir: Path, caption: str) -> None:
    if name.startswith("protocol_b_"):
        caption = f"{caption}\n\nNote: {_negligible_missingness_note()}"
    markdown = (
        f"# {name.replace('_', ' ').title()}\n\n{caption}\n\n"
        f"{frame.to_markdown(index=False, tablefmt='github')}\n"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{name}.md").write_text(markdown, encoding="utf-8")
    latex_table = tabulate(
        frame, headers="keys", tablefmt="latex", showindex=False, floatfmt=".6g"
    )
    latex = (
        "\\begin{table}[ht]\n\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{tab:{name}}}\n"
        f"{latex_table}\n"
        "\\end{table}\n"
    )
    (output_dir / f"{name}.tex").write_text(latex, encoding="utf-8")


def _write_versioned_table(
    frame: pd.DataFrame,
    name: str,
    output_dir: Path,
    caption: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_dir / f"{name}.csv", index=False)
    _write_tables(frame, name, output_dir, caption)


def _with_categorical_caveat(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    categorical_columns = [
        column for column in result
        if "categorical" in column.lower()
    ]
    if "metric" in result:
        categorical_rows = result["metric"].astype(str).str.contains(
            "categorical", case=False, na=False
        )
        result["categorical_metric_caveat"] = np.where(
            categorical_rows, CATEGORICAL_METRIC_CAVEAT, ""
        )
    elif categorical_columns:
        result["categorical_metric_caveat"] = CATEGORICAL_METRIC_CAVEAT
    return result


def _with_coverage_label(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if "mechanism" in result and "uncertainty_coverage90_numeric" in result:
        result["coverage_nominal_target"] = MNAR_COVERAGE_LABEL
    return result


def _negligible_missingness_note() -> str:
    names = sorted(
        name for name, spec in DATASETS.items()
        if spec.natural_missing_fraction < 0.01
    )
    return (
        "Datasets with <1% natural missingness (negligible natural missingness): "
        + ", ".join(names)
        + "."
    )


def _add_rmse_ratio_vs_mean(frame: pd.DataFrame) -> pd.DataFrame:
    """Add trial-matched method RMSE divided by its mean-imputer RMSE."""
    result = frame.copy()
    match_columns = ["dataset", "mechanism", "mask_rate", "trial"]
    required = {*match_columns, "method", "numeric_rmse"}
    missing = required.difference(result.columns)
    if missing:
        raise ValueError(f"Protocol A CSV is missing required columns: {sorted(missing)}.")
    means = result.loc[result["method"].eq("mean"), match_columns + ["numeric_rmse"]]
    if means.duplicated(match_columns).any():
        raise ValueError("Protocol A CSV has duplicate mean-imputer rows for a trial cell.")
    means = means.rename(columns={"numeric_rmse": "_mean_numeric_rmse"})
    result = result.merge(means, on=match_columns, how="left", validate="many_to_one")
    denominator = result.pop("_mean_numeric_rmse")
    valid = denominator.notna() & denominator.ne(0)
    result["rmse_ratio_vs_mean"] = np.nan
    result.loc[valid, "rmse_ratio_vs_mean"] = (
        result.loc[valid, "numeric_rmse"] / denominator.loc[valid]
    )
    return result


def _concat_unique(
    frames: list[pd.DataFrame], keys: list[str], label: str
) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return pd.DataFrame()
    combined = pd.concat(nonempty, ignore_index=True)
    duplicates = combined.duplicated(keys, keep=False)
    if duplicates.any():
        examples = combined.loc[duplicates, keys].head(8).to_dict("records")
        raise ValueError(f"Duplicate {label} keys {keys}: {examples}")
    return combined


def _merge_summaries(frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return pd.DataFrame()
    all_rows = pd.concat(nonempty, ignore_index=True)
    merged: list[pd.Series] = []
    for _, group in all_rows.groupby("name", sort=False):
        loaded = group.loc[group["load_status"].eq("loaded")]
        row = (loaded if not loaded.empty else group).iloc[-1].copy()
        failed = group.loc[group["load_status"].ne("loaded")]
        attempts = []
        for _, attempt in failed.iterrows():
            source = str(attempt.get("source_dir", ""))
            error_columns = [
                column for column in attempt.index
                if (
                    "error" in column.lower()
                    or "failure_reason" in column.lower()
                )
                and pd.notna(attempt[column])
                and str(attempt[column]).strip()
            ]
            detail = "; ".join(
                f"{column}={attempt[column]}" for column in error_columns
            )
            status = str(attempt.get("load_status", "unknown"))
            attempts.append(
                f"{source}: load_status={status}"
                + (f"; {detail}" if detail else "")
            )
        row["attempts_log"] = " | ".join(attempts)
        for protocol, statuses in (
            ("protocol_a", ("completed", "skipped", "not_requested", "not_run")),
            (
                "protocol_b",
                ("completed", "skipped_no_natural_missingness", "not_requested", "not_run"),
            ),
        ):
            status_column = f"{protocol}_status"
            if status_column not in group:
                continue
            observed = group[status_column].astype(str)
            status = next(
                (candidate for candidate in statuses if observed.eq(candidate).any()),
                str(row[status_column]),
            )
            row[status_column] = status
            if status in {"skipped", "skipped_no_natural_missingness"}:
                reason_column = f"{protocol}_skip_reason"
                if reason_column in group:
                    reasons = group.loc[observed.eq(status), reason_column].dropna()
                    if not reasons.empty:
                        row[reason_column] = reasons.iloc[-1]
        for column in (
            "protocol_a_dropped_incomplete_columns",
            "protocol_a_dropped_constant_columns",
        ):
            if column in group and (
                pd.isna(row.get(column)) or row.get(column) == ""
            ):
                values = group[column].dropna()
                if not values.empty:
                    row[column] = values.iloc[-1]
        if "source_dir" not in row or pd.isna(row.get("source_dir")):
            row["source_dir"] = ""
        merged.append(row)
    return pd.DataFrame(merged).reset_index(drop=True)


def _study_labels(dataset: str, protocol: str) -> list[str]:
    labels: list[str] = []
    spec = DATASETS.get(dataset)
    if spec is None:
        return labels
    if dataset == "diabetes":
        labels.append(
            "sentinel-coded missingness (zeros treated as missing), not native NaN"
        )
    if protocol == "A" and dataset == "cylinder-bands":
        labels.append("marginal: 7 retained columns, 2 numeric")
    if protocol == "B" and spec.natural_missing_fraction < 0.01:
        labels.append("negligible natural missingness")
    return labels


def _negligible_missingness_datasets(datasets: object) -> str:
    names = sorted({str(name) for name in datasets})
    labeled = [
        name for name in names
        if name in DATASETS and DATASETS[name].natural_missing_fraction < 0.01
    ]
    return "; ".join(
        f"{name} (negligible natural missingness)" for name in labeled
    )


def _rules_summary_table(rules: dict[str, object]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    protocol_a = rules["protocol_a_headline"]
    protocol_b = rules["protocol_b_downstream_headline"]
    assert isinstance(protocol_a, dict) and isinstance(protocol_b, dict)
    for dataset, values in protocol_a["datasets"].items():
        rows.append({
            "protocol": "A",
            "dataset": dataset,
            "placement": "headline" if values["protocol_a_headline"] else "supplementary",
            "criterion": protocol_a["include_when"],
            "exclusion_reason": values["protocol_a_exclusion_reason"],
            "study_labels": "; ".join(values.get("study_labels", [])),
        })
    for dataset, values in protocol_b["datasets"].items():
        rows.append({
            "protocol": "B downstream",
            "dataset": dataset,
            "placement": (
                "headline" if values["protocol_b_downstream_headline"] else "supplementary"
            ),
            "criterion": protocol_b["exclude_when"],
            "exclusion_reason": values["protocol_b_downstream_exclusion_reason"],
            "study_labels": "; ".join(values.get("study_labels", [])),
        })
    rows.append({
        "protocol": "B held-out recovery",
        "dataset": "",
        "placement": "include all saved Protocol B datasets",
        "criterion": "include_all_protocol_b_datasets=true",
        "exclusion_reason": "",
        "study_labels": "",
    })
    return pd.DataFrame(rows)


def _write_results_pack(output_dir: Path) -> Path:
    table_names = [
        "rules_summary",
        "dataset_summary",
        "protocol_a_win_tie_loss_vs_best_baseline",
        "protocol_a_project_mice_nonwinning_cells",
        "protocol_a_project_mice_uncertainty",
        "protocol_a_headline",
        "protocol_a_dataset_level_significance",
        "protocol_b_downstream_headline",
        "protocol_b_heldout_recovery_all",
        "protocol_b_dataset_level_significance",
        "protocol_a_effect_sizes",
        "protocol_a_effect_sizes_by_dataset",
        "protocol_b_effect_sizes",
        "protocol_b_effect_sizes_by_dataset",
    ]
    sections = ["# Real-Dataset Benchmark Results Pack\n"]
    for name in table_names:
        csv_path = output_dir / f"{name}.csv"
        if not csv_path.is_file():
            raise FileNotFoundError(f"Results pack source CSV is missing: {csv_path}")
        frame = pd.read_csv(csv_path)
        sections.extend([
            f"## {name.replace('_', ' ').title()}\n",
            f"Source CSV: `{csv_path.name}`\n",
            frame.to_markdown(index=False, tablefmt="github"),
            "",
        ])
    pack_path = output_dir / "RESULTS_PACK.md"
    pack_path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return pack_path


def _uncertainty_distribution_table(
    uncertainty: pd.DataFrame, headline_names: set[str]
) -> pd.DataFrame:
    if uncertainty.empty:
        return pd.DataFrame()
    headline = uncertainty.loc[uncertainty["dataset"].isin(headline_names)]
    rows: list[dict[str, object]] = []
    for mechanism, group in headline.groupby("mechanism"):
        for metric in (
            "uncertainty_spearman_numeric",
            "uncertainty_coverage90_numeric",
        ):
            values = group[metric].dropna()
            if values.empty:
                continue
            rows.append({
                "mechanism": mechanism,
                "metric": metric,
                "n_headline_datasets": int(values.size),
                "minimum": float(values.min()),
                "median": float(values.median()),
                "maximum": float(values.max()),
                "coverage_target": (
                    MNAR_COVERAGE_LABEL
                    if metric.endswith("coverage90_numeric") else ""
                ),
            })
    return pd.DataFrame(rows)


def _write_headline_summary(output_dir: Path) -> Path:
    names = [
        "rules_summary",
        "dataset_summary",
        "protocol_a_win_tie_loss_vs_best_baseline",
        "protocol_a_effect_sizes",
        "protocol_a_dataset_level_significance",
        "protocol_a_project_mice_uncertainty_summary",
        "protocol_a_project_mice_uncertainty",
        "protocol_b_downstream_headline",
        "protocol_b_heldout_recovery_all",
        "protocol_b_effect_sizes",
        "protocol_b_dataset_level_significance",
    ]
    sections = ["# Real-Dataset Benchmark Headline Summary\n"]
    for name in names:
        path = output_dir / f"{name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Headline summary source CSV is missing: {path}")
        frame = pd.read_csv(path)
        if name == "rules_summary":
            columns = [
                "protocol", "dataset", "placement", "exclusion_reason", "study_labels"
            ]
            frame = frame[columns]
        elif name == "dataset_summary":
            columns = [
                "name", "n_rows", "n_numeric",
                "n_categorical", "natural_missing_fraction", "load_status",
                "protocol_a_status", "protocol_b_status", "source_dir",
                "study_labels",
            ]
            frame = frame[[column for column in columns if column in frame]]
        if "categorical_metric_caveat" in frame:
            frame = frame.drop(columns=["categorical_metric_caveat"])
        note = ""
        if name.startswith("protocol_b_"):
            note = f"Note: {_negligible_missingness_note()}\n"
        if name in {
            "protocol_a_dataset_level_significance",
            "protocol_b_dataset_level_significance",
            "protocol_b_downstream_headline",
            "protocol_b_heldout_recovery_all",
            "protocol_b_effect_sizes",
        }:
            note += (
                "Categorical metrics: harness ordinal-encoding adapter; not "
                "production behavior (production uses mode fallback); not for "
                "headline claims.\n"
            )
        if name in {
            "protocol_a_project_mice_uncertainty_summary",
            "protocol_a_project_mice_uncertainty",
        }:
            note = "Coverage target: nominal 0.90.\n"
        sections.extend([
            f"## {name.replace('_', ' ').title()}\n",
            f"Source CSV: `{path.name}`\n",
            note,
            frame.to_markdown(index=False, tablefmt="github"),
            "",
        ])
    destination = output_dir / "HEADLINE_SUMMARY.md"
    destination.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return destination


def _protocol_a_inclusion(summary: pd.DataFrame) -> dict[str, dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    placements: dict[str, dict[str, object]] = {}
    for _, row in summary.iterrows():
        name = str(row["name"])
        if name not in DATASETS or name not in manifest:
            continue
        if row.get("protocol_a_status") not in {"completed", "skipped"}:
            placements[name] = {
                "retained_complete_columns": None,
                "retained_numeric_columns": None,
                "retained_categorical_columns": None,
                "protocol_a_headline": False,
                "protocol_a_exclusion_reason": "no saved Protocol A result available",
                "study_labels": _study_labels(name, "A"),
            }
            continue
        spec = DATASETS[name]
        incomplete = set(json.loads(row.get("protocol_a_dropped_incomplete_columns", "[]") or "[]"))
        constant = set(json.loads(row.get("protocol_a_dropped_constant_columns", "[]") or "[]"))
        dropped = incomplete | constant
        feature_types = manifest[name].get("openml_feature_type_by_column", {})
        numeric_names = {
            column
            for column, kind in feature_types.items()
            if kind.lower() == "numeric"
            or column in NUMERIC_STRING_COLUMNS.get(name, ())
        }
        n_features = spec.n_numeric + spec.n_categorical
        retained_columns = max(0, n_features - len(dropped))
        retained_numeric = len(numeric_names.difference(dropped))
        retained_categorical = retained_columns - retained_numeric
        raw_skip_reason = row.get("protocol_a_skip_reason", "")
        reason = "" if pd.isna(raw_skip_reason) else str(raw_skip_reason)
        if not reason:
            if retained_columns < 5:
                reason = f"only {retained_columns} complete retained columns (<5)"
            elif retained_numeric < 2:
                reason = f"only {retained_numeric} retained numeric columns (<2)"
        placements[name] = {
            "retained_complete_columns": retained_columns,
            "retained_numeric_columns": retained_numeric,
            "retained_categorical_columns": retained_categorical,
            "protocol_a_headline": not reason,
            "protocol_a_exclusion_reason": reason,
            "study_labels": _study_labels(name, "A"),
        }
    return placements


def _protocol_b_inclusion(raw_b: pd.DataFrame) -> dict[str, dict[str, object]]:
    placements: dict[str, dict[str, object]] = {}
    groups = (
        {str(dataset): frame for dataset, frame in raw_b.groupby("dataset")}
        if not raw_b.empty
        else {}
    )
    for dataset in DATASETS:
        frame = groups.get(dataset)
        if frame is None:
            placements[dataset] = {
                "mean_imputer_accuracy": None,
                "protocol_b_downstream_headline": False,
                "protocol_b_downstream_exclusion_reason": "no saved Protocol B result available",
                "protocol_b_heldout_recovery_included": False,
                "study_labels": _study_labels(dataset, "B"),
            }
            continue
        mean_rows = (
            frame.loc[frame["method"].eq("mean"), "accuracy"].dropna()
            if "accuracy" in frame
            else pd.Series(dtype=float)
        )
        if mean_rows.empty:
            reason = "mean-imputer accuracy unavailable"
            mean_accuracy = np.nan
        else:
            mean_accuracy = float(mean_rows.mean())
            reason = (
                f"mean-imputer accuracy {mean_accuracy:.6g} >= 0.999 ceiling"
                if mean_accuracy >= 0.999
                else ""
            )
        placements[str(dataset)] = {
            "mean_imputer_accuracy": mean_accuracy,
            "protocol_b_downstream_headline": not reason,
            "protocol_b_downstream_exclusion_reason": reason,
            "protocol_b_heldout_recovery_included": True,
            "study_labels": _study_labels(str(dataset), "B"),
        }
    return placements


def _summarize_protocol_b(protocol_b: pd.DataFrame) -> pd.DataFrame:
    if protocol_b.empty:
        return pd.DataFrame()
    metric_columns = [
        column
        for column in (
            "accuracy",
            "auc",
            "rmse",
            "heldout_numeric_rmse",
            "heldout_categorical_accuracy",
            "heldout_categorical_error_rate",
        )
        if column in protocol_b
    ]
    return protocol_b.groupby(
        ["dataset", "task_type", "method"], as_index=False
    )[metric_columns].mean()


def _dataset_level_significance(
    protocol_a: pd.DataFrame, protocol_b: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    a_records: list[dict[str, object]] = []
    if not protocol_a.empty:
        for metric in ("numeric_rmse", "categorical_error_rate"):
            if metric not in protocol_a:
                continue
            per_dataset = (
                protocol_a.groupby(["dataset", "mechanism", "method"], as_index=False)[metric]
                .mean()
            )
            for mechanism, rows in per_dataset.groupby("mechanism"):
                pivot = rows.pivot(index="dataset", columns="method", values=metric)
                for baseline in BASELINE_METHODS:
                    if baseline not in pivot or PROJECT_METHOD not in pivot:
                        continue
                    pairs = pivot[[PROJECT_METHOD, baseline]].dropna()
                    n = len(pairs)
                    if n == 0:
                        continue
                    diff = pairs[PROJECT_METHOD] - pairs[baseline]
                    pvalue = (
                        float(stats.wilcoxon(diff).pvalue)
                        if n >= 2 and (diff != 0).any()
                        else (1.0 if n >= 2 else np.nan)
                    )
                    a_records.append({
                        "metric": metric,
                        "mechanism": mechanism,
                        "vs": baseline,
                        "n_datasets": n,
                        "low_power_n_lt_10": n < 10,
                        "mean_loss_diff": float(diff.mean()),
                        "p_value": pvalue,
                    })
    a_result = pd.DataFrame(a_records)
    if not a_result.empty:
        valid_p = a_result["p_value"].notna()
        a_result["p_holm"] = np.nan
        a_result.loc[valid_p, "p_holm"] = holm_adjust(
            a_result.loc[valid_p, "p_value"].to_numpy()
        )

    b_records: list[dict[str, object]] = []
    if not protocol_b.empty:
        metrics = (
            ("accuracy", True),
            ("rmse", False),
            ("heldout_numeric_rmse", False),
            ("heldout_categorical_error_rate", False),
        )
        for metric, higher_is_better in metrics:
            if metric not in protocol_b:
                continue
            values = protocol_b[["dataset", "method", metric]].copy()
            if higher_is_better:
                values["_loss"] = 1.0 - values[metric]
            else:
                values["_loss"] = values[metric]
            per_dataset = values.groupby(["dataset", "method"], as_index=False)["_loss"].mean()
            pivot = per_dataset.pivot(index="dataset", columns="method", values="_loss")
            for baseline in BASELINE_METHODS:
                if baseline not in pivot or PROJECT_METHOD not in pivot:
                    continue
                pairs = pivot[[PROJECT_METHOD, baseline]].dropna()
                n = len(pairs)
                if n == 0:
                    continue
                diff = pairs[PROJECT_METHOD] - pairs[baseline]
                pvalue = (
                    float(stats.wilcoxon(diff).pvalue)
                    if n >= 2 and (diff != 0).any()
                    else (1.0 if n >= 2 else np.nan)
                )
                b_records.append({
                    "metric": metric,
                    "vs": baseline,
                    "n_datasets": n,
                    "low_power_n_lt_10": n < 10,
                    "mean_loss_diff": float(diff.mean()),
                    "p_value": pvalue,
                })
    b_result = pd.DataFrame(b_records)
    if not b_result.empty:
        valid_p = b_result["p_value"].notna()
        b_result["p_holm"] = np.nan
        b_result.loc[valid_p, "p_holm"] = holm_adjust(
            b_result.loc[valid_p, "p_value"].to_numpy()
        )
    a_result = _with_categorical_caveat(a_result)
    b_result = _with_categorical_caveat(b_result)
    return (
        _add_power_transparency(a_result),
        _add_power_transparency(b_result),
    )


def _add_power_transparency(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    result = frame.copy()
    comparisons = int(result["p_value"].notna().sum())
    result["n_comparisons_in_holm_family"] = comparisons
    minimum_ps = []
    can_reach = []
    notes = []
    for n_value in result["n_datasets"]:
        n = int(n_value)
        minimum_p = min(1.0, 2.0 / (2**n)) if n >= 0 else np.nan
        attainable = bool(minimum_p * comparisons <= 0.05)
        minimum_ps.append(minimum_p)
        can_reach.append(attainable)
        notes.append(
            f"n={n}; p_min={minimum_p:.6g}; Holm m={comparisons}; "
            f"p_min*m={minimum_p * comparisons:.6g}; "
            + ("attainable" if attainable else "cannot reach 0.05")
            + "."
        )
    result["min_attainable_two_sided_exact_p"] = minimum_ps
    result["can_reach_0_05_after_holm"] = can_reach
    result["power_note"] = notes
    return result


def _relative_rmse_tables(protocol_a: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if protocol_a.empty:
        return pd.DataFrame(), pd.DataFrame()
    ratios = _add_rmse_ratio_vs_mean(protocol_a)
    cell_keys = ["dataset", "mechanism", "mask_rate"]
    records: list[dict[str, object]] = []
    nonwins: list[dict[str, object]] = []
    for key, cell in ratios.groupby(cell_keys):
        method_ratio = cell.groupby("method")["rmse_ratio_vs_mean"].mean().dropna()
        baseline_ratios = method_ratio.reindex(BASELINE_METHODS).dropna()
        if baseline_ratios.empty:
            continue
        best_baseline = str(baseline_ratios.idxmin())
        best_ratio = float(baseline_ratios.min())
        for method, ratio in method_ratio.items():
            if ratio < best_ratio * 0.99:
                result = "win"
            elif ratio <= best_ratio * 1.01:
                result = "tie"
            else:
                result = "loss"
            records.append({
                **dict(zip(cell_keys, key)),
                "method": method,
                "best_baseline": best_baseline,
                "method_rmse_ratio_vs_mean": float(ratio),
                "best_baseline_rmse_ratio_vs_mean": best_ratio,
                "result": result,
            })
        project_ratio = method_ratio.get(PROJECT_METHOD, np.nan)
        if not np.isfinite(project_ratio) or project_ratio >= best_ratio * 0.99:
            nonwins.append({
                **dict(zip(cell_keys, key)),
                "project_mice_rmse_ratio_vs_mean": project_ratio,
                "best_baseline": best_baseline,
                "best_baseline_rmse_ratio_vs_mean": best_ratio,
                "result": (
                    "tie_within_1_percent"
                    if np.isfinite(project_ratio) and project_ratio <= best_ratio * 1.01
                    else "loss"
                ),
            })
    if not records:
        return pd.DataFrame(), pd.DataFrame(nonwins)
    outcomes = pd.DataFrame(records)
    counts = (
        outcomes.groupby(["method", "result"]).size().unstack(fill_value=0)
        .reindex(columns=["win", "tie", "loss"], fill_value=0)
        .reset_index()
    )
    return counts, pd.DataFrame(nonwins)


def _uncertainty_table(protocol_a: pd.DataFrame) -> pd.DataFrame:
    if protocol_a.empty:
        return pd.DataFrame()
    mice = protocol_a.loc[protocol_a["method"].eq(PROJECT_METHOD)]
    metrics = [
        column
        for column in (
            "uncertainty_spearman_numeric",
            "uncertainty_coverage90_numeric",
        )
        if column in mice
    ]
    result = mice.groupby(["dataset", "mechanism"], as_index=False)[metrics].mean()
    return _with_coverage_label(result)


def _holm_per_metric_sensitivity(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "p_value" not in frame:
        return frame.copy()
    result = frame.copy()
    result["p_holm"] = np.nan
    for _, indexes in result.groupby("metric", dropna=False).groups.items():
        valid = result.loc[indexes, "p_value"].notna()
        valid_indexes = result.loc[indexes].index[valid]
        if len(valid_indexes):
            result.loc[valid_indexes, "p_holm"] = holm_adjust(
                result.loc[valid_indexes, "p_value"].to_numpy()
            )
    result["holm_sensitivity_label"] = (
        "post-hoc sensitivity, family definition chosen after seeing results"
    )
    return _add_power_transparency(result)


def _scoreable_protocol_a_cell_count(protocol_a: pd.DataFrame) -> int:
    if protocol_a.empty:
        return 0
    rows = protocol_a.loc[protocol_a["method"].eq("mean")]
    if rows.empty:
        return 0
    cells = ["dataset", "mechanism", "mask_rate"]
    return int(
        rows.groupby(cells)["numeric_rmse"]
        .apply(lambda values: bool(values.notna().any()))
        .sum()
    )


def _select_protocol_b_significance_input(
    protocol_b: pd.DataFrame, headline_names: set[str]
) -> pd.DataFrame:
    selected = protocol_b.copy()
    non_headline = ~selected["dataset"].isin(headline_names)
    for metric in ("accuracy", "auc", "rmse"):
        if metric in selected:
            selected.loc[non_headline, metric] = np.nan
    return selected


def _bootstrap_median_ci(
    values: np.ndarray, seed: int = 42, n_resamples: int = 10_000
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(n_resamples, len(values)), replace=True)
    medians = np.median(samples, axis=1)
    low, high = np.percentile(medians, [2.5, 97.5])
    return float(low), float(high)


def _effect_size_tables(
    protocol_a: pd.DataFrame, protocol_b: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}

    if not protocol_a.empty and "numeric_rmse" in protocol_a:
        ratios = _add_rmse_ratio_vs_mean(protocol_a)
        per_dataset = (
            ratios.groupby(["dataset", "mechanism", "method"], as_index=False)
            ["rmse_ratio_vs_mean"].median()
        )
        details: list[dict[str, object]] = []
        summaries: list[dict[str, object]] = []
        for mechanism, mechanism_rows in per_dataset.groupby("mechanism"):
            pivot = mechanism_rows.pivot(
                index="dataset", columns="method", values="rmse_ratio_vs_mean"
            )
            for baseline in BASELINE_METHODS:
                if baseline not in pivot or PROJECT_METHOD not in pivot:
                    continue
                pairs = pivot[[PROJECT_METHOD, baseline]].dropna()
                effects = pairs[PROJECT_METHOD] - pairs[baseline]
                better = effects < -0.01 * pairs[baseline].abs().clip(lower=1e-12)
                worse = effects > 0.01 * pairs[baseline].abs().clip(lower=1e-12)
                tie = ~(better | worse)
                for dataset, row in pairs.iterrows():
                    details.append({
                        "dataset": dataset,
                        "mechanism": mechanism,
                        "vs": baseline,
                        "project_mice_median_rmse_ratio_vs_mean": float(row[PROJECT_METHOD]),
                        "baseline_median_rmse_ratio_vs_mean": float(row[baseline]),
                        "project_minus_baseline_ratio": float(
                            row[PROJECT_METHOD] - row[baseline]
                        ),
                        "outcome": (
                            "better" if better.loc[dataset]
                            else "worse" if worse.loc[dataset]
                            else "tie_within_1_percent"
                        ),
                    })
                ci_low, ci_high = _bootstrap_median_ci(effects.to_numpy())
                summaries.append({
                    "mechanism": mechanism,
                    "vs": baseline,
                    "n_datasets": len(effects),
                    "median_project_minus_baseline_ratio": float(effects.median()),
                    "bootstrap_95_ci_low": ci_low,
                    "bootstrap_95_ci_high": ci_high,
                    "datasets_project_better": int(better.sum()),
                    "datasets_project_worse": int(worse.sum()),
                    "datasets_tied_within_1_percent": int(tie.sum()),
                })
        tables["protocol_a_effect_sizes_by_dataset"] = pd.DataFrame(details)
        tables["protocol_a_effect_sizes"] = pd.DataFrame(summaries)

    if not protocol_b.empty:
        directions = {
            "accuracy": "higher",
            "auc": "higher",
            "rmse": "lower",
            "heldout_numeric_rmse": "lower",
            "heldout_categorical_accuracy": "higher",
            "heldout_categorical_error_rate": "lower",
        }
        b_detail_rows: list[dict[str, object]] = []
        b_summary_rows: list[dict[str, object]] = []
        for metric, direction in directions.items():
            if metric not in protocol_b:
                continue
            per_dataset = (
                protocol_b.groupby(["dataset", "method"], as_index=False)[metric]
                .mean()
            )
            pivot = per_dataset.pivot(index="dataset", columns="method", values=metric)
            for baseline in BASELINE_METHODS:
                if baseline not in pivot or PROJECT_METHOD not in pivot:
                    continue
                pairs = pivot[[PROJECT_METHOD, baseline]].dropna()
                differences = pairs[PROJECT_METHOD] - pairs[baseline]
                if direction == "higher":
                    better = differences > 0.01 * pairs[baseline].abs().clip(lower=1e-12)
                    worse = differences < -0.01 * pairs[baseline].abs().clip(lower=1e-12)
                else:
                    better = differences < -0.01 * pairs[baseline].abs().clip(lower=1e-12)
                    worse = differences > 0.01 * pairs[baseline].abs().clip(lower=1e-12)
                tie = ~(better | worse)
                for dataset, row in pairs.iterrows():
                    difference = float(row[PROJECT_METHOD] - row[baseline])
                    b_detail_rows.append({
                        "dataset": dataset,
                        "study_labels": "; ".join(
                            _study_labels(str(dataset), "B")
                        ),
                        "metric": metric,
                        "metric_direction": direction,
                        "vs": baseline,
                        "project_mice_mean_metric": float(row[PROJECT_METHOD]),
                        "baseline_mean_metric": float(row[baseline]),
                        "project_minus_baseline_metric": difference,
                        "outcome": (
                            "better" if better.loc[dataset]
                            else "worse" if worse.loc[dataset]
                            else "tie_within_1_percent"
                        ),
                    })
                ci_low, ci_high = _bootstrap_median_ci(differences.to_numpy())
                b_summary_rows.append({
                    "metric": metric,
                    "metric_direction": direction,
                    "vs": baseline,
                    "n_datasets": len(differences),
                    "median_project_minus_baseline_metric": float(differences.median()),
                    "bootstrap_95_ci_low": ci_low,
                    "bootstrap_95_ci_high": ci_high,
                    "datasets_project_better": int(better.sum()),
                    "datasets_project_worse": int(worse.sum()),
                    "datasets_tied_within_1_percent": int(tie.sum()),
                })
        tables["protocol_b_effect_sizes_by_dataset"] = pd.DataFrame(b_detail_rows)
        tables["protocol_b_effect_sizes"] = pd.DataFrame(b_summary_rows)
    return tables


def build_tables(
    input_dirs: Path | list[Path],
    output_dir: Path | None = None,
) -> Path:
    if isinstance(input_dirs, Path):
        input_dirs = [input_dirs]
    resolved_inputs = [path.expanduser().resolve() for path in input_dirs]
    if not resolved_inputs:
        raise ValueError("Provide at least one saved run directory.")
    for path in resolved_inputs:
        if PROTECTED_RUN_NAME in path.parts:
            raise ValueError(f"Refusing to read frozen evidence under {PROTECTED_RUN_NAME}.")
    output_dir = (output_dir or resolved_inputs[0] / "tables").expanduser().resolve()
    if PROTECTED_RUN_NAME in output_dir.parts:
        raise ValueError(f"Refusing to write inside frozen evidence under {PROTECTED_RUN_NAME}.")
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    protocol_a_frames = []
    protocol_b_frames = []
    for input_dir in resolved_inputs:
        summary_path = input_dir / "dataset_summary.csv"
        if summary_path.is_file():
            saved_summary = _read_saved(summary_path)
            try:
                saved_summary["source_dir"] = input_dir.relative_to(
                    output_dir.parent
                ).as_posix()
            except ValueError:
                saved_summary["source_dir"] = os.path.relpath(
                    input_dir, output_dir.parent
                )
            summaries.append(saved_summary)
        a_path = input_dir / "protocol_a_ground_truth.csv"
        if a_path.is_file():
            protocol_a_frames.append(_read_saved(a_path))
        b_path = input_dir / "protocol_b_natural_missingness.csv"
        if b_path.is_file():
            protocol_b_frames.append(_read_saved(b_path))

    summary = _merge_summaries(summaries)
    if not summary.empty:
        summary_by_name = summary.set_index("name")
        for name, spec in DATASETS.items():
            if name not in summary_by_name.index:
                summary = pd.concat(
                    [
                        summary,
                        pd.DataFrame([{
                            "name": name,
                            "source": spec.source,
                            "data_id": spec.data_id,
                            "version": spec.version,
                            "target_column": spec.target_column,
                            "task_type": spec.task_type,
                            "n_rows": spec.n_rows,
                            "n_numeric": spec.n_numeric,
                            "n_categorical": spec.n_categorical,
                            "natural_missing_fraction": spec.natural_missing_fraction,
                            "load_status": "not_run",
                            "protocol_a_status": "not_run",
                            "protocol_b_status": "not_run",
                            "load_failure_reason": "",
                            "source_dir": "",
                            "attempts_log": "No saved run output was supplied.",
                        }]),
                    ],
                    ignore_index=True,
                )
        summary = summary.drop_duplicates("name", keep="last")
        if set(summary["name"]) != set(DATASETS):
            raise ValueError("Merged dataset summary does not cover the full registry.")
        summary["natural_missing_fraction"] = summary["name"].map(
            {name: spec.natural_missing_fraction for name, spec in DATASETS.items()}
        )
        summary["study_labels"] = summary["name"].map(
            lambda name: "; ".join(_study_labels(str(name), "B"))
        )
        summary = summary.sort_values("name").reset_index(drop=True)
    protocol_a = _concat_unique(
        protocol_a_frames,
        ["dataset", "mechanism", "mask_rate", "trial", "method"],
        "Protocol A",
    )
    protocol_b = _concat_unique(
        protocol_b_frames,
        ["dataset", "repeat", "fold", "method"],
        "Protocol B",
    )
    placements_a = _protocol_a_inclusion(summary) if not summary.empty else {}
    placements_b = _protocol_b_inclusion(protocol_b)
    rules = {
        "protocol_a_headline": {
            "include_when": "retained_complete_columns >= 5 and retained_numeric_columns >= 2",
            "datasets": {
                name: values
                for name, values in placements_a.items()
            },
        },
        "protocol_b_downstream_headline": {
            "exclude_when": "mean-imputer accuracy >= 0.999",
            "datasets": placements_b,
        },
        "protocol_b_heldout_recovery": {
            "include_all_protocol_b_datasets": True,
        },
        "dataset_labels": {
            name: {
                "protocol_a": _study_labels(name, "A"),
                "protocol_b": _study_labels(name, "B"),
            }
            for name in DATASETS
        },
    }
    (output_dir / "rules.json").write_text(
        json.dumps(rules, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("Protocol A headline/supplementary placement:")
    for name, values in sorted(placements_a.items()):
        status = "headline" if values["protocol_a_headline"] else "supplementary"
        reason = values["protocol_a_exclusion_reason"] or "meets pre-declared thresholds"
        print(f"  {name}: {status} — {reason}")
    print("Protocol B downstream headline/supplementary placement:")
    for name, values in sorted(placements_b.items()):
        status = "headline" if values["protocol_b_downstream_headline"] else "supplementary"
        reason = values["protocol_b_downstream_exclusion_reason"] or "below accuracy ceiling"
        print(f"  {name}: {status} — {reason}")
    print("Protocol B held-out-observed recovery: all loaded Protocol B datasets")

    if not summary.empty:
        if len(summary) != len(DATASETS):
            raise ValueError(
                f"Expected one summary row for each of {len(DATASETS)} datasets; "
                f"got {len(summary)}."
            )
        summary.to_csv(output_dir / "dataset_summary.csv", index=False)
        _write_tables(
            summary,
            "dataset_summary",
            output_dir,
            "Merged dataset metadata and run status read from saved run CSVs.",
        )
    a_headline_names = {
        name for name, values in placements_a.items() if values["protocol_a_headline"]
    }
    b_headline_names = {
        name
        for name, values in placements_b.items()
        if values["protocol_b_downstream_headline"]
    }
    a_headline_raw = protocol_a.loc[
        protocol_a["dataset"].isin(a_headline_names)
    ].copy()
    b_primary_input = _select_protocol_b_significance_input(
        protocol_b, b_headline_names
    )

    a_significance_all = (
        _significance_a(protocol_a) if not protocol_a.empty else pd.DataFrame()
    )
    b_significance_all = (
        _significance_b(protocol_b) if not protocol_b.empty else pd.DataFrame()
    )
    if not a_significance_all.empty:
        a_significance_all = _with_categorical_caveat(a_significance_all)
        _write_tables(
            a_significance_all,
            "protocol_a_pooled_significance",
            output_dir,
            "Existing paired tests pooled across trials/rates within dataset-mechanism; not dataset-level generalization tests. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )
    if not b_significance_all.empty:
        b_significance_all = _with_categorical_caveat(b_significance_all)
        if "dataset" in b_significance_all:
            b_significance_all["study_labels"] = b_significance_all["dataset"].map(
                lambda name: "; ".join(_study_labels(str(name), "B"))
            )
        _write_tables(
            b_significance_all,
            "protocol_b_pooled_significance",
            output_dir,
            "Existing paired tests pooled across repeated folds within dataset; not dataset-level generalization tests. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )

    dataset_a_significance_all, dataset_b_significance_all = _dataset_level_significance(
        protocol_a, protocol_b
    )
    dataset_a_significance, _ = _dataset_level_significance(
        a_headline_raw, pd.DataFrame()
    )
    _, dataset_b_significance = _dataset_level_significance(
        pd.DataFrame(), b_primary_input
    )
    if not dataset_a_significance_all.empty:
        _write_versioned_table(
            dataset_a_significance_all,
            "protocol_a_dataset_level_significance_all_datasets_supplementary",
            output_dir,
            "Supplementary all-dataset Protocol A significance; includes datasets outside the pre-declared headline set.",
        )
    if not dataset_b_significance_all.empty:
        _write_versioned_table(
            dataset_b_significance_all,
            "protocol_b_dataset_level_significance_all_datasets_supplementary",
            output_dir,
            "Supplementary all-dataset Protocol B significance; downstream and held-out outcomes include all available datasets.",
        )
    if not dataset_a_significance.empty:
        dataset_a_significance = _with_categorical_caveat(dataset_a_significance)
        _write_versioned_table(
            dataset_a_significance,
            "protocol_a_dataset_level_significance",
            output_dir,
            "Primary Protocol A significance restricted to the ten pre-declared headline datasets. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )
        _write_versioned_table(
            _holm_per_metric_sensitivity(dataset_a_significance),
            "protocol_a_dataset_level_significance_holm_per_metric_sensitivity",
            output_dir,
            "Post-hoc sensitivity, family definition chosen after seeing results: Holm correction applied separately by metric; primary family unchanged.",
        )
        cannot_reach = dataset_a_significance.loc[
            ~dataset_a_significance["can_reach_0_05_after_holm"]
        ]
        low_power = dataset_a_significance.loc[
            dataset_a_significance["low_power_n_lt_10"]
        ]
        print(
            "Protocol A dataset-level tests unable to reach 0.05 after Holm: "
            f"{len(cannot_reach)}/{len(dataset_a_significance)}; "
            "the exact signed-rank p-value floor times the Holm family size exceeds 0.05."
        )
        print(
            "Protocol A low-power (<10 datasets) comparisons "
            f"{len(low_power)}/{len(dataset_a_significance)} "
            "(mechanism, metric, baseline, n):"
        )
        for _, test in low_power.iterrows():
            print(
                f"  {test.get('mechanism', '')} / {test['metric']} vs {test['vs']}: "
                f"n={int(test['n_datasets'])}"
            )
    if not dataset_b_significance.empty:
        dataset_b_significance = _with_categorical_caveat(dataset_b_significance)
        _write_versioned_table(
            dataset_b_significance,
            "protocol_b_dataset_level_significance",
            output_dir,
            "Primary Protocol B downstream significance is restricted to the pre-declared headline set; held-out recovery significance includes all saved Protocol B datasets. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )
        _write_versioned_table(
            _holm_per_metric_sensitivity(dataset_b_significance),
            "protocol_b_dataset_level_significance_holm_per_metric_sensitivity",
            output_dir,
            "Post-hoc sensitivity, family definition chosen after seeing results: Holm correction applied separately by metric; primary family unchanged.",
        )
        cannot_reach = dataset_b_significance.loc[
            ~dataset_b_significance["can_reach_0_05_after_holm"]
        ]
        print(
            "Protocol B dataset-level tests unable to reach 0.05 after Holm: "
            f"{len(cannot_reach)}/{len(dataset_b_significance)}; "
            "the exact signed-rank p-value floor times the Holm family size exceeds 0.05."
        )

    if not protocol_a.empty:
        protocol_a = _add_rmse_ratio_vs_mean(protocol_a)
        a_supplementary_names = set(placements_a).difference(a_headline_names)
        for table_name, names in (
            ("protocol_a_headline", a_headline_names),
            ("protocol_a_supplementary", a_supplementary_names),
        ):
            table = protocol_a.loc[protocol_a["dataset"].isin(names)].copy()
            table["study_labels"] = table["dataset"].map(
                lambda name: "; ".join(_study_labels(str(name), "A"))
            )
            table["exclusion_reason"] = table["dataset"].map(
                lambda name: placements_a.get(name, {}).get(
                    "protocol_a_exclusion_reason", ""
                )
            )
            if not table.empty:
                grouped = table.groupby(
                    ["dataset", "mechanism", "mask_rate", "method"], as_index=False
                ).agg(
                    numeric_rmse=("numeric_rmse", "mean"),
                    rmse_ratio_vs_mean=("rmse_ratio_vs_mean", "mean"),
                    categorical_error_rate=("categorical_error_rate", "mean"),
                    uncertainty_spearman_numeric=("uncertainty_spearman_numeric", "mean"),
                    uncertainty_coverage90_numeric=("uncertainty_coverage90_numeric", "mean"),
                    repeats=("trial", "nunique"),
                    exclusion_reason=("exclusion_reason", "first"),
                    study_labels=("study_labels", "first"),
                )
                grouped = _with_coverage_label(_with_categorical_caveat(grouped))
                grouped.to_csv(output_dir / f"{table_name}.csv", index=False)
                _write_tables(
                    grouped,
                    table_name,
                    output_dir,
                    "Protocol A results from saved CSVs; inclusion follows pre-declared column-count rules. Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims. MNAR coverage is labeled nominal 0.90.",
                )
        a_headline = protocol_a.loc[
            protocol_a["dataset"].isin(a_headline_names)
        ].copy()
        counts_all, nonwins_all = _relative_rmse_tables(protocol_a)
        counts_primary, nonwins_primary = _relative_rmse_tables(a_headline)
        wtl_caption = (
            "For each dataset × mechanism × mask-rate cell, the best conventional "
            "baseline is the lowest mean-imputer-relative numeric RMSE among mean, "
            "median, KNN5, and single IterativeImputer. Each listed method is "
            "compared with that best baseline: win means >1% lower RMSE, tie means "
            "within 1%, and loss means >1% higher RMSE."
        )
        if not counts_all.empty:
            _write_versioned_table(
                counts_all,
                "protocol_a_win_tie_loss_vs_best_baseline_all_datasets_supplementary",
                output_dir,
                "Supplementary all-dataset outcomes. " + wtl_caption,
            )
        if not nonwins_all.empty:
            _write_versioned_table(
                nonwins_all,
                "protocol_a_project_mice_nonwinning_cells_all_datasets_supplementary",
                output_dir,
                "Supplementary all-dataset non-winning cells. " + wtl_caption,
            )
        if not counts_primary.empty:
            _write_versioned_table(
                counts_primary,
                "protocol_a_win_tie_loss_vs_best_baseline",
                output_dir,
                "Primary headline-dataset outcomes. " + wtl_caption,
            )
        _write_versioned_table(
            nonwins_primary,
            "protocol_a_project_mice_nonwinning_cells",
            output_dir,
            "Primary headline-dataset non-winning cells. " + wtl_caption,
        )
        uncertainty_all = _uncertainty_table(protocol_a)
        uncertainty_primary = uncertainty_all.loc[
            uncertainty_all["dataset"].isin(a_headline_names)
        ].copy()
        uncertainty_caveat = (
            "Categorical metrics are not included in this numeric uncertainty table. "
            "Coverage is assessed against the nominal 0.90 interval target."
        )
        _write_versioned_table(
            uncertainty_all,
            "protocol_a_project_mice_uncertainty_all_datasets_supplementary",
            output_dir,
            "Supplementary all-dataset uncertainty metrics. " + uncertainty_caveat,
        )
        _write_versioned_table(
            uncertainty_primary,
            "protocol_a_project_mice_uncertainty",
            output_dir,
            "Primary uncertainty metrics restricted to Protocol A headline datasets. "
            + uncertainty_caveat,
        )
        uncertainty_summary = _uncertainty_distribution_table(
            uncertainty_primary, a_headline_names
        )
        _write_versioned_table(
            uncertainty_summary,
            "protocol_a_project_mice_uncertainty_summary",
            output_dir,
            "Per-mechanism min/median/max across Protocol A headline datasets. Coverage assesses the nominal 0.90 interval target.",
        )
        print(
            "Protocol A headline win/tie/loss scoreable cell count:",
            _scoreable_protocol_a_cell_count(a_headline),
        )

    if not protocol_b.empty:
        b_summary = _summarize_protocol_b(protocol_b)
        b_summary["study_labels"] = b_summary["dataset"].map(
            lambda name: "; ".join(_study_labels(str(name), "B"))
        )
        b_summary["exclusion_reason"] = b_summary["dataset"].map(
            lambda name: placements_b.get(name, {}).get(
                "protocol_b_downstream_exclusion_reason", ""
            )
        )
        b_headline = b_summary.loc[
            b_summary["dataset"].map(
                lambda name: placements_b.get(name, {}).get(
                    "protocol_b_downstream_headline", False
                )
            )
        ]
        b_supplementary = b_summary.loc[
            ~b_summary["dataset"].map(
                lambda name: placements_b.get(name, {}).get(
                    "protocol_b_downstream_headline", False
                )
            )
        ]
        for frame, name in (
            (b_headline, "protocol_b_downstream_headline"),
            (b_supplementary, "protocol_b_downstream_supplementary"),
        ):
            if not frame.empty:
                frame = _with_categorical_caveat(frame)
                frame.to_csv(output_dir / f"{name}.csv", index=False)
                _write_tables(
                    frame,
                    name,
                    output_dir,
                    "Protocol B downstream performance; ceiling-rule exclusions are supplementary. Categorical held-out metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
                )
        recovery = b_summary.copy()
        recovery["exclusion_reason"] = ""
        recovery = _with_categorical_caveat(recovery)
        recovery.to_csv(output_dir / "protocol_b_heldout_recovery_all.csv", index=False)
        _write_tables(
            recovery,
            "protocol_b_heldout_recovery_all",
            output_dir,
            "Held-out-observed natural-missingness recovery; includes all Protocol B datasets, including ceiling datasets. Categorical held-out metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )

    effects_all = _effect_size_tables(protocol_a, protocol_b)
    effects_a_primary = _effect_size_tables(a_headline_raw, pd.DataFrame())
    effects_b_headline = _effect_size_tables(
        pd.DataFrame(),
        protocol_b.loc[protocol_b["dataset"].isin(b_headline_names)].copy(),
    )
    effect_tables_primary = dict(effects_a_primary)
    for suffix in ("protocol_b_effect_sizes", "protocol_b_effect_sizes_by_dataset"):
        all_effect = effects_all.get(suffix, pd.DataFrame())
        headline_effect = effects_b_headline.get(suffix, pd.DataFrame())
        if not all_effect.empty and not headline_effect.empty:
            heldout_all = all_effect["metric"].astype(str).str.startswith("heldout_")
            heldout_headline = headline_effect["metric"].astype(str).str.startswith("heldout_")
            effect_tables_primary[suffix] = pd.concat(
                [
                    headline_effect.loc[~heldout_headline],
                    all_effect.loc[heldout_all],
                ],
                ignore_index=True,
            )
        elif not all_effect.empty:
            effect_tables_primary[suffix] = all_effect.loc[
                all_effect["metric"].astype(str).str.startswith("heldout_")
            ].copy()
        elif not headline_effect.empty:
            effect_tables_primary[suffix] = headline_effect.loc[
                ~headline_effect["metric"].astype(str).str.startswith("heldout_")
            ].copy()

    for name, table in effects_all.items():
        table = _with_categorical_caveat(table)
        _write_versioned_table(
            table,
            f"{name}_all_datasets_supplementary",
            output_dir,
            "Supplementary all-dataset effect sizes from saved CSVs. "
            "Percentile bootstrap intervals use 10,000 dataset-level resamples with seed 42. "
            "Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )
    for name, table in effect_tables_primary.items():
        table = _with_categorical_caveat(table)
        _write_versioned_table(
            table,
            name,
            output_dir,
            "Primary headline-set effect sizes from saved CSVs. Held-out recovery includes all Protocol B datasets. "
            "Percentile bootstrap intervals use 10,000 dataset-level resamples with seed 42. "
            "Categorical metrics use the harness ordinal-encoding adapter; not production behavior (production uses mode fallback); not for headline claims.",
        )

    for protocol_name, tests in (
        ("Protocol A", dataset_a_significance),
        ("Protocol B", dataset_b_significance),
    ):
        print(f"{protocol_name} primary dataset-level test power details:")
        for _, test in tests.iterrows():
            group = f"{test.get('mechanism', '')} " if "mechanism" in test else ""
            print(
                f"  {group}{test['metric']} vs {test['vs']}: "
                f"n={int(test['n_datasets'])}, "
                f"min_p={test['min_attainable_two_sided_exact_p']:.6g}, "
                f"can_reach_0_05_after_holm={bool(test['can_reach_0_05_after_holm'])}"
            )

    rules_summary = _rules_summary_table(rules)
    rules_summary.to_csv(output_dir / "rules_summary.csv", index=False)
    _write_tables(
        rules_summary,
        "rules_summary",
        output_dir,
        "Table-time inclusion criteria and dataset labels from rules.json.",
    )

    _write_results_pack(output_dir)
    headline_summary = _write_headline_summary(output_dir)
    print(
        f"Headline summary: {headline_summary} "
        f"({headline_summary.stat().st_size} bytes)"
    )
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        required=True,
        nargs="+",
        type=Path,
        help="One or more completed run directories whose saved CSVs should be merged.",
    )
    parser.add_argument("--out", type=Path, help="Output directory for merged tables.")
    args = parser.parse_args()
    print(build_tables(args.input_dir, args.out))


if __name__ == "__main__":
    main()
