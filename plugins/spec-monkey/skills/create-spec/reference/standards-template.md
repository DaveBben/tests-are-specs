# Standards Template — the project constitution (v3)

Read this when a repo needs a constitution and has none. This template produces
**`standards.md`**: the single source of truth for the **invariants**, the **six areas**,
and the **agent boundaries** that gate every change and every v3 slice spec in a repo.

`onboard` generates this file from the real codebase. `create-spec` references it: every v3
slice carries `standards: standards.md` in front-matter and inlines a short, slice-relevant
**excerpt** (the Principles that gate that slice, the boundary tiers that apply to it). The
constitution lives **once** here; a slice never copies the whole thing.

## How to use this template

- **Fill from the real repo, never invent.** Read the lint config, the test layout, one
  representative module's error-handling idiom, the CI workflow, and any existing
  `CLAUDE.md` / `AGENTS.md`. Every command must be copy-pasteable; every rule must trace to
  something in the code. A guessed package manager (`npm` vs `pnpm` vs `uv`) is the classic
  failure.
- **The file may be named `standards.md`, `CLAUDE.md`, or `AGENTS.md`** — whichever the repo
  already uses as its agent constitution. Pick **one** name and use that exact form
  everywhere: in each slice's `standards:` front-matter and in every in-prose mention. One
  canonical form, no path-format drift (a slice may not say `/standards.md` in prose and
  `standards.md` in front-matter).
- **Then shrink `CLAUDE.md`/`AGENTS.md` to a pointer** at this file, so the constitution has
  one home. Propose that edit to the user before overwriting an existing `CLAUDE.md`.
- **Replace every `{guidance}` block** with content for this repo. Keep the seven headings and
  their order. The illustrative bullets are a real example (from an async Python ingest
  pipeline) — overwrite them; they show the bar, not the content.

---

````markdown
# standards.md — project constitution ({project-name})

The single source of truth for the **invariants**, the **six areas**, and the **agent
boundaries** that gate every change and every spec in this repo. Each v3 slice spec
references this file (`standards: standards.md`) and inlines a short, slice-relevant
excerpt — the principles that gate that slice and the boundary tiers that apply to it.

> Status: draft for review ({YYYY-MM-DD}). Once accepted, `CLAUDE.md` shrinks to a pointer here.

---

## Invariants (non-negotiable)

{The 3–6 rules that gate every change. A spec that violates one is wrong even if it works.
These are the project's "constitution" in the strict sense — the rules an agent must never
trade away for convenience. Pull them from how the code actually behaves at its edges, not
from aspiration. State each as one rule + why it exists. Example shape:}

- **Fail open / bias to recall.** A parse failure or service error must **never** silently
  drop a record. On error, degrade — return `None`, store a NULL field, retry next run — but
  never lose good data.
- **Never silently drop.** Every failure path logs a **named** structured warning. In a
  fail-open stage the log is the only signal that anything went wrong.
- **Crash-safe ordering.** Durable write, *then* mark seen. A crash leaves work un-seen (it
  retries), never seen-but-unwritten (silently lost).
- **Secrets are env-only.** Never commit `.env`, credentials, or untracked config.

## Commands

{Exact invocations with their flags — the ones an agent runs, copy-pasteable. Group install,
run, test, type-check, lint, format. End with "the gate": the single command an agent runs
before every PR. If a category has no command, say so; never invent one.}

```bash
{install}                                 # install dependencies
{run}                                     # run the app / CLI
{test}                                    # tests
{typecheck}                               # type check
{lint}                                    # lint
{format}                                  # format

# the gate — run before every PR:
{lint} && {typecheck} && {test}
```

## Testing

{Framework(s), where tests live, how to run them, and the project's test rules. Pull the real
conventions: the per-module layout, which mocking library intercepts the real transport, the
fixture style. Two rules that belong here in almost every repo:}

- **Framework & layout:** {e.g. pytest (asyncio auto mode), one `test_<module>.py` per module
  in `tests/`; mirror a sibling test file when adding one}.
- **Error paths are required.** Every failure branch (network error, empty response, wrong
  shape) gets its own test. Assert on the observable contract, not internal calls.
- **No tautological tests.** Never derive a test's expected value from the same constant the
  code uses (e.g. don't size a mock vector from `EMBEDDING_DIM`). Build it independently.

## Project structure

{Where code lives, in one line each. Top-level only — the directories and key files an agent
must know to navigate. Name the entry point. Don't paste a deep tree.}

- `{src/pkg/}` — the package; entry point is `{__main__.py:main()}`.
- `{tests/}` — the test suite.
- `{.github/workflows/ci.yml}` — CI ({what it runs}).
- `{docs/specs/}` — project spec, current state, and the spec index.

## Code style

{The linter/formatter/type-checker config that's enforced, plus **ONE real snippet pulled
from this repo** — the house idiom for the thing that matters most (usually error handling).
A snippet beats three paragraphs: paste the actual pattern an agent should copy. Note any
lint rule that encodes an invariant (e.g. a rule that bans silent error-swallowing).}

- {Tooling: e.g. ruff (rule families in `pyproject.toml`); mypy `--strict`; structlog for
  logging.}
- {Any lint rule that enforces an invariant — e.g. the config bans bare `except` and
  try-except-pass, so an error cannot be silently swallowed.}
- The house {fail-open client} idiom (from `{module.py}`) — copy this shape:

```{lang}
{paste the real pattern here — the actual error-handling / client-lifecycle / boundary idiom
the repo uses, lifted verbatim from a representative module. This is the example an agent
mirrors; keep it short and real.}
```

## Git workflow

{Branch, commit, and PR rules an agent must follow. Pull the real ones — pre-commit hooks,
staging discipline, the gate. Common shape:}

- **Branch per slice/feature**; one PR per slice. If you're on `main`, branch first.
- {Run the formatter before staging if a pre-commit hook would otherwise abort the commit.}
- {Stage explicit paths; never `git add -A` if the repo has untracked dirs that must not be
  committed (e.g. embedded worktrees, local config).}
- Pass the full gate (lint + types + tests) before opening the PR.

## Boundaries (agent permissions, project-wide)

{The three-tier permission system — the single highest-value section per the research. A
slice spec inlines the subset relevant to it; these are the project-wide defaults. Always
include an Ask-first catch-all: "anything not covered here." State each as a concrete action,
not a vague quality.}

- ✅ **always** — {run the gate before a PR; fail open on a parse/service error; add a test
  for every error branch; stage explicit paths}.
- ⚠️ **ask-first** — {add or bump a dependency; change a stored schema or external target;
  alter a reliability invariant; **anything not covered by this constitution**}.
- 🚫 **never** — {commit secrets or untracked config; `git add -A`; silently drop a record on
  error; commit with failing lint, types, or tests}.
````

---

## What this is NOT

- **Not the project spec.** `docs/specs/spec.md` describes *what is implemented now* (Current
  State, architecture). `standards.md` describes *the rules that gate change*. If a line
  answers "what does this project do today?", it belongs in the project spec, not here.
- **Not a slice spec.** A slice inlines a short excerpt of the Principles and the boundary
  tiers that gate *it*. It never copies this whole file. This file is the DRY master.
- **Not a style-rule dump.** A rule a linter already enforces does not need restating — except
  the one snippet and the rules that encode an invariant, which are load-bearing context.
