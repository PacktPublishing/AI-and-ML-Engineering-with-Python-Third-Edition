"""Calculate illustrative cost from the token totals observed by run_demo.py.

Reads ``token_usage.json`` (written by ``run_demo.py``) and applies
per-million-token prices:

    cost = (
        input_tokens / 1_000_000 * input_price_per_million
        + output_tokens / 1_000_000 * output_price_per_million
    )

Run it with:

    uv run python calculate_cost.py
"""

import json
import sys

# --- Pricing ------------------------------------------------------------------
# These prices are ILLUSTRATIVE PLACEHOLDERS, not a source of truth. AWS
# prices change over time and vary by region and by commitment type
# (on-demand vs provisioned). Copy the latest on-demand prices from
# https://aws.amazon.com/bedrock/pricing/ before running this script, and
# make sure the keys match the model IDs you used in run_demo.py.
MODEL_PRICING = {
    "us.amazon.nova-micro-v1:0": {
        "input_per_million": 0.035,
        "output_per_million": 0.14,
    },
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": {
        "input_per_million": 3.00,
        "output_per_million": 15.00,
    },
}

USAGE_FILE = "token_usage.json"


def calculate_cost(usage: dict[str, int], pricing: dict[str, float]) -> float:
    """Calculate the cost of the supplied token usage for one model.

    Args:
        usage: Token totals with ``input_tokens`` and ``output_tokens`` keys.
        pricing: Prices per million tokens for input and output.

    Returns:
        Illustrative cost in USD.
    """
    return (
        usage["input_tokens"] / 1_000_000 * pricing["input_per_million"]
        + usage["output_tokens"] / 1_000_000 * pricing["output_per_million"]
    )


def main() -> None:
    try:
        with open(USAGE_FILE) as f:
            observed_usage: dict[str, dict[str, int]] = json.load(f)
    except FileNotFoundError:
        sys.exit(f"{USAGE_FILE} not found -- run `uv run python run_demo.py` first.")

    print(f"{'model':<50} {'input':>8} {'output':>8} {'cost (USD)':>12}")
    total_cost = 0.0
    for model_id, usage in observed_usage.items():
        pricing = MODEL_PRICING.get(model_id)
        if pricing is None:
            print(
                f"{model_id:<50} -- no entry in MODEL_PRICING, "
                "add one with the latest AWS prices"
            )
            continue
        cost = calculate_cost(usage, pricing)
        total_cost += cost
        print(
            f"{model_id:<50} "
            f"{usage['input_tokens']:>8} "
            f"{usage['output_tokens']:>8} "
            f"{cost:>12.6f}"
        )

    print(f"\n{'TOTAL':<50} {'':>8} {'':>8} {total_cost:>12.6f}")
    print(
        "\nSame prompts, very different bills: this is why model selection "
        "is a first-order FinOps decision."
    )


if __name__ == "__main__":
    main()
