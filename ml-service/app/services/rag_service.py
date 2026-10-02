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

    context = _build_context(frame, question)
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
            # Merge retrieved (stored) schema with the current-frame context so
            # retrieval actually shapes the answer (was discarded before, and the
            # previous "fix" queried columns that don't exist in schema.sql --
            # schema_info/sample_rows -- which silently failed every time and made
            # it a no-op. This queries the real schema_json column instead.)
            retrieved_schema = _retrieve_dataset(connection, dataset_id, column, query_embedding)
            if retrieved_schema:
                context = json.dumps(
                    {"current_context": json.loads(context), "retrieved_schema": retrieved_schema},
                    default=str,
                )

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


def _build_context(frame: pd.DataFrame, question: str | None = None, max_rows: int = 20, max_cols: int = 15) -> str:
    """Schema + cell-budgeted sample rows (TableRAG-style budgeting; Chen et al.
    2024 / CRUSH4SQL, Pimplikar & Sarawagi-style collective selection). Instead of
    always dumping every column regardless of table width -- which blows the LLM's
    context window on wide tables and triggers "lost-in-the-middle" degradation --
    prioritize columns the question actually mentions, then fill the remaining
    budget with the rest, and report how many columns were omitted.
    """
    columns = list(frame.columns)
    if question and len(columns) > max_cols:
        q_lower = question.lower()
        mentioned = [c for c in columns if c.lower() in q_lower]
        remaining = [c for c in columns if c not in mentioned]
        selected = mentioned + remaining[: max(0, max_cols - len(mentioned))]
    else:
        selected = columns[:max_cols]

    schema = {column: str(frame[column].dtype) for column in selected}
    sample = frame[selected].head(max_rows).to_dict(orient="records")
    omitted = len(columns) - len(selected)
    return json.dumps(
        {"schema": schema, "sample_rows": sample, "columns_omitted": omitted},
        default=str,
    )


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


def _retrieve_dataset(connection: psycopg.Connection, dataset_id: int, column: str, query_embedding: list[float]) -> dict | None:
    """Retrieve the dataset's stored schema_json, ranked by embedding similarity.
    Uses the actual datasets.schema_json column (db/schema.sql) -- the prior
    version queried schema_info/sample_rows, which don't exist, so this always
    returned None in practice regardless of the embedding match.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT schema_json
            FROM datasets
            WHERE id = %s AND {column} IS NOT NULL
            ORDER BY {column} <=> %s::vector
            LIMIT 1
            """,
            (dataset_id, _vector_literal(query_embedding)),
        )
        row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    schema_json = row[0]
    if isinstance(schema_json, str):
        try:
            schema_json = json.loads(schema_json)
        except (json.JSONDecodeError, TypeError):
            return None
    return schema_json if isinstance(schema_json, dict) else None
