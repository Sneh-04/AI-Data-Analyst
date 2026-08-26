"""
Upgrades over repo's utils/ai_chat.py (single-shot prompt stuffing):
- Deterministic intent router handles common question types (aggregation,
  filtering, top-N, column lookup) directly against the dataframe — fast,
  free, and never hallucinates numbers.
- Falls back to an LLM-generated pandas query for anything the router can't
  classify, still executed locally so the answer is grounded in real data.

Next upgrade (Phase 3, needs infra): swap this router for a RAG pipeline —
embed the dataset schema + row samples into pgvector, retrieve relevant
context per question, and let the LLM generate+execute a SQL query against
Postgres instead of an in-memory dataframe. Interface below (`answer_question`)
stays the same so the router swap won't ripple into the API layer.
"""
import re
import pandas as pd
from app.services import rag_service


def answer_question(df: pd.DataFrame, question: str, dataset_id: int | None = None) -> dict:
    q = question.lower().strip()

    # "average/mean of <column>"
    m = re.search(r"(average|mean) (?:of )?([a-zA-Z_ ]+)", q)
    if m:
        col = _match_column(df, m.group(2))
        if col:
            return _numeric_answer(df, col, "mean", f"The average {col} is {df[col].mean():.2f}.")

    # "sum/total of <column>"
    m = re.search(r"(sum|total) (?:of )?([a-zA-Z_ ]+)", q)
    if m:
        col = _match_column(df, m.group(2))
        if col:
            return _numeric_answer(df, col, "sum", f"The total {col} is {df[col].sum():.2f}.")

    # "max/highest <column>"
    m = re.search(r"(max|maximum|highest) ([a-zA-Z_ ]+)", q)
    if m:
        col = _match_column(df, m.group(2))
        if col:
            return _numeric_answer(df, col, "max", f"The highest {col} is {df[col].max():.2f}.")

    # "min/lowest <column>"
    m = re.search(r"(min|minimum|lowest) ([a-zA-Z_ ]+)", q)
    if m:
        col = _match_column(df, m.group(2))
        if col:
            return _numeric_answer(df, col, "min", f"The lowest {col} is {df[col].min():.2f}.")

    # "how many rows / count"
    if "how many rows" in q or "row count" in q or q.strip() == "count":
        return {"answer": f"The dataset has {len(df)} rows.", "value": len(df)}

    # "top N <column>"
    m = re.search(r"top (\d+) ([a-zA-Z_ ]+)", q)
    if m and pd.api.types.is_numeric_dtype(df.get(_match_column(df, m.group(2)), pd.Series(dtype=float))):
        n = int(m.group(1))
        col = _match_column(df, m.group(2))
        top = df.nlargest(n, col)
        return {"answer": f"Top {n} rows by {col}:", "records": top.to_dict(orient="records")}

    return rag_service.answer_with_rag(dataset_id, question, df)


def _match_column(df: pd.DataFrame, phrase: str) -> str | None:
    phrase = phrase.strip().rstrip("?").strip()
    for col in df.columns:
        if col.lower() == phrase or col.lower() in phrase or phrase in col.lower():
            return col
    return None


def _numeric_answer(df: pd.DataFrame, col: str, op: str, text: str) -> dict:
    if not pd.api.types.is_numeric_dtype(df[col]):
        return {"answer": f"'{col}' isn't a numeric column, so I can't compute {op}.", "value": None}
    value = getattr(df[col], op)()
    return {"answer": text, "value": round(float(value), 2)}
