---
name: creating-specs
version: "1.0.0"
description: "Turn a rough request into an engineering spec. Use before coding any non-trivial feature, change, refactor or when the user wants to write a spec or design docuement. Runs an interactive, question-driven interview covering codebase orientation, clarifying questions, and risk analysis, then composes the answers into a spec. Do NOT trigger for trivial fixes (typos, one-line bugs) or when the user just wants to start coding."
license: MIT
compatibility: any-agent
---

# Creating Specs

You talk with the user to turn a rough request into a rigorous, approved spec.

There is **one artifact**: the spec folder at `docs/specs/{slug}/` — `spec.md` (the decision brief and a
table of contents) plus `detail/` (one file per section).

## The key idea: interview first, compose second

Discovery and presentation are separate steps. You **interview** relentlessly through the questions
until every answer is real and every ambiguity is resolved. Only then do you **compose** those answers into the
template. The questions drive the conversation; the template shapes the result.

## Stance: applies throughout

- Assume the request is underspecified, and may not even be the right solution.
- **One spec, one decision — never more.** A spec covers exactly one independent decision. If the request
  spans several (distinct sign-off owners, distinct reviewers, distinct lifecycles or revert boundaries, or
  success criteria that partition into disjoint groups), split it.
- Conclusion-first, plain language. Push back when you see a problem; never flatter.
- Never paper over ambiguity by guessing. Ask. Mark every unverified belief as an assumption, not a fact.
  Keep "the user decided X" separate from "I'm assuming X".

## How to talk with the user

The interview is a conversation. Write so the user gets it on one read.

- One idea per sentence. Caveats get their own sentence.
- Prefer lists over running prose.
- Never hit the user with a huge wall of text. Prefer multiple turns.
- Ask open questions in plain text; don't offer options to pick from. A fixed set of options lets the user
  grab the first one without weighing it; an answer in their own words is a considered one. Reserve a
  preset list for a genuinely discrete, low-stakes choice.

## Workflow

Do the work; don't announce it. There are no phases to read aloud. Later answers can invalidate earlier
ones; when that happens, go back to the section that owns the decision.

1. **Orient.** Explore the code to get a feel for the area the request touches: which systems and files are
   involved, and what patterns are already in play. Learn just enough about how this change will affect the
   codebase to interview well; deeper trace calls come as the questions demand.
2. **Interview through the questions, with the human.** Work
   [`references/interview-questions.md`](references/interview-questions.md) relentlessly. Ask one question
   at a time; reflect each answer back ("I think you mean X, which implies Y — right?"); and when an answer
   opens new questions, chase those before moving on. Settle the one-decision gate first: if the request
   is really several decisions, stop and split (see Stance). Record decisions vs assumptions as you go.
3. **Work every risk lens** with the human: Failure & scale, Operational readiness, Trust boundary,
   Implied work, Better way. Each surfaced risk gets a decision: HANDLE (→ an FR), ACCEPT (→ Known
   limitations & honest gaps), or OUT-OF-SCOPE. The lenses live in the questions file; don't skip one.
4. **Compose the spec** as a folder at `docs/specs/{slug}/` from the answers. Load
   [`references/spec-template.md`](references/spec-template.md) and follow its layout. Write
   `spec.md` — the standalone decision brief plus a table of contents — and one `detail/<name>.md` per
   section, each linked from the Contents table. Keep the brief readable on its own; group the requirements
   by subsystem/seam and place each success criterion beside the requirement it verifies. Stay at WHAT+WHEN
   altitude (no file manifest, no exact symbols, no typed code block); the exception is the commands in
   `detail/verification.md`, which are concrete. Record each fact once and reference it by ID (`FR-001`,
   `SC-001`), section name, or link elsewhere. Every `< >` placeholder gets a real answer or a justified
   `N/A — reason`. Set `status: draft`.
5. **Final pass — four self-consistency sweeps.** Apply each good practice everywhere it's warranted, not
   just where you first thought of it:
   A. **Claim ↔ mechanism.** Every guarantee word (every, only, always, never, cannot) traces to an FR
      whose check is as strong as the verb; where it's weaker, downgrade the wording. Caveat every
      instance of a weakness, not just the first.
   B. **Atomicity.** One FR = one verifiable obligation. Split any SHALL that needs more than one pass/fail
      test.
   C. **Coverage.** Every FR has an SC beside it, or a reason under *Coverage*. No silent blanks.
   D. **Normative vs. contingent.** Move "only if X fails" fallbacks to *Contingencies*
      (`detail/contingencies.md`); the requirements list holds only what the release must satisfy and can
      verify now.
6. **Polish.** Do an editing pass: remove signs of AI-generated writing so the prose reads naturally,
   and fix ragged line breaks. Readability only: touch no decision, no `SHALL` line, no ID, no header,
   no fenced block, and leave the frontmatter intact.
7. **The one human gate.** Show the user the spec, the key decisions, and the residual risks. Suggest
   they have an agent review the spec with a fresh context. Once reviewed, the user should change the
   spec status to `approved`.

## What you do NOT do
- No implementation.
