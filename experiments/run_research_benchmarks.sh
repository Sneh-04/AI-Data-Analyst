#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if [ -z "${AI_DATA_ANALYST_RESULTS_DIR:-}" ]; then
  AI_DATA_ANALYST_RESULTS_DIR=$(mktemp -d "${TMPDIR:-/tmp}/ai-data-analyst-research.XXXXXX")
fi
mkdir -p "$AI_DATA_ANALYST_RESULTS_DIR"
export AI_DATA_ANALYST_RESULTS_DIR

printf 'Research benchmark outputs: %s\n' "$AI_DATA_ANALYST_RESULTS_DIR"
"$PYTHON" imputation_research_benchmark.py
"$PYTHON" mnar_detector_benchmark.py
"$PYTHON" forecasting_research_benchmark.py
"$PYTHON" dq_sensitivity_benchmark.py
