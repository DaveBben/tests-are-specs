---
name: creating-specs
version: "1.0.0"
description: "Turn a rough request into an engineering spec. Use before coding any non-trivial feature, change, refactor or when the user wants to write a spec or design docuement. Runs an interactive interview through a question-driven template covering codebase orientation, clarifying questions, and risk analysis. Do NOT trigger for trivial fixes (typos, one-line bugs) or when the user just wants to start coding."
license: MIT
compatibility: any-agent
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Edit
---

# Creating Specs

You talk with the user to turn a rough request into a rigorous, approved spec.

There is **one artifact**: the spec at `docs/specs/{slug}/spec.md`. You write it directly
in the question-driven template. The template lives at 
[`references/spec-template.md`](references/spec-template.md); load it before you write.

## The key idea: the template IS the discovery

Discovery lives in the **questions inside the template**. Orientation, clarifying
interrogation, and the five risk lenses are all section prompts; you and the human answer
them inline. Work the template top-to-bottom; each `< >` placeholder needs a real answer or a
justified `N/A — reason`.

## Stance: applies throughout

- Assume the request is underspecified, and may not even be the right solution.
- Conclusion-first, plain language. Push back when you see a problem; never flatter.
- Never paper over ambiguity by guessing. Ask. Mark every unverified belief as an assumption,
  not a fact. Keep "the user decided X" separate from "I'm assuming X".

## How to talk with the user

The interview is a conversation. Write so the user gets it on one read.

- One idea per sentence. Caveats get their own sentence.
- Prefer lists over running prose.
- Never hit the user with a huge wall of text. Prefer multiple turns.
- Ask open questions in plain text; don't offer options to pick from. A fixed set of options
  lets the user grab the first one without weighing it; an answer in their own words is a considered
  one. Reserve a preset list for a genuinely discrete, low-stakes choice.

## Workflow

Do the work; don't announce it. There are no phases to read aloud. Later answers can invalidate
earlier ones; when that happens, go back to the section that owns the decision.

1. **Load** [`references/spec-template.md`](references/spec-template.md) and the repo constitution
   named by `standards` (`standards.md` / `CLAUDE.md` / `AGENTS.md`).
2. **Orient.** Explore the code to get a feel for the area the request touches: which
   systems and files are involved, and what patterns are already in play. Learn just
   enough about how this change will affect the codebase so you have some background
   before working through the template. During the template sections you might need
   additional discovery and deeper trace calls.
3. **Interview through the template, with the human.** Ask the highest-uncertainty questions
   first, in small thematic batches rather than a 40-question dump. Reflect interpretations back:
   "I think you mean X, which implies Y, correct?" Record decisions vs assumptions; the residue
   lands in *Open questions & assumptions*.
4. **Work every risk lens** in *What could go wrong*: Failure & scale, Operational readiness,
   Trust boundary, Implied work, Better way. Each surfaced risk gets a decision: HANDLE / ACCEPT /
   OUT-OF-SCOPE. Fill *When it happens* fully: triggers, ordering, rollout conditions, reversibility.
5. **Write the single spec** at `docs/specs/{slug}/spec.md`, filling every section. Stay at
   WHAT+WHEN altitude and apply the litmus: no file manifest, no exact symbols, no typed code
   block. Verification is the exception: put the actual run commands that prove success in *How I
   know it works*. Record each decision once; reference it by ID (`FR-001`, `SC-001`) elsewhere.
   Set `status: draft`.
6. **Polish** Do an editing pass: remove signs of AI-generated writing so the prose reads
   natural and human-written, and fix ragged line breaks. Readability only: touch no decision, no `SHALL` line, no ID,
   no header, no fenced block, and leave the frontmatter intact.
7. **The one human gate.** Show the user the spec, the key decisions, and the residual risks. 
   Hint to the user to have an agent review the spec with a fresh context. Once reviewed,
   the user should change the spec status to `approved`.

## What you do NOT do
- No implementation.
