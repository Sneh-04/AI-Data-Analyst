"""Write cellwise research tables and figures without aggregating study cells."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rubin_study.diagnostics import (
    paired_coverage_difference,
    summarize_no_missing_gate,
    summarize_pmm_donor_draws,
    variance_decomposition,
)
from rubin_study.evaluation import summarize_replicates


DEFAULT_CELL_FIELDS = (
    "dgp",
    "mechanism",
    "mask_rate",
    "mechanism_slope",
    "estimand",
    "method",
    "delta_sd",
)


def summarize_by_cell(
    records: Sequence[Mapping[str, Any]],
    cell_fields: Sequence[str] = DEFAULT_CELL_FIELDS,
) -> list[dict[str, Any]]:
    """Return one coverage/reliability/variance summary per observed cell."""
    if not records:
        raise ValueError("records must contain study replicates")
    fields = [field for field in cell_fields if any(field in row for row in records)]
    if not fields:
        raise ValueError("at least one requested cell field must exist in the records")
    groups: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in records:
        key = tuple(row.get(field) for field in fields)
        groups[key].append(row)
    summaries = []
    for key in sorted(groups, key=lambda value: tuple(str(part) for part in value)):
        summary = summarize_replicates(groups[key])
        summary.update(dict(zip(fields, key, strict=True)))
        summaries.append(summary)
    return summaries


def paired_coverage_summaries(
    records: Sequence[Mapping[str, Any]],
    *,
    comparator: str,
    method_field: str = "method",
    cell_fields: Sequence[str] = DEFAULT_CELL_FIELDS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Calculate descriptive, valid-interval paired coverage differences by cell."""
    fields = [
        field
        for field in cell_fields
        if field != method_field and any(field in row for row in records)
    ]
    groups: dict[tuple[Any, ...], dict[str, list[Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in records:
        method = row.get(method_field)
        if method is None:
            raise ValueError(f"records must contain {method_field!r}")
        groups[tuple(row.get(field) for field in fields)][str(method)].append(row)

    summaries: list[dict[str, Any]] = []
    replicate_rows: list[dict[str, Any]] = []
    for key, methods in sorted(
        groups.items(), key=lambda item: tuple(str(part) for part in item[0])
    ):
        candidates = sorted(name for name in methods if name != comparator)
        for method in candidates:
            if not methods[method] or not methods.get(comparator):
                continue
            result = paired_coverage_difference(methods[method], methods[comparator])
            summary: dict[str, Any] = dict(zip(fields, key, strict=True))
            summary.update({
                "method": method,
                "comparator": comparator,
                **{
                    name: value
                    for name, value in result.items()
                    if name != "paired_replicate_differences"
                },
            })
            summaries.append(summary)
            for paired in result["paired_replicate_differences"]:
                replicate_rows.append({
                    **dict(zip(fields, key, strict=True)),
                    "method": method,
                    "comparator": comparator,
                    **paired,
                })
    return summaries, replicate_rows


def write_study_report(
    records: Sequence[Mapping[str, Any]],
    output_dir: Path,
    *,
    comparator: str | None = None,
    cell_fields: Sequence[str] = DEFAULT_CELL_FIELDS,
    no_missing_gate_records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create cellwise CSVs, paired tables, JSON metadata, and coverage plot."""
    if not records:
        raise ValueError("records must contain study replicates")
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = summarize_by_cell(records, cell_fields)
    _write_csv(output_dir / "cellwise_metrics.csv", summaries)

    variance_rows = []
    donor_rows = []
    conditional_rows = []
    for record in records:
        identity = {field: record.get(field) for field in cell_fields if field in record}
        decomposition = record.get("variance_decomposition")
        if isinstance(decomposition, Mapping):
            variance_rows.append({**identity, **decomposition})
        elif (
            record.get("within_imputation_variance") is not None
            and record.get("between_imputation_variance") is not None
            and isinstance(record.get("imputations", record.get("m")), int)
        ):
            imputations = record.get("imputations", record.get("m"))
            if not isinstance(imputations, bool) and imputations >= 2:
                variance_rows.append({
                    **identity,
                    **variance_decomposition(
                        float(record["within_imputation_variance"]),
                        float(record["between_imputation_variance"]),
                        imputations,
                    ),
                    "imputations": imputations,
                    "pooled_degrees_of_freedom": record.get(
                        "pooled_degrees_of_freedom",
                        record.get("degrees_of_freedom"),
                    ),
                })
        elif any(
            name in record
            for name in ("within_imputation_variance", "between_imputation_variance")
        ):
            variance_rows.append({
                **identity,
                **{
                    name: record.get(name)
                    for name in (
                        "within_imputation_variance",
                        "between_imputation_variance",
                        "total_variance",
                        "relative_increase_in_variance",
                        "fraction_of_missing_information",
                        "relative_efficiency",
                        "within_variance_share",
                        "between_variance_share",
                        "imputations",
                    )
                },
            })
        donor = record.get("pmm_diagnostics")
        if isinstance(donor, Mapping):
            draws = donor.get("draws", [])
            if isinstance(draws, Sequence):
                donor_rows.append({
                    **identity,
                    **summarize_pmm_donor_draws(draws),
                    "distance_definition": donor.get("distance_definition"),
                    "distance_outlier_rule": donor.get("distance_outlier_rule"),
                    "donor_identity_definition": donor.get("donor_identity_definition"),
                })
        conditional = record.get("conditional_diagnostics")
        if isinstance(conditional, Mapping):
            for region in conditional.get("regions", []):
                conditional_rows.append({
                    **identity,
                    "diagnostic_scope": conditional.get("diagnostic_scope"),
                    "overall_conditional_mean_bias": conditional.get(
                        "conditional_mean_bias"
                    ),
                    "overall_conditional_mean_rmse": conditional.get(
                        "conditional_mean_rmse"
                    ),
                    **region,
                })

    _write_csv(output_dir / "variance_decomposition.csv", variance_rows)
    _write_csv(output_dir / "pmm_donor_diagnostics.csv", donor_rows)
    _write_csv(output_dir / "conditional_dgp_diagnostics.csv", conditional_rows)
    _plot_bias_variance(summaries, output_dir / "bias_variance_diagnostics.png")
    _plot_pmm_donors(donor_rows, output_dir / "pmm_donor_diagnostics.png")
    _plot_conditional_means(
        conditional_rows, output_dir / "conditional_mean_diagnostics.png"
    )

    gate_groups: dict[tuple[Any, ...], list[bool]] = defaultdict(list)
    if no_missing_gate_records is not None and len(no_missing_gate_records) > 0:
        gate_fields = ("dgp", "estimand")
        if any(
            not all(field in row for field in (*gate_fields, "covered"))
            for row in no_missing_gate_records
        ):
            raise ValueError(
                "no-missing gate records require dgp/estimand identity and covered values"
            )
        for row in no_missing_gate_records:
            gate_groups[tuple(row.get(field) for field in gate_fields)].append(
                row["covered"]
            )
        gate_rows = []
        for key, values in sorted(
            gate_groups.items(), key=lambda item: tuple(str(part) for part in item[0])
        ):
            gate_rows.append({
                **dict(zip(gate_fields, key, strict=True)),
                **summarize_no_missing_gate(values),
            })
    else:
        gate_rows = []
    _write_csv(output_dir / "no_missing_gate.csv", gate_rows)

    paired_summaries: list[dict[str, Any]] = []
    paired_replicates: list[dict[str, Any]] = []
    if comparator is not None:
        paired_summaries, paired_replicates = paired_coverage_summaries(
            records, comparator=comparator, cell_fields=cell_fields
        )
    _write_csv(output_dir / "paired_coverage_cellwise.csv", paired_summaries)
    _write_csv(output_dir / "paired_coverage_replicates.csv", paired_replicates)
    _plot_cellwise_coverage(summaries, output_dir / "cellwise_coverage.png")

    metadata = {
        "report_scope": (
            "cellwise summaries and descriptive paired Monte Carlo contrasts; "
            "no cross-cell aggregate or superiority/equivalence claim"
        ),
        "scheduled_replicate_records": len(records),
        "reported_cells": len(summaries),
        "paired_comparator": comparator,
        "cell_fields": [
            field for field in cell_fields if any(field in row for row in records)
        ],
        "outputs": [
            "cellwise_metrics.csv",
            "variance_decomposition.csv",
            "paired_coverage_cellwise.csv",
            "paired_coverage_replicates.csv",
            "pmm_donor_diagnostics.csv",
            "conditional_dgp_diagnostics.csv",
            "no_missing_gate.csv",
            "cellwise_coverage.png",
            "bias_variance_diagnostics.png",
            "pmm_donor_diagnostics.png",
            "conditional_mean_diagnostics.png",
        ],
    }
    (output_dir / "report_metadata.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return metadata


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(field for row in rows for field in row))
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                field: json.dumps(value, allow_nan=False)
                if isinstance(value, (dict, list, tuple))
                else value
                for field, value in row.items()
            })


def _plot_cellwise_coverage(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    valid = [
        row
        for row in rows
        if row.get("coverage_among_finite_intervals") is not None
        and row.get("exact_95_percent_binomial_interval") is not None
    ]
    figure, axis = plt.subplots(figsize=(11, 6))
    if valid:
        methods = sorted({str(row.get("method", "method")) for row in valid})
        positions = {method: index for index, method in enumerate(methods)}
        counts: dict[str, int] = defaultdict(int)
        for row in valid:
            method = str(row.get("method", "method"))
            index = counts[method]
            counts[method] += 1
            jitter = ((index * 0.61803398875) % 1.0 - 0.5) * 0.35
            lower, upper = row["exact_95_percent_binomial_interval"]
            coverage = float(row["coverage_among_finite_intervals"])
            axis.errorbar(
                positions[method] + jitter,
                coverage,
                yerr=[[coverage - float(lower)], [float(upper) - coverage]],
                fmt="o",
                alpha=0.55,
                markersize=4,
                capsize=2,
            )
        axis.set_xticks(range(len(methods)), methods, rotation=20, ha="right")
        axis.axhline(0.95, color="black", linestyle="--", linewidth=1)
        axis.set_ylabel("Coverage among valid finite intervals")
        axis.set_title("Cellwise coverage with exact 95% binomial intervals")
        axis.set_ylim(0, 1)
        axis.grid(axis="y", alpha=0.2)
    else:
        axis.text(0.5, 0.5, "No valid finite intervals", ha="center", va="center")
        axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _plot_bias_variance(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    methods = sorted({str(row.get("method", "method")) for row in rows})
    plotted = False
    for method in methods:
        selected = [
            row
            for row in rows
            if str(row.get("method", "method")) == method
            and row.get("mean_bias_available_estimates") is not None
            and row.get("empirical_estimate_sd_available_estimates") not in (None, 0)
            and row.get("mean_pooled_se_to_empirical_sd") is not None
        ]
        if not selected:
            continue
        x_values = [
            abs(float(row["mean_bias_available_estimates"]))
            / float(row["empirical_estimate_sd_available_estimates"])
            for row in selected
        ]
        y_values = [float(row["mean_pooled_se_to_empirical_sd"]) for row in selected]
        axis.scatter(x_values, y_values, alpha=0.65, s=24, label=method)
        plotted = True
    if plotted:
        axis.axhline(1.0, color="black", linestyle="--", linewidth=1)
        axis.set_xlabel("Absolute mean bias / empirical estimate SD")
        axis.set_ylabel("Mean pooled SE / empirical estimate SD")
        axis.set_title("Cellwise bias and variance calibration diagnostics")
        axis.legend()
        axis.grid(alpha=0.2)
    else:
        axis.text(0.5, 0.5, "Bias/variance diagnostics unavailable", ha="center", va="center")
        axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _plot_pmm_donors(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    valid = [
        row
        for row in rows
        if row.get("mean_selected_distance") is not None
        and row.get("mean_source_donor_selection_hhi") is not None
    ]
    if valid:
        axis.scatter(
            [float(row["mean_selected_distance"]) for row in valid],
            [float(row["mean_source_donor_selection_hhi"]) for row in valid],
            alpha=0.65,
            s=24,
        )
        axis.set_xlabel("Mean selected donor distance (target units)")
        axis.set_ylabel("Source-donor selection HHI")
        axis.set_title("PMM donor distance and reuse concentration")
        axis.grid(alpha=0.2)
    else:
        axis.text(0.5, 0.5, "PMM donor diagnostics unavailable", ha="center", va="center")
        axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _plot_conditional_means(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 6))
    if rows:
        dgp_names = sorted({str(row.get("dgp", "DGP")) for row in rows})
        for dgp in dgp_names:
            selected = [row for row in rows if str(row.get("dgp", "DGP")) == dgp]
            axis.scatter(
                [float(row["true_conditional_mean"]) for row in selected],
                [float(row["predicted_conditional_mean"]) for row in selected],
                alpha=0.55,
                s=20,
                label=dgp,
            )
        limits = [
            min(
                float(row["true_conditional_mean"])
                for row in rows
            ),
            max(
                float(row["true_conditional_mean"])
                for row in rows
            ),
            min(
                float(row["predicted_conditional_mean"])
                for row in rows
            ),
            max(
                float(row["predicted_conditional_mean"])
                for row in rows
            ),
        ]
        axis.plot([min(limits), max(limits)], [min(limits), max(limits)], "--", color="black")
        axis.set_xlabel("Analytic true E[x2 | x1]")
        axis.set_ylabel("Imputation-model predicted E[x2 | x1]")
        axis.set_title("Synthetic DGP conditional-mean diagnostic")
        axis.legend()
        axis.grid(alpha=0.2)
    else:
        axis.text(0.5, 0.5, "Synthetic conditional diagnostics unavailable", ha="center", va="center")
        axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
