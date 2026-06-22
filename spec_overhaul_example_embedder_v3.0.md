---
schema_version: v3
name: embedder
status: Implemented
depends_on: []
standards: /standards.md          # repo-root constitution; six-areas + boundaries + invariants
execution:
  total_cost: $4.64
  total_duration: 19m 45s
  usage_by_models:
    - { model: claude-sonnet-4-6, input: 464, output: 47.1k, cache_read: 6.5m, cache_write: 206.4k, cost: $3.71 }
    - { model: claude-haiku-4-5,  input: 714, output: 10.7k, cache_read: 1.1m, cache_write: 75.1k,  cost: $0.26 }
    - { model: claude-opus-4-8,   input: 34,  output: 8.1k,  cache_read: 310.6k, cache_write: 49.4k, cost: $0.67 }
---

<!-- ════════ LAYER 1 · NARRATIVE (prose · human-reviewed) ════════ -->

## Why
The `feeds.articles` table stores a `vector(768)` embedding of each summary and
indexes it with HNSW for semantic search. Something must produce that vector. The
pipeline now owns embedding: after it summarizes an article, it embeds the summary
and stores both. This slice adds the embedding client; slice 4 calls it.

## Summary
Add an `Embedder`: an async client for the `embeddinggemma` model on the local
server's OpenAI-compatible `/v1/embeddings` endpoint. It takes a title and a
summary, formats them with embeddinggemma's document prefix, and returns a
768-float vector. Any failure returns `None` — embedding is fail-open, so a missing
vector never blocks the summary write. Additive: nothing calls it yet.

## Context
No embedding stage exists today. The pipeline classifies and stores a verdict; it
never vectorizes anything. The `feeds.articles` schema (live, in `feeds_articles.sql`)
already defines `embedding vector(768)` and an HNSW cosine index, but nothing fills
the column. The embedding model runs on the same host as the chat model, on a
separate GPU, at the same base URL:

```bash
curl -s http://ai-server:8080/v1/embeddings -H "Content-Type: application/json" \
  -d '{"model":"embeddinggemma","input":"title: none | text: your chunk"}'
```

`embeddinggemma-300m` outputs 768 dims natively; its context limit is 2048 tokens
(the server truncates longer input).

<!-- ════════ LAYER 2 · CONTRACT (parseable · linted) ════════ -->

## Data model & contracts
```python
# embedder.py — source of truth
EMBED_DIM = 768                       # == feeds.articles.embedding vector(768); NOT configurable

class Embedder:
    def __init__(self, settings: Settings) -> None: ...   # one async OpenAI client; max_retries=0; timeout=embed_timeout_seconds
    async def embed(self, title: str, summary: str) -> list[float] | None: ...
    async def aclose(self) -> None: ...                   # release the client
```
```python
# config.py — Settings additions
embed_enabled: bool = True
embed_base_url: str = "http://ai-server.local:8080/v1"
embed_model: str = "embeddinggemma"
embed_timeout_seconds: float = Field(default=60.0, gt=0)
```
```text
# wire contract — POST {embed_base_url}/v1/embeddings
request.input = "title: {title} | text: {summary}"      # embeddinggemma document prefix
request.model = embed_model
response      → 768-float vector  →  list[float]
              → anything else      →  None               # fail-open
```

## Alternatives rejected
- **Reuse the summarizer's chat client** — embeddings hit a different endpoint and
  model, with their own base URL and timeout. Coupling entangles two
  independently-failing services.
- **Generate embeddings in a separate downstream process** — rejected by David. The
  pipeline owns embedding so the warehouse row is complete on write.
- **Hard-cap the summary to 2048 tokens locally** — embeddinggemma uses the Gemma
  tokenizer (not the vendored Qwen one), which we don't ship. The server truncates
  at 2048; a truncated-tail embedding is acceptable degradation (accepted by David).

## Assumptions
| claim | if_wrong → | confidence |
|-------|-----------|------------|
| Embedding endpoint shares the chat base URL; `embeddinggemma` serves from a separate GPU, so no model swap | per-call model swaps make embedding far slower; design needs phase-batching | high (David) |
| embeddinggemma returns exactly 768 dims | the dim guard returns `None`, every embedding drops, surfaces loudly in logs | high (David) |
| Server truncates input >2048 tokens rather than erroring | long summaries return an HTTP error and embed to `None` | med (David) |

## Constraints
- Add `src/ai_ingest_pipeline/embedder.py`; do **not** wire it into `main()` this slice.
- `Embedder.embed(title, summary)` returns `list[float] | None`.
- Format the input as `f"title: {title} | text: {summary}"`.
- Validate the returned vector length is exactly `EMBED_DIM` (768); any other → `None` + one warning.
- Catch `openai.OpenAIError` **and** `ValueError`; let `asyncio.CancelledError` propagate.
- Build the client with `max_retries=0` and an explicit timeout from `embed_timeout_seconds`.
- Add the four `embed_*` `Settings` fields with the defaults above.
- `EMBED_DIM = 768` is a module constant, not configurable.

## Approach
- **Mirror:** the classifier's async-client lifecycle — one client, explicit timeout, `max_retries=0`, an `aclose()` to release it.
- **Don't-touch:** `classifier.py`, `__main__.py`. Slice 4 wires this in.
- **Ordering:** validate the 768-dim length *before* returning; fail-open to `None` on any failure path.
- **Gotchas:** the OpenAI SDK parser raises `ValueError("No embedding data received")` on an empty `data` list *before* you can inspect `response.data` — so `ValueError` must be caught alongside `OpenAIError`. Use the **real** article title in the prefix (not the curl example's literal `none`); the document prefix affects retrieval quality.

## Edge cases
- `embed_enabled` false: the orchestrator (slice 4) never builds or calls it; the module itself always attempts the call when invoked.
- Network / HTTP / timeout error: `None` + one warning. Never raise except `CancelledError`.
- Empty or missing embedding (`data` empty, or length 0): `None` + one warning.
- Vector length ≠ 768: `None` + one warning. A wrong-dim vector would fail the `vector(768)` insert and abort the run — fail open instead.
- Summary > 2048 embeddinggemma tokens: send as-is, rely on server truncation; optionally log when the summary looks long.
- Lone surrogate in the summary: already surrogate-stripped before storage (slice 3); embed whatever string it is given.

## Files
| id | path | mode | symbol | why |
|----|------|------|--------|-----|
| F1 | `src/ai_ingest_pipeline/embedder.py` | new | `Embedder`, `embed()`, `EMBED_DIM` | the client |
| F2 | `src/ai_ingest_pipeline/config.py` | modify | `Settings` | add 4 `embed_*` fields near `llm_*` (~:164) |
| F3 | `src/ai_ingest_pipeline/classifier.py` | context | `Classifier.__init__` (:186), `aclose` (:236) | async-client lifecycle to mirror |
| F4 | `feeds_articles.sql` | context | `embedding vector(768)` (:43) | the dimension contract |
| F5 | `src/ai_ingest_pipeline/models.py` | context | `SafeStr` (:28) | the summary string type |
| F6 | `tests/test_embedder.py` | new | — | mirrors `test_classifier.py` respx structure |
| F7 | `tests/test_config.py` | modify | — | extend the default assertions |

## Tasks
| id | task | files | [P] | done |
|----|------|-------|-----|------|
| T1 | add the four `embed_*` fields to `Settings` | F2 |  | x |
| T2 | define `Embedder` + `EMBED_DIM` + client lifecycle (`__init__`, `aclose`) | F1 |  | x |
| T3 | implement `embed()`: format prefix → call → validate 768 → fail-open `None` | F1 |  | x |
| T4 | tests: respx happy path + 4 error paths + cancellation | F6 | P | x |
| T5 | extend config default + validation tests | F7 | P | x |

## Verification
```bash
uv sync
uv run ruff check src tests && uv run mypy src && \
  uv run pytest tests/test_embedder.py tests/test_config.py
```

EARS assertions (respx mocks `/v1/embeddings`; a real `Settings` drives the fields):

- **V1** — WHEN `embed(title, summary)` is called THE SYSTEM SHALL POST to `/v1/embeddings` with `input == "title: {title} | text: {summary}"` and `model == embed_model`.
- **V2** *(worked example)* — WHEN the endpoint returns a 768-float vector THE SYSTEM SHALL return that exact list of 768 floats.
  > Worked: `embed("Edge AI ships", "- **TL;DR:** ...")`; mock returns `[0.01, -0.04, …]` (len 768) → `embed` returns the identical 768-float list, in order.
- **V3** `[error — required]` — WHEN the endpoint returns a vector of length ≠ 768 (e.g. 512) THE SYSTEM SHALL return `None` and log exactly one warning.
- **V4** `[error — required]` — WHEN the response `data` list is empty THE SYSTEM SHALL return `None` and log one warning.
- **V5** `[error — required]` — WHEN the call raises an HTTP 500, a connect error, or a timeout THE SYSTEM SHALL return `None` after exactly one request, log one warning, and not retry.
- **V6** — WHEN an `asyncio.CancelledError` is raised during the call THE SYSTEM SHALL propagate it (never swallow).
- **V7** `[config]` — WHEN `Settings()` is built with defaults THE SYSTEM SHALL set `embed_enabled` true, `embed_model` `embeddinggemma`, `embed_base_url` == the chat base URL, and `embed_timeout_seconds` 60.0; AND WHEN `embed_timeout_seconds ≤ 0` THE SYSTEM SHALL raise a validation error.

**Seams**
- S1 — Build the mock vector independently (e.g. `[0.0] * 512`); do **not** derive its length from `EMBED_DIM`, or the test passes tautologically.
- S2 — respx intercepts the OpenAI SDK because it is httpx-based; assert on the wire payload, not an internal call.

**Manual sanity check (not a test):** against the real server, embed one summary and confirm a 768-float vector comes back.

---

<!-- For the demo only — not part of the spec. -->
### What changed vs your v2 embedder.md
- **Two layers** now explicit (narrative vs linted contract), with a divider.
- **Data model** is a typed signature block (source of truth), not prose + a curl.
- **Assumptions** became a table — every row has an `if_wrong`, so the linter can check it.
- **Approach** collapsed from prose + "Things to consider" into 4 buckets (Mirror / Don't-touch / Ordering / Gotchas).
- **Files** is a parseable table with `mode` + `symbol`; diff-lint covers F1/F2/F6/F7.
- **Tasks** is new — an ordered table with `[P]` + `done` (didn't exist in v2).
- **Verification** is EARS assertions with IDs, one worked case, error-paths tagged, seams split out — instead of one dense prose blob.
- Telemetry stays inline but compacted to one line per model; `standards: /standards.md` replaces the CLAUDE.md dependency.
