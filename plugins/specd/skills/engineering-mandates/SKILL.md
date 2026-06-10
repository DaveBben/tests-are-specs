---
name: engineering-mandates
user-invocable: false
description: >
  The shared engineering mandates — ten "how to build it well" rules
  (concurrency & I/O, unbounded memory, structural parsing, error
  handling, authentic testing, context & consistency, deletion,
  semantic documentation, dependency integrity, simplicity). Loaded
  when designing, writing, or reviewing code that must stay
  resilient and consistent — and especially when /specd:create-spec or
  /specd:execute-spec runs, since both invoke this skill to apply the
  mandates to spec design and implementation. Reference content, not a
  standalone workflow; invoked to load its text, never run on its own.
---

# Engineering Mandates

*These ten mandates target the areas where AI-generated code reliably
fails — code that compiles cleanly and reads well but hangs, leaks
memory, corrupts state, or fails silently under real network and
filesystem conditions. Treat them as your known blind spots, not
generic style advice.*

1. Concurrency & I/O — no blocking in async, localized pools, explicit locks
2. Unbounded Memory — stream by default, validate before loading
3. Structural Parsing — no regex for structured formats, validate at boundary
4. Error Handling — no generic catches, fail loud
5. Authentic Testing — real inputs, no sleep-based sync, dirty fixtures
6. Context & Consistency — emulate existing patterns, consolidate
7. Deletion — delete dead code, refactor don't patch
8. Semantic Documentation — document why, never explain syntax
9. Dependency Integrity — real packages only, pinned versions, no hallucinated APIs
10. Simplicity & Least Structure — guard clauses, stdlib over reinvention, no stubs

---
## 1. The Concurrency & I/O Mandate

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

## 2. The Unbounded-Memory Mandate (streaming first)

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

## 3. The Structural Parsing & Protocol Mandate

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

## 4. The Error-Handling Mandate (fail loud)

*You try to make code look "resilient" by silently swallowing errors.*

- **No generic catching.** You are forbidden from catching base
  exception classes (`Exception`, `Error`, `Throwable`) to simulate
  graceful degradation.
- **Catch specifics.** Catch only the exact exceptions the operations
  inside the `try` block actually raise (`requests.Timeout`,
  `JSONDecodeError`). On an unexpected error the application MUST crash
  or bubble the error up — do not hide your own logic bugs behind a
  generic log warning.

## 5. The Authentic-Testing Mandate

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

## 6. The Context & Consistency Mandate (anti-drift)

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
  violates a mandate (regex over structured data, a swallowed base
  exception, an eager buffer of unbounded data), the mandate wins. Use
  the correct approach for your change and flag the inconsistency; do
  not propagate the slop just to match it. "Emulate, don't invent"
  applies to good patterns, not to copying a latent bug.

## 7. The Deletion Mandate (anti-hoarding)

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

## 8. The Semantic Documentation Mandate (the "why", not the "what")

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

## 9. The Dependency-Integrity Mandate (real packages only)

*You invent plausible-sounding packages and API methods that do not
exist — predicting what a library probably exports rather than
checking what it does.*

- **Import only what exists.** Before adding an import or a
  package-manifest entry, confirm the package is already in the
  project's lockfile/manifest or is a real, maintained library. Never
  add a dependency whose name you are *predicting* rather than
  *verifying* — attackers pre-register the common hallucinated names
  ("slopsquatting"), so an invented package can install malware on the
  next build.
- **Call only real APIs.** Only call methods, attributes, and
  functions that exist in the version the project pins. Do not assume a
  library exposes a method because the name sounds right — check its
  actual surface (the installed source, the docs for that version).
- **Pin versions.** Never add a dependency with a wildcard or floating
  specifier (`*`, `+`, `latest`, a bare range where the project pins
  exactly). Match the project's existing pinning discipline so builds
  stay deterministic and cannot silently pull a different — possibly
  breaking or malicious — version.

## 10. The Simplicity Mandate (least structure, no stubs)

*You pad simple logic into enterprise-shaped scaffolding to look
thorough, and you leave stub placeholders that fake success when you
cannot finish a path.*

- **Least structure that works.** Use guard clauses / early returns
  instead of deep conditional nesting. Do not add indirection layers (a
  util that calls a util that calls a util), mapping passes, or
  transforms the task does not need.
- **Use the standard library.** Never hand-roll a loop that
  re-implements a builtin or stdlib primitive (`map`, `filter`, `sum`,
  a date parser, a path join). Reach for the language's own tools
  first.
- **No speculative abstraction.** Do not add a factory, interface,
  generic, or config hook for a single caller "in case we need it
  later." Build the second abstraction when the second caller actually
  appears.
- **No stub placeholders.** Never ship a function that *fakes* success —
  a hardcoded `return True` / `return []` with a `# in a real
  implementation we would …` comment, or a mock wired into a non-test
  path. Implement the behavior, or fail loudly (Mandate 4); never leave
  a pretend-working stub behind.
