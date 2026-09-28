# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
from datetime import date
from typing import Literal
from ..data.examples import TRANSACTIONS

def _filter_transactions(
    customer_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    transaction_type: Literal["purchase", "refund"] | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
) -> list[dict]:
    """Apply deterministic filters before returning anything to the model."""

    rows = [
        transaction
        for transaction in TRANSACTIONS
        if transaction["customer_id"] == customer_id
    ]

    if start_date is not None:
        rows = [
            row
            for row in rows
            if row["processed_at"].date() >= start_date
        ]

    if end_date is not None:
        rows = [
            row
            for row in rows
            if row["processed_at"].date() <= end_date
        ]

    if transaction_type is not None:
        rows = [
            row
            for row in rows
            if row["type"] == transaction_type
        ]

    if min_value is not None:
        rows = [
            row
            for row in rows
            if row["value"] >= min_value
        ]

    if max_value is not None:
        rows = [
            row
            for row in rows
            if row["value"] <= max_value
        ]

    return rows


def _project_transaction(
    transaction: dict,
    include: list[str],
) -> dict[str, Any]:
    """
    Return only fields explicitly useful to the caller.

    Identity is retained even if it was not requested so individual
    records can subsequently be referenced.
    """

    allowed = {
        "processed_at",
        "type",
        "value",
        "merchant",
        "location",
        "description",
    }

    fields = set(include)

    unknown = fields - allowed
    if unknown:
        raise ValueError(
            f"Unknown transaction fields requested: {sorted(unknown)}"
        )

    result = {
        "transaction_id": transaction["transaction_id"],
    }

    for field in include:
        result[field] = transaction[field]

    return result
