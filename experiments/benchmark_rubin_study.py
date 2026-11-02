#!/usr/bin/env python3
"""Outcome-blind runtime and process-memory benchmark for Study 2 methods.

The generated samples are performance fixtures only. This command does not
evaluate interval coverage or authorize execution of the registered study.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
import scipy
import sklearn

from rubin_study.imputers import analyze_ols_coefficient, impute_m_datasets, pool_scalar_analysis
from rubin_study.study2_methods import impute_uncertainty_ablation


_METHODS = ("mice_improper", "mice_proper", "bootstrap_pmm_candidate")
_SCENARIOS = (
    ("dgp1_bivariate_normal", "MCAR", 0.10),
    ("dgp1_bivariate_normal", "MCAR", 0.50),
    ("dgp2_lognormal", "MAR", 0.10),
    ("dgp2_lognormal", "MAR", 0.50),
    ("dgp3_quadratic", "MNAR", 0.10),
    ("dgp3_quadratic", "MNAR", 0.50),
)


def build_performance_fixture(
    dgp: str, mechanism: str, missing_rate: float, n: int, seed: int
) -> pd.DataFrame:
    """Create a deterministic synthetic input for timing, not inferential evaluation."""
    if n < 20:
        raise ValueError("n must be at least 20 for the benchmark fixture")
    if not 0 < missing_rate < 1:
        raise ValueError("missing_rate must be strictly between zero and one")
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    noise = rng.normal(size=n)
    if dgp == "dgp1_bivariate_normal":
        x2 = 0.4 + 0.7 * x1 + 0.75 * noise
    elif dgp == "dgp2_lognormal":
        x2 = np.exp(-0.2 + 0.35 * x1 + 0.45 * noise)
    elif dgp == "dgp3_quadratic":
        x2 = 0.3 + 0.45 * x1 + 0.3 * (x1**2 - 1.0) + 0.7 * noise
    else:
        raise ValueError(f"unknown performance fixture DGP: {dgp}")

    if mechanism == "MCAR":
        probabilities = np.full(n, missing_rate)
    else:
        score = x1 if mechanism == "MAR" else (x2 - np.mean(x2)) / np.std(x2)
        probabilities = _calibrated_logistic(score, missing_rate)
    missing = rng.random(n) < probabilities
    if int((~missing).sum()) < 5:
        keep = rng.choice(n, size=5, replace=False)
        missing[keep] = False
    if not missing.any():
        missing[int(rng.integers(0, n))] = True
    return pd.DataFrame({"x1": x1, "x2": np.where(missing, np.nan, x2)})


def estimate_workload(
    measurements: list[dict[str, Any]],
    condition_counts: dict[str, int],
    worker_assumptions: dict[int, float] | None = None,
) -> dict[str, Any]:
    """Extrapolate measured per-condition time; mark all parallel values as estimates."""
    worker_assumptions = worker_assumptions or {1: 1.0, 4: 0.75, 8: 0.55}
    by_method: dict[str, list[float]] = {method: [] for method in _METHODS}
    complete_seconds_by_method: dict[str, list[float]] = {
        method: [] for method in _METHODS
    }
    analysis_seconds_by_method: dict[str, list[float]] = {
        method: [] for method in _METHODS
    }
    rss_by_method: dict[str, list[int]] = {method: [] for method in _METHODS}
    scenario_method_seconds: dict[tuple[Any, ...], dict[str, float]] = {}
    for row in measurements:
        method = str(row["method"])
        if method not in by_method:
            raise ValueError(f"unexpected benchmark method: {method}")
        by_method[method].append(float(row["imputation_seconds_per_draw"]))
        imputation_seconds = float(
            row.get("imputation_seconds", float(row["imputation_seconds_per_draw"]) * 20)
        )
        analysis_seconds = float(row.get("analysis_and_pooling_seconds", 0.0))
        analysis_seconds_by_method[method].append(analysis_seconds)
        complete_seconds_by_method[method].append(
            imputation_seconds + analysis_seconds
        )
        rss_by_method[method].append(int(row["peak_process_rss_bytes"]))
        scenario_key = tuple(
            row.get(name) for name in ("dgp", "mechanism", "missing_rate", "scenario_id")
        )
        if all(value is None for value in scenario_key):
            scenario_key = ("single_scenario",)
        scenario_methods = scenario_method_seconds.setdefault(scenario_key, {})
        if method in scenario_methods:
            raise ValueError(f"duplicate method result in scenario: {scenario_key}/{method}")
        scenario_methods[method] = imputation_seconds + analysis_seconds
    if any(not values for values in by_method.values()):
        raise ValueError("every configured method requires at least one measurement")
    scenario_costs = []
    for scenario_key, scenario_methods in scenario_method_seconds.items():
        if set(scenario_methods) != set(_METHODS):
            raise ValueError(f"scenario lacks one or more methods: {scenario_key}")
        scenario_costs.append(sum(scenario_methods.values()))
    method_summary = {
        method: {
            "scenario_count": len(by_method[method]),
            "mean_seconds_per_draw": float(np.mean(by_method[method])),
            "median_seconds_per_draw": float(np.median(by_method[method])),
            "minimum_seconds_per_draw": float(np.min(by_method[method])),
            "maximum_seconds_per_draw": float(np.max(by_method[method])),
            "mean_analysis_and_pooling_seconds": float(
                np.mean(analysis_seconds_by_method[method])
            ),
            "mean_complete_method_seconds": float(
                np.mean(complete_seconds_by_method[method])
            ),
            "mean_end_to_end_seconds_per_draw": float(
                np.mean(complete_seconds_by_method[method]) / 20
            ),
            "minimum_complete_method_seconds": float(
                np.min(complete_seconds_by_method[method])
            ),
            "maximum_complete_method_seconds": float(
                np.max(complete_seconds_by_method[method])
            ),
            "maximum_peak_process_rss_bytes": max(rss_by_method[method]),
        }
        for method in _METHODS
    }

    estimates = {}
    for label, conditions in condition_counts.items():
        per_condition_mean = float(np.mean(scenario_costs))
        per_condition_median = float(np.median(scenario_costs))
        sequential_seconds = per_condition_mean * conditions
        parallel = {}
        for workers, efficiency in worker_assumptions.items():
            if workers < 1 or not 0 < efficiency <= 1:
                raise ValueError("worker counts and parallel efficiencies must be positive")
            parallel[str(workers)] = {
                "assumed_parallel_efficiency": efficiency,
                "estimated_wall_seconds": sequential_seconds / (workers * efficiency),
                "estimated_peak_worker_rss_bytes": max(
                    max(values) for values in rss_by_method.values()
                ) * workers,
            }
        estimates[label] = {
            "condition_count": conditions,
            "methods_per_condition": len(_METHODS),
            "m_per_method": 20,
            "sequential_estimated_hours_mean": sequential_seconds / 3600,
            "estimated_cpu_hours_at_single_worker": sequential_seconds / 3600,
            "sequential_estimated_hours_median": (
                per_condition_median * conditions / 3600
            ),
            "sequential_estimated_hours_range": [
                min(scenario_costs) * conditions / 3600,
                max(scenario_costs) * conditions / 3600,
            ],
            "parallel_estimates": parallel,
            "parallel_memory_note": (
                "max single-worker process peak RSS multiplied by workers; "
                "conservative and excludes scheduler/IPC overhead"
            ),
        }
    return {
        "extrapolation_scope": (
            "performance-only extrapolation from six synthetic timing fixtures; "
            "not a study result or feasibility guarantee"
        ),
        "per_method_measurements": method_summary,
        "workload_scenarios": estimates,
    }


def _calibrated_logistic(score: np.ndarray, rate: float) -> np.ndarray:
    standardized = (score - np.mean(score)) / np.std(score)
    low, high = -30.0, 30.0
    for _ in range(80):
        intercept = (low + high) / 2.0
        probabilities = 1.0 / (1.0 + np.exp(-np.clip(intercept + standardized, -35, 35)))
        if float(np.mean(probabilities)) < rate:
            low = intercept
        else:
            high = intercept
    intercept = (low + high) / 2.0
    return 1.0 / (1.0 + np.exp(-np.clip(intercept + standardized, -35, 35)))


def _peak_rss_bytes() -> int:
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024


def _physical_memory_bytes() -> int | None:
    try:
        page_size = int(os.sysconf("SC_PAGE_SIZE"))
        page_count = int(os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, OSError, ValueError):
        return None
    return page_size * page_count if page_size > 0 and page_count > 0 else None


def _declared_package_versions() -> dict[str, str]:
    requirements = Path(__file__).with_name("requirements.txt")
    declared = {}
    for line in requirements.read_text(encoding="utf-8").splitlines():
        if "==" in line and not line.lstrip().startswith("#"):
            package, version = line.split("==", maxsplit=1)
            declared[package.strip().lower().replace("-", "_")] = version.strip()
    return declared


def _run_worker(scenario: dict[str, Any]) -> dict[str, Any]:
    dgp = str(scenario["dgp"])
    mechanism = str(scenario["mechanism"])
    rate = float(scenario["missing_rate"])
    n = int(scenario["n"])
    m = int(scenario["m"])
    seed = int(scenario["seed"])
    method = str(scenario["method"])
    frame = build_performance_fixture(dgp, mechanism, rate, n, seed)

    start = time.perf_counter()
    if method in {"mice_improper", "mice_proper"}:
        completed = impute_m_datasets(frame, m, seed, method)
        pmm_diagnostics = None
    elif method == "bootstrap_pmm_candidate":
        result = impute_uncertainty_ablation(
            frame,
            m,
            seed,
            method,
            target_column="x2",
            return_diagnostics=True,
        )
        if not isinstance(result, tuple):
            raise RuntimeError("PMM benchmark did not return requested diagnostics")
        completed, pmm_diagnostics = result
    else:
        raise ValueError(f"unknown benchmark method: {method}")
    imputation_seconds = time.perf_counter() - start

    analysis_start = time.perf_counter()
    pooled = pool_scalar_analysis(
        completed, lambda data: analyze_ols_coefficient(data, "x2", "x1")
    )
    analysis_seconds = time.perf_counter() - analysis_start
    return {
        **scenario,
        "imputation_seconds": imputation_seconds,
        "imputation_seconds_per_draw": imputation_seconds / m,
        "analysis_and_pooling_seconds": analysis_seconds,
        "analysis_and_pooling_seconds_per_draw": analysis_seconds / m,
        "end_to_end_seconds": imputation_seconds + analysis_seconds,
        "end_to_end_seconds_per_draw": (imputation_seconds + analysis_seconds) / m,
        "peak_process_rss_bytes": _peak_rss_bytes(),
        "pmm_donor_diagnostic_draws": (
            len(pmm_diagnostics["draws"]) if pmm_diagnostics else None
        ),
        "pooled_estimate_finite": math.isfinite(pooled.estimate),
        "benchmark_scope": "synthetic performance fixture; no coverage evaluation",
    }


def run_benchmark(
    *,
    n: int = 500,
    m: int = 20,
    seed: int = 20261101,
    worker_assumptions: dict[int, float] | None = None,
) -> dict[str, Any]:
    """Run isolated processes for each method/scenario and derive workload estimates."""
    if n < 20 or m != 20:
        raise ValueError("benchmark requires n >= 20 and m=20 to match Study 2")
    measurements = []
    for scenario_index, (dgp, mechanism, rate) in enumerate(_SCENARIOS):
        for method in _METHODS:
            config = {
                "dgp": dgp,
                "mechanism": mechanism,
                "missing_rate": rate,
                "n": n,
                "m": m,
                "seed": seed + scenario_index,
                "method": method,
            }
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                json.dumps(config, separators=(",", ":")),
            ]
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                raise RuntimeError(
                    f"benchmark worker failed for {method}/{dgp}/{rate:.2f}:\n"
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )
            try:
                measurement = json.loads(result.stdout)
            except json.JSONDecodeError as error:
                raise RuntimeError(
                    f"benchmark worker returned invalid JSON: {result.stdout!r}"
                ) from error
            measurements.append(measurement)

    # Protocol v5.1: 3 DGPs * 7 mechanism settings * 3 rates * 100 replicates.
    # The 63,000 figure is the superseded 1,000-replicate scale, shown only as
    # a sensitivity projection and not written into the active study config.
    feasibility = estimate_workload(
        measurements,
        {
            "active_protocol_v5_1_100_replicates": 3 * 7 * 3 * 100,
            "illustrative_1000_replicates": 3 * 7 * 3 * 1000,
        },
        worker_assumptions,
    )
    actual_versions = {
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
    }
    declared_versions = _declared_package_versions()
    version_differences = {
        package: {
            "declared": declared_versions.get(package),
            "actual": actual_versions.get(package),
        }
        for package in actual_versions
        if declared_versions.get(package) != actual_versions.get(package)
    }
    return {
        "benchmark_status": "performance-only; no Study 2 coverage results generated",
        "fixture_note": (
            "One synthetic fixture per DGP/mechanism and 10%/50% missingness; "
            "fixture parameters are not protocol DGP parameters."
        ),
        "sample_size": n,
        "imputations_per_method": m,
        "seed": seed,
        "scenario_count": len(_SCENARIOS),
        "method_count": len(_METHODS),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "physical_memory_bytes": _physical_memory_bytes(),
            **actual_versions,
            "declared_experiments_requirements": declared_versions,
            "version_differences_vs_requirements": version_differences,
        },
        "measurements": measurements,
        "feasibility": feasibility,
    }


def write_benchmark_report(result: dict[str, Any], output_dir: Path) -> None:
    """Persist measured rows and explicitly qualified feasibility estimates."""
    output_dir.mkdir(parents=True, exist_ok=True)
    measurements = result["measurements"]
    with (output_dir / "runtime_samples.csv").open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        writer = csv.DictWriter(destination, fieldnames=list(measurements[0]))
        writer.writeheader()
        writer.writerows(measurements)
    feasibility = result["feasibility"]
    physical_memory = result["environment"]["physical_memory_bytes"]
    memory_assessment = {}
    for workload, estimate in feasibility["workload_scenarios"].items():
        memory_assessment[workload] = {}
        for workers, parallel in estimate["parallel_estimates"].items():
            projected = parallel["estimated_peak_worker_rss_bytes"]
            memory_assessment[workload][workers] = {
                "projected_peak_worker_rss_bytes": projected,
                "physical_memory_bytes": physical_memory,
                "projected_within_physical_memory": (
                    projected <= physical_memory if physical_memory is not None else None
                ),
                "estimated_wall_hours": parallel["estimated_wall_seconds"] / 3600,
            }
    feasibility["host_resource_assessment"] = {
        "physical_memory_bytes": physical_memory,
        "current_free_disk_bytes": shutil.disk_usage(output_dir).free,
        "study_output_storage_estimate_bytes": None,
        "storage_estimate_status": (
            "not estimated because the primary run output schema and runner are "
            "still blocked by protocol TODOs"
        ),
        "parallel_scenarios": memory_assessment,
        "wall_time_feasibility": (
            "not classified; no maximum acceptable wall-time was prespecified"
        ),
    }
    (output_dir / "benchmark_results.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    with (output_dir / "feasibility_estimates.csv").open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        columns = (
            "workload",
            "condition_count",
            "sequential_estimated_hours_mean",
            "estimated_cpu_hours_at_single_worker",
            "sequential_estimated_hours_min",
            "sequential_estimated_hours_max",
            "4_worker_estimated_hours",
            "8_worker_estimated_hours",
            "4_worker_estimated_peak_rss_gib",
            "8_worker_estimated_peak_rss_gib",
        )
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        for workload, estimate in feasibility["workload_scenarios"].items():
            writer.writerow({
                "workload": workload,
                "condition_count": estimate["condition_count"],
                "sequential_estimated_hours_mean": estimate[
                    "sequential_estimated_hours_mean"
                ],
                "estimated_cpu_hours_at_single_worker": estimate[
                    "estimated_cpu_hours_at_single_worker"
                ],
                "sequential_estimated_hours_min": estimate[
                    "sequential_estimated_hours_range"
                ][0],
                "sequential_estimated_hours_max": estimate[
                    "sequential_estimated_hours_range"
                ][1],
                "4_worker_estimated_hours": estimate["parallel_estimates"]["4"][
                    "estimated_wall_seconds"
                ] / 3600,
                "8_worker_estimated_hours": estimate["parallel_estimates"]["8"][
                    "estimated_wall_seconds"
                ] / 3600,
                "4_worker_estimated_peak_rss_gib": estimate["parallel_estimates"]["4"][
                    "estimated_peak_worker_rss_bytes"
                ] / 1024**3,
                "8_worker_estimated_peak_rss_gib": estimate["parallel_estimates"]["8"][
                    "estimated_peak_worker_rss_bytes"
                ] / 1024**3,
            })
    lines = [
        "# Study 2 performance feasibility benchmark",
        "",
        f"- Status: {result['benchmark_status']}.",
        f"- Sample size / imputations: n={result['sample_size']}, m={result['imputations_per_method']}.",
        f"- Fixture design: {result['fixture_note']}",
        f"- Environment: Python {result['environment']['python']}, scikit-learn {result['environment']['scikit_learn']}, "
        f"{result['environment']['cpu_count']} logical CPUs.",
        f"- Environment/manifest version differences: {json.dumps(result['environment']['version_differences_vs_requirements'], sort_keys=True)}.",
        "- Runtime samples are measured in isolated processes; peak RSS includes interpreter and imported-library memory.",
        "- Workload projections assume equal average cost per configured sample/mask condition and use six timing scenarios; ranges use scenario minima/maxima.",
        "- Parallel wall times are arithmetic projections at assumed 75% efficiency for 4 workers and 55% for 8; parallel execution was not run.",
        "- Memory projections multiply the largest measured worker peak by worker count; this is conservative and excludes IPC/scheduler overhead.",
        f"- Host assessment: {physical_memory / 1024**3:.2f} GiB physical RAM"
        if physical_memory is not None
        else "- Host assessment: physical RAM could not be queried",
        f"- Current free disk: {shutil.disk_usage(output_dir).free / 1024**3:.2f} GiB. See JSON for projected memory fit; no runtime feasibility cutoff was prespecified.",
        "- Study-result storage volume is not estimated: the inferential run output schema/runner remains unfinalized.",
        "- The active v5 workload is 6,300 sample/mask replicates; 63,000 is shown only as a 1,000-replicate scale projection. Neither projection changes or authorizes the study protocol.",
        "- This benchmark reports no empirical bias, coverage, or method ranking. Full Study 2 remains blocked by protocol freeze requirements.",
        "",
        "See `runtime_samples.csv`, `feasibility_estimates.csv`, and `benchmark_results.json`.",
    ]
    (output_dir / "BENCHMARK_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--m", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--worker", type=str, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker is not None:
        print(json.dumps(_run_worker(json.loads(args.worker)), allow_nan=False))
        return
    result = run_benchmark(n=args.n, m=args.m, seed=args.seed)
    if args.output_dir is None:
        raise SystemExit("--output-dir is required")
    write_benchmark_report(result, args.output_dir)
    print(json.dumps({
        "status": result["benchmark_status"],
        "output_dir": str(args.output_dir),
        "measured_worker_runs": len(result["measurements"]),
        "workload_estimates": {
            name: {
                "conditions": estimate["condition_count"],
                "mean_sequential_hours": estimate["sequential_estimated_hours_mean"],
            }
            for name, estimate in result["feasibility"]["workload_scenarios"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
