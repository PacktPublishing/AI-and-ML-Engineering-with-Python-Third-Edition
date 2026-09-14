# Context compression: what it saves, and what it costs

Tool output is where context windows quietly fill up. This demo runs four
realistic tool payloads — a city information API, a paper search, an event API
and a batch of platform logs — through
[Headroom](https://pypi.org/project/headroom-ai/), and reports the token counts
before and after compression alongside an illustrative cost.

```text
tool output (verbose JSON)
  ↓
compress()
  ↓
tokens before / tokens after / % saved
  ↓
× input price per million tokens = cost avoided
```

```text
headroom-compression-demo/
├── pyproject.toml               # Python 3.10 + headroom-ai, managed with uv
├── dataset.py                   # the four sample tool payloads
├── context_compression_demo.py  # compresses each one, tabulates, plots
└── Makefile
```

## Run it

```bash
make setup
make run
```

Everything runs locally — no API keys, no cloud resources, no cost. Compression
is measured against the `claude-sonnet-4-5-20250929` tokenizer, so the token
counts match what you would actually be billed for.

You get a table on stdout and two charts written to the working directory:

| File | Shows |
| --- | --- |
| `compression_tokens.png` | tokens before vs after, per payload |
| `compression_savings.png` | percentage saved, per payload |

## Reading the result

Compression ratios vary a lot by payload, and that variation is the point.
Verbose, repetitive, highly structured output — logs, JSON APIs with long
field names, repeated record shapes — compresses hard. Dense prose does not.
Which of your tools return the first kind is what decides whether this is worth
doing.

> **Update the price before quoting the cost column.**
> `INPUT_COST_PER_MILLION` in `context_compression_demo.py` is an illustrative
> placeholder. Substitute the current input price for the model you actually
> use.

The cost figures also assume these payloads are sent once. Multi-turn agents
resend the whole conversation on every step, so the same saving repeats on each
turn — which is where compression stops being a rounding error.

## Why this example pins Python 3.10

The `headroom-ai[all,ml]` extras support 3.10, while the rest of the repository
uses 3.12. `uv` reads `.python-version` and provisions the right interpreter, so
there is nothing to configure — it is called out here only so the difference
does not look accidental.
