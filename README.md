# AI Data Analyst Platform

Full-stack rebuild of [Ganeshmuna/AI-Data-Analyst](https://github.com/Ganeshmuna/AI-Data-Analyst)
(a single-file Streamlit prototype) into a proper multi-tier system:

```
React (frontend/)  →  Spring Boot (backend/)  →  FastAPI ML service (ml-service/)
                              ↓
                        PostgreSQL (db/)
```

## What changed vs. the original repo

| Area | Original repo | This platform |
|---|---|---|
| Architecture | Single Streamlit app, no API layer | React SPA + Spring Boot gateway + FastAPI ML microservice |
| Persistence | None — session state only | PostgreSQL: users, workspaces, versioned datasets, dashboards, forecasts, chat history, audit log |
| Imputation | Mean/median/mode | + KNN imputation |
| Outliers | IQR only | + Isolation Forest (multivariate) |
| Forecasting | Exponential Smoothing / Holt's only | + ARIMA, SARIMA, auto-select by backtested MAPE/RMSE |
| Insights | Anomalies + correlations | + trend detection, LLM executive summary (grounded in computed stats, never hallucinated) |
| Chat with data | Single-shot LLM prompt | Deterministic query router (fast, free, no hallucination) with a documented RAG/pgvector upgrade path |
| Users | None | Multi-user, workspace-based, role-based access (schema in place) |
| Deployment | Desktop .exe/.app + PWA | Docker Compose, all 4 services |

## Run it

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend gateway: http://localhost:8080
- ML service (FastAPI docs): http://localhost:8000/docs
- Postgres: localhost:5432

## Local dev (without Docker)

```bash
# ML service
cd ml-service && pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload --port 8000

# Backend
cd backend && mvn spring-boot:run

# Frontend
cd frontend && npm install && npm run dev
```

## What's fully implemented vs. scaffolded

**Fully implemented and tested:**
- `ml-service/` — every endpoint (cleaning, health score, stats, forecasting, insights, chat) runs and was verified against sample data.
- `frontend/` — builds cleanly. Upload, overview, cleaning, forecasting, insights, chat, and reports call the Spring Boot API. `Visualization.jsx` is intentionally client-side only and does not persist chart configurations.
- `backend/` — authentication, JWT request filtering, CSV upload to local storage, dataset persistence, dataset records, cleaning/version persistence, restore, and report generation are implemented. The active report endpoint is in `DatasetController.java`; the unused `ReportController.java` stub was removed.
- `db/schema.sql` — full schema, ready to run. `users`, `workspaces`, `datasets`, `dataset_versions`, and `reports` currently have backend persistence.

**Scaffolded, needs finishing before production:**
- `backend/` — forecast persistence, chat session/message persistence, dashboard persistence, audit logging, workspace membership, scheduled reports, production JWT secret management, and refresh-token rotation are not implemented.
- The frontend still parses CSV in-browser for its active working dataset. The uploaded file is also persisted by Spring Boot, but pages currently use the client-side records rather than fetching `/api/datasets/{id}/records`.
- The following schema tables are currently schema-only with no backend persistence: `forecasts`, `chat_sessions`, `chat_messages`, `dashboards`, `audit_log`, and `workspace_members`.
- The ML insights LLM provider integration and the Phase 3 pgvector/RAG chat upgrade remain extension points; the current implementations are offline/deterministic.

## Suggested next phases
1. **Auth** — JWT filter in Spring Security, `/api/auth/login` + `/api/auth/register`, wire `users` table
2. **Real upload pipeline** — Spring Boot receives multipart file → object storage → `datasets` row → frontend fetches by `dataset_id` instead of parsing client-side
3. **Dataset versioning** — persist every cleaning operation into `dataset_versions`, add undo/redo in the Cleaning Studio UI
4. **RAG chat upgrade** — pgvector + embeddings, swap `chat_service.answer_question` for a retrieval+SQL-generation pipeline (interface is already designed for this swap)
5. **Reports** — ReportLab/Excel export service, Spring Batch for scheduled report emails
