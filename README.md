# spec-monkey

A set of portable skills for spec-driven development.

A spec is a **design contract**. It describes what to build, why it's needed, what constrains the solution, 
and how you know it works. It's so a reviewer can approve the plan before any code exists. 

---

### Installing

**Claude Code (plugin):**

```bash
/plugin marketplace add DaveBben/spec-monkey
/plugin install spec-monkey@spec-monkey
```

Skills are namespaced under `spec-monkey:`, so you get `/spec-monkey:running-lifecycle`,
`/spec-monkey:grounding-specs`, `/spec-monkey:shaping-specs`, `/spec-monkey:writing-specs`,
`/spec-monkey:reviewing-specs`, `/spec-monkey:implementing-specs`, and `/spec-monkey:auditing-specs`.

**Any agent (Skills CLI):**

```bash
npx skills add DaveBben/spec-monkey
```

Installs all seven skills into whatever skills-compatible agent you have — Claude Code, Cursor,
Codex, opencode, and others. Target one explicitly with `-a`, e.g. `npx skills add DaveBben/spec-monkey -a claude-code`.

**Test locally:**

```bash
claude --plugin-dir ./plugins/spec-monkey
```

### The seven skills

| Skill | What it does | Produces |
|---|---|---|
| `running-lifecycle` | Drives the full flow end to end: grounds the project, then for each work item shapes, writes, reviews, implements, and audits its spec, pausing at every human approval gate. Invokes the six phase skills in order; never crosses a gate on its own. Portable; auto-start is an optional Claude Code hook. | Nothing of its own — it runs the other six |
| `grounding-specs` | An interactive interview that establishes the **project spec**: the one architecture document every work-item spec grounds on. Captures the shared data contracts, system-wide invariants, trust boundaries, and hard architectural constraints, plus the planned work items and their order. A living, versioned document; gates on the human approving it. | `docs/specs/project/spec.md` (`kind: project`) |
| `shaping-specs` | The thinking phase: an interactive interview that works a change through before its spec is written. Covers the ask, orientation, the five risk lenses, and a comparison of 2-3 approaches with a recommendation. Writes the reasoning the spec rests on. Divergent by design; a strong default, not a hard gate. | `docs/specs/{slug}/` — `detail/evidence.md` plus the brief's *Drivers* and *Decisions to sign off* (`status: draft`) |
| `writing-specs` | Composes the formal work-item spec from the shaped reasoning: turns the evidence and decisions into the binding FR/SC contract, the data and interface contract, the timing, and the verification commands, grounded on the project spec. Reads the shaped evidence rather than re-interviewing. Gates on the human setting the spec's status to `approved`. | `docs/specs/{slug}/` — `spec.md` plus `detail/contract.md` (the default; a user-named path wins) |
| `reviewing-specs` | A skeptical, report-only critique of a drafted spec: soundness, grounding against the real code, edge-case coverage, traceability, weak success criteria, and any HOW that leaked past design altitude. Returns findings + an APPROVE / REVISE verdict. | A review report (never edits the spec) |
| `implementing-specs` | Takes an approved spec and builds it: works out the HOW from the spec and the real code, then verifies against the spec's own success criteria and commands. Stops before pushing or opening a PR. | Working code + a commit that points back to the spec |
| `auditing-specs` | Audits a finished implementation against the approved spec: traces every requirement to code, runs the spec's own verification, and confirms the success criteria, data contracts, constraints, and scope boundaries actually hold. Report-only. | A COMPLIANT / NON_COMPLIANT report with evidence |

The flow is ground → shape → write → review → implement → audit. Each skill ends by naming and offering the
next, while the human still holds the approval gates; nothing auto-executes. `running-lifecycle` drives
the whole flow in one guided pass, or you run each skill by hand: `grounding-specs` once at a project's
start, then `shaping-specs` and `writing-specs` per work item, each grounded on the project spec.

#### `running-lifecycle`

Invoke it and it drives the whole flow so you don't have to remember each hop. It checks for an approved
project spec (running `grounding-specs` if there is none), then walks each work item through
`shaping-specs` → `writing-specs` → `reviewing-specs` → the human's approval → `implementing-specs` → `auditing-specs`,
routing any audit deviations back to the right skill before moving on. It orchestrates; each phase's own
skill does the work, and it never crosses a human approval gate. The skill is portable; auto-starting it
from the first message is an optional Claude Code hook (see [`hooks/`](hooks/)), off by default.

#### `grounding-specs`

You establish the **project spec** before any work-item spec exists. The skill interviews you for the
shared ground every work item stands on — the canonical data contracts, the system-wide invariants
(`INV-NNN`), the trust boundaries, and the hard architectural constraints — then composes them into one
living document at `docs/specs/project/spec.md`. It holds no work-item requirements; those stay in each
work-item spec, which sets `parent` to the project spec and cites its invariants rather than restating
them. On an existing codebase it reads the invariants that already hold out of the code, then ratifies
them with you. A shared change after approval is an amendment: it bumps the doc's `version` and re-approves.

#### `shaping-specs`

You describe a change; the skill interviews you to think it through before any binding requirement is
written. It works the ask, orients in the code, runs the five risk lenses, and weighs 2-3 approaches with
their tradeoffs and a recommendation. The output is the reasoning: `detail/evidence.md` plus the brief's
*Drivers* and *Decisions to sign off*. It is a strong default, not a hard gate; a trivial slice can go
straight to writing.

- **Orient.** Read the repo constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`) and
  scan the touched area just enough to ask sharp questions.
- **Interrogate.** Drive ambiguity to near-zero, highest-uncertainty questions first,
  reflecting interpretations back.
- **Worry.** Work five risk lenses (failure & scale, operational readiness, trust boundary,
  implied work, better way); each surfaced risk gets HANDLE / ACCEPT / OUT-OF-SCOPE.
- **Weigh approaches.** Name 2-3 real alternatives, lay out their tradeoffs, and recommend one
  with a reason; the choice lands in *Decisions to sign off*.

#### `writing-specs`

You hand it the shaped reasoning; the skill composes the contract onto it. It writes `spec.md` (the
reviewer approves from it alone) and `detail/contract.md` (the implementer and auditor consume it),
resting on the `detail/evidence.md` that `shaping-specs` already wrote. It reads the shaped evidence
rather than re-interviewing, keeps each spec to one thin slice, and grounds it on the project spec,
citing the invariants there.

- **Requirements.** Turn each observable behavior into an FR with a success criterion beside it,
  grouped by subsystem or seam.
- **Sequence.** A first-class *When it happens* section covers triggers, ordering, rollout
  conditions, and reversibility.

#### `reviewing-specs`

Point it at a `spec.md`. It reads the spec and the codebase and works its rubric — a decomposition
gate, a six-item self-consistency sweep, and eight review dimensions — and flags any unanswered
template question. It returns BLOCKING / SHOULD_FIX / SUGGESTIONS findings with a verdict.

#### `implementing-specs`

Point it at an approved `spec.md`. It reads the requirements, the contracts, and
the success criteria, and builds until every requirement holds. On a subagent-capable harness, and a spec
with three or more FR-groups, it can run an optional orchestrated build (a fresh implementer per group, a
review gate, a fix loop, a compaction-proof progress ledger); the single-agent path is the portable default.

#### `auditing-specs`

Point it at an implemented `spec.md`. It traces every requirement to code, runs the spec's own
verification, and reports COMPLIANT or NON_COMPLIANT with `file:line` evidence, tagging each deviation
fix-code, amend-spec, or amend-project-spec. Report-only by default; on request it can run an opt-in
fix-and-re-audit loop that applies only `fix-code` fixes and leaves contract changes for a human.

### The spec

A spec is three documents, one per reader. `spec.md` carries the decision brief: the reviewer
approves or rejects from that page alone. `detail/contract.md` carries the binding sections
(requirements, contracts, verification commands, the worked case): the implementer and auditor load
it whole, with no review-time material diluting their context. `detail/evidence.md` carries the
reasoning behind the design (current-state facts, failure-mode lenses, impact): a deep reviewer
opens it on doubt, and after approval it is rarely read again.

The full work-item template is the canonical format reference:
[`plugins/spec-monkey/skills/writing-specs/references/spec-template.md`](plugins/spec-monkey/skills/writing-specs/references/spec-template.md).

Above the work items sits **one project spec** (`docs/specs/project/spec.md`, `kind: project`): a single
living document holding the shared data contracts, invariants, trust boundaries, and constraints every work
item grounds on. Its format lives in
[`plugins/spec-monkey/skills/grounding-specs/references/project-template.md`](plugins/spec-monkey/skills/grounding-specs/references/project-template.md).

### Design principles

- **Discovery lives in the questions.** The interview and risk analysis live in
  `interview-questions.md`; the template only composes the answers.
- **Single source of truth.** Each decision lives in one place and is referenced by ID elsewhere. A shared
  fact lives in the project spec; work items cite its `INV-NNN`, never restate it.
- **Ground before you slice.** The project spec establishes the shared architecture once; each work-item
  spec stays thin and stands on it.
- **Handoffs, not auto-run.** Each skill names and offers the next; the human holds the approval gates.
  Portable, and no hook required.
- **Harness-specific glue lives outside the skills.** The skills are plain, portable Markdown. Anything
  that needs a hook or a subagent — the optional Claude Code auto-start, the opt-in orchestrated build,
  the fix-and-re-audit loop — is optional and sits outside `skills/` or behind a capability check.
- **Skip the skills when you don't need them.** A one- or two-line change doesn't need a spec, and a
  throwaway with no shared architecture doesn't need a project spec.

