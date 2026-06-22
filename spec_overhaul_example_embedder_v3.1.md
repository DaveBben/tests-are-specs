---
schema_version: v3
name: embedder
status: Implemented
depends_on: []
standards: /standards.md
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
Semantic search over the warehouse needs a vector for every stored summary, and
nothing produces those vectors today. The pipeline owns that job: each summary must
become a 768-dim embedding so a `feeds.articles` row is searchable the moment it
lands. Without it, the HNSW index added to the table stays empty and the warehouse
is keyword-only.

## Summary
Add an `Embedder`: an async client for `embeddinggemma` on the local server's
OpenAI-compatible `/v1/embeddings` endpoint. It turns a title + summary into a
768-float vector, and fails open — any error returns `None`, so a missing vector
never blocks the summary write. Additive only: this slice ships the module and its
config; the orchestrator wires it in at slice 4.

## Context
No embedding stage exists today. The pipeline summarizes and stores; it never
vectorizes anything. The `feeds.articles` schema (live, in `feeds_articles.sql`)
already defines `embedding vector(768)` and an HNSW cosine index, but nothing fills
the column. The embedding model runs on the same host as the chat model, on a
separate GPU, at the same base URL:

```bash
curl -s http://ai-server.local:8080/v1/embeddings -H "Content-Type: application/json" \
  -d '{"model":"embeddinggemma","input":"title: Edge AI ships | text: your summary"}'
```

`embeddinggemma-300m` outputs 768 dims natively; its context limit is 2048 tokens
(the server truncates longer input).

<!-- ════════ LAYER 2 · CONTRACT (parseable · linted) ════════ -->

## Principles (this slice)
Governed by `standards.md`; this slice complies with:
- **Fail-open** — an embedding failure degrades to a NULL embedding; it never blocks or drops an article.
- **Never silently drop** — every failure path logs a *named* warning; in a fail-open stage the log is the only signal.
- **Additive-only (this slice)** — no runtime behavior changes; nothing calls the embedder until slice 4.
- **Isolated failure surface** — embedding is its own client and endpoint, so its failures cannot take down summarization.

## Data model & contracts
```python
# embedder.py — source of truth
EMBEDDING_DIM = 768          # == feeds.articles.embedding vector(768); a module constant, never configurable

class Embedder:
    def __init__(self, settings: Settings) -> None: ...   # one async OpenAI client; max_retries=0; timeout=embed_timeout_seconds
    async def embed(self, title: str, summary: str) -> list[float] | None: ...
        # title/summary are SafeStr-sanitized upstream (slice 3); embed() trusts the caller
    async def aclose(self) -> None: ...                   # release the client
```
```python
# config.py — Settings additions
embed_enabled: bool = True            # read by the ORCHESTRATOR (slice 4), never by Embedder
embed_base_url: str = "http://ai-server.local:8080/v1"
embed_model: str = "embeddinggemma"
embed_timeout_seconds: float = Field(default=60.0, gt=0)
```
```text
# wire contract — POST {embed_base_url}/embeddings      (embed_base_url already ends in /v1)
request.input = "title: {title} | text: {summary}"      # embeddinggemma document prefix; use the REAL title
request.model = embed_model
response → 768-float vector → list[float]
        → anything else      → None                      # fail-open
```

## Alternatives rejected
- **Reuse the summarizer's chat client** — embeddings hit a different endpoint and
  model, with their own base URL and timeout. Coupling entangles two
  independently-failing services.
- **Generate embeddings in a separate downstream process** — the pipeline owns
  embedding so the warehouse row is complete on write; a second process would leave
  rows half-populated.
- **Hard-cap the summary to 2048 tokens locally** — embeddinggemma uses the Gemma
  tokenizer (not the vendored Qwen one), which we don't ship. The server truncates at
  2048; a truncated-tail embedding is acceptable degradation.

## Assumptions
| claim | if_wrong → | confidence | verify |
|-------|-----------|------------|--------|
| The embedding endpoint shares the chat base URL; `embeddinggemma` serves from a separate GPU, so no model swap occurs | per-call model swaps make embedding far slower; the design would need phase-batching | high | server config serves both models concurrently |
| embeddinggemma returns exactly 768 dims | the dim guard returns `None`, every embedding drops — surfaces loudly via `embed_wrong_dimension` | high | matches `feeds_articles.sql` `vector(768)`; the dim guard enforces it |
| The server truncates input >2048 tokens rather than 4xx-ing | long summaries return an HTTP error → embed to `None` | **med — OPEN** | verify-plan: POST a >2048-token summary, confirm a 768-vector returns (not a 4xx). owner: David |

## Boundaries (this slice)
- ✅ **always** — create `embedder.py`; add the four `embed_*` `Settings` fields; mirror `summarizer.py`'s client lifecycle.
- ⚠️ **ask-first** — changing `EMBEDDING_DIM`; adding a new dependency; altering the `title: … | text: …` document prefix (it affects retrieval quality).
- 🚫 **never** — wire the embedder into `main()` this slice; edit `summarizer.py` or `__main__.py`; make the dimension configurable; enable SDK-level retries.

## Constraints
- Add `src/ai_ingest_pipeline/embedder.py`; do **not** wire it into `main()` this slice.
- `Embedder.embed(title, summary)` returns `list[float] | None`.
- `Embedder` does **not** read `embed_enabled`; the orchestrator gates it (slice 4).
- Format the input as `f"title: {title} | text: {summary}"`.
- Validate the returned vector length is exactly `EMBEDDING_DIM` (768); any other → `None` + one `embed_wrong_dimension` warning (fields: `expected`, `got`).
- On a request failure (HTTP / connect / timeout / empty `data`) → `None` + one `embed_request_failed` warning (field: `kind`).
- Catch `openai.OpenAIError` **and** `ValueError`; let `asyncio.CancelledError` propagate.
- Build the client with `max_retries=0` and an explicit timeout from `embed_timeout_seconds`.
- Add the four `embed_*` `Settings` fields with the defaults above.
- `EMBEDDING_DIM = 768` is a module constant, not configurable.

## Approach
- **Mirror:** `summarizer.py`'s async-client lifecycle — one client, explicit timeout, `max_retries=0`, an `aclose()` to release it.
- **Ordering:** validate the 768-dim length *before* returning; fail-open to `None` on every failure path.
- **Gotchas:** the OpenAI SDK parser raises `ValueError("No embedding data received")` on an empty `data` list *before* you can inspect `response.data` — so `ValueError` must be caught alongside `OpenAIError`.

## Edge cases
- `embed_enabled` false: the orchestrator (slice 4) never builds or calls it; the module itself always attempts the call when invoked.
- Network / HTTP / timeout error: `None` + one `embed_request_failed` warning. Never raise except `CancelledError`.
- Empty or missing embedding (`data` empty → SDK `ValueError`): `None` + one `embed_request_failed` warning.
- Vector length ≠ 768: `None` + one `embed_wrong_dimension` warning. A wrong-dim vector would fail the `vector(768)` insert and abort the run — fail open instead.
- Summary > 2048 embeddinggemma tokens: send as-is, rely on server truncation (see the OPEN assumption).
- Lone surrogate in the summary: already surrogate-stripped before storage (slice 3); embed whatever string it is given.

## Files
| id | path | mode | symbol | why |
|----|------|------|--------|-----|
| F1 | `src/ai_ingest_pipeline/embedder.py` | new | `Embedder`, `embed()`, `EMBEDDING_DIM` | the client |
| F2 | `src/ai_ingest_pipeline/config.py` | modify | `Settings` | add 4 `embed_*` fields near `llm_*` |
| F3 | `src/ai_ingest_pipeline/summarizer.py` | context | `Summarizer.__init__`, `aclose` | the async-client lifecycle to mirror |
| F4 | `feeds_articles.sql` | context | `embedding vector(768)` | the dimension contract |
| F5 | `src/ai_ingest_pipeline/models.py` | context | `SafeStr` | the upstream-sanitized string type |
| F6 | `tests/test_embedder.py` | new | — | mirrors `test_summarizer.py` respx structure |
| F7 | `tests/test_config.py` | modify | — | extend the default assertions |

## Tasks
| id | task | files | [P] | done |
|----|------|-------|-----|------|
| T1 | add the four `embed_*` fields to `Settings` | F2 |  | x |
| T2 | define `Embedder` + `EMBEDDING_DIM` + client lifecycle (`__init__`, `aclose`) | F1 |  | x |
| T3 | implement `embed()`: format prefix → call → validate 768 → fail-open `None` + named logs | F1 |  | x |
| T4 | tests: respx happy path + 4 error paths + cancellation | F6 | P | x |
| T5 | extend config default + validation tests | F7 | P | x |

## Verification
```bash
uv sync
uv run ruff check src tests && uv run mypy src && \
  uv run pytest tests/test_embedder.py tests/test_config.py
```

EARS assertions (respx mocks `/v1/embeddings`; a real `Settings` drives the fields):

- **V1** — WHEN `embed(title, summary)` is called THE SYSTEM SHALL POST to `{embed_base_url}/embeddings` with `input == "title: {title} | text: {summary}"` and `model == embed_model`.
- **V2** *(worked example)* — WHEN the endpoint returns a 768-float vector THE SYSTEM SHALL return that exact list of 768 floats, in order.
  > Worked: `embed("Edge AI ships", "- **TL;DR:** ...")`; mock returns `mk = [i/1000 for i in range(768)]` → `embed` returns a list equal to `mk`, `len == 768`.
- **V3** `[error — required]` — WHEN the endpoint returns a vector of length ≠ 768 (e.g. 512) THE SYSTEM SHALL return `None` and log exactly one `embed_wrong_dimension` warning carrying `expected=768` and `got=512`.
- **V4** `[error — required]` — WHEN the response `data` list is empty THE SYSTEM SHALL return `None` and log exactly one `embed_request_failed` warning.
- **V5** `[error — required]` — WHEN the call raises an HTTP 500, a connect error, or a timeout THE SYSTEM SHALL return `None` after exactly one request, log exactly one `embed_request_failed` warning, and not retry.
- **V6** — WHEN an `asyncio.CancelledError` is raised during the call THE SYSTEM SHALL propagate it (never swallow).
- **V7** `[config]` — WHEN `Settings()` is built with no `embed_*` env vars THE SYSTEM SHALL set `embed_enabled` true, `embed_model` `embeddinggemma`, and `embed_timeout_seconds` 60.0.
- **V8** `[config]` — WHEN `Settings()` is built with no `embed_*` env vars THE SYSTEM SHALL set `embed_base_url` to `"http://ai-server.local:8080/v1"`.
- **V9** `[config]` — WHEN `embed_timeout_seconds ≤ 0` THE SYSTEM SHALL raise a pydantic validation error.

**Seams**
- S1 — Build the mock vector independently (e.g. `[i/1000 for i in range(512)]`); do **not** derive its length from `EMBEDDING_DIM`, or the test passes tautologically.
- S2 — respx intercepts the OpenAI SDK because it is httpx-based; assert on the wire payload, not an internal call.

**Self-check (before marking done)**
- Re-walk V1–V9; each MUST map to exactly one passing test.
- Confirm every Constraint is satisfied in the diff.
- Confirm the Files manifest (mode `new`/`modify`) equals the changed files — no stray edits, nothing listed-but-untouched.

**Manual sanity check (not a test):** against the real server, embed one summary and confirm a 768-float vector comes back.

---

<!-- For the demo only — not part of the spec. -->
### What changed vs v3.0
- **`Why` de-coupled from how** — outcome-only; the "slice 4 calls it" mechanics moved to `Summary`. (research A)
- **New `Principles (this slice)`** — the `standards.md` invariants that gate this slice, shown in-document. (C)
- **New tiered `Boundaries`** — ✅/⚠️/🚫, slice-scoped; absorbed Approach's "Don't-touch". `Approach` is now Mirror / Ordering / Gotchas. (F)
- **`Assumptions` de-laundered** — honest confidence + a `verify` column; the med-confidence truncation item is flagged **OPEN** with a verify-plan and an owner, not laundered as "(David)". (H/L)
- **`V7` split into atomic `V7/V8/V9`**; one canonical base URL everywhere fixes the `ai-server` vs `ai-server.local` contradiction and the doubled `/v1`. (B, P)
- **Pinned log event names** (`embed_request_failed`, `embed_wrong_dimension`) so the fail-open principle is testable. (round-1 M4)
- **New `Self-check`** in Verification — re-walk every EARS + Constraint + manifest. (I)
- **Corrected drift** — `Mirror`/F3 point at `summarizer.py` (not the deleted `classifier.py`); constant is `EMBEDDING_DIM`; dropped the untestable "optionally log when long".
