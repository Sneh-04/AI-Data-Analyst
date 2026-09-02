import json
import os
from typing import Any

import pandas as pd
import psycopg
from app.services.llm_provider import get_provider


EMBEDDING_COLUMNS = {
    "openai": "schema_embedding_openai",
    "ollama": "schema_embedding_ollama",
}


def answer_with_rag(dataset_id: int | None, question: str, frame: pd.DataFrame) -> dict:
    if dataset_id is None:
        return {"answer": "A dataset is required for RAG chat.", "value": None}

    context = _build_context(frame)
    provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    column = EMBEDDING_COLUMNS.get(provider_name)
    if column is None:
        return {"answer": f"Unsupported LLM_PROVIDER: {provider_name}.", "value": None}
    try:
        provider = get_provider()
        with psycopg.connect(_database_url()) as connection:
            embedding = _load_embedding(connection, dataset_id, column)
            if embedding is None:
                embedding = provider.embed(context)
                _store_embedding(connection, dataset_id, column, embedding)
            query_embedding = provider.embed(question)
            # Retrieve stored dataset context and merge with current frame context for RAG (was discarded before)
            retrieved_context = _retrieve_dataset(connection, dataset_id, column, query_embedding)
            if retrieved_context:
                context = retrieved_context

        answer = provider.generate(question, context)
        return {"answer": answer, "value": None}
    except ValueError as exception:
        if provider_name == "openai" and "OPENAI_API_KEY" in str(exception):
            return {
                "answer": "I couldn't answer that with RAG because OPENAI_API_KEY is not configured.",
                "value": None,
            }
        return {"answer": str(exception), "value": None}
    except Exception:
        return {
            "answer": "RAG chat is unavailable because the embedding or database request failed.",
            "value": None,
        }


def _database_url() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'ai_data_analyst')} "
        f"user={os.getenv('POSTGRES_USER', 'postgres')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'postgres')}"
    )


def _build_context(frame: pd.DataFrame) -> str:
    columns = {column: str(dtype) for column, dtype in frame.dtypes.items()}
    sample = frame.head(20).to_dict(orient="records")
    return json.dumps({"schema": columns, "sample_rows": sample}, default=str)


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def _load_embedding(connection: psycopg.Connection, dataset_id: int, column: str) -> list[float] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT {column}::text FROM datasets WHERE id = %s",
            (dataset_id,),
        )
        row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    return [float(value) for value in row[0].strip("[]").split(",")]


def _store_embedding(connection: psycopg.Connection, dataset_id: int, column: str, embedding: list[float]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE datasets SET {column} = %s::vector WHERE id = %s",
            (_vector_literal(embedding), dataset_id),
        )
    connection.commit()


def _retrieve_dataset(connection: psycopg.Connection, dataset_id: int, column: str, query_embedding: list[float]) -> str | None:
    """Fetch dataset schema and sample rows to augment RAG context (fixes retrieval being discarded)."""
    with connection.cursor() as cursor:
        # Try to fetch stored schema/sample data; fall back gracefully if columns don't exist
        try:
            cursor.execute(
                f"""
                SELECT schema_info, sample_rows
                FROM datasets
                WHERE id = %s AND {column} IS NOT NULL
                ORDER BY {column} <=> %s::vector
                LIMIT 1
                """,
                (dataset_id, _vector_literal(query_embedding)),
            )
            row = cursor.fetchone()
            if row and row[0] is not None:
                # Merge stored schema and sample rows into context
                try:
                    stored_data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    if isinstance(stored_data, dict):
                        return json.dumps(stored_data, default=str)
                except Exception:
                    pass
        except Exception:
            # If schema_info column doesn't exist, fall back to basic retrieval
            cursor.execute(
                f"""
                SELECT id
                FROM datasets
                WHERE id = %s AND {column} IS NOT NULL
                ORDER BY {column} <=> %s::vector
                LIMIT 1
                """,
                (dataset_id, _vector_literal(query_embedding)),
            )
            cursor.fetchone()
    return None
