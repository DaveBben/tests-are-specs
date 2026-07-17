---
name: scoping
version: "0.2.0"
description: "Scope a change before any code exists — interview the human to uncover requirements (you never invent them), surface edge cases, and emit a one-page intent plus a decision-log receipt. Use for expensive-to-change work: crossing a seam, a data shape or migration, an external contract, a trust boundary, or anything needing sign-off. Do NOT fire on trivial changes (typo, null check, copy tweak, version bump) — those go straight to build."
license: MIT
compatibility: any-agent
metadata:
  effort: interview before you build; the intent is a page, not a document
  namespaced-as: "spec-intents:scoping"
---

# Scoping

You scope a change before code exists: pin the goal, uncover the requirements from the human, decide how you'll verify. The requirements are the human's; you only uncover and format them, never author them. Output is a one-page intent in the PR body plus a receipt in the decision log.

## 1. Triage by cost-of-change

State the lane and why, in one line, before anything else.

- **Just build it:** trivial, one sane approach, no blast radius (typo, null check, copy tweak, version bump). Skip scoping. Go build.
- **Scope it** if it's expensive to reverse: crosses a seam, touches a data shape or migration, changes an external contract, crosses a trust boundary, or needs sign-off. Run the rest of this skill.
- **Too big to scope as one thing:** the ask is really several changes with different reviewers or ship dates ("build our auth system"). Don't scope it as one. Name the smaller independently shippable parts and the order between them, then scope only the first.

Don't manufacture ceremony to look careful.

## 2. Probe (only if the ground is unfamiliar)

Ask yourself one question: **what are the things that must exist for this to actually work?** If you don't know them, you can't write correct acceptance criteria yet. Investigate: read the code, or build a throwaway spike to learn, then delete the spike and scope. If the ground is already known, skip this.

## 3. Interview: the requirements come from the human

Load `references/interview-questions.md` and work through it. It covers functional requirements (what the system does) and non-functional ones (how well it does it).

This is the one rule that matters most:

- **You never state a requirement the user didn't give.** You uncover requirements by asking; you do not supply them.
- **When you spot a gap, ask, don't tell.** If you believe a requirement is missing, you must not tell the user what to add. Ask a question that leads them to surface it themselves. Say "What happens when two users submit at once?", not "you need idempotency here."
- The final list is **functional and non-functional requirements that all came from the user.** Your job is to uncover and format, never to author.

Run it as a conversation: one question at a time, hardest-uncertainty first, plain language. Reflect each answer back ("I take you to mean X, which implies Y, right?") and get agreement. Ask for their answer before you offer your own.

## 4. Surface edge cases; the human dispositions each

Here you add real value: you surface, the human decides. Load `references/edge-cases.md` and walk the dimensions it lists that actually bite (input, quantity, time, state, failure, the human). Sketch the flow as you go so gaps show up as blank space; the requester describes the happy path by default, so probe the incident cases hardest. Surface each edge case as a question. The human gives each one a disposition:

- **Handle** → becomes an acceptance criterion → becomes a test.
- **Accept** (a known gap) or **Out-of-scope** → a receipt in the decision log.

## 5. Decide how you'll prove it

Name the check that will prove each acceptance criterion and the goal; this is the verification plan. You're choosing the *method* now, not writing the tests; that happens in build. Each check must be:

- an **observable behavior**, stated as an outcome: "expired link → 400", not "function X returns Y";
- **executed**: an automated test, or a written manual script a human actually runs; never a check nobody runs;
- **able to fail** if the behavior broke.

Use the repo's existing test tooling; don't impose a framework. If you already know the command, note it (`pytest -k expired_link`). A criterion with no runnable check isn't ready; take it back to step 4.

## 6. Emit the intent

One scoped change gets one home: a single draft PR, opened early for this change. Its branch is where `build` commits the slices, and the intent dies when it merges. Write the intent to that **PR body**, formatted with the template at `pr_template` (read from `.spec-intents/config.json`; default `.spec-intents/pr-template.md`). If the branch/PR doesn't exist yet, open a draft one now (or put the intent in the **ticket** and let `build` open the PR). Not one PR per slice; slices are commits inside this one. Not one PR for a whole initiative; a large ask was split into separate scoped changes upstream, each with its own PR and intent.

A one-page intent, max. It holds:

- **Goal:** the checkable delta ("X moves from A to B"), confirmable true or false.
- **Requirements:** the functional and non-functional requirements the human gave, formatted as a list.
- **Acceptance criteria:** the HANDLE dispositions, each checkable.
- **Verification plan:** the tests or observation script from step 5.
- **Out-of-scope:** what you're deliberately not doing.

If it grows past a page, the change is probably two changes; go back to triage. The intent is disposable; it dies at merge.

## 7. Log the why, then ratify

Append a receipt to the **decision log**, an append-only, ADR-style file in the repo. It records *why*, never *what is true now*; constraint values live in tests, not here. One entry per genuinely expensive decision or per consciously-unhandled edge case. Per entry:

```
DATE · the decision
  Why:      the rationale
  Rejected: the alternatives you turned down
  Verify:   (optional) a verification-approach note, if it was a real tradeoff
  Not handled (out of scope): the ACCEPT / OUT-OF-SCOPE dispositions
```

Then ratify the decision **before any code**. How ratification happens is a team policy, not a per-change call. Read `decision_review`: check `.spec-intents/config.json` first (run `cat .spec-intents/config.json`, or open it with your file tool). If the file or the key is missing, fall back to a value stated in `CLAUDE.md` / `AGENTS.md`; otherwise default to `expensive-only`.

- **`always`:** every scoped decision gets a human PR review before code (open a separate decision-only PR carrying the log receipt).
- **`expensive-only`** (default): put the decision in the feature branch's PR description; open the PR early as a draft and get a quick sign-off on the approach, then build. Escalate to a separate decision-only PR only for a genuinely big, irreversible call (a schema change, a public API contract).
- **`never`:** solo / high-trust; the human still authors the intent, but there's no separate review gate before code.

Default to the PR description. A separate PR is an escalation, never a per-change habit.

## Stance

- Conclusion first, plain language, one idea per sentence.
- The human authors intent; you never do. Push back when the ask looks wrong; never invent a requirement to fill a gap; ask.
- Mark every unverified belief an assumption, not a fact.
- Respect the repo's house rules. A scope that fights one is wrong however clean it reads; surface the conflict, don't work around it quietly.
- "Agreed" means an explicit yes from the human, not silence, not a vague "looks good", and never a yes you record on their behalf.

## Next step

Hand the intent to the human. Once the direction is ratified per the policy above, use the `build` skill to implement it slice by slice.
