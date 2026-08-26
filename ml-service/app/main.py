"""
AI Data Analyst - ML Microservice
Upgraded from the original Streamlit utils/ logic into a stateless,
production-style FastAPI service. Spring Boot backend calls these
endpoints; this service never talks to the DB or users directly.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cleaning, stats, forecasting, insights, health, chat
from app.routers import reports

app = FastAPI(
    title="AI Data Analyst - ML Service",
    description="Stateless ML/DL/NLP microservice for data cleaning, stats, forecasting, insights, and chat-with-data",
    version="1.0.0",
)

# In production restrict this to the Spring Boot gateway's origin only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
