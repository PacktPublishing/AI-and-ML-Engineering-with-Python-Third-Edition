# ---------------------------------------------------------------------------
# Stub data
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "12345": {
        "customer_id": "12345",
        "segment": "retail",
        "home_region": "UK",
        "preferred_currency": "GBP",
        "customer_since": date(2021, 6, 12),
    },
    "67890": {
        "customer_id": "67890",
        "segment": "business",
        "home_region": "UK",
        "preferred_currency": "GBP",
        "customer_since": date(2019, 2, 3),
    },
}


TRANSACTIONS = [
    {
        "transaction_id": "txn-001",
        "customer_id": "12345",
        "processed_at": datetime(
            2026, 9, 27, 8, 30, tzinfo=timezone.utc
        ),
        "type": "purchase",
        "value": 79.99,
        "merchant": "Example Electronics",
        "location": "Glasgow",
        "description": "Headphones",
    },
    {
        "transaction_id": "txn-002",
        "customer_id": "12345",
        "processed_at": datetime(
            2026, 9, 27, 10, 15, tzinfo=timezone.utc
        ),
        "type": "refund",
        "value": 149.99,
        "merchant": "Example Electronics",
        "location": "Glasgow",
        "description": "Refund for damaged monitor",
    },
    {
        "transaction_id": "txn-003",
        "customer_id": "12345",
        "processed_at": datetime(
            2026, 9, 27, 14, 5, tzinfo=timezone.utc
        ),
        "type": "refund",
        "value": 220.00,
        "merchant": "Example Home",
        "location": "Edinburgh",
        "description": "Refund for returned furniture",
    },
    {
        "transaction_id": "txn-004",
        "customer_id": "12345",
        "processed_at": datetime(
            2026, 9, 28, 9, 45, tzinfo=timezone.utc
        ),
        "type": "purchase",
        "value": 24.50,
        "merchant": "Example Books",
        "location": "Glasgow",
        "description": "Books",
    },
    {
        "transaction_id": "txn-005",
        "customer_id": "12345",
        "processed_at": datetime(
            2026, 9, 28, 11, 10, tzinfo=timezone.utc
        ),
        "type": "refund",
        "value": 45.00,
        "merchant": "Example Books",
        "location": "Glasgow",
        "description": "Duplicate purchase refund",
    },
]


POLICY_DOCUMENTS = [
    {
        "id": "refund-policy-1",
        "title": "Retail refund policy",
        "section": "Refund authorisation",
        "text": (
            "Refunds above £100 require manager approval before "
            "processing, except where an automated statutory refund "
            "process applies."
        ),
    },
    {
        "id": "refund-policy-2",
        "title": "Retail refund policy",
        "section": "Standard refunds",
        "text": (
            "Standard refunds should normally be returned to the "
            "original payment method."
        ),
    },
    {
        "id": "refund-policy-3",
        "title": "Customer service procedures",
        "section": "Damaged goods",
        "text": (
            "Customers returning damaged goods may be asked to provide "
            "supporting information before a refund is processed."
        ),
    },
]