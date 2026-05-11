---
name: review
argument-hint: "[spec path or base branch]"
description: >
  Spec-grounded multi-lens code review. Works through four focused
  lenses sequentially in one context (security → correctness →
  performance → reliability), then verifies findings against the
  source before reporting. Use when you want a thorough second
  opinion on implemented changes before pushing.
model: opus
effort: max
---

# Review — Spec-Grounded Multi-Lens Code Review

Review code changes against the specification that defined them.

This skill runs four focused review passes sequentially in one
context, then a verification pass that drops unsupported findings.

---

## Input

Resolve `$ARGUMENTS`:

1. **Spec path** (`docs/specs/features/{slug}/spec.md`): use as
   the review ground truth. Diff against the branch base.
2. **Slug**: try `docs/specs/features/{slug}/spec.md`.
3. **Base branch/commit**: diff against it. Look for a related
   spec in the Spec Index (`docs/specs/spec.md`). If no spec
   found, warn that the review will be ungrounded.
4. **No input**: diff against main. Search for related spec.

Read the spec (if found) and the diff in full.

**If no spec is found:** warn the user the review will be
ungrounded and less effective. Run all four lenses anyway, but
mark the final verdict as low-confidence. The Spec Compliance
checks within each lens will be skipped.

---

## Review Process

Work through the four lenses below **in order**. For each lens:

1. Read the spec sections relevant to that lens (listed under each
   phase).
2. Scan the diff for issues in that lens's scope.
3. For each candidate issue, record: `file:line`, trace/evidence,
   suggested fix.
4. Do NOT report findings yet — collect them for the verification
   pass at the end.

Stay disciplined: when you're in the Security lens, ignore
correctness/perf/reliability issues you spot. They get their own
pass.

The checks listed under each lens are illustrative, not
exhaustive — flag anything in the lens's scope, not only what's
listed.

### Phase 1 — Security lens

Scope: injection, auth/authz, secrets, crypto, deserialization,
dependency risk.

Spec sections to read: **Constraints**, **Do NOT** (for explicit
security requirements like "must validate input", "must not log
PII").

**Applicability:** if the diff touches none of (user input
handling, auth/authz, persistence, network I/O, crypto,
subprocess/shell, LLM prompts incorporating untrusted content,
security-affecting config, dependencies), mark this lens
**NOT_APPLICABLE** and move on.

Otherwise check:

- **Injection** — SQL/NoSQL, command, path traversal, template/SSRF/XSS via unsanitized input.
- **Prompt injection** — untrusted content (user input, fetched pages, tool outputs, retrieved docs) concatenated into LLM prompts without isolation.
- **Auth / authz** — missing authz on new endpoints, tenant/scope mixing, privilege escalation paths.
- **IDOR** — object-level authz gaps (user A can read/modify user B's resource by ID).
- **Mass assignment** — user-controlled fields flowing into ORM/model updates without an allowlist.
- **CSRF** — state-changing endpoints with cookie auth and no token / SameSite protection.
- **File upload** — missing type/size/extension checks, unsafe storage location, server-side execution risk.
- **Secrets / data exposure** — hardcoded credentials, secrets in logs or telemetry, PII where it shouldn't be.
- **Crypto / randomness** — weak password hashing (MD5/SHA1), non-CSPRNG for tokens, static IVs, ECB mode.
- **Memory safety** — use-after-free, double-free, buffer overflow, out-of-bounds read/write, uninitialized reads (C/C++/unsafe Rust).
- **Deserialization / parsing** — unsafe deserialization (pickle/eval/yaml.load), XXE, zip-slip, billion-laughs.
- **Dependencies** — new unpinned deps, known-vulnerable version ranges (flag, don't audit exhaustively).

Each candidate finding needs a concrete **exploit path** (one
sentence attacker scenario). Drop speculative risks without a
path.

### Phase 2 — Correctness lens

Scope: logic errors, boundaries, nullability, concurrency, error
handling, edge case coverage.

Spec sections to read: **Edge cases**, **Constraints**, **Do
NOT**, **Alternatives rejected** (verify rejected approaches were
not silently adopted).

**Applicability:** if the diff is doc-only, config-only, or has
no executable logic changes, mark **NOT_APPLICABLE**.

Otherwise check:

- **Spec compliance** — change matches the spec's Approach; rejected Alternatives not silently adopted.
- **Edge case coverage** — every Edge case in the spec traced through the code; missing handling is a finding.
- **Boundary errors** — off-by-one in loops/slices, inclusive vs exclusive ends, empty / single-element cases.
- **Nullability** — missing null/nil checks on optional fields or raw pointer/reference derefs, default handling, iteration over empty collections.
- **Concurrency** — races on shared state, missing locks, async ordering assumptions.
- **Error handling** — uncaught exceptions, swallowed errors, silent failures, missing cleanup on error paths, partial-failure states. AI code has **2x more error handling gaps** (CodeRabbit) — be specifically suspicious here.
- **Time / timezone** — TZ confusion, DST transitions, leap years, wall-clock vs monotonic, locale/ISO parsing.
- **Atomicity / transactions** — multi-step writes without a transaction, dual-writes (DB + external) without compensation, partial commits.
- **Idempotency / retry safety** — retried operations (network failure, queue redelivery) that mutate twice; missing idempotency keys on POSTs.
- **Numeric precision / coercion** — money in floats, integer overflow, implicit coercion (JS `==`, Python `int`/`str`), Decimal vs float drift.
- **State mutation / aliasing** — shared mutable references, Python mutable default args, unintended in-place mutation of caller's data.
- **Ordering assumptions** — relying on dict/map/Set iteration order, assuming sort stability, locale-dependent string compare.
- **Caching / staleness** — cache keys missing scope (per-user/tenant), TTLs outliving writes, stale read after write.
- **Encoding / serialization** — UTF-8 vs bytes, JSON serialization of Decimal/datetime, escaping at trust boundaries.

Each candidate finding needs a **concrete repro condition** (one
sentence describing the input that triggers the bug). Drop
findings without one.

### Phase 3 — Performance lens

Scope: algorithmic complexity, N+1, unbounded resources, blocking
I/O, missing indexes.

Spec sections to read: **Constraints** (perf budgets like p99
latency, throughput targets).

**Applicability:** if the change is purely structural (renames,
refactors with no algorithm changes), doc-only, or affects code
not on a hot path and not user-facing, mark **NOT_APPLICABLE**.

Otherwise check:

- **Algorithmic complexity** — O(n²) or worse on growable collections, repeated computation that could be hoisted, suboptimal sorting/searching.
- **Database / I/O** — N+1 queries, missing batch ops, missing indexes implied by new query patterns, full table scans.
- **Pagination / unbounded results** — fetching all rows when only a page is needed, missing `LIMIT`, unbounded in-memory lists.
- **Resource use** — unbounded memory growth, leaked file handles / connections, missing pool limits.
- **Memory allocation / GC pressure** — allocations in tight loops, string concat in loops (vs builder), boxing/unboxing, large temporaries in hot paths.
- **Concurrency / network** — sync I/O in async contexts, blocking in event loops, sequential calls that could be parallel, missing timeouts on outbound calls.
- **Lock contention** — coarse-grained locks held across I/O, single mutex serializing the hot path, missing read/write lock distinction.
- **Regex / ReDoS** — catastrophic backtracking on user-controlled input.
- **Caching gaps / thundering herd** — repeatable work with no cache, simultaneous backfill on expiry without single-flight or jitter.
- **Payload / serialization cost** — JSON-encoding huge objects, missing compression, `SELECT *` shipping unused columns, oversized responses.
- **Startup / cold start** — heavy imports, eager initialization on serverless/CLI paths, missing lazy load.

Each candidate finding needs a **cost analysis** (what scales)
and a **likely impact** (when this bites at realistic scale).
Speculative "this might be slow" without scaling analysis gets
dropped.

### Phase 4 — Reliability & maintainability lens

Scope: operational readiness, observability, retry/timeout,
maintainability, test coverage of new logic.

Spec sections to read: **Constraints** (reliability/observability
requirements).

**Applicability:** if the diff is doc-only or a trivial
constant/string update with no behavioral change, mark
**NOT_APPLICABLE**.

Otherwise check:

- **Operational readiness** — silently swallowed errors, missing retries / timeouts / circuit breakers, missing observability on key state transitions. AI agents "do not handle non-functional requirements unless explicitly told" — most-missed dimension.
- **Failure modes** — partial-failure states without rollback, resource leaks on error paths, crash-loop potential, dependency unavailability handling.
- **Graceful degradation** — fail-open vs fail-closed when a dependency is down, half-up state handling, sensible defaults on external-call failure.
- **Health checks / readiness** — missing liveness/readiness, deep-dependency health leaking into liveness (crash-loop risk).
- **Metrics / alerting** — missing metrics on new features, no SLI defined, alertable conditions with no alert wired.
- **Logging hygiene** — log injection (untrusted content in log lines), missing correlation IDs, over- or under-verbose for the path.
- **Migrations / backward compatibility** — schema migrations without back-out, breaking API changes without versioning, removed fields still in use, missing data backfill or transition period.
- **Deployability / rollback** — deploy ordering (migration before code), unsafe init order, rollback-unsafe changes.
- **Configuration / feature flags** — flag without kill switch, config drift between environments, hardcoded values that should be config, no rollback path for config changes.
- **Maintainability** — functions over ~50 lines bundling multiple concerns, magic numbers/strings, deep nesting, names describing implementation rather than purpose, dead code, duplicated logic across files.
- **Test coverage of new logic** — new conditional branches, error paths, or config/flags with no tests.
- **Test quality** — flaky / time- or network-dependent tests, mock-heavy tests that drift from prod, tests that pass without asserting the behavior.

Each candidate finding needs a **concrete impact** (what fails,
what becomes hard). "Could be more elegant" without concrete
impact gets dropped.

---

## Verification pass

After all four lenses, before writing the report, re-check every
candidate finding:

1. Open the file at the cited line. Does the code actually
   contain what your trace claims?
2. Is the trace a real data flow, or a guess based on naming?
3. Could existing code higher in the call chain already address
   the concern?
4. For security: can you construct a concrete exploit path?
5. For correctness: can you describe a concrete input that
   triggers the bug?
6. For perf: is the code path actually hot, with a real scaling
   axis?
7. For reliability: is the issue actually present, or handled
   nearby in code you didn't read?

Drop findings that fail verification. **False positives erode
trust faster than false negatives.** A clean report developers
trust beats a thorough report they ignore.

After verification, **deduplicate** — if two lenses flagged the
same `file:line`, merge them. Keep the strongest evidence and
note that multiple lenses caught it.

---

## Output

```markdown
# Code Review

**Spec**: {spec path or "ungrounded — no spec found"}
**Changes**: {X files, +Y/-Z lines}
**Scope**: {1-2 sentences}

## Lens verdicts

| Lens | Verdict |
|---|---|
| 1. Security | NOT_APPLICABLE / PASS / FINDINGS |
| 2. Correctness | NOT_APPLICABLE / PASS / FINDINGS |
| 3. Performance | NOT_APPLICABLE / PASS / FINDINGS |
| 4. Reliability & Maintainability | NOT_APPLICABLE / PASS / FINDINGS |

## Findings

### BLOCKING
- `file:line` — [**{lens}**] {description}. Trace: {flow}. Fix: {change}.

### SHOULD_FIX
- `file:line` — [**{lens}**] {description}. Trace: {flow}. Fix: {change}.

### SUGGESTIONS
- `file:line` — [**{lens}**] {suggestion with rationale}.

## Verdict

**[APPROVE | REQUEST CHANGES]** — {one sentence}.
```

Omit empty severity sections. A clean review with 0 findings is a
valid outcome — do not manufacture findings.

**Severity rules:**
- BLOCKING = will cause a production problem, or violates a spec
  Constraint / Do NOT rule.
- SHOULD_FIX = should be fixed before merging, but not urgent.
- SUGGESTIONS = optional improvements.
- Any BLOCKING or SHOULD_FIX → REQUEST CHANGES.
- Only SUGGESTIONS or clean → APPROVE.
- All four lenses NOT_APPLICABLE → APPROVE with a note that no
  lens applied (the user may want to verify the right base/spec
  was selected).

**What this skill does NOT review:** style, formatting, naming —
linters handle those. Don't burn AI tokens on what deterministic
tools catch for free.
