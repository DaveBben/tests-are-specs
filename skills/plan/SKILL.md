---
name: plan
effort: medium
model: opus
disable-model-invocation: true
argument-hint: "[feature slug or .claude/features/{slug} path]"
description: >
  Takes an approved brainstorm.md and produces plan.md and task JSONs
  ready for /act. Minimal user interaction — Think already made the
  decisions. Do NOT run without an approved brainstorm.md (run /think
  first). Do NOT use for bugs (use /cks:bug).
---

# Plan — Implementation Specification

> Think made the decisions. Plan translates them into a verified,
> executable specification. The output is plan.md and task JSONs that
> /act can run without needing to ask questions.

```
/cks:plan {slug}
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
> "No brainstorm.md found at `.claude/features/{slug}/`. Run
> `/cks:think {description}` first to produce one."

Hard stop if:
- Status is not `Approved` — tell user to complete `/cks:think` first
- At-risk tests section contains `[unverified]` entries — ask user to
  confirm or remove them before proceeding. Unverified test context is
  worse than no test context.
- More than 3 `[TBD]` entries — too many open decisions. Return to
  `/cks:think` to resolve them.

Read `CLAUDE.md` and any domain `spec.md` for the affected area.
Do not summarize — use to orient the investigation below.

Check the `Last verified` date on any `spec.md` read. If older than
30 days, warn before continuing:
> "spec.md was last verified {date} — {N} days ago. It may not reflect
> the current codebase. Consider running /cks:onboard to refresh it
> before planning. Continue anyway? (yes/no)"
A stale spec means the investigation may be anchored to wrong
assumptions. Do not block — warn and let the user decide.

---

## Step 2 — Deepen Investigation

brainstorm.md identified what changes. This step finds the exact code
the plan will reference.

For each file in brainstorm.md's Impact Surface, read targeted extracts:
- The specific symbol being changed (function signature, type definition,
  schema shape) — not the full file
- The reference implementation from brainstorm.md's Chosen Approach
- Any interface or contract the changed symbol must satisfy

**Cap reads to what the plan will actually cite.** Do not read files
speculatively. Every file read here should produce at least one
`file:line` reference in plan.md. If it doesn't, stop reading it.

Resolve the dependency chain from brainstorm.md against the actual
codebase — verify each hop in the chain exists at the stated path.
If a hop is wrong, find the correct path now. Do not carry stale
dependency chains into task JSONs.

---

## Step 3 — Write plan.md

Write `.claude/features/{slug}/plan.md` using the
[plan.md template](references/templates.md#planmd).

**Content rules:**

- **Real code, not pseudocode.** Every symbol in the Implementation
  section must exist in the codebase or be the exact proposed new
  signature. Paste the current signature alongside the proposed change.
- **Omit empty sections.** A shorter plan outperforms a comprehensive
  one. If a template section has no content, leave it out.
- **Impact table is exhaustive.** Every file that will be created,
  modified, or deleted — with the specific symbol and reason.
- **Patterns to Follow** cites at most 2 references. More than 2 is
  noise. Pick the closest analogue only.
- **What NOT to Do** pulls directly from brainstorm.md's Do NOT and
  Constraints sections — do not rewrite, copy verbatim.
- **Delivery strategy**: under ~500 lines total → single PR.
  Over → vertical slices only. Never horizontal layers.
- End with "Do not implement yet."

**Target: 100–200 lines.** If approaching 200, cut — the plan is
input to task decomposition, not documentation.

---

## Step 4 — Verify plan.md

Launch the `plan-verifier` agent. It checks that every `file:line`
reference, type, and function signature in the plan actually exists.

Note: the plan-verifier was written for the old feature skill schema
which included `testContext` and `implementationContext`. Those fields
are removed in this skill. The verifier's checks on file references,
code snippets, assumptions, pattern references, impact table, and
at-risk tests all still apply — ignore any output about missing
`testContext`/`implementationContext` fields.

Apply every `@FIX:` correction before proceeding. Do not present a
plan with unresolved discrepancies.

If the verifier finds more than 3 discrepancies, re-read the affected
files and rewrite those sections before re-running verification.
A plan with many stale references indicates the investigation in Step 2
was insufficient — do not patch one by one, fix the source.

---

## Step 5 — Decompose into Task JSONs

### Re-anchor before decomposing

Re-read from brainstorm.md: Chosen Approach, Do NOT, Constraints,
At-Risk Tests. Re-read from plan.md: Impact table, What NOT to Do.
These are the boundaries every task inherits. Do not proceed without
re-reading — they degrade in attention over long sessions.

### Task granularity

- **Single concern** — 1–3 files, hard max 4. Route + controller +
  types = one concern. Auth + schema + frontend = three concerns.
- **Count decisions, not lines.** 200 lines / one decision > 30 lines /
  three decisions.
- **Over 20 tasks**: the feature needs splitting.

### Vertical slices only

Each slice = complete vertical path (data layer + service + API + test).
Never a horizontal layer (all models, then all controllers).
Each slice must be independently reviewable and have exactly one reason
it would be reverted.

### Task JSON fields

Each task JSON contains exactly these fields — no others:

```
id, slice, repository, title, status, implementer
intent        — WHY this task exists (one sentence, enables
                ambiguity resolution — not what it does)
files         — 1–4 paths, hard max 4
symbol        — specific function or type to create/modify
reference     — single closest pattern (file:line), from plan.md
                Patterns to Follow. One entry only.
dependencyChain — ordered import path, entry point → target (3–5 hops)
                  verified against codebase in Step 2
relevantFiles — each file in `files` with action: "create" or "modify".
                Used by /act to verify filesystem state before dispatch.
blockedBy     — task IDs that create types/interfaces this task consumes
atRiskTests   — from brainstorm.md At-Risk Tests, confirmed by user.
                Each entry: path, symbol, reason.
                Empty array only if no existing tests touch affected code.
doNot         — at least one boundary, pulled from plan.md What NOT to Do
acceptanceCriteria — GIVEN/WHEN/THEN, one entry per observable behaviour
verificationCommand — single runnable test command
regressionCheck — command to run atRiskTests. Empty only if atRiskTests
                  is empty. MUST be set when atRiskTests is non-empty.
doneWhen      — mechanically verifiable. MUST include "and regressionCheck
                passes" when atRiskTests is non-empty.
scopeBoundaries — what this task owns vs what adjacent tasks own
```

**Fields removed from the old schema and why:**
- `testContext` — merged into `atRiskTests` (same information, one
  channel reduces context interference)
- `implementationContext` — removed. Research shows adding a third
  context type on top of blast radius + patterns can catastrophically
  interfere (36% → 19% resolution). `reference` (one entry) is
  sufficient.
- `environmentCheck` — keep if the project requires it; omit otherwise.
  Not a universal field.

### Validate each task JSON before writing

- `files` has 1–4 entries. More than 4: split the task.
- Every path in `files` has a matching entry in `relevantFiles`
- `relevantFiles` paths with `action: modify` exist on disk
- `relevantFiles` paths with `action: create` do NOT exist on disk
- `doNot` and `acceptanceCriteria` are non-empty
- `doneWhen` is non-empty and mechanically verifiable
- `intent` explains *why*, not *what*
- `regressionCheck` is set whenever `atRiskTests` is non-empty
- `reference` is a single entry pointing to a verified `file:line`
- No `[TBD]` values — all fields must be resolved

Write `tasks/plan.json` + `tasks/task_{N}.json` per task.

---

## Step 6 — Single Review Pass

Present plan.md to the user:

> "The plan is at `.claude/features/{slug}/plan.md` and {N} task JSONs
> are in `tasks/`. Review the plan and either:
> 1. **Give feedback** — tell me what's wrong, I'll revise once
> 2. **Approve** — say 'approve' to proceed to /cks:act"

Process feedback as one revision pass. Re-run the plan-verifier after
any changes to plan.md that touch code references.

After revision, if the user gives further feedback: apply it, but flag:
> "This is the second revision. If the plan still doesn't match your
> intent, consider returning to /cks:think — the approach may need
> revisiting rather than the plan."

On approval: set plan.json status to `Approved`. Say:

> "Run `/cks:act .claude/features/{slug}` to execute."
