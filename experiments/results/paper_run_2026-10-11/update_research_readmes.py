"""Update research documentation from the frozen paper-run CSV/JSON evidence."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pandas as pd


RUN_DIR = Path(__file__).resolve().parent
TABLES_DIR = RUN_DIR / "followup_tables"
REPO_ROOT = RUN_DIR.parents[2]
BEGIN = "<!-- BEGIN GENERATED FROZEN PAPER RESULTS -->"
END = "<!-- END GENERATED FROZEN PAPER RESULTS -->"


def read_table(name: str) -> pd.DataFrame:
    path = TABLES_DIR / f"{name}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Required generated evidence table is missing: {path}")
    return pd.read_csv(path)


def replace_generated_section(path: Path, section: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError(f"Expected exactly one generated-section marker pair in {path}.")
    start = text.index(BEGIN) + len(BEGIN)
    finish = text.index(END)
    if finish < start:
        raise ValueError(f"Generated-section markers are out of order in {path}.")
    updated = text[:start] + "\n" + section.rstrip() + "\n" + text[finish:]
    path.write_text(updated, encoding="utf-8")


def make_section(link_prefix: str) -> str:
    model_summary = read_table("m3_model_summary").set_index("method")
    comparisons = read_table("m3_auto_comparisons").set_index("model")
    m3_ni = read_table("m3_shortlisting_noninferiority").iloc[0]
    six_ni = read_table("six_series_shortlisting_noninferiority").iloc[0]
    runtime = read_table("m3_shortlisting_runtime").iloc[0]
    metadata = json.loads(
        (RUN_DIR / "forecasting_m3" / "m3_environment.json").read_text(
            encoding="utf-8"
        )
    )
    if metadata["selection"].get("selection_precedes_model_evaluation") is not True:
        raise ValueError("M3 metadata does not attest to pre-model series selection.")
    if int(m3_ni["series_count"]) != 20 or int(six_ni["series_count"]) != 6:
        raise ValueError("Frozen shortlisting tests have unexpected series counts.")
    if float(m3_ni["noninferiority_margin"]) != float(
        six_ni["noninferiority_margin"]
    ):
        raise ValueError("The six-series and M3 margins do not match.")

    arima = comparisons.loc["arima"]
    significant_count = int(comparisons["p_holm_lt_0_05"].astype(bool).sum())
    margin = float(m3_ni["noninferiority_margin"])
    m3_status = (
        "established"
        if bool(m3_ni["noninferiority_established"])
        else "not established"
    )
    six_status = (
        "established"
        if bool(six_ni["noninferiority_established"])
        else "not established"
    )
    bootstrap_reason = (
        "both bounds are below the margin."
        if float(m3_ni["one_sided_95pct_bootstrap_upper"]) < margin
        and float(m3_ni["one_sided_95pct_t_upper_df19"]) < margin
        else (
            "the percentile-bootstrap bound exceeds the margin, although the "
            "t upper bound is below it."
        )
    )
    six_reason = (
        "both bounds are below the margin."
        if float(six_ni["one_sided_95pct_bootstrap_upper"]) < margin
        and float(six_ni["one_sided_95pct_t_upper_df5"]) < margin
        else (
            "the t upper bound narrowly exceeds the margin."
            if float(six_ni["one_sided_95pct_t_upper_df5"]) >= margin
            else "the bootstrap upper bound exceeds the margin."
        )
    )
    selection = metadata["selection"]
    section = f"""### Frozen forecasting evidence

The supplementary frozen run evaluates {int(model_summary.loc["auto", "n_series"])} M3 Monthly series over {int(model_summary.loc["auto", "evaluation_windows"])} scored windows. Auto's mean series-level MASE was {float(model_summary.loc["auto", "mean_series_mase"]):.8f}; fixed ARIMA's was {float(model_summary.loc["arima", "mean_series_mase"]):.8f}. For the paired Auto-minus-ARIMA comparison, the mean difference was {float(arima["mean_series_mase_diff_auto_minus_model"]):.8f} over {int(arima["pairs"])} series, with {int(arima["auto_wins"])} Auto wins; raw p={float(arima["p_raw"]):.12g} and Holm-adjusted p={float(arima["p_holm"]):.12g}. It was not significant after Holm correction. Across the seven Auto-versus-alternative comparisons, {significant_count} were significant after Holm correction. See the full [model summary]({link_prefix}/m3_model_summary.csv), [Auto comparisons]({link_prefix}/m3_auto_comparisons.csv), and [series-level results]({link_prefix}/m3_series_results.csv).

For shortlisting, differences are per-series mean MASE (Auto minus auto_no_shortlist), with the series as the paired unit and four rolling windows averaged within each series. The +{margin:.2f} MASE margin was fixed before the M3 results existed. On M3 (n={int(m3_ni["series_count"])}), the mean difference was {float(m3_ni["mean_paired_mase_difference"]):.8f}; the one-sided 95% t upper bound (df=19) was {float(m3_ni["one_sided_95pct_t_upper_df19"]):.8f}, and the percentile-bootstrap upper bound was {float(m3_ni["one_sided_95pct_bootstrap_upper"]):.8f}. Non-inferiority was **{m3_status}**: {bootstrap_reason} The earlier six-series test also **{six_status}** (mean difference {float(six_ni["mean_paired_mase_difference"]):.8f}; t upper bound, df=5, {float(six_ni["one_sided_95pct_t_upper_df5"]):.8f}; bootstrap upper bound {float(six_ni["one_sided_95pct_bootstrap_upper"]):.8f}), because {six_reason} Neither result establishes accuracy equivalence. See the [M3 non-inferiority calculation]({link_prefix}/m3_shortlisting_noninferiority.csv) and the [six-series per-series results]({link_prefix}/six_series_shortlisting_by_series.csv).

The M3 shortlisting comparison measured mean runtime of {float(runtime["auto_mean_seconds_per_window"]):.8f} seconds per window with shortlisting and {float(runtime["no_shortlist_mean_seconds_per_window"]):.8f} without; the mean per-series runtime reduction was {float(runtime["mean_per_series_runtime_reduction_percent"]):.8f}% (paired runtime Wilcoxon p={float(runtime["paired_wilcoxon_p"]):.12g}). This is evidence about measured runtime on this subset, not an accuracy-equivalence result. The fixed-model and per-series comparison tables are linked above.

Series were selected before model evaluation: {selection["eligible_series"]} source-order M3 Monthly series met the length threshold of {selection["minimum_series_length"]} observations, then {metadata["evaluation"]["series_count"]} evenly spaced indices from first to last were selected with integer `numpy.linspace` indices. Selection used series length and source order only, not model scores or runtime. The full rule, selected IDs, and pre-evaluation flag are recorded in [M3 environment metadata]({link_prefix.rsplit("/followup_tables", 1)[0]}/forecasting_m3/m3_environment.json). M3 series may share domains, so these results do not remove all dependence or establish generalization beyond this dataset. Canonical environment pins are listed [here]({link_prefix.rsplit("/followup_tables", 1)[0]}/environment_pins.txt).
"""
    paragraphs = section.strip().split("\n\n")
    return "\n\n".join(
        textwrap.fill(
            " ".join(paragraph.split()),
            width=88,
            break_long_words=False,
            break_on_hyphens=False,
        )
        for paragraph in paragraphs
    )


def main() -> None:
    targets = {
        REPO_ROOT / "README.md": "experiments/results/paper_run_2026-10-11/followup_tables",
        REPO_ROOT / "experiments" / "README.md": "results/paper_run_2026-10-11/followup_tables",
        REPO_ROOT / "research" / "README.md": "../experiments/results/paper_run_2026-10-11/followup_tables",
        REPO_ROOT / "research" / "research-upgrade-status.md": (
            "../experiments/results/paper_run_2026-10-11/followup_tables"
        ),
    }
    for path, prefix in targets.items():
        replace_generated_section(path, make_section(prefix))
        print(f"Updated {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
