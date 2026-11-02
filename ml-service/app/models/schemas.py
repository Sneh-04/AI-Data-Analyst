from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DatasetPayload(BaseModel):
    """Every ML endpoint receives the dataset as JSON records (like df.to_dict('records')).
    Spring Boot fetches the raw file from storage, converts to JSON, and forwards it here.
    Keeping this service stateless makes it horizontally scalable."""
    records: List[Dict[str, Any]] = Field(..., description="Dataset rows as JSON records")


class CleaningRequest(DatasetPayload):
    strategy: str = Field("auto", description="'auto' | 'knn' | 'multiple' | 'custom'")
    custom_strategies: Optional[Dict[str, str]] = None
    mnar_deltas: Optional[Dict[str, float]] = Field(
        None,
        description="Optional additive numeric delta adjustments for MNAR sensitivity scenarios",
    )
    remove_duplicates: bool = True
    outlier_method: str = Field("iqr", description="'iqr' | 'isolation_forest' | 'none'")
    outlier_columns: Optional[List[str]] = None


class TypeConversionRequest(DatasetPayload):
    conversions: Dict[str, str]


class ForecastRequest(DatasetPayload):
    date_column: str
    value_column: str
    periods: int = Field(30, ge=1, le=365)
    model: Literal["auto", "naive", "seasonal_naive", "holt", "arima", "sarima", "ensemble"] = Field(
        "auto",
        description="'auto' | 'naive' | 'seasonal_naive' | 'holt' | 'arima' | 'sarima' | 'ensemble'",
    )


class InsightsRequest(DatasetPayload):
    focus_columns: Optional[List[str]] = None
    use_llm: bool = False
    llm_provider: str = Field("offline", description="'offline' | 'openai' | 'gemini'")


class ChatRequest(DatasetPayload):
    dataset_id: int
    question: str
    history: Optional[List[Dict[str, str]]] = None
