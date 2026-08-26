from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetPayload(BaseModel):
    """Every ML endpoint receives the dataset as JSON records (like df.to_dict('records')).
    Spring Boot fetches the raw file from storage, converts to JSON, and forwards it here.
    Keeping this service stateless makes it horizontally scalable."""
    records: List[Dict[str, Any]] = Field(..., description="Dataset rows as JSON records")


class CleaningRequest(DatasetPayload):
    strategy: str = Field("auto", description="'auto' | 'knn' | 'custom'")
    custom_strategies: Optional[Dict[str, str]] = None
    remove_duplicates: bool = True
    outlier_method: str = Field("iqr", description="'iqr' | 'isolation_forest' | 'none'")
    outlier_columns: Optional[List[str]] = None


class TypeConversionRequest(DatasetPayload):
    conversions: Dict[str, str]


class ForecastRequest(DatasetPayload):
    date_column: str
    value_column: str
    periods: int = 30
    model: str = Field("auto", description="'auto' | 'holt' | 'arima' | 'sarima' | 'prophet'")


class InsightsRequest(DatasetPayload):
    focus_columns: Optional[List[str]] = None
    use_llm: bool = False
    llm_provider: str = Field("offline", description="'offline' | 'openai' | 'gemini'")


class ChatRequest(DatasetPayload):
    dataset_id: int
    question: str
    history: Optional[List[Dict[str, str]]] = None
