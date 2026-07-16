# spec-monkey + superpowers — who owns what

spec-monkey and [superpowers](https://github.com/obra/superpowers) are not rivals for the same slot. spec-monkey is strongest at the front half of a build (deciding *what* to build and getting a human to sign the contract) and the back half (proving the built thing matches the contract). superpowers is strongest in the middle (executing a plan with disciplined TDD, subagent orchestration, and worktrees). They compose, and the seam is clean because of one rule spec-monkey holds and superpowers doesn't touch:

> **spec-monkey forbids HOW only *in the spec*.** A plan is a downstream artifact. Putting file paths and code in a *plan* violates nothing.

So a spec-monkey `detail/contract.md` (WHAT/WHEN) can feed a superpowers `writing-plans` plan (HOW) without either system breaking its own rules.

## The division of labor

| Phase | Owner | Why |
|---|---|---|
| Project / architecture spec, invariants | **spec-monkey** `grounding-specs` | superpowers has no cross-feature grounding layer |
| Shape a fuzzy ask into a design, weigh approaches | **spec-monkey** `shaping-specs` (or superpowers `brainstorming`) | either works; pick one, don't run both |
| Review the design before a contract exists | **spec-monkey** `reviewing-design` | catches a wrong approach cheaply, before the contract |
| The binding FR/SC contract | **spec-monkey** `writing-specs` | the reader-split spec is the durable artifact |
| Review the contract before build | **spec-monkey** `reviewing-specs` | the self-consistency sweep with a decomposition gate |
| Turn the contract into a HOW-carrying plan | **superpowers** `writing-plans` | exact file paths + code, dispatchable to cheap models |
| Execute: red/green TDD, subagents, worktrees | **superpowers** (spec-monkey has a portable floor) | superpowers is the mature middle; spec-monkey now ships an isolated-branch/worktree step (`implementing-specs/references/build-workspace.md`), enough to build safely without it |
| Debug a break mid-build | **superpowers** `systematic-debugging` / `root-cause-tracing` | dedicated skills; deeper than spec-monkey's escape hatch |
| Independent audit of build vs contract | **spec-monkey** `auditing-specs` | spec-compliance audit with faked-done checks; superpowers has no equivalent |

## The one seam that matters

The handoff is `contract.md → plan`. The contract states the obligations (`FR`/`SC`), the data and interface contract, the timing, and the verification commands. A superpowers plan then names the files, the symbols, and the code to satisfy those obligations. Point the plan back at the contract's IDs so the audit can still trace `FR-NNN` to the change.

When the audit routes a deviation `amend-spec`, it goes to the **contract**, not the plan: the contract is the signed artifact, and it regresses to `draft` and re-earns its gate (see `writing-specs`, "Amending an approved spec"). The plan is regenerated from the amended contract.

### The executable handoff

The seam is one paste, not a doc to reread. Once `writing-specs` has produced an approved contract, hand it to superpowers `writing-plans` with this — no re-explaining the feature, because the contract already carries it:

```
Use the writing-plans skill to turn an approved spec-monkey contract into an
implementation plan.

Source of truth (WHAT/WHEN — do not restate, read and cite):
  docs/specs/<slug>/detail/contract.md
  docs/specs/<slug>/spec.md            (the decision brief)
  docs/specs/project/spec.md           (the INV-NNN and shared contracts this grounds on)

Write the plan as HOW: the files, the symbols, and the code that satisfy the
contract. Two rules make the audit still work afterward:
  1. Tag each plan task with the FR/SC ids it satisfies (e.g. "satisfies FR-003,
     SC-003"), so auditing-specs can trace every requirement to the change.
  2. Treat every cited INV-NNN and the "Verification approach & commands" block
     as binding. The plan may add detail; it may not drop or weaken an obligation.

The contract is signed and frozen. If building reveals it is wrong, do not fix it
in the plan — stop and route it back to writing-specs as an amend-spec (the
contract regresses to draft and re-earns its gate).
```

Then superpowers owns execution (its TDD, subagents, worktrees, `systematic-debugging`). When it finishes, run spec-monkey `auditing-specs` against the same contract: because the plan tagged its tasks with `FR`/`SC` ids, the audit traces each requirement to real code and re-runs the contract's verification, independent of how the plan built it. Contract in, plan out, audit closes the loop.

## If you don't run superpowers

spec-monkey's middle is deliberately lean but not empty. `implementing-specs` builds slice by slice, test-first, on an isolated branch or worktree, keeping a slice ledger so a killed session recovers which slice is done; the design's *Approach* carries the high-level shape across the gap (`references/build-workspace.md`). `references/build-discipline.md` carries the faked-done anti-patterns and a self-review rubric; `references/debugging.md` is the root-cause escape hatch for a slice that won't go green. On a subagent-capable harness, `references/subagent-mode.md` runs an orchestrated build with a per-group review gate. That is enough to build a spec-monkey spec end to end without another framework. superpowers deepens the middle — mature TDD, `systematic-debugging`, richer worktree flows — but it no longer gates it.

## Cost note

Running both is not free. You pay spec-monkey's interviews and audit *plus* superpowers' plan and execution. The payoff is a signed WHAT/WHEN contract, a HOW plan cheap models can execute, and an independent compliance audit — the front, middle, and back each held by the tool that's best at it. On a small change, that's overkill; use one system, or neither. See the README's "What it costs, and when to skip it."
