# ---------------------------------------------------------------------------
# Structured result models
# ---------------------------------------------------------------------------
from pydantic import BaseModel
from typing import Any

class TransactionSearchResult(BaseModel):
    customer_id: str
    total_matches: int
    returned: int
    offset: int
    next_offset: int | None
    truncated: bool
    transactions: list[dict[str, Any]]


class TransactionSummary(BaseModel):
    customer_id: str
    count: int
    total_value: float
    average_value: float | None
    maximum_value: float | None


class PolicyResult(BaseModel):
    document_id: str
    title: str
    section: str
    text: str
    score: float