"""
AI Data Analyst - ML Microservice
Upgraded from the original Streamlit utils/ logic into a stateless,
production-style FastAPI service. Spring Boot backend calls these
endpoints; this service never talks to the DB or users directly.
"""
import os
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cleaning, stats, forecasting, insights, health, chat
from app.routers import reports

app = FastAPI(
    title="AI Data Analyst - ML Service",
    description="Stateless ML/DL/NLP microservice for data cleaning, stats, forecasting, insights, and chat-with-data",
    version="1.0.0",
)

@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    internal_api_key = os.getenv("INTERNAL_API_KEY")
    if (
        request.url.path.startswith("/api/ml/")
        and internal_api_key
        and not secrets.compare_digest(request.headers.get("X-Internal-Key", ""), internal_api_key)
    ):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid internal API key"})
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("BACKEND_ORIGIN", "http://localhost:8080")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/ml/health", tags=["Health & Quality"])
app.include_router(cleaning.router, prefix="/api/ml/cleaning", tags=["Cleaning"])
app.include_router(stats.router, prefix="/api/ml/stats", tags=["Statistics"])
app.include_router(forecasting.router, prefix="/api/ml/forecasting", tags=["Forecasting"])
app.include_router(insights.router, prefix="/api/ml/insights", tags=["AI Insights"])
app.include_router(chat.router, prefix="/api/ml/chat", tags=["Chat with Data"])
app.include_router(reports.router, prefix="/api/ml/reports", tags=["Reports"])


@app.get("/")
def root():
    return {"service": "ai-data-analyst-ml-service", "status": "up"}
