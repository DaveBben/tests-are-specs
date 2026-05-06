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

**Resume check:** if `tasks/plan.json` exists with `status: "PendingDecomposition"`, skip to Step 5. If `status: "Approved"`, the plan is already complete — inform the user and suggest running `/tpe:execute`.

Read `brainstorm.md`. Hard stop if no `brainstorm.md` exists:
> "No brainstorm.md found at `.claude/features/{slug}/`. Run `/tpe:think {description}` first to produce one."

Hard stop if:
- Status is not `Approved` — tell user to complete `/tpe:think` first
- At-risk tests section contains `[unverified]` entries — ask user to confirm or remove them before proceeding. Unverified test context is worse than no test context.
- More than 3 `[TBD]` entries — too many open decisions. Return to `/tpe:think` to resolve them.

Warn (do not hard stop) if:
- Dependency Chain section is empty or absent — dependency chains prevent NameError-class failures on multi-file tasks. Warn:
  > "brainstorm.md has no dependency chain. Multi-file tasks are at higher risk of cross-file reference errors. Continue or return to /tpe:think to add one?"

If 1–3 `[TBD]` entries remain (allowed by think), extract them now. During Step 2 investigation, search the codebase for evidence that resolves each TBD; if not resolvable within 2-3 targeted reads per TBD, leave it unresolved. Any that remain unresolved after Step 2 must appear in the relevant task's `doNot` as: "Do not assume [TBD topic] — decision pending."

Read `CLAUDE.md` and any domain `spec.md` for orientation. If any `spec.md`'s `Last verified` date is >30 days old, warn (do not block):
> "spec.md was last verified {date}. Consider refreshing before planning. Continue anyway?"

---

## Step 2 — Deepen Investigation

brainstorm.md identified what changes. This step finds the exact code the plan will reference.

For each file in brainstorm.md's Impact Surface, read targeted extracts:
- The specific symbol being changed (function signature, type definition, schema shape) — not the full file
- The reference implementation from brainstorm.md's Chosen Approach
- Any interface or contract the changed symbol must satisfy

**Cap reads to what the plan will actually cite.** Do not read files speculatively. Before reading a file, state what you expect to find (a signature, a type, a pattern). After reading, it must produce at least one `file:line` reference in plan.md — if it doesn't, stop and do not read the next file in that concern group. If the impact surface exceeds 10 files, read only files involved in breaking changes or the chosen approach's critical path; list remaining files as "verified exists, not read in detail."

**Breaking-change call-site sweep.** The cap-reads rule governs *speculative* file reading. The call-site sweep is *investigation*, not speculation — you may read discovered files to determine whether they are at risk. For every symbol in brainstorm.md's Impact Surface undergoing a breaking change (signature change, field removal, rename, deletion), grep the entire repo for references — especially tests. This is mechanical completeness: you must find every call site that will stop compiling or pass/fail differently after the change. After grepping, read each discovered file to assess risk status.

For each **test** file that references a symbol undergoing a breaking change, it must either appear in the task's `atRiskTests` or you must justify in plan.md why it isn't at risk. A plan that lists one obviously-named test but misses sibling tests hitting the same call site creates an impossible situation for the implementor: "change the signature, don't modify tests, regressionCheck must pass" becomes unsatisfiable.

For each **non-test** file that references a symbol undergoing a breaking change, it must appear in plan.md's Impact table as a `modify` entry (or be explicitly justified as not-at-risk). Changing a function signature while leaving unlisted callers in their old form produces a compile/type-check failure in files the plan never mentioned. Same root cause as the test gap, different failure surface.

Resolve the dependency chain from brainstorm.md against the actual codebase — verify each hop in the chain exists at the stated path. If a hop is wrong, find the correct path now. Do not carry stale dependency chains into task JSONs.

**Escape hatch — unexamined constraints.** If the investigation reveals that the chosen approach requires substantial complexity (parallel fetches, retry logic, translation shims, caching to bridge mismatches) that stems from an inherited upstream shape brainstorm.md did not interrogate, stop and flag to the user before writing plan.md:
> "The chosen approach requires [complexity] because [upstream shape]. Brainstorm didn't examine whether [upstream shape] is fixed. Returning to /tpe:think to surface 'redesign upstream' as an alternative may produce a simpler design. Continue with current approach, or return to think?"

Plan's job is to translate an approved approach, not to second-guess it — but if investigation surfaces an inherited-constraint issue think didn't see, the revision cycle is cheaper than shipping the complexity.

---

## Step 3 — Write plan.md

Write `.claude/features/{slug}/plan.md` using the [plan.md template](references/templates.md#planmd).

**Audience model — write for a stranger who will make false assumptions.** The implementor agent has no prior context on this codebase. It has not read the files you read in Step 2. It will not infer your project's conventions. Where a symbol "obviously" behaves a certain way, it will assume it does — and act on that assumption without checking. Where two things share a similar name, it will conflate them. Where a pattern is implicit, it will invent its own.

Plan as if every named symbol, path, and convention is something the implementor encounters cold. Concrete implications:

- **Cite, don't reference.** Every named symbol must come with paste-ready code or a `file:line` pointer — never a bare name the implementor has to go find. If you mention `UserValidator`, show its signature.
- **Disambiguate aggressively.** If two symbols/files share a basename, or if a name in your plan resembles a name the implementor will encounter elsewhere, qualify it (parent dir, role annotation). Naked basenames pattern-match to whatever the implementor saw last.
- **State the non-obvious explicitly.** If the code looks like it should do X but actually does Y, say so. If a function's name suggests behavior it doesn't have, call that out. Silence reads as confirmation of the implementor's first guess.
- **Show conventions, don't imply them.** Project-specific patterns (error handling, layering, naming, where logic lives) must be shown via the `Reference` pattern or pasted code. "Follow the existing pattern" is invisible to a stranger.
- **Pre-empt the likely wrong move.** After drafting each section, ask: "What's the most plausible wrong thing a stranger could do here that still satisfies the words I wrote?" If the plan doesn't rule it out, add a constraint to `What NOT to Do` or sharpen the section.

**Content rules:** real code (not pseudocode), omit empty sections, exhaustive impact table, max 2 pattern references, What NOT to Do copied verbatim from brainstorm.md's "Do NOT" section (if that section exists; if absent, write "None identified during brainstorm"). Under ~500 lines → single PR; over → vertical slices only. End with "Do not implement yet."

**"Real code" means:** paste-ready signatures, type definitions, and structural code that would compile/parse as-is. A function signature with typed parameters and return type is real code. A function body with `// handle validation here` is pseudocode. When the exact body isn't known yet, show the signature and say "body implements [one sentence]" — do not invent placeholder logic.

**Target: 100–200 lines.**

---

## Step 4 — Verify plan.md

Launch the `plan-verifier` agent using the Agent tool with `subagent_type: "plan-verifier"`. Apply every `@FIX:` correction. Ignore verifier output about missing `testContext`/`implementationContext` (removed fields). If >3 discrepancies, re-investigate the affected files rather than patching one by one.

After verification passes, write `tasks/plan.json` with `status: "PendingDecomposition"`. On resume: if plan.json exists with this status, skip to Step 5.

---

## Step 5 — Decompose into Task JSONs

### Re-anchor before decomposing

Re-read from brainstorm.md: Chosen Approach, Do NOT, Constraints, At-Risk Tests. Re-read from plan.md: Impact table, What NOT to Do. These are the boundaries every task inherits. Do not proceed without re-reading — they degrade in attention over long sessions.

### Audience model carries through

The same stranger-will-make-false-assumptions posture from Step 3 applies harder here. Each task JSON is read in isolation by an implementor with no memory of plan.md or the other tasks. A bare path in `files`, a symbol in `dependencyChain`, or a one-line `intent` is all the context they get for that field. Anywhere a name could be misread or a constraint could be silently ignored, encode it explicitly in `doNot`, `scopeBoundaries`, or the acceptance criteria — do not rely on the task ordering, the slice number, or "they'll figure it out from the file."

### Explore alternative decompositions before committing

For features with **4+ files or 3+ concerns**, generate **2-3 candidate decompositions** with different slice boundaries, task groupings, or ordering. For simpler features (fewer files/concerns), one decomposition is sufficient — skip the comparison.

For each candidate, evaluate against these criteria:

**Hard gate (must pass):**
1. **No unsatisfiable tasks** — every task's AC + doNot + atRiskTests are internally consistent

**Scoring axes (in priority order — first distinguishing criterion wins):**
2. **Minimal cross-task interface coupling** — fewer shared symbols between tasks means fewer integration failures
3. **Short blockedBy chains** (ideally ≤2 deep) — long chains serialize execution and amplify single-task failures
4. **Every task within 1–4 file hard max**
5. **Each slice independently reviewable with one revert reason**

Select the candidate that wins on the highest-priority distinguishing
criterion. If two are equivalent through all criteria, prefer fewer
tasks.

### Task granularity

- **Single concern** — 1–3 files, hard max 4
- **Count decisions, not lines.** 200 lines / one decision > 30 lines / three decisions
- **Over 20 tasks**: the feature needs splitting
- **Vertical slices only** — each slice is a complete functional path through all affected layers. Never a horizontal layer. Each slice must be independently reviewable with exactly one reason it would be reverted.

### Task JSON schema and validation

Use the schema and field notes in [task_{N}.json template](references/templates.md#task_njson). Key rules:

- `intent` explains *why*, not *what*. Litmus test: if the intent
  reads like a commit message ("Extract validation into shared module"),
  it's a *what* — rewrite as the reason ("Validation duplicated across
  3 handlers, causing drift when rules change")
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

**Ambiguity signals to catch:**
- Criterion uses "correct" or "appropriate" without defining what that means for this case
- Criterion names two behaviors joined by "and" — split into two criteria
- Criterion cannot be checked by running a command or reading a specific output — it's an aspiration, not an AC
- **Observable** means: the implementor can verify it by running a command, inspecting a file, or observing a behavior — not by reading the code and judging whether it "looks right"

**Validate before writing:** all paths exist/don't-exist as expected, `dependencyChain` hops have real import relationships (grep to confirm), no `[TBD]` values remain.

**Ground-before-terse:** any path appearing in a task's `files` or `dependencyChain` that isn't already in plan.md's Impact table must be added to the Impact table before writing the task. Task JSONs compress context into bare path strings — every path must be grounded in plan.md first, or a fresh reader has no context for what it is.

**Collision check against negated names:** for each basename in `files`/`dependencyChain`, check plan.md's `Scope > Out` and `What NOT to Do` and brainstorm.md's Do NOT. If the basename collides with anything there (e.g. dependencyChain references `s3.py` when plan.md said "no s3.py is created"), use a disambiguated form — parent dir prefix (`synthetic_data_gen/s3.py`) or a role annotation in the task's `intent`. A naked colliding basename will pattern-match onto the negated artifact in a reader's head.

**blockedBy integrity:** after all task JSONs are drafted, verify the dependency graph:
- Every id in any `blockedBy` array refers to a real task id in this plan (no dangling references like `task_99` when only `task_1..3` exist).
- No cycles — transitively follow `blockedBy` from each task; a task must not be reachable from itself. A cycle makes /tpe:execute deadlock.

**Task contract consistency:** for each task, cross-read `acceptanceCriteria`, `atRiskTests` / `regressionCheck`, and `doNot`. If an AC removes or changes something that an at-risk test asserts must behave the old way, *and* `doNot` forbids modifying tests, the task is unsatisfiable (change-X + X-must-still-work + can't-touch-test). Fix by scoping the test change into this task, moving the test change to a prior blocking task, or loosening the AC. Do not ship an unsatisfiable task — the implementor will stop and report, wasting a full execute cycle.

Write `tasks/plan.json` + `tasks/task_{N}.json` per task.

### Conditional: Architecture Decision documentation task

After writing the implementation tasks, check whether the architecture decision from brainstorm.md should be captured in spec.md's Architecture Decisions table.

**Skip this task if:**
- No `spec.md` was found during Step 1 orientation — there is nowhere to write the ARD
- brainstorm.md's Chosen Approach has no `**Rejected**:` entry — a decision with no rejected alternatives is a default, not an architecture decision worth recording

**When conditions are met**, generate one additional `task_{N+1}.json` as the final task (where N is the last implementation task):

```json
{
  "id": "task_{N+1}",
  "slice": 1,
  "repository": ".",
  "title": "Task {N+1}: Document architecture decision in spec.md",
  "status": "PENDING",
  "implementer": "AI",
  "intent": "Architecture decisions from the think phase should be captured in spec.md's Architecture Decisions table so future agents and developers understand why this approach was chosen without needing to find the feature's brainstorm.md",
  "files": ["{path to the relevant spec.md}"],
  "symbol": "Architecture Decisions",
  "reference": "",
  "dependencyChain": [],
  "relevantFiles": [
    {"path": "{spec.md path}", "action": "modify"}
  ],
  "blockedBy": ["task_{N}"],
  "atRiskTests": [],
  "doNot": [
    "Do not modify any section of spec.md other than the Architecture Decisions table",
    "Do not add the entry if the decision is obvious (can be inferred from reading the code)",
    "Do not remove or modify existing Architecture Decisions entries"
  ],
  "acceptanceCriteria": [
    "GIVEN brainstorm.md's Chosen Approach, WHEN the decision is non-obvious and has rejected alternatives, THEN a new row is appended to spec.md's Architecture Decisions table with columns mapped per the content mapping below",
    "GIVEN spec.md has no Architecture Decisions table, WHEN adding the entry, THEN create the subsection under Architecture Overview with the standard table header and the new row",
    "GIVEN the Chosen Approach is obvious or has no rejected alternatives, THEN report DONE with a note explaining why the decision was not recorded"
  ],
  "verificationCommand": "grep '<actual approach name>' <actual spec.md path>",
  "regressionCheck": "",
  "scopeBoundaries": "This task owns only the Architecture Decisions table in spec.md / all other spec.md sections are owned by execute's post-implementation step",
  "doneWhen": "Architecture Decisions table in spec.md contains a row matching brainstorm.md's Chosen Approach, or task reports DONE with justification for skipping"
}
```

**Content mapping** from brainstorm.md to spec.md ARD columns:

| brainstorm.md field | spec.md ARD column |
|--------------------|--------------------|
| `**Approach**: [name]` | Decision |
| `**Why chosen**: [text]` | Rationale |
| `**Date**` (brainstorm header) | Date |
| `**Rejected**: [alt] — [why not]` | Alternatives Considered |

**Which spec.md?** Use the same spec.md consulted during Step 1 orientation. If the feature's Impact Surface files are concentrated in a domain directory with its own spec.md, use that domain spec. Otherwise, use the root spec.md.

**Housekeeping:**
- This task does not count toward the 20-task complexity limit — it is a mechanical follow-on, not a feature decomposition task
- Update `plan.json`'s `totalTasks` to include it
- Include it in the blockedBy integrity check (trivially satisfied — it depends only on the last implementation task)

---

## Step 6 — Single Review Pass

Present plan.md to the user with a focused review guide. Identify the 2-3 highest-risk aspects of *this specific plan* — areas where a mistake would be hardest to fix downstream. Common risk areas: breaking-change call sites that might be incomplete, tasks with the most cross-task coupling, acceptance criteria for the most complex task.

> "The plan is at `.claude/features/{slug}/plan.md` and {N} task JSONs are in `tasks/`.
>
> **Highest-risk areas to scrutinize:**
> - [specific risk 1 — e.g. "Task 2 changes the User interface — verify the 4 listed call sites are complete"]
> - [specific risk 2]
>
> Review the plan and either:
> 1. **Give feedback** — tell me what's wrong, I'll revise once
> 2. **Approve** — say 'approve' to proceed to /tpe:execute"

Process feedback as one revision pass. Re-run the plan-verifier after any changes to plan.md that touch code references.

After revision, if the user gives further feedback: apply it, but flag:
> "This is the second revision. If the plan still doesn't match your intent, consider returning to /tpe:think — the approach may need revisiting rather than the plan."

On approval: update plan.json status from `PendingDecomposition` to `Approved`. Say:

> "Clear your context and run `/tpe:execute .claude/features/{slug}`."
