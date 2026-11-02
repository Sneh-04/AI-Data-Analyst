#!/usr/bin/env bash
set -uo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
DEMO_CSV="${DEMO_CSV:-demo/demo_missing.csv}"
TIMEOUT="${TIMEOUT:-120}"

if [[ ! -f "$DEMO_CSV" ]]; then
  printf 'FAIL: demo CSV not found: %s\n' "$DEMO_CSV" >&2
  printf 'Run: python3 demo/make_demo_csv.py\n' >&2
  exit 1
fi
if ! command -v curl >/dev/null || ! command -v jq >/dev/null; then
  printf 'FAIL: smoke test requires curl and jq\n' >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
passed=0
failed=0
failures=()
token=""
dataset_id=""
records=""

record_pass() {
  printf 'PASS: %s\n' "$1"
  passed=$((passed + 1))
}

record_fail() {
  printf 'FAIL: %s — %s\n' "$1" "$2"
  failed=$((failed + 1))
  failures+=("$1")
}

request_json() {
  local name="$1" method="$2" path="$3" payload="$4" expected_status="$5" assertion="$6"
  local response_file="$tmp_dir/$name.json" status
  local -a curl_args=(--silent --show-error --max-time "$TIMEOUT" -o "$response_file" -w '%{http_code}' -X "$method")
  if [[ -n "$token" ]]; then
    curl_args+=(-H "Authorization: Bearer $token")
  fi
  if [[ -n "$payload" ]]; then
    curl_args+=(-H 'Content-Type: application/json' --data "$payload")
  fi
  if ! status="$(curl "${curl_args[@]}" "$BASE_URL$path")"; then
    record_fail "$name" "request failed (expected HTTP $expected_status)"
    return 1
  fi
  if [[ "$status" != "$expected_status" ]]; then
    record_fail "$name" "expected HTTP $expected_status, received HTTP $status"
    if [[ -s "$response_file" ]]; then
      sed -n '1,4p' "$response_file" >&2
    fi
    return 1
  fi
  if ! jq -e "$assertion" "$response_file" >/dev/null 2>&1; then
    record_fail "$name" "HTTP $status response did not contain the expected fields"
    sed -n '1,4p' "$response_file" >&2
    return 1
  fi
  record_pass "$name (HTTP $status)"
  return 0
}

email="smoke-$(date +%s)-$$@example.test"
registration_payload="$(jq -cn --arg email "$email" \
  '{email:$email, fullName:"Demo Smoke Test", password:"Demo-smoke!2026"}')"
if request_json "register user" POST /api/auth/register "$registration_payload" 201 \
  '(.token | type == "string" and length > 0) and (.email | type == "string")'; then
  token="$(jq -r '.token' "$tmp_dir/register user.json")"
else
  printf '\nSmoke test stopped: registration is required for the remaining checks.\n'
  printf 'Summary: %d passed, %d failed\n' "$passed" "$failed"
  exit 1
fi

upload_file="$tmp_dir/upload.json"
upload_status="$(curl --silent --show-error --max-time "$TIMEOUT" \
  -o "$upload_file" -w '%{http_code}' \
  -H "Authorization: Bearer $token" \
  -F "file=@$DEMO_CSV;type=text/csv" \
  "$BASE_URL/api/datasets/upload")" || upload_status=000
if [[ "$upload_status" == 201 ]] && jq -e \
  '(.datasetId | type == "number") and (.rowCount == 800) and (.columnCount == 5)' \
  "$upload_file" >/dev/null 2>&1; then
  dataset_id="$(jq -r '.datasetId' "$upload_file")"
  record_pass "upload demo CSV (HTTP $upload_status)"
else
  record_fail "upload demo CSV" "expected HTTP 201 and datasetId, 800 rows, and 5 columns (received HTTP $upload_status)"
  sed -n '1,4p' "$upload_file" >&2
  printf '\nSmoke test stopped: dataset upload is required for the remaining checks.\n'
  printf 'Summary: %d passed, %d failed\n' "$passed" "$failed"
  exit 1
fi

if request_json "load uploaded records" GET "/api/datasets/$dataset_id/records" "" 200 \
  'type == "array" and length == 800'; then
  records="$(jq -c '.' "$tmp_dir/load uploaded records.json")"
else
  printf '\nSmoke test stopped: uploaded records are required for the remaining checks.\n'
  printf 'Summary: %d passed, %d failed\n' "$passed" "$failed"
  exit 1
fi

health_payload="$(jq -cn --argjson records "$records" '{records:$records}')"
request_json "health score" POST "/api/datasets/$dataset_id/health-score" "$health_payload" 200 \
  '(.score | type == "number" and . >= 0 and . <= 100) and (.grade | type == "string" and length > 0)' || true

clean_payload="$(jq -cn --argjson records "$records" \
  '{records:$records,strategy:"auto",remove_duplicates:false,outlier_method:"none"}')"
request_json "clean dataset" POST "/api/datasets/$dataset_id/clean" "$clean_payload" 200 \
  '(.cleaned_records | type == "array" and length == 800) and (.summary | type == "object") and (.repair_log | type == "array")' || true

run_inference() {
  local estimand="$1" method="$2" name="inference $1 $2" payload
  payload="$(jq -cn --arg estimand "$estimand" --arg method "$method" \
    '{target_column:"x2",estimand:$estimand,method:$method,m:5,seed:42,deltas:[-1,0,1]} +
     (if $estimand == "ols_slope" then {predictor_column:"x1"} else {} end)')"
  request_json "$name" POST "/api/datasets/$dataset_id/inference" "$payload" 200 \
    '(.results | type == "array" and length == 3) and
     ([.results[].delta] | sort == [-1,0,1]) and
     all(.results[]; (.estimate | type == "number") and
       (.ci_lower | type == "number") and (.ci_upper | type == "number")) and
     (.naive_single_imputation.estimate | type == "number") and
     (.missing_fraction | type == "number" and . > 0.2 and . < 0.4) and
     (.warnings | type == "array")'
}

run_inference mean proper || true
run_inference mean improper || true
run_inference ols_slope proper || true
run_inference ols_slope improper || true

if jq -e 'length > 0 and (.[0] | has("date") and has("x1"))' <<<"$records" >/dev/null 2>&1; then
  forecast_payload="$(jq -cn \
    '{date_column:"date",value_column:"x1",periods:3,model:"naive"}')"
  request_json "forecast date and x1" POST "/api/datasets/$dataset_id/forecast" "$forecast_payload" 200 \
    '(.forecast | type == "array" and length == 3)' || true
else
  record_pass "forecast skipped (no date/value pair in the uploaded records)"
fi

report_file="$tmp_dir/report.pdf"
report_headers="$tmp_dir/report.headers"
report_status="$(curl --silent --show-error --max-time "$TIMEOUT" \
  -o "$report_file" -D "$report_headers" -w '%{http_code}' -X POST \
  -H "Authorization: Bearer $token" -H 'Content-Type: application/json' \
  --data '{"format":"PDF"}' "$BASE_URL/api/datasets/$dataset_id/reports")" || report_status=000
if [[ "$report_status" == 200 ]] &&
  grep -qi '^content-type: application/pdf' "$report_headers" &&
  [[ "$(head -c 5 "$report_file")" == '%PDF-' ]]; then
  record_pass "PDF report (HTTP $report_status)"
else
  record_fail "PDF report" "expected HTTP 200, application/pdf, and a %PDF- file (received HTTP $report_status)"
fi

printf '\nSmoke test summary: %d passed, %d failed\n' "$passed" "$failed"
if (( failed > 0 )); then
  printf 'Failed checks: %s\n' "${failures[*]}"
  exit 1
fi
printf 'All smoke checks passed.\n'
