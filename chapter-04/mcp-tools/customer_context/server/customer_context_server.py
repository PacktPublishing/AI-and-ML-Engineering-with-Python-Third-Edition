from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal

from fastmcp import FastMCP
from pydantic import BaseModel

from ..models.results import PolicyResult, TransactionSearchResult, TransactionSummary
from ..data.examples import TRANSACTIONS, CUSTOMERS, POLICY_DOCUMENTS
from ..utils.helpers import (
    _filter_transactions, 
    _project_transaction
)

mcp = FastMCP("Customer Context Server")

# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

@mcp.tool
def get_customer_metadata(
    customer_id: str,
    include: list[
        Literal[
            "segment",
            "home_region",
            "preferred_currency",
            "customer_since",
        ]
    ] | None = None,
) -> dict[str, Any]:
    """
    Fetch selected metadata for a customer.

    Use this when customer-level attributes are required. Prefer specifying
    only the fields needed for the current task rather than retrieving the
    complete customer record.
    """

    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        raise ValueError(f"Unknown customer: {customer_id}")

    include = include or [
        "segment",
        "home_region",
        "preferred_currency",
    ]

    return {
        "customer_id": customer_id,
        **{
            field: customer[field]
            for field in include
        },
    }


@mcp.tool
def get_transactions(
    customer_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    transaction_type: Literal["purchase", "refund"] | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    include: list[
        Literal[
            "processed_at",
            "type",
            "value",
            "merchant",
            "location",
            "description",
        ]
    ] | None = None,
    limit: int = 25,
    offset: int = 0,
    sort: Literal[
        "date_desc",
        "date_asc",
        "value_desc",
        "value_asc",
        "relevance",
    ] = "date_desc",
    query: str | None = None,
) -> TransactionSearchResult:
    """
    Retrieve a bounded set of customer transactions.

    Filter at source whenever possible. Use `include` to request only
    fields needed for the task. Results are paginated and capped to avoid
    injecting an unbounded transaction history into model context.

    `relevance` sorting requires `query`.
    """

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    if offset < 0:
        raise ValueError("offset cannot be negative")

    include = include or [
        "processed_at",
        "type",
        "value",
        "merchant",
    ]

    rows = _filter_transactions(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        min_value=min_value,
        max_value=max_value,
    )

    if sort == "date_desc":
        rows.sort(
            key=lambda row: row["processed_at"],
            reverse=True,
        )

    elif sort == "date_asc":
        rows.sort(key=lambda row: row["processed_at"])

    elif sort == "value_desc":
        rows.sort(
            key=lambda row: row["value"],
            reverse=True,
        )

    elif sort == "value_asc":
        rows.sort(key=lambda row: row["value"])

    elif sort == "relevance":
        if not query:
            raise ValueError(
                "query is required when sort='relevance'"
            )

        terms = query.lower().split()

        def relevance_score(row: dict) -> int:
            searchable = " ".join(
                str(row.get(field, ""))
                for field in (
                    "merchant",
                    "location",
                    "description",
                    "type",
                )
            ).lower()

            return sum(
                searchable.count(term)
                for term in terms
            )

        rows.sort(
            key=relevance_score,
            reverse=True,
        )

    total_matches = len(rows)

    page = rows[offset : offset + limit]

    next_offset = (
        offset + limit
        if offset + limit < total_matches
        else None
    )

    return TransactionSearchResult(
        customer_id=customer_id,
        total_matches=total_matches,
        returned=len(page),
        offset=offset,
        next_offset=next_offset,
        truncated=next_offset is not None,
        transactions=[
            _project_transaction(row, include)
            for row in page
        ],
    )


@mcp.tool
def summarize_transactions(
    customer_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    transaction_type: Literal["purchase", "refund"] | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> TransactionSummary:
    """
    Aggregate matching transactions without returning individual records.

    Prefer this tool when the task asks for a count, total, average or
    maximum rather than requiring transaction-level evidence.
    """

    rows = _filter_transactions(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        min_value=min_value,
        max_value=max_value,
    )

    values = [row["value"] for row in rows]

    return TransactionSummary(
        customer_id=customer_id,
        count=len(rows),
        total_value=round(sum(values), 2),
        average_value=(
            round(sum(values) / len(values), 2)
            if values
            else None
        ),
        maximum_value=max(values) if values else None,
    )


@mcp.tool
def search_policy_context(
    query: str,
    limit: int = 3,
) -> list[PolicyResult]:
    """
    Search policy documents for context relevant to a natural-language query.

    This demo uses a tiny lexical scorer. In a production system the body of
    this function could call pgvector, a search engine or another retrieval
    service while leaving the MCP tool contract unchanged.
    """

    if limit < 1 or limit > 5:
        raise ValueError("limit must be between 1 and 5")

    terms = {
        term.strip(".,?!").lower()
        for term in query.split()
        if len(term) > 2
    }

    matches = []

    for document in POLICY_DOCUMENTS:
        searchable = (
            f"{document['title']} "
            f"{document['section']} "
            f"{document['text']}"
        ).lower()

        matched_terms = sum(
            1 for term in terms
            if term in searchable
        )

        score = (
            matched_terms / len(terms)
            if terms
            else 0.0
        )

        if score > 0:
            matches.append(
                PolicyResult(
                    document_id=document["id"],
                    title=document["title"],
                    section=document["section"],
                    text=document["text"],
                    score=round(score, 3),
                )
            )

    matches.sort(
        key=lambda result: result.score,
        reverse=True,
    )

    return matches[:limit]


if __name__ == "__main__":
    mcp.run()