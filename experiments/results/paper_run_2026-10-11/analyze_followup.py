"""Analyze saved reproducibility and forecasting CSV evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


RUN_DIR = Path(__file__).resolve().parent
TABLES_DIR = RUN_DIR / "followup_tables"
M3_DIR = RUN_DIR / "forecasting_m3"
BOOTSTRAP_SEED = 20261011
BOOTSTRAP_REPLICATES = 200_000
NONINFERIORITY_MARGIN = 0.05


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required saved CSV is missing: {path}")
    return pd.read_csv(path)


def write_table(directory: Path, name: str, frame: pd.DataFrame, note: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_csv(directory / f"{name}.csv", index=False)
    (directory / f"{name}.md").write_text(
        f"# {name.replace('_', ' ').title()}\n\n{note}\n\n"
        f"{frame.to_markdown(index=False, tablefmt='github')}\n",
        encoding="utf-8",
    )


def holm_adjust(pvalues: list[float]) -> np.ndarray:
    values = np.asarray(pvalues, dtype=float)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def make_reproducibility_tables() -> None:
    comparison_dir = RUN_DIR / "reproducibility"
    filenames = [
        "imputation_raw.csv",
        "imputation_summary.csv",
        "imputation_significance.csv",
        "environment_imputation.json",
    ]
    rows = []
    for filename in filenames:
        first = comparison_dir / "run_1" / filename
        second = comparison_dir / "run_2" / filename
        if not first.is_file() or not second.is_file():
            raise FileNotFoundError(f"Missing repeat-run artifact for {filename}.")
        rows.append(
            {
                "file": filename,
                "run_1_bytes": first.stat().st_size,
                "run_2_bytes": second.stat().st_size,
                "byte_identical": first.read_bytes() == second.read_bytes(),
            }
        )
    comparison = pd.DataFrame(rows)
    write_table(
        TABLES_DIR,
        "imputation_reproducibility",
        comparison,
        "Byte-for-byte comparison of saved files from the two fresh repeat runs.",
    )

    frozen_path = RUN_DIR / "imputation" / "environment_imputation.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    run_one = json.loads(
        (comparison_dir / "run_1" / "environment_imputation.json").read_text(
            encoding="utf-8"
        )
    )
    run_two = json.loads(
        (comparison_dir / "run_2" / "environment_imputation.json").read_text(
            encoding="utf-8"
        )
    )
    if frozen != run_one or run_one != run_two:
        raise ValueError("The canonical and repeated-run environments do not match.")
    env = run_one
    lines = [
        f"Python=={env['python']}",
        f"numpy=={env['numpy']}",
        f"pandas=={env['pandas']}",
        f"scikit-learn=={env['scikit-learn']}",
        f"scipy=={env['scipy']}",
        f"statsmodels=={env['statsmodels']}",
        "",
        "These exact versions are read from the saved canonical environment JSON.",
    ]
    (RUN_DIR / "environment_pins.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def make_six_series_shortlisting_analysis() -> None:
    raw = read_csv(RUN_DIR / "forecasting" / "forecasting_raw.csv")
    required = {"series", "window", "method", "mase", "seconds"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Saved forecasting CSV is missing columns: {sorted(missing)}")

    selected = raw.loc[raw["method"].isin(["auto", "auto_no_shortlist"])].copy()
    per_series = selected.pivot_table(
        index="series", columns="method", values="mase", aggfunc="mean"
    )
    runtimes = selected.pivot_table(
        index="series", columns="method", values="seconds", aggfunc="mean"
    )
    per_series["auto_minus_no_shortlist_mase"] = (
        per_series["auto"] - per_series["auto_no_shortlist"]
    )
    per_series["auto_mean_seconds_per_window"] = runtimes["auto"]
    per_series["no_shortlist_mean_seconds_per_window"] = runtimes["auto_no_shortlist"]
    per_series["shortlisting_runtime_reduction_percent"] = (
        1.0 - runtimes["auto"] / runtimes["auto_no_shortlist"]
    ) * 100.0
    per_series["runtime_speedup_no_shortlist_over_auto"] = (
        runtimes["auto_no_shortlist"] / runtimes["auto"]
    )
    per_series = per_series.reset_index().round(8)

    differences = per_series["auto_minus_no_shortlist_mase"].to_numpy(dtype=float)
    n = len(differences)
    if n != 6:
        raise ValueError(
            f"Expected six frozen series for the pre-specified analysis; found {n}."
        )
    mean_difference = float(differences.mean())
    standard_error = float(stats.sem(differences))
    t_upper = mean_difference + float(stats.t.ppf(0.95, df=5)) * standard_error
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_indices = rng.integers(
        0, n, size=(BOOTSTRAP_REPLICATES, n)
    )
    bootstrap_means = differences[bootstrap_indices].mean(axis=1)
    bootstrap_upper = float(np.quantile(bootstrap_means, 0.95, method="linear"))
    established = (
        t_upper < NONINFERIORITY_MARGIN
        and bootstrap_upper < NONINFERIORITY_MARGIN
    )
    runtimes_by_series = per_series[
        [
            "auto_mean_seconds_per_window",
            "no_shortlist_mean_seconds_per_window",
        ]
    ]
    summary = pd.DataFrame(
        [
            {
                "series_count": n,
                "paired_difference_definition": "Auto minus auto_no_shortlist MASE",
                "mean_paired_mase_difference": mean_difference,
                "one_sided_95pct_t_upper_df5": t_upper,
                "one_sided_95pct_bootstrap_upper": bootstrap_upper,
                "bootstrap_method": (
                    "Nonparametric percentile bootstrap resampling series differences; "
                    f"{BOOTSTRAP_REPLICATES} replicates; seed {BOOTSTRAP_SEED}"
                ),
                "noninferiority_margin": NONINFERIORITY_MARGIN,
                "noninferiority_established": established,
                "auto_mean_seconds_per_window": float(
                    runtimes_by_series["auto_mean_seconds_per_window"].mean()
                ),
                "no_shortlist_mean_seconds_per_window": float(
                    runtimes_by_series[
                        "no_shortlist_mean_seconds_per_window"
                    ].mean()
                ),
            }
        ]
    ).round(8)
    conclusion = (
        "Non-inferiority established against the fixed +0.05 MASE margin."
        if established
        else "Non-inferiority not established."
    )
    note = (
        "Frozen six-series evidence; one observation per series is the mean over "
        "that series' saved rolling windows. Differences are Auto minus "
        "auto_no_shortlist MASE. The margin was fixed at +0.05 before examining "
        "per-series differences. Both the one-sided t upper bound (df=5) and the "
        "nonparametric percentile-bootstrap upper bound must be below the margin "
        "to establish non-inferiority. " + conclusion
    )
    write_table(
        TABLES_DIR,
        "six_series_shortlisting_noninferiority",
        summary,
        note,
    )
    write_table(
        TABLES_DIR,
        "six_series_shortlisting_by_series",
        per_series,
        "Per-series paired Auto minus auto_no_shortlist MASE differences and "
        "mean seconds per forecast window, all derived from the frozen "
        "`forecasting_raw.csv`.",
    )


def make_m3_tables() -> None:
    raw = read_csv(M3_DIR / "m3_forecasting_raw.csv")
    subset = read_csv(M3_DIR / "m3_monthly_subset.csv")
    if raw.empty or subset.empty:
        raise ValueError("M3 forecast evidence CSVs must not be empty.")
    if raw["series"].nunique() != 20:
        raise ValueError(f"Expected 20 selected M3 series, got {raw['series'].nunique()}.")
    if raw.groupby("series")["window"].nunique().ne(4).any():
        raise ValueError("Every M3 series must have exactly four scored windows.")

    per_series = (
        raw.groupby(["series", "method"], as_index=False, sort=True)
        .agg(
            mean_mase=("mase", "mean"),
            mean_seconds_per_window=("seconds", "mean"),
            evaluation_windows=("window", "nunique"),
        )
    )
    point_counts = subset.groupby("series", as_index=False).agg(
        observations=("y", "count")
    )
    per_series = per_series.merge(point_counts, on="series", validate="many_to_one")
    per_series = per_series[
        ["series", "observations", "method", "mean_mase",
         "mean_seconds_per_window", "evaluation_windows"]
    ].round(8)
    write_table(
        TABLES_DIR,
        "m3_series_results",
        per_series,
        "Series-level mean MASE and mean model-call runtime over four 18-month "
        "rolling windows. The subset is fixed by the sampling rule in "
        "`m3_environment.json`; source observations come from the saved M3 subset CSV.",
    )

    summary = (
        per_series.groupby("method", as_index=False, sort=True)
        .agg(
            mean_series_mase=("mean_mase", "mean"),
            mean_seconds_per_window=("mean_seconds_per_window", "mean"),
            median_seconds_per_window=("mean_seconds_per_window", "median"),
            n_series=("series", "nunique"),
            evaluation_windows=("evaluation_windows", "sum"),
        )
        .round(8)
    )
    write_table(
        TABLES_DIR,
        "m3_model_summary",
        summary,
        "Means are computed by averaging within-series MASE first, so each of "
        "the 20 series receives equal weight. Runtime is mean model-call seconds "
        "per forecast window.",
    )

    wide = per_series.pivot(index="series", columns="method", values="mean_mase")
    alternatives = [method for method in wide.columns if method != "auto"]
    comparison_rows = []
    for method in alternatives:
        difference = (wide["auto"] - wide[method]).dropna()
        p_raw = (
            float(stats.wilcoxon(difference).pvalue)
            if (difference != 0).any()
            else 1.0
        )
        comparison_rows.append(
            {
                "model": method,
                "mean_series_mase_diff_auto_minus_model": float(difference.mean()),
                "auto_wins": int((difference < 0).sum()),
                "pairs": int(difference.size),
                "p_raw": p_raw,
            }
        )
    comparisons = pd.DataFrame(comparison_rows)
    comparisons["p_holm"] = holm_adjust(comparisons["p_raw"].tolist())
    comparisons["p_holm_lt_0_05"] = comparisons["p_holm"] < 0.05
    comparisons = comparisons.round(
        {
            "mean_series_mase_diff_auto_minus_model": 8,
            "p_raw": 12,
            "p_holm": 12,
        }
    )
    write_table(
        TABLES_DIR,
        "m3_auto_comparisons",
        comparisons,
        "Exploratory paired Wilcoxon tests on per-series mean MASE (n=20 series), "
        "Auto minus each alternative. Holm correction is across all seven "
        "alternatives; negative differences favor Auto. Series may share M3 domains.",
    )

    shortlist_differences = (
        wide["auto"] - wide["auto_no_shortlist"]
    ).dropna().to_numpy(dtype=float)
    n_shortlist = len(shortlist_differences)
    if n_shortlist != 20:
        raise ValueError(
            f"Expected 20 paired M3 series for the non-inferiority analysis; "
            f"found {n_shortlist}."
        )
    shortlist_mean = float(shortlist_differences.mean())
    shortlist_t_upper = shortlist_mean + float(
        stats.t.ppf(0.95, df=n_shortlist - 1)
    ) * float(stats.sem(shortlist_differences))
    shortlist_rng = np.random.default_rng(BOOTSTRAP_SEED)
    shortlist_bootstrap_indices = shortlist_rng.integers(
        0, n_shortlist, size=(BOOTSTRAP_REPLICATES, n_shortlist)
    )
    shortlist_bootstrap_upper = float(
        np.quantile(
            shortlist_differences[shortlist_bootstrap_indices].mean(axis=1),
            0.95,
            method="linear",
        )
    )
    shortlist_ni_established = (
        shortlist_t_upper < NONINFERIORITY_MARGIN
        and shortlist_bootstrap_upper < NONINFERIORITY_MARGIN
    )
    shortlist_ni = pd.DataFrame(
        [
            {
                "series_count": n_shortlist,
                "paired_difference_definition": (
                    "Auto minus auto_no_shortlist MASE"
                ),
                "mean_paired_mase_difference": shortlist_mean,
                "one_sided_95pct_t_upper_df19": shortlist_t_upper,
                "one_sided_95pct_bootstrap_upper": shortlist_bootstrap_upper,
                "bootstrap_method": (
                    "Nonparametric percentile bootstrap resampling series "
                    f"differences; {BOOTSTRAP_REPLICATES} replicates; "
                    f"seed {BOOTSTRAP_SEED}"
                ),
                "noninferiority_margin": NONINFERIORITY_MARGIN,
                "noninferiority_established": shortlist_ni_established,
            }
        ]
    ).round(8)
    shortlist_ni_note = (
        "Frozen M3 evidence; one paired observation per series is Auto minus "
        "auto_no_shortlist MASE averaged over that series' four saved rolling "
        "windows. The +0.05 MASE margin was fixed before M3 results existed. "
        "As in the six-series analysis, both the one-sided t upper bound "
        "(df=19) and nonparametric percentile-bootstrap upper bound must be "
        "below the margin to establish non-inferiority. "
        + (
            "Non-inferiority established."
            if shortlist_ni_established
            else "Non-inferiority not established."
        )
    )
    write_table(
        TABLES_DIR,
        "m3_shortlisting_noninferiority",
        shortlist_ni,
        shortlist_ni_note,
    )

    runtime_wide = per_series.pivot(
        index="series", columns="method", values="mean_seconds_per_window"
    )
    mase_wide = per_series.pivot(index="series", columns="method", values="mean_mase")
    runtime_rows = pd.DataFrame(
        {
            "series": runtime_wide.index,
            "auto_mean_mase": mase_wide["auto"].values,
            "no_shortlist_mean_mase": mase_wide["auto_no_shortlist"].values,
            "auto_minus_no_shortlist_mase": (
                mase_wide["auto"] - mase_wide["auto_no_shortlist"]
            ).values,
            "auto_seconds_per_window": runtime_wide["auto"].values,
            "no_shortlist_seconds_per_window": runtime_wide[
                "auto_no_shortlist"
            ].values,
        }
    )
    runtime_rows["runtime_reduction_percent"] = (
        1.0
        - runtime_rows["auto_seconds_per_window"]
        / runtime_rows["no_shortlist_seconds_per_window"]
    ) * 100.0
    runtime_rows["speedup_no_shortlist_over_auto"] = (
        runtime_rows["no_shortlist_seconds_per_window"]
        / runtime_rows["auto_seconds_per_window"]
    )
    runtime_rows = runtime_rows.round(8)
    runtime_p = float(
        stats.wilcoxon(
            runtime_rows["no_shortlist_seconds_per_window"]
            - runtime_rows["auto_seconds_per_window"]
        ).pvalue
    )
    runtime_summary = pd.DataFrame(
        [
            {
                "series_count": int(runtime_rows["series"].nunique()),
                "auto_mean_seconds_per_window": runtime_rows[
                    "auto_seconds_per_window"
                ].mean(),
                "no_shortlist_mean_seconds_per_window": runtime_rows[
                    "no_shortlist_seconds_per_window"
                ].mean(),
                "mean_per_series_runtime_reduction_percent": runtime_rows[
                    "runtime_reduction_percent"
                ].mean(),
                "paired_wilcoxon_p": runtime_p,
            }
        ]
    ).round(12)
    write_table(
        TABLES_DIR,
        "m3_shortlisting_runtime",
        runtime_summary,
        "Runtime is averaged per series after averaging the four scored windows. "
        "The paired Wilcoxon test compares per-series mean seconds without "
        "shortlisting minus with shortlisting; positive differences indicate a "
        "runtime reduction with shortlisting.",
    )
    summary_row = {
        "series": "MEAN",
        "auto_mean_mase": runtime_rows["auto_mean_mase"].mean(),
        "no_shortlist_mean_mase": runtime_rows["no_shortlist_mean_mase"].mean(),
        "auto_minus_no_shortlist_mase": runtime_rows[
            "auto_minus_no_shortlist_mase"
        ].mean(),
        "auto_seconds_per_window": runtime_rows["auto_seconds_per_window"].mean(),
        "no_shortlist_seconds_per_window": runtime_rows[
            "no_shortlist_seconds_per_window"
        ].mean(),
        "runtime_reduction_percent": runtime_rows[
            "runtime_reduction_percent"
        ].mean(),
        "speedup_no_shortlist_over_auto": runtime_rows[
            "speedup_no_shortlist_over_auto"
        ].mean(),
    }
    runtime_rows = pd.concat(
        [runtime_rows, pd.DataFrame([summary_row])], ignore_index=True
    ).round(8)
    write_table(
        TABLES_DIR,
        "m3_shortlisting_by_series",
        runtime_rows,
        "Per-series Auto versus auto_no_shortlist accuracy and model-selection "
        "runtime, averaged over four windows. The final MEAN row is the arithmetic "
        "mean over 20 series. Runtime Wilcoxon p-value across per-series times: "
        f"{runtime_p:.12g}. Non-significance of an accuracy test is not an "
        "equivalence or non-inferiority claim.",
    )


def audit_csv_tables() -> None:
    issues = []
    for path in sorted(TABLES_DIR.glob("*.csv")):
        frame = pd.read_csv(path, keep_default_na=False)
        for row_index, row in frame.iterrows():
            for column, value in row.items():
                if value == "" or (
                    isinstance(value, str)
                    and value.strip().lower() in {"nan", "na", "null"}
                ):
                    issues.append(f"{path.name}: row {row_index + 2}, column {column}")
    if issues:
        raise ValueError("Blank/NaN cells in generated CSV tables:\n" + "\n".join(issues))
    print("Blank/NaN cells in generated CSV tables: none.")


def write_followup_readme() -> None:
    env = json.loads(
        (RUN_DIR / "imputation" / "environment_imputation.json").read_text(
            encoding="utf-8"
        )
    )
    prior_env_path = Path(__file__).resolve().parents[1] / "environment_imputation.json"
    prior_env = json.loads(prior_env_path.read_text(encoding="utf-8"))
    repeat = read_csv(TABLES_DIR / "imputation_reproducibility.csv")
    if not repeat["byte_identical"].all():
        raise ValueError("Cannot report reproducibility success when output files differ.")
    prior_comparison = (RUN_DIR / "imputation_prior_run_comparison.txt").read_text(
        encoding="utf-8"
    )
    reproducibility_rows = repeat.to_markdown(index=False, tablefmt="github")
    m3_env_path = M3_DIR / "m3_environment.json"
    m3_env = json.loads(m3_env_path.read_text(encoding="utf-8"))
    m3_env["source"]["archive_sha256"] = hashlib.sha256(
        (M3_DIR / m3_env["source"]["archive"]).read_bytes()
    ).hexdigest()
    m3_env_path.write_text(
        json.dumps(m3_env, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    m3_summary = read_csv(TABLES_DIR / "m3_model_summary.csv")
    m3_shortlist = read_csv(TABLES_DIR / "m3_shortlisting_by_series.csv")
    m3_runtime_summary = read_csv(TABLES_DIR / "m3_shortlisting_runtime.csv").iloc[0]
    m3_auto = m3_summary.loc[m3_summary["method"] == "auto"].iloc[0]
    m3_brute = m3_summary.loc[m3_summary["method"] == "auto_no_shortlist"].iloc[0]
    m3_mean_row = m3_shortlist.loc[m3_shortlist["series"] == "MEAN"].iloc[0]
    ni = read_csv(TABLES_DIR / "six_series_shortlisting_noninferiority.csv").iloc[0]
    m3_ni = read_csv(TABLES_DIR / "m3_shortlisting_noninferiority.csv").iloc[0]
    six_series = read_csv(TABLES_DIR / "six_series_shortlisting_by_series.csv")
    six_series_raw = read_csv(RUN_DIR / "forecasting" / "forecasting_raw.csv")
    six_series_count = int(six_series["series"].nunique())
    six_window_count = int(
        six_series_raw.loc[
            six_series_raw["method"].isin(["auto", "auto_no_shortlist"]),
            ["series", "window"],
        ].drop_duplicates().shape[0]
    )
    m3_comparisons = read_csv(TABLES_DIR / "m3_auto_comparisons.csv")
    m3_shortlist_comparison = m3_comparisons.loc[
        m3_comparisons["model"] == "auto_no_shortlist"
    ].iloc[0]
    m3_arima = m3_comparisons.loc[m3_comparisons["model"] == "arima"].iloc[0]
    old = prior_env
    current = env
    text = f"""# Paper run reproducibility and forecasting extension

This run-specific note supersedes any earlier environment/result summaries for
the frozen evidence in this directory.

## Canonical imputation evidence and reproducibility

The canonical imputation CSVs remain the originally frozen files under
[`imputation/`](imputation/). Two new benchmark executions in fresh output
folders, using the canonical run's environment, produced byte-identical raw,
summary, significance, and environment files:

{reproducibility_rows}

The original frozen run and repeat runs record Python {current['python']},
NumPy {current['numpy']}, pandas {current['pandas']}, scikit-learn
{current['scikit-learn']}, SciPy {current['scipy']}, and statsmodels
{current['statsmodels']}. Pin these versions to reproduce the canonical
numbers; see [`environment_pins.txt`](environment_pins.txt).

The earlier saved run records Python {old['python']}, NumPy {old['numpy']},
pandas {old['pandas']}, scikit-learn {old['scikit-learn']}, SciPy
{old['scipy']}, and statsmodels {old['statsmodels']}. The matched raw-row
comparison is preserved in
[`imputation_prior_run_comparison.txt`](imputation_prior_run_comparison.txt):

```text
{prior_comparison.rstrip()}
```

This supports environment-dependent results, not unseeded randomness in the
same recorded environment. The canonical CSVs were not replaced by either
repeat execution.

## Forecasting results and shortlisting

The frozen {six_series_count}-series, {six_window_count}-window Auto versus no-shortlist comparison
has mean per-series MASE difference (Auto minus no-shortlist)
{ni['mean_paired_mase_difference']:.8f}. The pre-specified one-sided 95% t
upper bound (five degrees of freedom) is
{ni['one_sided_95pct_t_upper_df5']:.8f}; the percentile-bootstrap upper bound
is {ni['one_sided_95pct_bootstrap_upper']:.8f}. The fixed non-inferiority
margin is {ni['noninferiority_margin']:.2f} MASE. **Non-inferiority not
established**: the t upper bound narrowly exceeds the margin, and both bounds
are required to be below the margin. This does not support an equivalence
claim. Full paired per-series results are in
[`followup_tables/six_series_shortlisting_by_series.csv`](followup_tables/six_series_shortlisting_by_series.csv).

Mean measured runtime per forecast window in this six-series run was
{ni['auto_mean_seconds_per_window']:.8f} seconds for Auto and
{ni['no_shortlist_mean_seconds_per_window']:.8f} seconds for Auto without
shortlisting.

An additional M3 Monthly evaluation uses a deterministic subset of
{m3_env['evaluation']['series_count']} series from {m3_env['selection']['eligible_series']}
eligible source series and {m3_env['evaluation']['windows_per_series']} rolling
windows per series, with a horizon of {m3_env['evaluation']['horizon']}. Source:
[{m3_env['source']['title']}, DOI {m3_env['source']['doi']}]({m3_env['source']['url']}),
licensed {m3_env['source']['license']}. Series selection is specified in
[`forecasting_m3/m3_environment.json`](forecasting_m3/m3_environment.json);
eligibility and source order determine the evenly spaced subset, which was
frozen before any model was run. The selected input observations and raw
forecasts are also saved there.

On M3, Auto's mean per-series MASE was {m3_auto['mean_series_mase']:.8f}
versus {m3_brute['mean_series_mase']:.8f} without shortlisting (paired
difference {m3_shortlist_comparison['mean_series_mase_diff_auto_minus_model']:.8f},
Holm-adjusted p={m3_shortlist_comparison['p_holm']:.8f}). Mean measured
runtime per window was {m3_auto['mean_seconds_per_window']:.8f} seconds
versus {m3_brute['mean_seconds_per_window']:.8f}; the mean per-series runtime
reduction was {m3_mean_row['runtime_reduction_percent']:.8f} percent (paired
runtime Wilcoxon p={m3_runtime_summary['paired_wilcoxon_p']:.12g}). This is
descriptive timing evidence on the selected subset; see
[`followup_tables/m3_series_results.csv`](followup_tables/m3_series_results.csv)
for all series-level scores.

Against fixed ARIMA on the same 20 M3 series, Auto's paired mean per-series
MASE difference (Auto minus ARIMA) was
{m3_arima['mean_series_mase_diff_auto_minus_model']:.8f}
({m3_arima['auto_wins']} Auto wins of {m3_arima['pairs']} pairs;
raw p={m3_arima['p_raw']:.12g}, Holm-adjusted p={m3_arima['p_holm']:.12g}).
This comparison was not significant after Holm correction.

The same fixed +{m3_ni['noninferiority_margin']:.2f} MASE non-inferiority
analysis was applied to the 20 per-series Auto-minus-no-shortlist differences.
The mean difference was {m3_ni['mean_paired_mase_difference']:.8f}; the
one-sided 95% t upper bound (df=19) was
{m3_ni['one_sided_95pct_t_upper_df19']:.8f}, and the percentile-bootstrap
upper bound was {m3_ni['one_sided_95pct_bootstrap_upper']:.8f}. **Non-inferiority
not established** because the bootstrap bound exceeds the margin, despite the
t bound being below it. The same test on six series narrowly failed because
its t upper bound was {ni['one_sided_95pct_t_upper_df5']:.8f}, above the
margin. The M3 extension applies the already-fixed margin; its result does
not erase the six-series failure. See
[`followup_tables/m3_shortlisting_noninferiority.csv`](followup_tables/m3_shortlisting_noninferiority.csv)
for the generated calculation.

## Generated evidence and reproducibility

- [`followup_tables/`](followup_tables/) contains machine-generated CSV and
  Markdown analyses, including series-level and model-level summaries.
- [`forecasting_m3/`](forecasting_m3/) contains the open source archive, its
  SHA-256-recorded metadata, the deterministic selected data, raw evaluations,
  and execution log.
- [`reproducibility/`](reproducibility/) contains both complete fresh
  imputation run outputs and logs.
- Run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ml-service .venv/bin/python
  experiments/results/paper_run_2026-10-11/analyze_followup.py` from the
  repository root to regenerate the follow-up tables and this note from saved
  CSV/JSON evidence.
"""
    (RUN_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    make_reproducibility_tables()
    make_six_series_shortlisting_analysis()
    make_m3_tables()
    audit_csv_tables()
    write_followup_readme()
    print(f"Analysis tables written to {TABLES_DIR}")


if __name__ == "__main__":
    main()
