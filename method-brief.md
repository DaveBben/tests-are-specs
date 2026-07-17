# Design brief: a lightweight agentic-coding method (build this as a plugin)

This is a brief for an agent to build a skills plugin. It describes a method for
AI-assisted coding designed to fix the documented failures of spec-driven
development (SDD). Build the skills to enact this method. Working name:
**the method** — rename freely.

---

## Philosophy (the one paragraph)

The code and its tests are the only source of truth for what the system does.
Everything else is either short, disposable steering or dated history. We refuse
to create a long, generated, authoritative prose spec — that single artifact
causes most of SDD's failures. Ceremony scales to the cost of changing a
decision later: nothing for a typo, a real (but brief) scoping pass for something
expensive to reverse. The human authors intent; the agent never authors the
source of truth. Verify by driving the real feature *and* by an adversary reading
the code — never by a self-graded green check. Keep only the code, the tests, and
the *why*; throw away everything else at merge.

**The core move:** a spec fuses three jobs that want opposite things — steering
(short, disposable), verification (executable, deterministic), and rationale (the
"why", durable). Split them into three artifacts, each with the right lifespan.

---

## Actors

- **Human** — authors intent and drivers, dispositions edge cases, ratifies the
  decision, reads diffs. The only author of the source of intent.
- **Builder** — the implementing agent. Proposes approach and edge cases; writes
  tests and code. Never the final grader of its own work.
- **Reviewer** — a *separate* agent in a fresh context. The adversary. Attacks the
  diff for correctness, security, and fake tests.

---

## Artifacts and their lifespans

| Artifact | Home | Lifespan | Holds |
|---|---|---|---|
| **Intent** | PR body (or ticket), formatted with the `pr_template` | Disposable — dies at merge | Goal, requirements, acceptance criteria, verification plan, out-of-scope |
| **Slice checklist** | the `task_list` path (default `.spec-intents/task-list.md`, gitignored) | Ephemeral — deleted at merge | The thin-slice to-do list for *this* change; session-resume memory |
| **Decision log** | Append-only file in the repo (ADR-style) | Durable — kept forever | The *why*: rationale, rejected alternatives, and consciously-unhandled edge cases |
| **Tests + code** | The repo | Durable — the source of truth | What the system does; the executable form of every constraint |

Hard rules:
- **Constraint values live in tests, never as prose in the log.** The log records
  *why* a constraint exists, not its value — else you have two sources of truth
  that drift (the rotting second-spec).
- **Never use persistent/global agent memory for slice state.** Slice memory is
  branch-local and dies at merge. The durable slot belongs to tests and the log.
- Test for where something goes: *would a developer six weeks from now want to
  read this?* Yes → log or test. No → intent or slice checklist (disposable).

---

## The flow, step by step

### Step 0 — Triage (always, cheap)
On any change request, decide the lane by **cost of change**:
- **Just build it** — trivial, one sane approach, no blast radius (typo, null
  check, copy tweak, version bump). Skip ceremony. Go straight to Build (Step 4).
- **Ceremony** — expensive to reverse: crosses seams, touches a data
  shape/migration, changes an external contract, crosses a trust boundary, or
  needs sign-off. Run the full flow.

State the lane and why in one line. Do not manufacture ceremony to look careful.

### Step 1 — Probe (only if the change is unfamiliar)
If the builder doesn't understand the current-state code well enough to scope
correctly, build a throwaway spike to *learn*, report what was learned, then
**delete the spike**. You cannot write correct acceptance criteria for something
you don't understand yet. Skip this step when the ground is already known.

### Step 2 — Scope ceremony (human authors; agent interviews)
The skill interviews the human — hardest-uncertainty first — and the **human
answers**. The agent does not invent requirements. The agent's active jobs here:
1. Ask the questions that pin the **goal as a checkable delta** and the
   **constraints that actually bind**.
2. **Surface edge cases** via risk lenses (failure & scale, trust boundary,
   malformed/hostile input, concurrency, implied work). This is where the agent
   adds real value — the human dispositions each surfaced case:
   - **Handle** → becomes an acceptance criterion → becomes a test.
   - **Accept** (known gap) or **Out-of-scope** → a receipt in the decision log.
3. Decide the **verification method now** — executable tests written before the
   code (not a "?"). Where the surface is genuinely exploratory (UI feel), the
   check is a written manual observation script that a human runs; the rule is
   only that the check is *executed*, never prose nobody runs.

Output: a short **intent** in the PR body — goal, constraints, acceptance
criteria, verification plan, out-of-scope. A page maximum (respect the ~1-page
comprehension ceiling).

### Step 3 — Log the why, ratify the decision before code
Append the drivers to the **decision log**: the rationale, the rejected
alternatives, any verification-approach decision that was a real tradeoff, and the
consciously-unhandled edge cases (the Accept/Out-of-scope dispositions).

Then get the *decision ratified before any code exists* — cheap review of the one
thing that steers everything. The review artifact is small (the intent plus the
log receipt — a page), so this is the good kind of gate, not SDD's review-2,500-
lines-of-prose ceremony. **How** the ratification happens is a **team policy**, not
a per-change judgment call. Expose it as a setting the `scope` skill reads from the
repo's standards doc (`CLAUDE.md` / `AGENTS.md` / plugin config):

```
decision_review:  always | expensive-only | never
```

- **`always`** — every ceremony-lane decision gets a human PR review before code.
  (Governance-heavy teams. Cheap here, because the artifact is a page.)
- **`expensive-only`** (default) — a decision gets its ratification in the feature
  branch's **PR description**: open the PR early as a draft, get a quick 👍 on the
  approach, then build. Escalate to a **separate small decision-only PR** (just the
  log receipt) only for a genuinely big, irreversible call — a schema change, a
  public API contract — where you want sign-off before spending build effort.
- **`never`** — solo / high-trust flow; the human still authors the intent, but no
  separate review gate before code.

Default to putting the decision in the feature branch's PR description. A separate
PR is an escalation for big decisions or a team-wide `always` policy — never a
per-change habit you invent each time. This is the governance gate for the
highest-leverage artifact (fixes the "highest-leverage, least-governed file"
problem).

### Step 4 — Build in thin slices
Work one vertical slice at a time (the smallest change that produces observable
behavior). For each slice:
1. Builder writes the **failing test first**; human eyeballs it (seconds, because
   it's three concrete assertions, not prose).
2. Builder implements until the slice is green.
3. Prove the slice before starting the next. Track slices in the `task_list`
   file (default `.spec-intents/task-list.md`, gitignored; dies at merge).

Bug-fix protocol (explicit): reproduce with one failing test, fix, keep the test.
No story fan-out. A one-line bug is a one-line fix plus a regression test.

### Step 5 — The two-part gate (both required; they guard each other)
A green check alone is never trusted. The two gates run at **different times**,
because they cost different amounts and catch different things.

- **Gate A — behavioral. Runs after *every* slice.** Run the real feature end to
  end with real inputs and *observe* the outcome — including an abuse case. Not
  "tests green"; demonstrated behavior. This isn't optional per-slice: proving each
  slice before the next *is* Gate A, and it's cheap (you just run it). It stops you
  building slice 3 on a slice 1 that silently doesn't work.
- **Gate B — adversarial review (fresh-context Reviewer). Runs once, on the
  complete diff, before merge.** Reads the actual diff hunting for where it's
  wrong, unsafe, or mismatched to intent. Standing mandate on every run:
  - **Correctness** against the intent.
  - **Security**: trust boundaries and authorization on the real code.
  - **Test integrity**: every test would actually fail if the code were broken —
    no assertions on constants, no self-verifying mocks, no stubbed-out real path.

  It runs at the end, not per slice, because its best catches — security holes,
  cross-slice inconsistency — are whole-change properties invisible in one slice,
  and a fresh-context pass is expensive to repeat.

  **Escalation — review a foundational slice early.** If a slice lays a shared
  abstraction, opens a trust boundary, or changes a data shape that later slices
  build on, run Gate B on *that* slice before building on it. Cost-of-change
  applied to review timing: catch a bad foundation before three floors sit on it.

This self-scales: a 1–2 slice change collapses the per-slice proof and the final
review into effectively one pass; a 4–5 slice change with a risky foundation earns
one early Gate B plus the final one — exactly where the extra pass pays off.

Gate A catches broken code; Gate B catches hollow tests and untested boundaries.
Ship only one and you keep the false sense of rigor while removing what made it
real.

### Step 6 — Route findings, then merge and clean up
- Reviewer FAIL → route each finding: "fix code" back to Builder; "the ask is
  wrong" back to the human/ceremony. Re-run Gate A on the affected slice and the
  final Gate B on the updated diff.
- Gate B green (and every slice's Gate A green) → the human merges (never the
  agent on its own read).
- **At merge, keep code + tests + the decision-log receipt. Delete the intent,
  the probe spike, and the `task_list` slice checklist.** Nothing that can rot
  survives.

---

## Task breakdown across developers (two levels)

Do **not** build a task-tracking system — that reinvents Jira, which is the
disease. Use two levels, only one of them shared:

- **Level 1 — across changes (team-visible, durable): the existing ticket
  tracker.** One expensive change = one ticket = one trip through this flow. A
  large initiative is decomposed *at ceremony time* into a **few coarse tickets**
  with dependencies noted (ticket B blocks on ticket A) — never a fine-grained
  2k-line task tree. Each ticket is independently flowable by a different
  developer. The decision log records *why* the seams were cut there.
- **Level 2 — within one change (private, ephemeral): the `task_list` file** (default `.spec-intents/task-list.md`, gitignored). The
  slices of a single ticket are one developer's working memory. Not shared team-
  wide; dies at merge.

**The rule that keeps coordination in the tracker:** one shippable slice = one
ticket = one branch. If two slices need two developers in parallel, they are two
tickets, not two slices — split them so the coordination surfaces in the tracker.

**Shared durable context across the team** is the committed decision log (read via
git). The tracker holds what's in flight; the log holds why past calls were made;
the code and tests hold what's true now.

---

## The decision log (spec)

- Append-only. Never edit a past entry; supersede it with a new dated one.
- One entry per genuinely expensive/irreversible decision, or per consciously-
  unhandled edge case. Prune ruthlessly — if it grows into a spec, it has the
  disease.
- Format per entry: date · the decision · why · rejected alternatives · (optional)
  a verification-approach note if it was a real tradeoff.
- It records *why*, never *what is true now*. To learn current behavior, read the
  code or run the tests.

Example:
```
2026-07-17 · Password reset tokens: single-use, 1h TTL.
  Why:      Replay defense — a leaked link must not work twice.
  Rejected: JWT-in-URL (can't revoke); multi-use links (replay risk).
  Verify:   Integration test against an SMTP stub, not mocked mail —
            a mock hid a delivery bug in the last mailer change.
  Not handled (out of scope): SMS reset — no provider budget this quarter.
```

---

## Skills to build (suggested shape — the builder decides final structure)

At minimum:
1. **`scope`** (or `plan`) — triage by cost-of-change; on the ceremony lane, probe
   if needed, interview the human, surface + disposition edge cases, emit the
   intent to the PR body and the receipt to the decision log. Ratifies the decision
   per the repo's `decision_review` policy (`always` → separate decision PR;
   `expensive-only` → PR-description sign-off, separate PR only for big irreversible
   calls; `never` → author-only). Trigger: an expensive-to-change request.
   Explicitly *does not* fire on trivial changes.
2. **`build`** — thin-slice, test-first implementation on an isolated branch;
   `task_list` slice checklist (gitignored, config-driven); runs **Gate A behavioral after every slice**; defined
   bug-fix protocol; hands the merge to the human.
3. **`check`** — the fresh-context Reviewer running **Gate B once on the complete
   diff** (and on a foundational slice early, when flagged): adversarial diff review
   with the standing correctness + security + test-integrity mandate. Report-only,
   PASS/FAIL, evidence on both sides (`file:line` + the intent line).

Plus a **decision-log convention** (ADR-style file + the append-only rule) that
`scope` writes to and `build`/`check` read.

Keep skill bodies lean and harness-neutral; push detail into reference files.

---

## Honest costs and non-goals (state these; don't hide them)

- **Gate B costs a second agent pass** on every expensive change. Real cost, worth
  it — it's where correctness actually comes from.
- **The decision log needs discipline.** One receipt per real decision, and prune.
  Undisciplined, it bloats back into a spec.
- **The human must author intent and read diffs.** This is deliberate — it's the
  only reliable defense against fabricated requirements. If you won't read the
  code, no method saves you.
- **If intent is wrong, you get a correct build of the wrong thing.** No method
  fixes that. This makes "it works" *demonstrated* and "conformance" *executable*;
  it does not make your intent correct.
- **Not a claim of proven results.** The design reverts to evidenced practices
  (vertical slices, code review, tests, ADRs) plus thin AI glue, and is
  lightweight enough to A/B against alternatives. Measure it; don't trust the
  feeling of progress.
