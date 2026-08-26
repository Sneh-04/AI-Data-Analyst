import json
import os
from typing import Any

import pandas as pd
import psycopg
from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-3-small"


def answer_with_rag(dataset_id: int | None, question: str, frame: pd.DataFrame) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "answer": "I couldn't answer that with RAG because OPENAI_API_KEY is not configured.",
            "value": None,
        }
    if dataset_id is None:
        return {"answer": "A dataset is required for RAG chat.", "value": None}

    context = _build_context(frame)
    client = OpenAI(api_key=api_key)
    try:
        with psycopg.connect(_database_url()) as connection:
            embedding = _load_embedding(connection, dataset_id)
            if embedding is None:
                embedding = _create_embedding(client, context)
                _store_embedding(connection, dataset_id, embedding)
            query_embedding = _create_embedding(client, question)
            _retrieve_dataset(connection, dataset_id, query_embedding)

        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer only from the supplied dataset context. If the context is insufficient, "
                        "say so. Do not invent values or rows. Return a concise natural-language answer."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Dataset context:\n{context}\n\nQuestion: {question}",
                },
            ],
        )
        answer = completion.choices[0].message.content or "I couldn't generate an answer."
        return {"answer": answer, "value": None}
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


def _create_embedding(client: OpenAI, text: str) -> list[float]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def _load_embedding(connection: psycopg.Connection, dataset_id: int) -> list[float] | None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT schema_embedding::text FROM datasets WHERE id = %s",
            (dataset_id,),
        )
        row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    return [float(value) for value in row[0].strip("[]").split(",")]


def _store_embedding(connection: psycopg.Connection, dataset_id: int, embedding: list[float]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE datasets SET schema_embedding = %s::vector WHERE id = %s",
            (_vector_literal(embedding), dataset_id),
        )
    connection.commit()


def _retrieve_dataset(connection: psycopg.Connection, dataset_id: int, query_embedding: list[float]) -> Any:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM datasets
            WHERE id = %s AND schema_embedding IS NOT NULL
            ORDER BY schema_embedding <=> %s::vector
            LIMIT 1
            """,
            (dataset_id, _vector_literal(query_embedding)),
        )
        return cursor.fetchone()
