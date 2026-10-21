"""Run a real-dataset benchmark one dataset at a time with safe resume support."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import pandas as pd

from datasets.registry import DATASETS, EXPERIMENTS_DIR
from run_real_datasets import MASK_RATES, MECHANISMS, METHODS


RUNNER = EXPERIMENTS_DIR / "run_real_datasets.py"
PROTOCOL_B_FOLDS = 5


def _expected_rows(protocol: str, repeats: int, section_status: str) -> int | None:
    if section_status == "skipped":
        return 0
    if section_status != "completed":
        return None
    if protocol == "A":
        return len(MECHANISMS) * len(MASK_RATES) * repeats * len(METHODS)
    return PROTOCOL_B_FOLDS * repeats * len(METHODS)


def is_complete_run(run_dir: Path, dataset: str, protocol: str) -> bool:
    """Check run metadata, protocol CSVs, summary status, and exact row counts."""
    config_path = run_dir / "run_config.json"
    summary_path = run_dir / "dataset_summary.csv"
    if not config_path.is_file() or not summary_path.is_file():
        return False
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        summary = pd.read_csv(summary_path)
    except (OSError, json.JSONDecodeError, pd.errors.ParserError):
        return False
    if dataset not in config.get("datasets_requested", []):
        return False
    configured_protocol = config.get("protocol")
    if (
        (protocol == "both" and configured_protocol != "both")
        or (protocol in {"A", "B"} and configured_protocol not in {protocol, "both"})
    ):
        return False
    dataset_summary = summary.loc[summary["name"].eq(dataset)]
    if len(dataset_summary) != 1 or dataset_summary.iloc[0].get("load_status") != "loaded":
        return False
    repeats = int(config.get("repeats", 0))
    if repeats < 1:
        return False

    checks: list[tuple[str, str, str]] = []
    if protocol in {"A", "both"}:
        checks.append(
            ("protocol_a_ground_truth.csv", "protocol_a_status", "A")
        )
    if protocol in {"B", "both"}:
        checks.append(
            ("protocol_b_natural_missingness.csv", "protocol_b_status", "B")
        )
    for filename, status_column, section_protocol in checks:
        csv_path = run_dir / filename
        if not csv_path.is_file() or status_column not in dataset_summary:
            return False
        status = str(dataset_summary.iloc[0][status_column])
        if section_protocol == "B" and status == "skipped_no_natural_missingness":
            expected = 0
        else:
            expected = _expected_rows(
                section_protocol, repeats, "skipped" if status == "skipped" else status
            )
        if expected is None:
            return False
        try:
            rows = pd.read_csv(csv_path)
        except (OSError, pd.errors.ParserError):
            return False
        if len(rows.loc[rows["dataset"].eq(dataset)]) != expected:
            return False
    return True


def _record_status(log_path: Path, record: dict[str, Any]) -> None:
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()


def run_stage(args: argparse.Namespace) -> Path:
    unknown = sorted(set(args.datasets).difference(DATASETS))
    if unknown:
        raise ValueError(f"Unknown dataset name(s): {', '.join(unknown)}")
    if not args.datasets:
        raise ValueError("Select at least one dataset.")
    if args.repeats < 1 or args.attempts < 1 or args.base_delay < 0:
        raise ValueError("--repeats and --attempts must be positive; --base-delay cannot be negative.")

    output_dir = Path(args.out).expanduser().resolve()
    protected = (
        EXPERIMENTS_DIR / "results" / "paper_run_2026-10-11"
    ).resolve()
    if output_dir == protected or protected in output_dir.parents:
        raise ValueError("Refusing to write inside the frozen paper_run_2026-10-11 results.")
    output_dir.mkdir(parents=True, exist_ok=True)
    status_log = output_dir / "stage_status.jsonl"
    failures: list[str] = []
    for dataset in args.datasets:
        final_dir = output_dir / dataset
        if final_dir.exists():
            if is_complete_run(final_dir, dataset, args.protocol):
                print(f"SKIP COMPLETE {dataset}: {final_dir}", flush=True)
                _record_status(status_log, {
                    "dataset": dataset,
                    "status": "skipped_complete",
                    "time_seconds": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                continue
            raise FileExistsError(
                f"Refusing to replace incomplete existing dataset directory: {final_dir}"
            )

        print(
            f"START {dataset}: protocol={args.protocol} repeats={args.repeats} "
            f"seed={args.seed} max_rows={args.max_rows}",
            flush=True,
        )
        _record_status(status_log, {
            "dataset": dataset,
            "status": "started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        succeeded = False
        for attempt in range(1, args.attempts + 1):
            attempt_dir = Path(
                tempfile.mkdtemp(prefix=f".{dataset}.attempt-{attempt}-", dir=output_dir)
            )
            started = time.monotonic()
            command = [
                sys.executable,
                str(RUNNER),
                "--datasets",
                dataset,
                "--protocol",
                args.protocol,
                "--repeats",
                str(args.repeats),
                "--seed",
                str(args.seed),
                "--max-rows",
                str(args.max_rows),
                "--out",
                str(attempt_dir),
            ]
            try:
                completed = subprocess.run(command, cwd=EXPERIMENTS_DIR.parent, check=False)
                elapsed = time.monotonic() - started
                if completed.returncode == 0 and is_complete_run(
                    attempt_dir, dataset, args.protocol
                ):
                    os.replace(attempt_dir, final_dir)
                    succeeded = True
                    print(
                        f"COMPLETE {dataset}: attempt={attempt} time_seconds={elapsed:.3f} "
                        f"dir={final_dir}",
                        flush=True,
                    )
                    _record_status(status_log, {
                        "dataset": dataset,
                        "status": "complete",
                        "attempt": attempt,
                        "time_seconds": elapsed,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    break
                reason = (
                    f"runner_exit={completed.returncode}"
                    if completed.returncode
                    else "output did not satisfy expected completion checks"
                )
                print(
                    f"FAILED {dataset}: attempt={attempt}/{args.attempts} "
                    f"time_seconds={elapsed:.3f} reason={reason}",
                    flush=True,
                )
                _record_status(status_log, {
                    "dataset": dataset,
                    "status": "failed_attempt",
                    "attempt": attempt,
                    "time_seconds": elapsed,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            finally:
                if attempt_dir.exists():
                    shutil.rmtree(attempt_dir)
            if not succeeded and attempt < args.attempts:
                time.sleep(args.base_delay * (2 ** (attempt - 1)))
        if not succeeded:
            print(f"EXHAUSTED {dataset}: failed after {args.attempts} attempts", flush=True)
            failures.append(dataset)
    if failures:
        raise RuntimeError(f"Benchmark datasets failed after retries: {', '.join(failures)}")
    return output_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", required=True)
    parser.add_argument("--protocol", choices=("A", "B", "both"), default="both")
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-rows", type=int, default=5000)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--base-delay", type=float, default=1.0)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.max_rows < 1:
        parser.error("--max-rows must be at least 1.")
    return args


def main() -> None:
    print(run_stage(parse_args()))


if __name__ == "__main__":
    main()
