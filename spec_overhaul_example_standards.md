# standards.md — project constitution (ai-ingest-pipeline)

The single source of truth for the **invariants**, the **six areas**, and the **agent
boundaries** that gate every change and every spec in this repo. Each v3 slice spec
references this file (`standards: standards.md`) and inlines a short, slice-relevant
excerpt — the principles that gate that slice and the boundary tiers that apply to it.

> Status: draft for review (2026-06-20). Once accepted, `CLAUDE.md` shrinks to a pointer here.

---

## Invariants (non-negotiable)

These gate every change. A spec that violates one is wrong, even if it works.

- **Fail open / bias to recall.** A parse failure or service error must **never** silently
  drop an article (`spec.md` §1, §4). On error, degrade — return `None`, store a NULL field,
  retry next run — but never lose a good article.
- **Never silently drop.** Every failure path logs a **named** structured warning. In a
  fail-open stage the log is the only signal that anything went wrong.
- **Crash-safe ordering.** Durable write, *then* mark seen. A crash leaves an article
  un-seen (it retries), never seen-but-unwritten (silently lost).
- **Secrets are env-only.** Config comes via pydantic-settings env vars **plus** `feeds.yaml`
  (untracked). Never commit `.env`, credentials, or `feeds.yaml`.
- **Specs stay in sync.** After a significant change, update `docs/specs/spec.md` Current
  State. A stale spec is worse than no spec.

---

## Commands

```bash
uv sync                                   # install dependencies (CI: uv sync --locked)
uv run ai-ingest-pipeline                 # run the CLI
uv run pytest                             # tests
uv run pytest --cov                       # tests with coverage
uv run mypy src                           # type check (strict)
uv run ruff check src tests               # lint
uv run ruff format src tests              # format
uv run pre-commit install                 # install git hooks

# the gate — run before every PR:
uv run ruff check src && uv run mypy src && uv run pytest
```

## Testing

- **Framework:** pytest (asyncio auto mode), pytest-cov, hypothesis, **respx** (httpx
  mocking — the OpenAI SDK is httpx-based, so respx intercepts it).
- **Location:** `tests/`, one `test_<module>.py` per module; mirror the structure of a
  sibling test file when adding one.
- **Error paths are required.** Every fail-open branch (network error, empty response,
  wrong shape) gets its own test. Assert on the **wire payload**, not internal calls.
- **No tautological tests.** Never derive a test's expected value from the same constant
  the code uses (e.g. don't size a mock vector from `EMBEDDING_DIM`). Build it independently.

## Project structure

- `src/ai_ingest_pipeline/` — the package; CLI entry point is `__main__.py:main()`.
- `tests/` — the pytest suite.
- `.github/workflows/ci.yml` — CI (lint, format check, mypy, pytest).
- `spec.md` (root) — stage-1 pipeline **design** (target architecture, reliability rules).
- `docs/specs/` — project spec, current state, and the spec index.

## Code style

- ruff (rule families in `pyproject.toml [tool.ruff.lint]`); mypy `--strict` with the
  pydantic plugin; **structlog** for all logging.
- The ruff config **enforces fail-open**: `BLE001` (blind `except Exception`) is allowed
  only when the catch logs `exc_info=True` or re-raises; `S110`/`S112` (try-except-pass/
  continue) and `E722` (bare except) are banned. You cannot silently swallow an error.
- The house fail-open client idiom (from `summarizer.py`) — copy this shape:

```python
logger = structlog.stdlib.get_logger(__name__)

try:
    response = await self._client.chat.completions.create(...)   # max_retries=0
except openai.OpenAIError as exc:
    # OpenAIError is an Exception subclass; asyncio.CancelledError is a
    # BaseException and PROPAGATES, so TaskGroup cancellation aborts the call.
    logger.warning("<stage>_request_failed", guid=article.guid,
                   kind=type(exc).__name__, error=str(exc))
    return None
```

- `max_retries=0` on every SDK client (no hidden retries). Named warning events read
  `<stage>_<condition>` (`llm_request_failed`, `llm_empty_response`, …).

## Git workflow

- **Branch per slice/feature**; one PR per slice. If you're on `main`, branch first.
- **Run `uv run ruff format` before staging** — the pre-commit `ruff-format` hook aborts the
  commit otherwise.
- **Stage explicit paths; never `git add -A`** — `.claude/` holds embedded worktrees that
  must not be committed.
- Pass the full gate (lint + mypy + pytest) before opening the PR.

## Boundaries (agent permissions, project-wide)

A slice spec inlines the subset relevant to it; these are the defaults.

- ✅ **always** — run the gate before a PR; run `ruff format` before staging; fail open on a
  parse/service error; stage explicit paths; add a test for every error branch.
- ⚠️ **ask-first** — add or bump a dependency (touches `uv.lock`); change the output schema or
  the Postgres target; edit `feeds.yaml`; change the llama-swap / model-server config;
  alter a reliability invariant.
- 🚫 **never** — commit `.env`, secrets, or `feeds.yaml`; `git add -A`; silently drop an article
  on error (no bare/passing excepts); commit with failing lint, types, or tests.
