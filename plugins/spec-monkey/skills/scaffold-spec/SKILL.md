---
name: scaffold-spec
disable-model-invocation: true
argument-hint: "[what you want to build or change]"
model: sonnet
effort: high
description: "Scaffold a blank spec for the user to write themselves, then critique it. Use when the user wants to author the spec by hand — to think it through and sharpen their engineering — instead of having create-spec do the interrogation and design for them. Creates a lean blank at docs/specs/{slug}/spec.md, then (when they're ready) runs the linter and spec-monkey:plan-reviewer and coaches them through the findings. Never writes the spec content for the user."
---

# Scaffold Spec

This is the **write-it-yourself** path. `create-spec` does the thinking for the user; this
skill hands them a blank and critiques what they write. The point is to make them a sharper
engineer — so they fill the sections, and the review teaches them where the gaps are.

You do two things: scaffold the blank, then (when the user is ready) critique it. **You never
write the spec content for the user.** Coaching, not ghost-writing.

## Phase 1 — Scaffold

- Settle on a short kebab-case `{slug}` for the change; confirm it with the user.
- Copy `reference/blank-spec.md` to `docs/specs/{slug}/spec.md`. Fill only `created` (today) and
  a stable `id`. Leave every other field blank — that's the user's to write.
- Tell the user the file is ready, and what each section asks for, one line each:
  - **Goal** — one measurable sentence; the delta.
  - **Context** — what exists today, why now.
  - **Requirements** — what it must do; each FR with testable acceptance criteria; the Edge Cases.
  - **Scope** — in vs out, with reasons.
  - **Approach** — the non-obvious path: mirror, ordering, gotchas.
  - **Files / Change Manifest** — every file you'll touch, and how.
  - **Verification** — the exact commands plus one worked case.
- Note the optional sections in the `handling-specs` skill (Glossary, Data Model, NFRs, Success
  Criteria) — add any that apply.
- Then stop. The user writes. They return when ready.

## Phase 2 — Critique (when the user says the spec is ready)

- **Cheap pass first:** dispatch `spec-monkey:reference-linter` on the spec. Relay any MISSING /
  MISLOCATED reference so the user fixes stale file or symbol citations before the deep review.
- **Then** dispatch `spec-monkey:plan-reviewer` on the spec. It returns BLOCKING / SHOULD_FIX /
  SUGGESTIONS.
- Relay the findings grouped by severity. For each, **explain the principle, not just the fix** —
  why a competent reviewer flags it, so the user learns the pattern. (E.g. "this acceptance
  criterion can't fail because it asserts a value the code constructs — derive the expected value
  independently.") That teaching is the whole point of this path.
- **Do not rewrite their spec.** Point at what's weak and why; give direction, not finished prose.
  Let them make the fix.
- Re-review after they revise, until the spec-monkey:plan-reviewer verdict is APPROVE.

## Phase 3 — Decompose & hand off

Once the spec-monkey:plan-reviewer verdict is APPROVE and the user approves the spec:

- Set the spec's `status` → `reviewed`.
- Hand it to `spec-monkey:spec-decomposer` to break it into tasks. It writes the Tasks table;
  relay its report — the parallel waves, the trade-offs, and any flagged tasks.
- Then **offer** to run the `execute-spec` skill to implement. If the user accepts, hand off to it;
  otherwise stop here with a reviewed, decomposed spec.
