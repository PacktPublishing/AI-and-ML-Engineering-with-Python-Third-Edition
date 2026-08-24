# Bedrock FinOps demo: token usage by model

A minimal demo for the FinOps chapter. It generates a small amount of Amazon
Bedrock traffic against two text models with very different pricing, prints
the token counts Bedrock reports for every call, and then shows the same
usage in CloudWatch.

The flow the demo makes visible:

```text
prompt
  ↓
Bedrock model (Converse API)
  ↓
input/output token counts (response metadata)
  ↓
CloudWatch usage metrics (AWS/Bedrock, by ModelId)
  ↓
different model pricing = different cost
```

```text
bedrock-finops-demo/
├── pyproject.toml       # Python 3.12 + boto3, managed with uv
├── run_demo.py          # generates traffic, prints per-call token usage
├── calculate_cost.py    # turns observed token totals into illustrative cost
└── README.md
```

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- AWS credentials and a default region configured locally — see
  [AWS_CREDENTIALS.md](AWS_CREDENTIALS.md) for a step-by-step guide, from
  creating an identity to verifying with `aws sts get-caller-identity`
- Model access enabled in the Bedrock console (**Bedrock → Model access**)
  for the two models you use

### Model IDs

The defaults are US cross-region inference profiles:

| Role | Default model ID |
| --- | --- |
| Cheap | `us.amazon.nova-micro-v1:0` |
| Premium | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |

Substitute them for models available in your region and account — either
edit the constants at the top of `run_demo.py` or set environment variables.
For European regions, swap the `us.` prefix for `eu.`:

```bash
export AWS_REGION=eu-west-1
export CHEAP_MODEL_ID=eu.amazon.nova-micro-v1:0
export PREMIUM_MODEL_ID=eu.anthropic.claude-sonnet-4-5-20250929-v1:0
```

Any two on-demand text models that support `converse()` will work; choose
one cheap and one premium model so the cost difference is obvious.

## Run the demo

```bash
uv sync
uv run python run_demo.py
```

This makes 18 calls (3 prompts × 2 models × 3 repeats) with modest output
lengths, so the total cost is a few cents at most. It prints per-call token
counts and latency, a per-model summary table, and writes the totals to
`token_usage.json`.

Then calculate an illustrative cost from the observed totals:

```bash
uv run python calculate_cost.py
```

> **Update the prices first.** `MODEL_PRICING` in `calculate_cost.py`
> contains placeholder numbers. Copy the latest on-demand prices from the
> [Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/) — prices
> change over time and vary by region.

## Required AWS permissions

To run the demo:

- `bedrock:InvokeModel` on the models/inference profiles you call. When
  using cross-region inference profiles (the `us.`/`eu.` prefixed IDs), you
  need `bedrock:InvokeModel` on both the inference profile **and** the
  underlying foundation models in the regions it routes to.

To view the metrics in the console:

- `cloudwatch:ListMetrics` and `cloudwatch:GetMetricData` (included in the
  AWS-managed `CloudWatchReadOnlyAccess` policy).

No infrastructure is created; Bedrock publishes usage metrics to CloudWatch
automatically.

## View the token usage in CloudWatch

Bedrock emits per-model usage metrics to the `AWS/Bedrock` namespace with no
setup required. After running the demo:

1. Open the **CloudWatch** console **in the same region** you invoked
   Bedrock (the region printed by `run_demo.py`).
2. In the left navigation, choose **Metrics → All metrics**.
3. Under **Custom namespaces / AWS namespaces**, choose **AWS/Bedrock**.
4. Choose the **ModelId** dimension group ("By ModelId").
5. Tick **InputTokenCount** and **OutputTokenCount** for both model IDs you
   used (4 lines in total). You can filter the list by pasting a model ID
   into the search box.
6. Switch to the **Graphed metrics** tab and set, for every line:
   - **Statistic**: `Sum`
   - **Period**: `1 minute`
7. Set the time range (top right) to the last **15 minutes** (or **1 hour**
   if you ran the demo a while ago).

You should see clear spikes for both models at the time the demo ran, with
the same token totals as the script printed. This graph — with token counts
split by model — is the screenshot for the book.

Also worth graphing from the same namespace: **Invocations** (count of
calls) and **InvocationLatency** (compare the cheap model's latency to the
premium model's).

> Metrics can take a minute or two to appear after the invocations.

## Optional: model invocation logging

CloudWatch metrics give you token *counts* per model. If you want the full
request/response bodies per invocation (for deeper analysis or auditing),
enable **Model invocation logging** under **Bedrock → Settings** and point
it at a CloudWatch Logs group or S3 bucket. This is not required for this
demo and is deliberately left out of the minimum working example.
