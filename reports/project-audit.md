# Project Audit Report

## Executive summary

This audit covered the repository in its current merged state, with emphasis on preserving the dirty working tree, existing app data, and research-upgrade changes already in place. The project is a Spring Boot backend, Python/FastAPI ML service, and React/Vite frontend, with PostgreSQL configured through Docker Compose and a live local database in the project environment.

Evidence-based status:
- Backend Java tests passed: 4/4.
- ML service tests passed after correcting the Python import configuration: 50/50.
- Frontend production build passed: Vite build succeeded.
- ML service startup smoke test passed on loopback (`http://127.0.0.1:8001`).
- Full database-backed end-to-end verification remains blocked because the project must not be started against the live user database, and no isolated PostgreSQL test database was available in a safe environment.
- Browser-level auth/upload/analysis flow remains unverified for the same reason.

Overall readiness: partially verified but not fully end-to-end proven.

## Architecture and actual data flow

### Verified architecture
- Backend: `backend/` contains the Spring Boot application and authenticated API gateway.
- ML service: `ml-service/` contains the stateless FastAPI service for cleaning, health scoring, forecasting, and insights.
- Frontend: `frontend/` contains the Vite React client.
- Database schema: `db/schema.sql` defines the core relational structure, including `datasets`, `dataset_health_scores`, and vector columns on `datasets`.
- Docker Compose: `docker-compose.yml` wires `postgres`, `ml-service`, `backend`, and `frontend` together.

### Actual flow intended by the code
1. User authenticates to the Spring Boot backend.
2. Frontend calls the backend API through `/api`.
3. Backend checks dataset ownership and retrieves the dataset file from storage.
4. Backend transforms the dataset rows to JSON and forwards them to the ML service endpoints.
5. ML service returns cleaning, health-scoring, or forecasting results.
6. Backend persists health-score history, forecast metadata, and dataset versions as needed.
7. Frontend renders the returned values.

### Observed integration points
- `backend/src/main/java/com/aidataanalyst/controller/DatasetController.java` calls `mlServiceClient.cleanDataset`, `healthScore`, and `runForecast` and persists related results.
- `backend/src/main/java/com/aidataanalyst/service/MlServiceClient.java` posts to `/api/ml/...` endpoints on the ML service.
- `ml-service/app/routers/forecasting.py` exposes `POST /api/ml/forecasting/run` and validates the dataset payload.
- `ml-service/app/routers/health.py` exposes `POST /api/ml/health/score` and accepts a `records` payload.
- `db/schema.sql` declares `dataset_health_scores` as a separate table with `dataset_id`, `score`, `grade`, and `assessed_at`.

## Safety and database assessment

### Critical safety rule observed
The backend configuration in `backend/src/main/resources/application.yml` contains:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/ai_data_analyst
    username: postgres
    password: postgres
  jpa:
    hibernate:
      ddl-auto: update
```

This is a risk if started against a live user database. The safe decision was made to avoid connecting the backend to the project database without an isolated test DB and explicit approval.

### Database schema check
`db/schema.sql` defines `dataset_health_scores` separately from `datasets`, with an index on `(dataset_id, assessed_at DESC, id DESC)`. This is consistent with an additive recording table rather than a replacement for `datasets.health_score`.

The project’s live `datasets` table is described as carrying `health_score`, `schema_embedding_openai`, and `schema_embedding_ollama` columns, while `dataset_health_scores` was not present in the previously inspected live DB. That is not automatically a bug; it is a schema drift/state mismatch that needs verification in a safe environment. The audit did not start the backend against the live environment to avoid modifying or destabilizing user data.

### Docker/db availability
The environment reported that Docker is installed, but the Docker daemon was not reachable at the configured socket:

```text
Cannot connect to the Docker daemon at unix:///Users/pawankumar/.colima/default/docker.sock. Is the docker daemon running?
```

Because of that, the project could not safely start or recreate an isolated PostgreSQL container in this session.

## Test commands executed and exact results

### 1. Backend Java tests
Command:
```sh
cd /Users/pawankumar/Downloads/ai-data-analyst-platform/backend && mvn test -DskipTests=false
```
Result:
- Tests run: 4
- Failures: 0
- Errors: 0
- Skipped: 0
- Build: SUCCESS

### 2. ML service tests
Initial run before fix:
```sh
cd /Users/pawankumar/Downloads/ai-data-analyst-platform/ml-service && . ../.venv/bin/activate && pytest -q
```
Result:
- 4 import errors during collection caused by missing Python path/module configuration.

Fix applied:
- Added `ml-service/pytest.ini` with:
```ini
[pytest]
pythonpath = .
testpaths = tests
```

Re-run:
```sh
cd /Users/pawankumar/Downloads/ai-data-analyst-platform/ml-service && . ../.venv/bin/activate && pytest -q
```
Result:
- 50 passed
- 0 failed
- 0 errors
- 76 warnings
- Runtime: ~7.04s

### 3. Frontend production build
Command:
```sh
cd /Users/pawankumar/Downloads/ai-data-analyst-platform/frontend && npm run build
```
Result:
- Vite build succeeded
- No build errors
- Warning only: one large JS chunk warning (non-fatal)

### 4. ML service startup smoke test
Command:
```sh
cd /Users/pawankumar/Downloads/ai-data-analyst-platform/ml-service && . ../.venv/bin/activate && PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8001
```
Smoke checks:
```sh
curl -sS http://127.0.0.1:8001/
```
Result:
```json
{"service":"ai-data-analyst-ml-service","status":"up"}
```

Additional endpoint probe to `/api/ml/health/score` and a forecast request returned a valid 400 / 404 response path status depending on the exact payload, which confirms the service is up and validating requests correctly rather than silently failing.

## Bugs found and fixes made

### 1. ML service pytest import configuration issue
- File(s): `ml-service/pytest.ini` added.
- Symptom: all ML tests failed during collection with `ModuleNotFoundError: No module named 'app'`.
- Cause: The project did not have a `pytest.ini`/Python path configuration, so the app package was not importable from the repo root when tests were run in the standard way.
- Fix: Added `pythonpath = .` to ensure `app` resolves correctly in the `ml-service` project.

### 2. API contract mismatch risk during direct curl probes
- Observed: A raw curl to `/api/ml/health/score` with a body of `{"data":...}` fails because the request model expects `records`, not `data`.
- Current status: This is not an application bug; it is a contract mismatch between a hand-written probe and the service’s actual request schema.
- Verified expectation: `ml-service/app/models/schemas.py` defines `DatasetPayload.records`, not `data`.

### 3. No database-backed full app verification possible without a safe isolated DB
- Status: This is a project block, not a code bug.
- Reason: Starting the Spring Boot backend against the live database would violate the user’s safety requirement and could alter user data under `ddl-auto: update`.

## Features verified versus not verified

### Verified
- Backend tests pass.
- ML service tests pass.
- Frontend build passes.
- ML API can start and respond on loopback.
- Research benchmark runner is safe and uses a temporary output dir (`experiments/run_research_benchmarks.sh`).
- The health/forecast model logic in the ML service is coherent and the unit tests directly cover key edge cases, including MASE boundaries and constant-series handling.

### Not verified / blocked
- Full end-to-end login → upload → clean → health → forecast → frontend display flow.
- Browser-level authenticated flow.
- Database-backed backend integration against a non-user database.
- Real backend startup against Postgres in a safe environment.
- DS access/ownership flow under live application context.

## Research and benchmark integrity

The repository contains benchmark scripts and research-related outputs in `experiments/`. The safe runner uses a temporary output directory rather than writing into the primary result tree.

The audit did not find evidence that the project was claiming more than the code and tests could support. The benchmark scripts remain research artifacts that need to be interpreted as observed results rather than universal claims of superiority.

## Prioritized fixes and remaining risks

### Critical
- Safe database isolation for full application validation.

### High
- Provide a dedicated PostgreSQL test database and a reproducible way to start the backend against it without touching the user database.
- Add a documented local test recipe for the full stack that does not rely on the live user DB.

### Medium
- Document the exact ML request contract (`records`) so frontend/backend callers and external tooling use the same JSON payload contract.
- Consider adding a lightweight integration test for the backend + ML service contract using a mock or isolated test database.

### Low
- Large frontend bundle warning remains non-fatal but could be optimized later.
- Some warning noise in the ML test suite is not a failure but indicates statistical warnings from `statsmodels`.

## Remaining blockers and unverified behavior

- No safe isolated PostgreSQL environment was available in this session.
- Docker daemon not reachable, so containerized database startup was not possible.
- Backend application startup against the live database was not performed because it risks user data, especially with `ddl-auto: update`.
- Browser-level end-to-end authenticated validation could not be completed under the required safety conditions.

## Exact next steps

1. Create or attach to a non-production Postgres database (for example `ai_data_analyst_test`) and configure backend settings to point to it.
2. Start the ML service and backend against that isolated DB.
3. Run the real login/upload/inspect/clean/health/forecast flow using a test dataset.
4. Verify the rendered frontend values match the backend and ML service payloads.
5. Only after that, make a final determination on full application readiness.

## Final verdict

The project is partially validated but not fully verified end-to-end. The merged code currently shows:
- working backend unit tests,
- working ML service tests,
- working frontend build,
- working ML service startup,
- but no safe proof of the complete dataset lifecycle against a protected database and app runtime.

For safety and correctness, the true end-to-end application should be treated as unproven until it is run against an isolated test database and the full flow is observed in a non-production environment.
