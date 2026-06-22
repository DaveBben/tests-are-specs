# Spec Template — v3 (two-layer slice)

Read this when producing a slice spec in Phase 2. The implementing agent
(`/spec-monkey:execute-spec`) consumes the result — fill every section with the precision the
placeholders describe. This is the **v3** format; legacy `schema: v2` specs use
`spec-template.md` and are frozen (never backfilled).

This fills ONE slice file (`{slice}.md`) in `docs/specs/features/{slug}/`, alongside an
`_index.md` (see `index-template-v3.md`). Each slice is self-contained; execute-spec runs one
per call as one PR, sized to ship on its own (~400 changed lines, one reviewer in a sitting).

## Two layers, sixteen sections

A v3 slice is **two layers in one document**, in this canonical order. Never reorder; never
omit a section — a section with nothing to say carries `N/A — {reason}`.

- **Layer 1 · Narrative** (prose, human-reviewed): **Why, Summary, Success metric, Context.**
  Everything a reviewer needs to approve *that* the change is worth making and *what* it
  achieves. Keep it outcome-oriented; push transport and mechanics down into the contract.
- **Layer 2 · Contract** (parseable, lint-ready): **Principles, Data model & contracts,
  Alternatives rejected, Assumptions, Clarifications, Boundaries, Constraints, Approach, Edge
  cases, Files, Tasks, Verification.** The binding contract a linter checks and the
  implementer executes.

The contract is **deliberately redundant** with itself — a constraint echoed in Constraints,
Files, and Verification survives context compaction during a long implementation. Keep that
redundancy; defend it if a reviewer flags it as bloat.

**Writing style.** The Layer 1 prose and the Edge-case / Approach descriptions follow
`writing-style.md`: one idea per sentence, actor-first, conclusion first, caveats in their
own sentence. The contract tables and signature blocks are exempt — there, identifier density
is load-bearing.

**DRY constitution.** The project-wide invariants, six areas, and boundaries live **once** in
`standards.md` (the constitution; may be `standards.md` / `CLAUDE.md` / `AGENTS.md`). A slice
inlines only a **short, slice-relevant excerpt** — the Principles that gate it, the boundary
tiers that apply to it. Never paste the whole constitution into a slice.

## Front-matter

Every v3 spec opens with a YAML block (`---` fences); a deterministic linter validates it.

- `schema_version` — always `v3`. This key (not v2's `schema`) is what gates the v3 linter and
  tells every reader which shape to expect.
- `name` — the slice slug = filename without `.md` (e.g. `data-model`). Matches this slice's
  `_index.md` row.
- `summary` — one scannable line; what execute-spec's menu shows. Quote it if it has a colon.
- `status` — the **v3 lifecycle enum**: `Draft` → `Reviewed` → `Implemented` → `Superseded`.
  New specs start `Draft`. Flip to `Reviewed` once it passes review and the user approves —
  **`Reviewed` is the "ready to implement" state** execute-spec picks up. execute-spec flips it
  to `Implemented` at finalize. `Superseded` retires it.
- `created` — `YYYY-MM-DD`, set once, never changes.
- `modified` — `YYYY-MM-DD`, refreshed on every edit or status change; equals `created` at
  creation. The Spec Index "Updated" column mirrors it.
- `drafter` — author; default to `git config user.name`.
- `standards` — the constitution file this slice complies with. **One canonical form**
  (`standards.md`, `CLAUDE.md`, or `AGENTS.md`), used identically here and in every in-prose
  mention. The linter flags a mismatch.
- `depends_on` — ordered list of **sibling slice slugs** this slice needs first (bare slugs,
  not paths). Mirrors `_index.md`, which wins on disagreement. Empty list when none.
- `execution` — run metadata recorded **after** the execute-spec run (an agent can't
  self-measure). Leave blank during drafting. When filled: `total_cost`, `total_duration`,
  `usage_by_models` (one entry per model: `model`, `input`, `output`, `cache_read`,
  `cache_write`, `cost`). Telemetry stays **inline** by design — a reviewer may call it
  ceremony; it is intentional. Keep it.

```
---
schema_version: v3
name: {slice-slug}
summary: {one-line summary of the change}
status: Draft
created: {YYYY-MM-DD}
modified: {YYYY-MM-DD}
drafter: {name}
standards: standards.md
depends_on: []
execution:
  total_cost:
  total_duration:
  usage_by_models:
---
```

---

# Template body

The illustrative content below is drawn from a real slice (an embedding stage in an async
Python ingest pipeline). It shows the bar for each section — **overwrite it**; don't ship the
example text. The whole body is wrapped in a 4-backtick fence so its inner code blocks render;
copy the inner content, not the outer fence.

````markdown
<!-- ════════ LAYER 1 · NARRATIVE (prose · human-reviewed) ════════ -->

## Why
{Intent, conclusion-first. The problem today and why this slice is worth doing now. Keep it
outcome-oriented — what becomes possible, not how. Do NOT leak transport/mechanics here (no
"adds the client," no endpoint names); those live in the contract. 2–4 sentences.}

## Summary
{What ships, in 1–3 sentences — intent, not procedure. Why + Summary is the reviewer's TLDR.
Linted: a word cap. Keep transport details (clients, URLs, return types) out — they belong in
Data model & contracts.}

## Success metric
{The measurable outcome this slice enables — the number or behavior that separates done from
not-done. For a slice that's user-invisible until a later one wires it in, state the
feature-level metric it contributes to, plus this slice's *local* proof (what you can verify
now). `N/A — {reason}` is allowed for a pure refactor with no observable change. Example:
"Once wired (slice 4), ≥99% of summarized articles carry a non-NULL 768-dim embedding on a
nightly run; this slice's local proof: `embed()` returns a valid 768-vector and fails open on
every error path (V3–V6)."}

## Context
{How the affected part of the system works today, in plain prose for someone who has never
seen this code. Explain the flow and the pieces this change touches — not the whole module.
Spend a small budget of `file:line` anchors; the precise locations live in Files. Paste a real
command or wire shape if it grounds the reader. `N/A — {reason}` if the slice adds something
wholly new with no current behavior. A paragraph or two, not a tour.}

<!-- ════════ LAYER 2 · CONTRACT (parseable · lint-ready) ════════ -->

## Principles (this slice)
{A SHORT excerpt of the constitution's invariants that gate THIS slice — not the whole thing.
Open with a one-line pointer to `standards.md` for the full six areas / boundaries / Git
workflow, then list only the 3–5 principles this slice must honor. Close with an anti-drift
line: the spec is the source of truth; if a signature changes, this contract updates in the
same PR. Example:}

Governed by `standards.md` (Commands, Testing, Code style, **Git workflow**, full Boundaries:
see `standards.md`). This slice complies with:
- **Fail-open** — an embedding failure degrades to a NULL embedding; it never blocks or drops an article.
- **Never silently drop** — every failure path logs a *named* warning; in a fail-open stage the log is the only signal.
- **Additive-only (this slice)** — no runtime behavior changes; nothing calls the embedder until slice 4.
- **Spec is the source of truth** — if `embedder.py`'s signature changes, this contract block is updated in the *same* PR (anti-drift).

## Data model & contracts
{The source of truth for this slice: typed signature blocks (Pydantic / dataclass / type
sketch) and DDL, fenced by language. Pin types precisely — this is the part a reviewer reads
closely and the linter resolves symbols against. Procedural code stays loose; types do not.
Include a "wire contract" block when the slice produces or consumes data another system reads:
pin the final URL/payload shape as a literal, so there's no base-URL fragility. Example:}

```python
# embedder.py — source of truth
EMBEDDING_DIM = 768          # == feeds.articles.embedding vector(768); a module constant, never configurable

class Embedder:
    def __init__(self, settings: Settings) -> None: ...   # one async client; max_retries=0; explicit timeout
    async def embed(self, title: str, summary: str) -> list[float] | None: ...
    async def aclose(self) -> None: ...                   # release the client
```
```text
# wire contract — the final shape, pinned as a literal
final request URL = http://ai-server.local:8080/v1/embeddings
request.input = "title: {title} | text: {summary}"
response → 768-float vector → list[float]  |  anything else → None   # fail-open
```

## Alternatives rejected
{Prose bullets, alternative bolded for scan-readability. Each names a real path considered and
why it lost. Prevents the implementer relitigating settled decisions. Example:}
- **Reuse the summarizer's chat client** — embeddings hit a different endpoint and model, with their own base URL and timeout. Coupling entangles two independently-failing services.
- **Generate embeddings in a separate downstream process** — the pipeline owns embedding so the warehouse row is complete on write; a second process would leave rows half-populated.

## Assumptions
{TABLE: `claim | if_wrong → | confidence | verify`. State each load-bearing assumption, even
ones the user confirmed, so the reasoning survives after the drafting chat is cleared. EVERY
row needs an `if_wrong`. A med/low confidence assumption is an open question in disguise —
mark it OPEN / [NEEDS CLARIFICATION] and give it a verify-plan with an owner. Separate "the
user decided X" (→ Alternatives / Principles) from "we assume X" (a risk; belongs here).
Example:}

| claim | if_wrong → | confidence | verify |
|-------|-----------|------------|--------|
| The embedding endpoint shares the chat base URL; a separate GPU serves it, so no model swap | per-call model swaps make embedding far slower; design would need phase-batching | high | server config serves both models concurrently |
| embeddinggemma returns exactly 768 dims | the dim guard returns `None`, every embedding drops — surfaces loudly via `embed_wrong_dimension` | high | matches `feeds_articles.sql` `vector(768)` |
| The server truncates input >2048 tokens rather than 4xx-ing | long summaries return an HTTP error → embed to `None` | **med — OPEN** | verify-plan: POST a >2048-token summary, confirm a 768-vector returns. owner: {who} |

## Clarifications
{TABLE: `# | question | resolution | status`. The drafting interrogation, preserved — what was
asked before any code, and how each resolved. This makes alignment visible instead of
laundered: an open item links to an OPEN assumption / [NEEDS CLARIFICATION]; a resolved one
points at the section that absorbed it. Don't dress an unresolved question as a settled
decision. Example:}

| # | question surfaced before coding | resolution | status |
|---|----------------------------------|------------|--------|
| Q1 | Embed in-pipeline, or as a downstream batch job? | in-pipeline — the warehouse row must be complete on write | resolved → Alternatives |
| Q2 | Is an embed failure an article failure, or fail-open to NULL? | fail-open to NULL; the summary is the costly artifact, the vector is backfillable | resolved → Principles |
| Q3 | Does the server truncate >2048-token input, or 4xx? | not yet verified | **OPEN** → Assumptions row 3 |

## Boundaries (this slice)
{The three tiers — ✅ always / ⚠️ ask-first / 🚫 never — scoped to THIS slice (the project-wide
defaults live in `standards.md`). This absorbs the old Approach "Don't-touch": what the slice
must not touch goes under 🚫. Example:}
- ✅ **always** — create `embedder.py`; add the four `embed_*` `Settings` fields; mirror `summarizer.py`'s client lifecycle.
- ⚠️ **ask-first** — changing `EMBEDDING_DIM`; adding a new dependency; altering the document prefix (it affects retrieval quality).
- 🚫 **never** — wire the embedder into `main()` this slice; edit `summarizer.py`; make the dimension configurable; enable SDK-level retries.

## Constraints
{Flat, hard MUSTs — bulleted, specific numbers not vague qualifiers, each testable.
Deliberately overlaps Files and Verification; redundancy is load-bearing here. Where the
change touches unbounded data, hanging calls, concurrency, or untrusted input, pin the
decision as a named seam ("5s timeout on the X call, raise on timeout"). Pin log-event
contracts a fail-open design relies on: the event name and its fields. Example:}
- Add `src/ai_ingest_pipeline/embedder.py`; do **not** wire it into `main()` this slice.
- `Embedder.embed(title, summary)` returns `list[float] | None`.
- Validate the returned vector length is exactly `EMBEDDING_DIM` (768); any other → `None` + one `embed_wrong_dimension` warning (fields: `expected`, `got`).
- On a request failure (HTTP / connect / timeout / empty `data`) → `None` + one `embed_request_failed` warning (field: `kind`).
- Catch `openai.OpenAIError` **and** `ValueError`; let `asyncio.CancelledError` propagate.
- Build the client with `max_retries=0` and an explicit timeout from `embed_timeout_seconds`.

## Approach
{Micro-schema — Mirror / Ordering / Gotchas, NOT pseudocode. Only the non-obvious path: which
existing pattern to copy, the order where order matters, and the trap a reasonable engineer
would hit. Cut any sentence the model would satisfy on its own. Push precision toward types
(above); let procedural code stay loose. Example:}
- **Mirror:** `summarizer.py`'s async-client lifecycle — one client, explicit timeout, `max_retries=0`, an `aclose()` to release it.
- **Ordering:** validate the 768-dim length *before* returning; fail-open to `None` on every failure path.
- **Gotchas:** the SDK parser raises `ValueError("No embedding data received")` on an empty `data` list *before* you can inspect `response.data` — so `ValueError` must be caught alongside `OpenAIError`.

## Edge cases
{Bulleted "condition: expected behavior". Probe the categories happy-path specs leak:
dependency failure (timeout, partial/malformed response), malformed/oversized input,
empty/boundary values. Each binds both the code and a test. Example:}
- Network / HTTP / timeout error: `None` + one `embed_request_failed` warning. Never raise except `CancelledError`.
- Empty or missing embedding (`data` empty → SDK `ValueError`): `None` + one `embed_request_failed` warning.
- Vector length ≠ 768: `None` + one `embed_wrong_dimension` warning. A wrong-dim vector would fail the `vector(768)` insert and abort the run — fail open instead.

## Files
{TABLE: `id | path | mode | symbol | why`. The manifest — symbol-first (the durable anchor;
line numbers drift). `mode` is one of new | modify | context. A linter checks: `new` must NOT
already exist; `modify`/`context` MUST exist; every `symbol` resolves. The diff must touch
exactly the `new`+`modify` rows — no stray edits, nothing listed-but-untouched. Aim for 6–10
rows. Example:}

| id | path | mode | symbol | why |
|----|------|------|--------|-----|
| F1 | `src/ai_ingest_pipeline/embedder.py` | new | `Embedder`, `embed()`, `EMBEDDING_DIM` | the client |
| F2 | `src/ai_ingest_pipeline/config.py` | modify | `Settings` | add 4 `embed_*` fields near `llm_*` |
| F3 | `src/ai_ingest_pipeline/summarizer.py` | context | `Summarizer.__init__`, `aclose` | the async-client lifecycle to mirror |
| F4 | `tests/test_embedder.py` | new | — | mirrors `test_summarizer.py` respx structure |

## Tasks
{TABLE: `id | task | files | [P] | done`. An ordered checklist the implementer flips
(`done` → `x`), resumable across runs. Order: types → tests/contracts → impl → wire → cleanup.
Mark `[P]` where a task can run in parallel with its siblings. Example:}

| id | task | files | [P] | done |
|----|------|-------|-----|------|
| T1 | add the four `embed_*` fields to `Settings` | F2 |  |  |
| T2 | define `Embedder` + `EMBEDDING_DIM` + client lifecycle | F1 |  |  |
| T3 | implement `embed()`: format prefix → call → validate 768 → fail-open `None` + named logs | F1 |  |  |
| T4 | tests: respx happy path + error paths + cancellation | F4 | P |  |

## Verification
{Open with the exact setup-and-run command sequence (the full install with needed extras, then
the command). Then EARS assertions with stable IDs: `WHEN {trigger} THE SYSTEM SHALL
{response}`. Rules a linter enforces:
- Atomic — one assertion per row; never bundle multiple ANDs (split them).
- Error paths tagged [error — required]; cover every fail-open branch.
- Testable — no "optionally SHALL" and no shall without a threshold or observable.
- One WORKED case — a single assertion shown with real, concrete expected values.
- A Seams list — where a test could cheat (the anti-tautology rule: a worked example MUST NOT
  source its mock dimensions/length from the constant under test).
- A Self-check — re-walk every assertion, every Constraint, and the Files manifest.
Example:}

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
- **V4** `[error — required]` — WHEN the response `data` list is empty THE SYSTEM SHALL return `None` and log exactly one `embed_request_failed` warning with `kind="empty_data"`.
- **V5** — WHEN an `asyncio.CancelledError` is raised during the call THE SYSTEM SHALL propagate it (never swallow).

**Seams**
- S1 — Build the mock vector independently (e.g. `[i/1000 for i in range(512)]`); do **not** derive its length from `EMBEDDING_DIM`, or the test passes tautologically.
- S2 — respx intercepts the SDK because it is httpx-based; assert on the wire payload, not an internal call.

**Self-check (before marking done)**
- Re-walk V1–Vn; each MUST map to exactly one passing test.
- Confirm every Constraint is satisfied in the diff.
- Confirm the Files manifest (mode `new`/`modify`) equals the changed files — no stray edits, nothing listed-but-untouched.

**Manual sanity check (not a test):** {any non-automated check — a real-server probe, a deploy, a dashboard — explicitly called out as not-a-test.}
````

---

Keep going until all tests pass and the verification criteria are met. Hit a problem →
investigate and fix, don't stop. Discover the spec is wrong (a constraint can't be met, a
referenced file is gone, a rejected alternative now looks right) → surface it before working
around it; don't silently change the approach.
