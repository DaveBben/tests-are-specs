---
name: bug
disable-model-invocation: true
argument-hint: "[bug symptom]"
description: >
  Bug investigation and spec producer. You describe a symptom, Claude
  reads the code, traces the root cause, and produces a bug spec ready
  for /specd:execute-spec. Use when something is broken and you need to
  understand why before fixing it. Do NOT use for features (use
  /specd:create-spec). Do NOT use for trivial one-line fixes.
---

# Bug — Symptom to Spec

> Bugs start from a symptom, not a change request. The highest-value
> step is understanding the root cause — not jumping to a fix.

**Write to be read on one pass.** Everything you say to the user — and the
prose sections of the bug spec (Intended/Actual behavior, Root cause,
Mitigation approach, Alternatives rejected) — follows the readable voice in
`skills/_shared/writing-voice.md`: one idea per sentence, actor-first,
caveats split into their own sentence, conclusion first. Keep the precision
(`file:line`, confidence levels); just unpack it across simpler sentences.
The contract sections (Constraints, Do NOT, Files that matter, Verification)
stay dense by design.

```
/specd:bug {symptom}
  → Understand the symptom
  → Read the code, trace the root cause
  → Confirm findings with user
  → Produce bug spec at docs/specs/bugs/{slug}/spec.md
```

---

## Phase 1 — Understand the Symptom

**Branch check.** Run `git rev-parse --abbrev-ref HEAD`. If on
`main`/`master`, note that you'll create a feature branch before
writing anything to disk in Phase 4 (the slug isn't known yet). If
on another branch, proceed — the spec will be written there. Never
write spec files or update the Spec Index on main.

Read `$ARGUMENTS`. If empty, ask:

> "Describe what you saw — the symptom, not the cause. For example:
> 'After saving, the old text still shows' rather than 'the cache
> doesn't invalidate.'"

If the user describes a root cause instead of an observable symptom,
redirect:

> "That sounds like a diagnosis. What did you actually see? What
> behavior was wrong?"

If the description contains multiple bugs:

> "That sounds like two issues. Which is more urgent? We'll handle
> the other separately."

Gather conversationally (not as a checklist):
- **Repro steps** — numbered, concrete actions
- **Expected behavior** — what should happen
- **Actual behavior** — what happens instead
- **Severity** — who is affected, how often, workaround?

**Stopping criterion:** you have enough when you could write a
failing test from the description alone. If the user doesn't know
details ("it just crashes sometimes"), note the gap and proceed —
code investigation may fill it. Max 2 rounds of questions.

---

## Phase 2 — Investigate

Read `CLAUDE.md` and `spec.md` if they exist. Then read the code
to trace the bug.

**Trace the code path.** Starting from the entry point of the repro
steps, follow the execution path to where the symptom manifests.
Read the actual files — don't guess from names. Cap at 8-10 files.

**Find the root cause.** Use two frames and check convergence:
1. Trace backward from symptom — what's the last correct state and
   where does it go wrong?
2. Trace forward from the suspected cause — if this is broken, what
   symptoms would it produce? Do they match the report?

If both frames converge on the same location, confidence is high.
If they diverge, surface the uncertainty to the user.

**Check for a working reference.** Is there a similar code path
that does the same thing correctly? (A different caller, a sibling
method, an older pattern.) If so, note it — the fix should follow
the working pattern.

**Assess blast radius.** What other callers invoke the affected
function? Does it read/write shared state? This determines whether
the fix is narrow or wide.

**Try to reproduce.** If there's an obvious test to run that would
confirm the bug, run it. Note whether it's RED (confirmed), GREEN
(did not reproduce), or ERROR (infrastructure issue).

---

## Phase 3 — Confirm with User

Present findings in two parts:

**Part 1 — Root cause:**

State the hypothesis with file:line evidence. Include your
confidence level:
- *Confirmed* — repro test fails at the exact location, both
  frames converge
- *Strong hypothesis* — both frames converge but no failing test
- *Candidate* — only one frame points here, evidence is
  circumstantial

If the root cause is architectural and a symptom-layer fix could
close the bug without touching the architecture, surface both
options:

> "Two ways to fix this:
> 1. **Fix at root** — [description]. Larger change, eliminates
>    the bug class entirely.
> 2. **Fix at symptom** — [description]. Smaller change, but the
>    underlying issue persists.
>
> Which approach?"

**Part 2 — Scope:**

> "The fix will touch [files]. It will NOT [boundaries]. Any
> concerns before I write the spec?"

Wait for confirmation.

**Complexity gate:** If investigation revealed >4 files affected or
the fix requires changing a shared interface, recommend escalating:

> "This is larger than a typical bug fix. Consider using /specd:create-spec
> instead — it'll help think through the approach more carefully.
> I can pass the findings. Escalate or continue?"

---

## Phase 4 — Produce the Bug Spec

Assemble the investigation into a bug spec. Write to
`docs/specs/bugs/{slug}/spec.md`. Create the directory if needed.

**Slug:** derive from the symptom (lowercase, hyphens, max 40
chars).

**Branch.** Before writing anything to disk, check the current
branch. If on `main`/`master`, create and switch to
`fix/{slug}`. If on another branch, confirm with the user that
this is where they want the spec committed. Never write spec files
on main.

Then launch the `specd-spec-reviewer` agent using the Agent tool with
`subagent_type: "specd-spec-reviewer"`. Pass the spec path. Fix any
failures before presenting.

After the reviewer passes, present the spec and ask:

> "Bug spec saved to `docs/specs/bugs/{slug}/spec.md`.
>
> Clear your context and run:
> `/specd:execute-spec docs/specs/bugs/{slug}/spec.md`"

Update the Spec Index in `docs/specs/spec.md` — add or update the
entry in a Bugs table (create the table if it doesn't exist). New
entries use status `Waiting Implementation`:

```markdown
### Bugs
| Spec | Path | Status | Updated | Description |
|------|------|--------|---------|-------------|
| {title} | `docs/specs/bugs/{slug}/spec.md` | Waiting Implementation | {YYYY-MM-DD} | {one-line description} |
```

Status values: `Waiting Implementation` | `Implemented` |
`Superseded` | `Deprecated` | `Needs Revision`. The `Updated` column
tracks the lifecycle — set it to today's date on every event:
created (new row), updated (any edit or status change, e.g. to
`Needs Revision`), or deleted (set status to `Superseded`/`Deprecated`
and keep the row). `/specd:execute-spec` flips to `Implemented` when
verification passes. If the bug is abandoned (e.g., turns out to be
expected behavior), set status to `Deprecated` rather than deleting
the row.

---

## Bug Spec Template

```
{One-line symptom description}

**Status**: Waiting Implementation
**Last updated**: {YYYY-MM-DD}

## Intended behavior
{What should happen. Concrete, observable.}

## Actual behavior
{What happens instead. Include error messages or observable output
if available.}

## Reproduce steps
{Numbered steps to trigger the bug.}

## Root cause
{What's broken and where. Include file:line. State confidence level
(Confirmed / Strong hypothesis / Candidate).}

## Mitigation approach
{The agreed fix approach and why. If a symptom-layer vs root fix
was discussed, state which was chosen and why.}

## Alternatives rejected
{If applicable — e.g., "Symptom-layer fix rejected because the
underlying issue would resurface as [scenario]".}

## Constraints
{What must be true for the fix to be correct. Specific, testable.}

## Edge cases
{Related scenarios that the fix must also handle. Format:
"condition: expected behavior"}

## Do NOT
{Scope boundaries. What the fix must not touch.}

## Files that matter
{Files involved in the fix, with symbols. Format:
- path/to/file.ext:symbolName() — role description}

## Verification
{Exact command to run, then:
- Repro test must go from RED to GREEN
- All existing tests listed must still pass
- Any new edge case tests must pass}

Keep going until all tests pass and the verification criteria are
met. If you hit a problem, investigate and fix it rather than
stopping.
```
