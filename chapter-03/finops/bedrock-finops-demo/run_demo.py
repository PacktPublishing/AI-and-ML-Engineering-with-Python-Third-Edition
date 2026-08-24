"""Generate a small amount of Amazon Bedrock traffic and report token usage.

Invokes three prompts of increasing size against two Bedrock text models with
noticeably different pricing, using the Converse API. Token counts are taken
from the Bedrock response metadata (``response["usage"]``), not estimated
locally, so they match exactly what CloudWatch records in the ``AWS/Bedrock``
namespace (``InputTokenCount`` / ``OutputTokenCount``, dimensioned by ModelId).

Run it with:

    uv run python run_demo.py

The final per-model summary is also written to ``token_usage.json`` so that
``calculate_cost.py`` can turn the observed token totals into an illustrative
cost.
"""

import json
import os
from collections import defaultdict
from typing import Any

import boto3

# --- Configuration -----------------------------------------------------------
# Everything here can be overridden with environment variables.
#
# The default model IDs are US cross-region inference profiles. Substitute
# them for models you have enabled in your account (Bedrock console -> Model
# access) and region. For example, when running against a European region,
# swap the "us." prefix for "eu.":
#
#   eu.amazon.nova-micro-v1:0
#   eu.anthropic.claude-sonnet-4-5-20250929-v1:0
#
# Any two on-demand text models that support converse() will work; pick one
# cheap and one premium model so the cost difference is obvious.
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Amazon Nova Micro: one of the cheapest text models on Bedrock.
CHEAP_MODEL_ID = os.environ.get("CHEAP_MODEL_ID", "us.amazon.nova-micro-v1:0")

# Anthropic Claude Sonnet: a premium model, roughly two orders of magnitude
# more expensive per token than Nova Micro.
PREMIUM_MODEL_ID = os.environ.get(
    "PREMIUM_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)

# How many times each prompt/model pair is invoked. Keep this small -- it only
# needs to be enough to make the CloudWatch metrics clearly visible.
CALLS_PER_PROMPT = 1#3

# Cap response length so the whole demo costs very little.
MAX_OUTPUT_TOKENS = 400

# Three prompts of increasing size (and increasingly long expected answers).
PROMPTS = [
    "Give me one interesting fact about Glasgow.",
    "Explain the significance of symmetry in theoretical physics in about 150 words.",
    (
        "Explain the main stages of a HYROX race and why pacing matters, "
        "in about 300 words."
    ),
]

USAGE_FILE = "token_usage.json"


def invoke_model(client: Any, model_id: str, prompt: str) -> dict[str, int]:
    """Invoke a Bedrock model via the Converse API and return call metrics.

    Args:
        client: A ``bedrock-runtime`` boto3 client.
        model_id: Bedrock model ID or inference profile ID.
        prompt: The user prompt to send.

    Returns:
        Token counts and latency reported by Bedrock for this call.
    """
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS, "temperature": 0.5},
    )
    usage = response["usage"]
    return {
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
        "total_tokens": usage["totalTokens"],
        "latency_ms": response["metrics"]["latencyMs"],
    }


def main() -> None:
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    totals: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
    )

    print(f"Region: {AWS_REGION}")
    print(f"Models: {CHEAP_MODEL_ID}, {PREMIUM_MODEL_ID}")
    print(f"Calls:  {CALLS_PER_PROMPT} per prompt per model\n")

    for model_id in (CHEAP_MODEL_ID, PREMIUM_MODEL_ID):
        for prompt in PROMPTS:
            for _ in range(CALLS_PER_PROMPT):
                metrics = invoke_model(client, model_id, prompt)
                print(
                    f"{model_id}  "
                    f"in={metrics['input_tokens']:>4}  "
                    f"out={metrics['output_tokens']:>4}  "
                    f"total={metrics['total_tokens']:>4}  "
                    f"latency={metrics['latency_ms']:>6} ms"
                )
                model_totals = totals[model_id]
                model_totals["requests"] += 1
                model_totals["input_tokens"] += metrics["input_tokens"]
                model_totals["output_tokens"] += metrics["output_tokens"]
                model_totals["total_tokens"] += metrics["total_tokens"]

    print("\nSummary by model")
    print(f"{'model':<50} {'requests':>8} {'input':>8} {'output':>8} {'total':>8}")
    for model_id, model_totals in totals.items():
        print(
            f"{model_id:<50} "
            f"{model_totals['requests']:>8} "
            f"{model_totals['input_tokens']:>8} "
            f"{model_totals['output_tokens']:>8} "
            f"{model_totals['total_tokens']:>8}"
        )

    with open(USAGE_FILE, "w") as f:
        json.dump(dict(totals), f, indent=2)
    print(f"\nWrote per-model token totals to {USAGE_FILE}")
    print("Now open CloudWatch to see the same traffic (see README.md).")


if __name__ == "__main__":
    main()
