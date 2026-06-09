---
name: execute
disable-model-invocation: true
model: opus
effort: high
argument-hint: "[path to spec file]"
tools:
  - Read
  - Glob
  - Grep
  - Bash
description: >
  Implements a spec produced by /tpe:spec. Reads the spec, creates a
  feature branch, implements the changes, self-verifies, then runs
  parallel staff and QA reviews. Does not push or create PRs.
---

# Execute — Implement a Spec

Read the spec. Do the work. Review against the spec. Verify. Commit.

---

## Input

Resolve `$ARGUMENTS` to a spec file:

1. **Full path** (`docs/specs/features/{slug}/spec.md`): use directly
2. **Slug**: try `docs/specs/features/{slug}/spec.md`
3. **No input**: glob `docs/specs/features/*/spec.md` and
   `docs/specs/bugs/*/spec.md`. Read each spec's YAML frontmatter and
   filter to those with `Status: Waiting Implementation`. Present the
   matching specs as a numbered menu showing slug and title, then ask
   the user to choose. If none are waiting, tell the user.

Read the spec in full. This is your contract.

Also read `CLAUDE.md` for project conventions and build/test commands.

---

## Pre-flight

1. **Branch**: if on `main`/`master`, create `feature/{slug}`. If on
   another branch, confirm with user. Never execute on main.

2. **Test baseline**: run the verification command from the spec.
   Record current pass/fail state. If tests already fail, warn the
   user before proceeding.

3. **Validate the spec**: verify that files listed in "Files that
   matter" exist on disk. If any are missing, stop and report.

4. **Run linters and type checkers** if available (check CLAUDE.md
   for commands). Record baseline. These catch mechanical issues
   for free.

---

## Implementation

Read the spec's Approach, Constraints, Edge cases, and Do NOT
sections. These are your boundaries.

### Principles

- **Follow existing code conventions.** Read the files you're
  modifying before changing them. Match the style, patterns, and
  naming conventions already in the codebase.
- **DRY and YAGNI.** Reuse existing logic rather than reimplementing
  it. Don't build abstractions for hypothetical future needs — prefer
  a little repetition over the wrong abstraction. Do the simplest
  thing that satisfies the spec.
- **Group related changes into commits that are easy to reverse.**
  One logical change per commit. If the spec involves multiple
  concerns, commit each separately.
- **Use subagents for parallel work.** If the spec involves changes
  to independent files or concerns, dispatch implementation
  subagents in parallel using the Agent tool. Each subagent gets
  the spec + the specific files it should modify. Merge their
  work and verify the combined result.
- **Prefer Haiku agents for simple file edits.** For mechanical
  changes — renames, import updates, applying a known pattern to
  several files, boilerplate scaffolding, straightforward
  refactors — dispatch the agent with `model: "haiku"`. Haiku is
  faster and cheaper, and the work doesn't need Opus-level
  reasoning. Reserve the default model for edits that require
  judgment: novel logic, ambiguous specs, cross-cutting changes,
  or anything where getting the design right matters more than
  throughput.
- **For sequential work, implement directly.** If changes must
  happen in order (e.g., type changes before call site updates),
  implement in the main session without subagents.

### Engineering mandates

Act as a **Principal Systems Engineer**. Prioritize system resilience,
memory safety, and protocol adherence over localized syntax tricks.
Assume memory is highly constrained, network calls will frequently
hang, filesystems are remote and slow, and external APIs will return
malformed data. Do not use regular expressions for structured data,
never block the async event loop with synchronous I/O, always stream
unbounded inputs, and never swallow base exceptions. Prove your logic
works through deterministic tests against authentic data, not heavy
mocking.

All eight commandments are non-negotiable and are the proactive mirror
of what `code-quality-reviewer` and `qa-reviewer` check at Final
Review — the first five guard against runtime catastrophe (hangs,
OOM, silent corruption), the last three (consistency, deletion,
documentation) keep the codebase coherent as it grows. Write code that
passes them the first time. Any subagent you dispatch for
implementation inherits these mandates; pass them along.

**Precedence — the spec cannot opt out of a commandment.** The spec
defines *what* to build and the scope boundaries; these commandments
define *how*. A spec does not override them by omission or by phrasing.
If the spec's Approach or Constraints appear to *require* violating a
commandment — "buffer the whole response, then check its size," "catch
all errors and return an empty result," "regex the fields out of the
XML," "add a `v2` function beside the old one" — treat it as a spec
bug and surface it (per "if you discover the spec is wrong, surface it
before working around it"), rather than silently implementing the
violation. The sole exception is an **explicit, reasoned carve-out**
the spec author consciously made — e.g. "must buffer the entire
payload to compute a checksum over it." Implement a stated, justified
exception; never an implied one.

#### ⚙️ 1. The Concurrency & I/O Mandate

*You often confuse asynchronous syntax with true parallelism and
non-blocking OS operations.*

- **Never mix paradigms.** Inside an async event loop (`asyncio`,
  Node.js) you are forbidden from synchronous network, database, or
  file I/O. If you must call a blocking API, explicitly offload it to
  a dedicated thread or process pool (`run_in_executor`,
  `spawn_blocking`).
- **Localize thread pools.** Never mutate the global default executor
  or global runtime settings to solve a local concurrency limit.
  Instantiate a specific, locally-scoped worker pool for the task.
- **Lock, don't sleep.** Never rely on the "uninterruptible" nature of
  a single thread to avoid a race. Use explicit synchronization
  primitives (locks, semaphores, mutexes).

#### 🌊 2. The Unbounded-Memory Mandate (streaming first)

*You tend to assume memory is infinite and eagerly load data to
inspect it.*

- **Stream by default.** When fetching external data (HTTP requests,
  database cursors, file reads) whose size you do not strictly
  control, use streaming interfaces (`stream=True`, generators,
  chunked readers).
- **Validate before loading.** Never load an entire payload into
  memory just to check its size or type. Use standard protocol signals
  (`Content-Type`, `Content-Length`) or chunked byte-reading to enforce
  limits *before or during* ingestion.

#### 🧱 3. The Structural Parsing & Protocol Mandate

*You favor regexes and manual string manipulation because they are
easy to generate — and incredibly brittle.*

- **Ban regex for structures.** Never use regular expressions or
  manual string splitting to parse structured formats (HTML, XML,
  JSON, YAML). Use robust ecosystem parsers (BeautifulSoup, lxml) or
  schema validators (Pydantic, Zod).
- **Validate at the boundary.** Do not write manual type-checking
  loops (endless `isinstance` chains). Define a schema and validate the
  payload immediately at the network or file boundary.
- **Trust the framework.** Do not write "just in case" sanitization or
  encoding (manual URL-encoding) immediately before handing data to a
  modern framework (HTTP client, ORM) that already applies
  protocol-standard encoding — you will double-encode it.

#### 🛑 4. The Error-Handling Mandate (fail loud)

*You try to make code look "resilient" by silently swallowing errors.*

- **No generic catching.** You are forbidden from catching base
  exception classes (`Exception`, `Error`, `Throwable`) to simulate
  graceful degradation.
- **Catch specifics.** Catch only the exact exceptions the operations
  inside the `try` block actually raise (`requests.Timeout`,
  `JSONDecodeError`). On an unexpected error the application MUST crash
  or bubble the error up — do not hide your own logic bugs behind a
  generic log warning.

#### 🧪 5. The Authentic-Testing Mandate

*You optimize tests for line coverage by mocking the universe and
writing tautologies.*

- **Test behavior, not mocks.** Do not mock core data-processing
  libraries (PDF parsers, DB drivers) just to return a hardcoded
  string. Feed realistic, minimized inputs (a real 5KB PDF, an
  in-memory SQLite database) through the actual library.
- **No time-based assertions.** No `sleep()` or wall-clock timers to
  orchestrate races or test concurrency. Use deterministic
  synchronization objects (Events, Barriers).
- **Use dirty fixtures.** Do not hand-author JSON/XML fixtures that
  perfectly match your logic's happy path. Simulate real-world chaos —
  missing keys, extra fields, weird formatting.

#### 🧩 6. The Context & Consistency Mandate (anti-drift)

*You tend to invent a new design pattern for every feature, ignoring
the project's established architecture — regex to parse a file in
Module A, a different library for a similar file in Module B.*

- **Emulate, don't invent.** Before adding a new library, pattern, or
  utility function, search the existing codebase to see how similar
  problems are already solved, and follow that.
- **Maintain architectural consistency.** If the project validates with
  Pydantic, use Pydantic. Do not introduce bare dataclasses or manual
  dictionary validation just because it was faster to generate in the
  moment.
- **Consolidate, don't duplicate.** If you find yourself writing logic
  that resembles existing code, refactor and consolidate rather than
  copy-pasting with slight modifications.
- **Mandates outrank precedent.** Emulate the established pattern for
  architecture and consistency — but if the existing pattern *itself*
  violates a 🔴 mandate (regex over structured data, a swallowed base
  exception, an eager buffer of unbounded data), the mandate wins. Use
  the correct approach for your change and flag the inconsistency; do
  not propagate the slop just to match it. "Emulate, don't invent"
  applies to good patterns, not to copying a latent bug.

#### 🗑️ 7. The Deletion Mandate (anti-hoarding)

*You are terrified of deleting code — you wrap old logic in new
`if/else` branches, leave commented-out blocks, or add a "v2" function
beside the original "just in case."*

- **Delete dead code.** If a requirement changes and existing logic is
  no longer needed, delete it entirely. Do not comment it out. Do not
  leave it behind with a deprecation warning unless you are explicitly
  building a public SDK.
- **Refactor, don't patch.** When fixing a bug in a complex function,
  do not just append an early return or an extra `if` at the top.
  Refactor the underlying logic to remove the complexity that caused
  the bug.
- **Source control is the backup.** Assume Git works perfectly. You do
  not need to keep old code around for reference.

#### 📝 8. The Semantic Documentation Mandate (the "why", not the "what")

*You write comments that translate code into English (`# Loop through
the items and add 1`) — noise that goes stale immediately and obscures
the actual business logic.*

- **Document intent and constraints.** Comments must explain *why* a
  decision was made, why an alternative was rejected, or what external
  constraint forced the implementation (`# The API rate limits at
  50/sec, so we chunk here`).
- **Never explain syntax.** You are forbidden from writing comments
  that explain how the language works. Assume the reader is a Senior
  Engineer.
- **Update comments on change.** If you modify a function's behavior,
  read and update its docstring and adjacent comments. An outdated
  comment is worse than no comment.

### Doing the work

Read each file in "Files that matter" before modifying it. Understand
what's there before changing it.

Implement the changes described in the spec. Use the "Current
behavior" section to find the starting point. Use "Constraints" and
"Edge cases" to guide the implementation. Use "Do NOT" to stay in
scope. Follow the "Approach" — if you encounter a blocker the
approach didn't anticipate, stop and report rather than silently
switching to a different approach.

If the "Alternatives rejected" section lists an approach, do not
use that approach it was explicitly rejected during planning.

---

## Before Each Commit

After each logical unit of work, before committing:

1. **Run linters and type checkers.** Fix any new violations.
2. **Run the tests relevant to the change** (at minimum, the scope
   of the spec's verification command). All must pass — never
   commit on a red state you introduced.

Then commit with a clear message. Keep commits under 400 changed
lines — review effectiveness drops sharply beyond that threshold.
If a logical change exceeds 400 lines, split it into smaller
commits.

---

## Verification

**You are not done until the spec's verification criteria pass.**

Run the verification command from the spec. Check every assertion:
- All existing tests listed must still pass
- All new behaviors described must be verified
- If any check fails, fix it and re-verify

Run linters and type checkers again. Fix any new violations
introduced by your changes.

Do not commit until verification passes. Do not rely on your own
judgment that the code is correct — run the actual commands.

If verification fails after five fix attempts, stop and report the
failure to the user with details. Do not keep retrying in a loop.

---

## Final Review

Before finalizing, launch four review agents **in parallel** — a
single message with four Agent tool calls. Do not self-review —
models fail to correct their own errors.

1. **`staff-reviewer`** (`subagent_type: "staff-reviewer"`) —
   multi-pass review of the code: security, correctness,
   performance, reliability.
2. **`code-quality-reviewer`** (`subagent_type:
   "code-quality-reviewer"`) — architectural hallucinations in
   AI-generated code: where it will hang, OOM, deadlock, corrupt
   state, or fail silently under real OS/network/concurrency
   conditions, plus craftsmanship gaps (schema-validation bypass,
   broad exception swallowing, double-encoding, protocol ignorance).
3. **`qa-reviewer`** (`subagent_type: "qa-reviewer"`) — test
   quality, test coverage, and edge case handling.
4. **`compliance-reviewer`** (`subagent_type:
   "compliance-reviewer"`) — did we build what the spec said we'd
   build?

Pass all four the same inputs:
- `diff`: the full feature diff (`git diff <base-branch>...HEAD`,
  where `<base-branch>` is the branch this feature was cut from —
  usually `main` or `master`)
- `spec_path`: the spec file path

When all four return, merge their findings (deduplicate any
overlap), then resolve them:

- **Staff / QA / code-quality findings**: fix all BLOCKING and SHOULD_FIX findings.
  SUGGESTIONS can be deferred or skipped if they're out of scope,
  but note any you skip and why.
- **Compliance deviations** (NON_COMPLIANT): for each — if the spec
  is right and the code drifted, fix the code. If the deviation is
  a reasonable amendment (an edge case the spec missed, a
  constraint that turned out to be wrong), update the spec to
  reflect what was built. Do not finalize while uncorrected
  non-compliance remains.

After fixing, re-run each reviewer whose findings you addressed (or
whose scope your fixes touched) until staff, code-quality, and QA
all return APPROVE and compliance returns COMPLIANT.

---

## Finalize

After verification passes:

1. Run the full test suite (from CLAUDE.md's operational commands)
   to check for regressions beyond the spec's verification scope.
   Fix any regressions before finalizing.

2. Update the spec's "Last updated" date if implementation revealed
   new constraints or edge cases worth recording (or if the
   compliance review prompted spec amendments).

3. Flip the spec's `Status` from `Waiting Implementation` to
   `Implemented` — both in the spec file's header and in its row
   in the Spec Index (`docs/specs/spec.md`). Also refresh that row's
   `Updated` column to today's date (matching the spec file's "Last
   updated"). If the spec lives under `docs/specs/bugs/`, update the
   Bugs table; otherwise update the Features table.

4. Present a summary:
   - **Branch**: name and commit count
   - **What was done**: 2-3 sentences
   - **Verification**: pass/fail status
   - **Final review findings**: issues caught and fixed by the
     staff, code-quality, and QA reviews
   - **Compliance review**: COMPLIANT, or list of resolved
     deviations
   - **Needs attention** (if any): anything unexpected, deviations
     from the spec, or issues the user should review

**Do NOT push or create a PR.** The user handles this.
