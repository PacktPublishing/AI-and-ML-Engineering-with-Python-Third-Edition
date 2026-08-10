"""
Low-level token accounting for a Claude Opus 5 call routed through an
Envoy AI Gateway, emitted as OpenTelemetry metrics.

Demonstrates the pattern described in Chapter 10: instrument at the call site,
attribute every token to a use case and an owning team, and keep the metric
dimensions low-cardinality enough to survive a real Prometheus/OTLP backend.

Envoy AI Gateway exposes an Anthropic-compatible /v1/messages endpoint, so the
official `anthropic` SDK works unchanged apart from `base_url`. The gateway
handles upstream credentials (direct Anthropic, Bedrock SigV4, Vertex), which
is why the client below never sees a provider key.

Requires:
    pip install anthropic opentelemetry-sdk opentelemetry-exporter-otlp
"""

from __future__ import annotations

import os
import socket
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

import anthropic
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# ---------------------------------------------------------------------------
# 1. Semantic convention constants
#
# The gen_ai.* conventions live in open-telemetry/semantic-conventions-genai and
# are still marked Development, so pin them as constants in one place rather
# than scattering string literals through the codebase. When the spec moves,
# you change this block, not fifty call sites.
# ---------------------------------------------------------------------------

GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_PROVIDER_NAME = "gen_ai.provider.name"      # replaced gen_ai.system in v1.37.0
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_TOKEN_TYPE = "gen_ai.token.type"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
GEN_AI_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"

SERVER_ADDRESS = "server.address"
ERROR_TYPE = "error.type"

# Local extensions. The spec has no token type for prompt-cache reads/writes,
# which on Claude are the single biggest lever on effective cost — so we add
# them as extra enum values rather than losing the signal.
TOKEN_TYPE_INPUT = "input"
TOKEN_TYPE_OUTPUT = "output"
TOKEN_TYPE_CACHE_READ = "cache_read"      # billed at ~10% of input
TOKEN_TYPE_CACHE_WRITE = "cache_write"    # billed at a premium to input

# Organisational dimensions. Prefix your own namespace so it is obvious at a
# glance which attributes are spec and which are yours.
AI_USE_CASE = "ai.use_case"
AI_TEAM = "ai.owning_team"
AI_COST_CENTRE = "ai.cost_centre"
AI_GATEWAY_ROUTE = "ai.gateway.route"


# ---------------------------------------------------------------------------
# 2. Telemetry bootstrap
#
# Identity of the *calling process* belongs on the Resource, not on every
# metric point. The backend joins it for you and you avoid multiplying
# cardinality across every series.
# ---------------------------------------------------------------------------

def build_resource(service_name: str, service_namespace: str) -> Resource:
    return Resource.create(
        {
            "service.name": service_name,
            "service.namespace": service_namespace,
            "service.version": os.getenv("APP_VERSION", "0.0.0-dev"),
            "service.instance.id": os.getenv("HOSTNAME", socket.gethostname()),
            "deployment.environment.name": os.getenv("ENVIRONMENT", "local"),
            "process.pid": os.getpid(),
            "process.runtime.name": "cpython",
        }
    )


def init_telemetry(resource: Resource) -> None:
    # Token counts are heavily right-skewed: a handful of long-context calls
    # dominate spend. Default histogram buckets top out far too low, so
    # override them or your p99 will be permanently pinned to the last bucket.
    token_buckets = [0, 100, 500, 1_000, 5_000, 10_000, 50_000,
                     100_000, 250_000, 500_000, 1_000_000]

    token_view = View(
        instrument_name="gen_ai.client.token.usage",
        aggregation=ExplicitBucketHistogramAggregation(boundaries=token_buckets),
    )

    metrics.set_meter_provider(
        MeterProvider(
            resource=resource,
            metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
            views=[token_view],
        )
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)


# ---------------------------------------------------------------------------
# 3. Call context
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CallContext:
    """Business metadata attached to every model invocation.

    Keep these low-cardinality. Anything unbounded — user id, request id,
    session id, tenant id in a large estate — goes on the span, never on the
    metric. A metric attribute with 100k distinct values will take down your
    time-series database long before it tells you anything useful.
    """

    use_case: str          # e.g. "kyc-doc-triage"
    owning_team: str       # e.g. "financial-crime-platform"
    cost_centre: str       # e.g. "CC-40871"
    extra: dict[str, str] = field(default_factory=dict)

    def as_attributes(self) -> dict[str, Any]:
        return {
            AI_USE_CASE: self.use_case,
            AI_TEAM: self.owning_team,
            AI_COST_CENTRE: self.cost_centre,
            **self.extra,
        }


# ---------------------------------------------------------------------------
# 4. Instrumented gateway client
# ---------------------------------------------------------------------------

class InstrumentedGatewayClient:
    """Thin wrapper over the Anthropic SDK pointed at Envoy AI Gateway."""

    def __init__(
        self,
        gateway_url: str,
        gateway_api_key: str,
        provider_name: str = "anthropic",
        gateway_route: str = "default",
    ) -> None:
        # The SDK sends x-api-key, which is what the gateway's
        # BackendSecurityPolicy expects from downstream clients. The real
        # provider credential is injected upstream by the gateway.
        self._client = anthropic.Anthropic(
            base_url=gateway_url,
            api_key=gateway_api_key,
            max_retries=2,
            timeout=120.0,
        )
        self._gateway_host = gateway_url.split("://")[-1].split("/")[0]
        self._provider_name = provider_name
        self._gateway_route = gateway_route

        meter = metrics.get_meter("ai.platform.gateway", "1.0.0")
        self._tracer = trace.get_tracer("ai.platform.gateway", "1.0.0")

        self._token_usage = meter.create_histogram(
            name="gen_ai.client.token.usage",
            unit="{token}",
            description="Number of tokens processed by a GenAI operation.",
        )
        self._duration = meter.create_histogram(
            name="gen_ai.client.operation.duration",
            unit="s",
            description="GenAI operation duration.",
        )
        # Derived, not observed. Useful for showback, but the rate table is a
        # config artefact with a shelf life measured in weeks — never hardcode.
        self._cost = meter.create_histogram(
            name="ai.client.cost.usd",
            unit="{USD}",
            description="Estimated USD cost of a GenAI operation.",
        )

    # -- public API ---------------------------------------------------------

    def create_message(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        ctx: CallContext,
        max_tokens: int = 4096,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> anthropic.types.Message:
        base_attrs = {
            GEN_AI_OPERATION_NAME: "chat",
            GEN_AI_PROVIDER_NAME: self._provider_name,
            GEN_AI_REQUEST_MODEL: model,
            SERVER_ADDRESS: self._gateway_host,
            AI_GATEWAY_ROUTE: self._gateway_route,
            **ctx.as_attributes(),
        }

        with self._observe(base_attrs, model, max_tokens, temperature) as obs:
            response = self._client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **({"temperature": temperature} if temperature is not None else {}),
                **kwargs,
            )
            obs["response"] = response
            return response

    def stream_message(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        ctx: CallContext,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> anthropic.types.Message:
        """Streaming variant.

        The usage block does not arrive with the first chunk: input counts come
        on message_start and output counts accumulate into message_delta. The
        SDK reconciles this for you via get_final_message(). If you hand-roll
        SSE parsing and only read message_start, your output token metric will
        silently read zero — a common and expensive instrumentation bug.
        """
        base_attrs = {
            GEN_AI_OPERATION_NAME: "chat",
            GEN_AI_PROVIDER_NAME: self._provider_name,
            GEN_AI_REQUEST_MODEL: model,
            SERVER_ADDRESS: self._gateway_host,
            AI_GATEWAY_ROUTE: self._gateway_route,
            **ctx.as_attributes(),
        }

        with self._observe(base_attrs, model, max_tokens, None) as obs:
            with self._client.messages.stream(
                model=model, messages=messages, max_tokens=max_tokens, **kwargs
            ) as stream:
                for _ in stream.text_stream:
                    pass  # replace with your real consumer
                final = stream.get_final_message()
            obs["response"] = final
            return final

    # -- internals ----------------------------------------------------------

    @contextmanager
    def _observe(
        self,
        base_attrs: dict[str, Any],
        model: str,
        max_tokens: int,
        temperature: float | None,
    ) -> Iterator[dict[str, Any]]:
        obs: dict[str, Any] = {"response": None}
        started = time.perf_counter()

        with self._tracer.start_as_current_span(
            f"chat {model}", kind=trace.SpanKind.CLIENT
        ) as span:
            # Request config goes on the span, where high-cardinality is fine.
            span.set_attributes(base_attrs)
            span.set_attribute(GEN_AI_REQUEST_MAX_TOKENS, max_tokens)
            if temperature is not None:
                span.set_attribute(GEN_AI_REQUEST_TEMPERATURE, temperature)

            try:
                yield obs
            except anthropic.APIStatusError as exc:
                self._record_failure(base_attrs, span, started, str(exc.status_code))
                raise
            except anthropic.APIError as exc:
                self._record_failure(base_attrs, span, started, type(exc).__name__)
                raise

            response = obs["response"]
            self._record_success(base_attrs, span, started, response)

    def _record_success(
        self,
        base_attrs: dict[str, Any],
        span: trace.Span,
        started: float,
        response: anthropic.types.Message,
    ) -> None:
        elapsed = time.perf_counter() - started
        usage = response.usage

        # response.model is what the gateway actually routed to, which may
        # differ from what you asked for once model-name virtualisation,
        # fallback, or A/B routing is in play. Record both.
        attrs = {**base_attrs, GEN_AI_RESPONSE_MODEL: response.model}

        self._duration.record(elapsed, attrs)

        counts = {
            TOKEN_TYPE_INPUT: usage.input_tokens,
            TOKEN_TYPE_OUTPUT: usage.output_tokens,
            TOKEN_TYPE_CACHE_READ: getattr(usage, "cache_read_input_tokens", 0) or 0,
            TOKEN_TYPE_CACHE_WRITE: getattr(usage, "cache_creation_input_tokens", 0) or 0,
        }
        for token_type, count in counts.items():
            if count:
                self._token_usage.record(count, {**attrs, GEN_AI_TOKEN_TYPE: token_type})

        self._cost.record(estimate_cost_usd(response.model, counts), attrs)

        span.set_attributes(
            {
                GEN_AI_RESPONSE_MODEL: response.model,
                GEN_AI_USAGE_INPUT_TOKENS: usage.input_tokens,
                GEN_AI_USAGE_OUTPUT_TOKENS: usage.output_tokens,
                GEN_AI_RESPONSE_FINISH_REASONS: [response.stop_reason or "unknown"],
            }
        )
        span.set_status(trace.Status(trace.StatusCode.OK))

    def _record_failure(
        self,
        base_attrs: dict[str, Any],
        span: trace.Span,
        started: float,
        error_type: str,
    ) -> None:
        # Failed calls still consume input tokens upstream. Record the duration
        # with an error dimension so success and failure latency never blend.
        attrs = {**base_attrs, ERROR_TYPE: error_type}
        self._duration.record(time.perf_counter() - started, attrs)
        span.set_attribute(ERROR_TYPE, error_type)
        span.set_status(trace.Status(trace.StatusCode.ERROR, error_type))


# ---------------------------------------------------------------------------
# 5. Cost estimation
#
# Load this from config, not source. Rates move monthly, introductory pricing
# expires, and tokenizer changes shift effective cost independently of the
# published rate. Treat it as a forecast, and reconcile against the provider
# invoice — the metric is for trend and attribution, not for accounting.
# ---------------------------------------------------------------------------

RATE_CARD_USD_PER_MTOK: dict[str, dict[str, float]] = {
    "claude-opus-5": {
        TOKEN_TYPE_INPUT: 5.00,
        TOKEN_TYPE_OUTPUT: 25.00,
        TOKEN_TYPE_CACHE_READ: 0.50,
        TOKEN_TYPE_CACHE_WRITE: 6.25,
    },
}


def estimate_cost_usd(model: str, counts: dict[str, int]) -> float:
    rates = RATE_CARD_USD_PER_MTOK.get(model)
    if rates is None:
        return 0.0
    return sum(counts.get(t, 0) / 1_000_000 * r for t, r in rates.items())


# ---------------------------------------------------------------------------
# 6. Usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_telemetry(build_resource("doc-triage-worker", "financial-crime"))

    client = InstrumentedGatewayClient(
        gateway_url=os.environ["AI_GATEWAY_URL"],      # e.g. https://ai-gw.internal/anthropic
        gateway_api_key=os.environ["AI_GATEWAY_KEY"],
        provider_name="anthropic",
        gateway_route="claude-frontier",
    )

    ctx = CallContext(
        use_case="kyc-doc-triage",
        owning_team="financial-crime-platform",
        cost_centre="CC-40871",
    )

    result = client.create_message(
        model="claude-opus-5",
        messages=[{"role": "user", "content": "Summarise the attached filing."}],
        ctx=ctx,
        max_tokens=1024,
    )

    print(result.usage)