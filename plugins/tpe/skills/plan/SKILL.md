---
name: plan
effort: max
model: opus
disable-model-invocation: true
argument-hint: "[feature slug or .claude/features/{slug} path]"
description: >
  Takes an approved brainstorm.md and produces plan.md and task JSONs
  ready for /tpe:execute. Minimal user interaction — Think already made the
  decisions. Do NOT run without an approved brainstorm.md (run /tpe:think
  first). Do NOT use for bugs (use /tpe:bug).
---

# Plan — Implementation Specification

> Think made the decisions. Plan translates them into a verified,
> executable specification. The output is plan.md and task JSONs that
> /act can run without needing to ask questions.

```
/tpe:plan {slug}
  Step 1: Load and validate brainstorm.md
  Step 2: Deepen codebase investigation
  Step 3: Write plan.md with real code snippets
  Step 4: Verify all references
  Step 5: Decompose into task JSONs
  Step 6: Present for single review pass
```

Artifacts written to `.claude/features/{slug}/`.

---

## Step 1 — Load brainstorm.md

Resolve `$ARGUMENTS` to a feature directory:
1. **Full path** (`.claude/features/{slug}/`): use directly
2. **Slug**: try `.claude/features/{slug}/`
3. **No input**: glob for available brainstorm.md files, present choices

Read `brainstorm.md`. Hard stop if no `brainstorm.md` exists:
> "No brainstorm.md found at `.claude/features/{slug}/`. Run `/tpe:think {description}` first to produce one."

Hard stop if:
- Status is not `Approved` — tell user to complete `/tpe:think` first
- At-risk tests section contains `[unverified]` entries — ask user to confirm or remove them before proceeding. Unverified test context is worse than no test context.
- More than 3 `[TBD]` entries — too many open decisions. Return to `/tpe:think` to resolve them.

Warn (do not hard stop) if:
- Dependency Chain section is empty or absent — dependency chains prevent NameError-class failures on multi-file tasks. Warn:
  > "brainstorm.md has no dependency chain. Multi-file tasks are at higher risk of cross-file reference errors. Continue or return to /tpe:think to add one?"

If 1–3 `[TBD]` entries remain (allowed by think), extract them now. During Step 2 investigation, attempt to resolve each from the codebase. Any that remain unresolved after Step 2 must appear in the relevant task's `doNot` as: "Do not assume [TBD topic] — decision pending."

Read `CLAUDE.md` and any domain `spec.md` for orientation. If any `spec.md`'s `Last verified` date is >30 days old, warn (do not block):
> "spec.md was last verified {date}. Consider refreshing before planning. Continue anyway?"

---

## Step 2 — Deepen Investigation

brainstorm.md identified what changes. This step finds the exact code the plan will reference.

For each file in brainstorm.md's Impact Surface, read targeted extracts:
- The specific symbol being changed (function signature, type definition, schema shape) — not the full file
- The reference implementation from brainstorm.md's Chosen Approach
- Any interface or contract the changed symbol must satisfy

**Cap reads to what the plan will actually cite.** Do not read files speculatively. Every file read here should produce at least one `file:line` reference in plan.md. If it doesn't, stop reading it.

**Breaking-change call-site sweep.** The "cap reads" rule above governs *file reading*, not *reference finding* — these are different. For every symbol in brainstorm.md's Impact Surface undergoing a breaking change (signature change, field removal, rename, deletion), grep the entire repo for references — especially tests. This is mechanical completeness, not speculation: you must find every call site that will stop compiling or pass/fail differently after the change.

For each **test** file that references a symbol undergoing a breaking change, it must either appear in the task's `atRiskTests` or you must justify in plan.md why it isn't at risk. A plan that lists one obviously-named test but misses sibling tests hitting the same call site creates an impossible situation for the implementor: "change the signature, don't modify tests, regressionCheck must pass" becomes unsatisfiable.

For each **non-test** file that references a symbol undergoing a breaking change, it must appear in plan.md's Impact table as a `modify` entry (or be explicitly justified as not-at-risk). Changing a function signature while leaving unlisted callers in their old form produces a compile/type-check failure in files the plan never mentioned. Same root cause as the test gap, different failure surface.

Resolve the dependency chain from brainstorm.md against the actual codebase — verify each hop in the chain exists at the stated path. If a hop is wrong, find the correct path now. Do not carry stale dependency chains into task JSONs.

---

## Step 3 — Write plan.md

Write `.claude/features/{slug}/plan.md` using the [plan.md template](references/templates.md#planmd).

**Content rules:** real code (not pseudocode), omit empty sections, exhaustive impact table, max 2 pattern references, What NOT to Do copied verbatim from brainstorm.md. Under ~500 lines → single PR; over → vertical slices only. End with "Do not implement yet."

**Target: 100–200 lines.**

---

## Step 4 — Verify plan.md

Launch the `plan-verifier` agent. Apply every `@FIX:` correction. Ignore verifier output about missing `testContext`/`implementationContext` (removed fields). If >3 discrepancies, re-investigate the affected files rather than patching one by one.

After verification passes, write `tasks/plan.json` with `status: "PendingDecomposition"`. On resume: if plan.json exists with this status, skip to Step 5.

---

## Step 5 — Decompose into Task JSONs

### Re-anchor before decomposing

Re-read from brainstorm.md: Chosen Approach, Do NOT, Constraints, At-Risk Tests. Re-read from plan.md: Impact table, What NOT to Do. These are the boundaries every task inherits. Do not proceed without re-reading — they degrade in attention over long sessions.

### Explore alternative decompositions before committing

Generate **2-3 candidate decompositions** with different slice
boundaries, task groupings, or ordering. For each candidate, evaluate:

- Does every task stay within the 1–4 file hard max?
- Are `blockedBy` chains short (ideally ≤2 deep)?
- Is each slice independently reviewable with one revert reason?
- Does the decomposition minimize cross-task interface coupling?

Select the candidate that scores best. If two are equivalent, prefer
fewer tasks. Do not default to the first decomposition you think of —
the first plausible split is often not the best.

### Task granularity

- **Single concern** — 1–3 files, hard max 4
- **Count decisions, not lines.** 200 lines / one decision > 30 lines / three decisions
- **Over 20 tasks**: the feature needs splitting
- **Vertical slices only** — each slice is a complete vertical path (data layer + service + API + test). Never a horizontal layer. Each slice must be independently reviewable with exactly one reason it would be reverted.

### Task JSON schema and validation

Use the schema and field notes in [task_{N}.json template](references/templates.md#task_njson). Key rules:

- `intent` explains *why*, not *what*
- `files` hard max 4 — more means split the task
- `reference` is a single entry only
- `atRiskTests` from brainstorm.md's confirmed list — not re-derived
- `regressionCheck` MUST be set when `atRiskTests` is non-empty
- `doneWhen` MUST include "and regressionCheck passes" when atRiskTests is non-empty

**Verify acceptance criteria before writing:** for each task, ask
"If I were implementing this and only had these criteria, could I
resolve every ambiguity? Does each criterion test exactly one
observable behavior?" If a criterion is ambiguous or tests multiple
behaviors, split or sharpen it now — the code-implementor's
verification chain is built on these.

**Validate before writing:** all paths exist/don't-exist as expected, `dependencyChain` hops have real import relationships (grep to confirm), no `[TBD]` values remain.

**Ground-before-terse:** any path appearing in a task's `files` or `dependencyChain` that isn't already in plan.md's Impact table must be added to the Impact table before writing the task. Task JSONs compress context into bare path strings — every path must be grounded in plan.md first, or a fresh reader has no context for what it is.

**Collision check against negated names:** for each basename in `files`/`dependencyChain`, check plan.md's `Scope > Out` and `What NOT to Do` and brainstorm.md's Do NOT. If the basename collides with anything there (e.g. dependencyChain references `s3.py` when plan.md said "no s3.py is created"), use a disambiguated form — parent dir prefix (`synthetic_data_gen/s3.py`) or a role annotation in the task's `intent`. A naked colliding basename will pattern-match onto the negated artifact in a reader's head.

**blockedBy integrity:** after all task JSONs are drafted, verify the dependency graph:
- Every id in any `blockedBy` array refers to a real task id in this plan (no dangling references like `task_99` when only `task_1..3` exist).
- No cycles — transitively follow `blockedBy` from each task; a task must not be reachable from itself. A cycle makes /tpe:execute deadlock.

**Task contract consistency:** for each task, cross-read `acceptanceCriteria`, `atRiskTests` / `regressionCheck`, and `doNot`. If an AC removes or changes something that an at-risk test asserts must behave the old way, *and* `doNot` forbids modifying tests, the task is unsatisfiable (change-X + X-must-still-work + can't-touch-test). Fix by scoping the test change into this task, moving the test change to a prior blocking task, or loosening the AC. Do not ship an unsatisfiable task — the implementor will stop and report, wasting a full execute cycle.

Write `tasks/plan.json` + `tasks/task_{N}.json` per task.

---

## Step 6 — Single Review Pass

Present plan.md to the user:

> "The plan is at `.claude/features/{slug}/plan.md` and {N} task JSONs are in `tasks/`. Review the plan and either:
> 1. **Give feedback** — tell me what's wrong, I'll revise once
> 2. **Approve** — say 'approve' to proceed to /tpe:execute"

Process feedback as one revision pass. Re-run the plan-verifier after any changes to plan.md that touch code references.

After revision, if the user gives further feedback: apply it, but flag:
> "This is the second revision. If the plan still doesn't match your intent, consider returning to /tpe:think — the approach may need revisiting rather than the plan."

On approval: update plan.json status from `PendingDecomposition` to `Approved`. Say:

> "Clear your context and run `/tpe:execute .claude/features/{slug}`."
