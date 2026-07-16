# spec-monkey

A set of portable skills for spec-driven development.

A spec is a **design contract**. It describes what to build, why it's needed, what constrains the solution, 
and how you know it works. It's so a reviewer can approve the plan before any code exists. 

**When it earns its keep.** Reach for the full flow on work where a missed requirement is expensive:
complex or multi-seam features, shared architecture several work items stand on, changes a team has to
agree on, or long agent runs that must survive a lost context. Skip it on the small stuff — a one-line fix
doesn't need a spec, and `running-lifecycle` triages a trivial item onto a fast lane rather than marching it
through the full flow. The ceremony scales to the risk; it isn't waterfall you pay on every change.

### What it costs, and when to skip it

The flow is not free, and pretending otherwise is how spec tools earn the "technical masturbation" charge.
Reach for it when a missed requirement is expensive; skip it when it isn't.

- **The interviews cost tokens up front.** Grounding, shaping, and writing each interview you, one question
  at a time. On a complex, multi-seam change that conversation surfaces requirements you'd have missed. On a
  solo throwaway it's overhead — take the trivial lane, or write no spec at all.
- **WHAT-only specs raise the implementer floor.** Because the spec never carries the HOW, the implementer
  re-derives it from the spec and the code each build. That keeps the spec from rotting when the code moves,
  but it means you can't hand the build to the cheapest model the way a plan with the code written in it can;
  mid-tier is the effective floor. The trade buys altitude-stable specs at a higher per-build model cost.
  The design's *Approach* carries the high-level shape into the build, so the implementer re-derives the
  detail, not the intent — but the spec itself still carries no HOW. (If you want a
  fully HOW-carrying plan for cheap execution, see [interop](docs/interop.md).)
- **The portable path costs context hops.** The review and the audit are worth more in a fresh context. On a
  harness without subagents that's a manual new session (a `/clear`, on harnesses that have it) for each — a few hops per feature. A
  subagent-capable harness and the optional hook fold those back in.
- **When it costs more than it saves:** a one- or two-line change; a spike where the design is discovered by
  building, not specified up front; a solo weekend project with no shared architecture. The mid-2026 SDD
  consensus agrees the full ceremony is overkill there.

---

### Installing

**Claude Code (plugin):**

```bash
/plugin marketplace add DaveBben/spec-monkey
/plugin install spec-monkey@spec-monkey
```

Skills are namespaced under `spec-monkey:`, so you get `/spec-monkey:running-lifecycle`,
`/spec-monkey:grounding-specs`, `/spec-monkey:shaping-specs`, `/spec-monkey:reviewing-design`,
`/spec-monkey:writing-specs`, `/spec-monkey:reviewing-specs`, `/spec-monkey:implementing-specs`, and
`/spec-monkey:auditing-specs`.

**Optional turnkey activation (Claude Code).** Out of the box you start the flow by invoking
`/spec-monkey:running-lifecycle`. If you'd rather have "let's build X" reach for it automatically —
the way an auto-triggering assistant does — run the shipped one-command installer for the optional
SessionStart hook:

```bash
hooks/install-hook.sh --user     # or drop --user for this project only
```

It merges one hook entry into your Claude Code settings idempotently (no hand-typed paths), and it is
reversible — delete the entry to undo. The hook stays **off by default and outside the plugin**, so the
skills themselves depend on nothing and remain portable to any harness. Details in [`hooks/`](hooks/).

**Any agent (Skills CLI):**

```bash
npx skills add DaveBben/spec-monkey
```

Installs all eight skills into whatever skills-compatible agent you have — Claude Code, Cursor,
Codex, opencode, and others. Target one explicitly with `-a`, e.g. `npx skills add DaveBben/spec-monkey -a claude-code`.

**Other harnesses (adapter layer).** The skills are the same everywhere; what varies per harness is a thin
adapter: a manifest that points at the skills (`.codex-plugin/`, `.cursor-plugin/` at the repo root), a
tool-mapping file that translates the skills' action words into that harness's real tools
([`docs/harness-tools/`](docs/harness-tools/)), and the optional session bootstrap in [`hooks/`](hooks/) —
one env-sniffing script that emits the right hook JSON for Claude Code, Cursor, or the SDK standard. The
Cursor adapter wires the bootstrap through its manifest; Codex needs none (skills surface natively). To add
a harness, see [`docs/porting-to-a-new-harness.md`](docs/porting-to-a-new-harness.md).

**Test locally:**

```bash
claude --plugin-dir ./plugins/spec-monkey
```

### The eight skills

| Skill | What it does | Produces |
|---|---|---|
| `running-lifecycle` | Drives the full flow end to end: grounds the project, then for each work item triages it into a lane, shapes, reviews the design, writes, reviews the spec, implements, and audits, pausing at every human gate. Invokes the seven phase skills in order; never crosses a gate on its own. Portable; auto-start is an optional session hook (see [`hooks/`](hooks/)). | Nothing of its own — it runs the other seven |
| `grounding-specs` | An interactive interview that establishes the **project spec**: the one architecture document every work-item spec grounds on. Captures the shared data contracts, system-wide invariants, trust boundaries, and hard architectural constraints, plus the planned work items and their order. A living, versioned document; gates on the human approving it. | `docs/specs/project/spec.md` (`kind: project`) |
| `shaping-specs` | The thinking phase: an interactive interview that works a fuzzy ask through before its spec is written. Explores the landscape, weighs 2-3 approaches with their costs, and converges on a design — the *Approach*, the failure modes, and a high-level verification strategy. Its sole output; a gated, reviewable document. | `docs/specs/{slug}/detail/design.md` (`kind: design`) — the converged design |
| `reviewing-design` | A skeptical, report-only critique of the **design** before a contract is written: soundness of the approach, grounding against the real code, risk-lens coverage, undefended decisions, and whether the verification strategy is credible. Also reviews a project spec. Returns APPROVE / REVISE. | A review report (never edits the design) |
| `writing-specs` | Composes the formal work-item spec from the approved design: turns it into the decision brief plus the binding FR/SC contract, the data and interface contract, the timing, and the verification commands, grounded on the project spec. Reads the design rather than re-interviewing. Gates on the human approving the spec. | `docs/specs/{slug}/` — `spec.md` plus `detail/contract.md` (the default; a user-named path wins) |
| `reviewing-specs` | A skeptical, report-only critique of the **contract**: the self-consistency sweep, traceability, weak or vacuous success criteria, whether the verification is trustworthy, and any HOW that leaked past altitude. Returns findings + an APPROVE / REVISE verdict. | A review report (never edits the spec) |
| `implementing-specs` | Takes an approved spec and builds it: works out the HOW from the spec and the real code, building one FR-group slice at a time, test-first, then verifies against the spec's own success criteria and commands. Stops before pushing or opening a PR. | Working code + a commit that points back to the spec |
| `auditing-specs` | Audits a finished implementation against the approved spec: traces every requirement to code, runs the spec's own verification, and confirms the success criteria, data contracts, constraints, and scope boundaries actually hold. Report-only. | A COMPLIANT / NON_COMPLIANT report with evidence |

The flow is ground → shape → review-design → write → review-spec → implement → audit. Each skill ends by naming and offering the
next, while the human still holds the approval gates; nothing auto-executes. `running-lifecycle` drives
the whole flow in one guided pass, or you run each skill by hand: `grounding-specs` once at a project's
start, then `shaping-specs` and `writing-specs` per work item, each grounded on the project spec.

#### `running-lifecycle`

Invoke it and it drives the whole flow so you don't have to remember each hop. It checks for an approved
project spec (running `grounding-specs` if there is none), then, for each work item, **triages it into a
lane first**: a one- or two-line change with nothing to sign never opens the flow at all (what the
section above calls "no spec"); a trivial slice with a contract still worth signing skips shaping (and, when
purely cosmetic, the audit) and goes straight to a light contract; a standard or complex item walks the full
`shaping-specs` → `reviewing-design` → the design gate → `writing-specs` → `reviewing-specs` → the spec gate → `implementing-specs` → `auditing-specs`,
routing any audit deviations back to the right skill before moving on. The approval gate is never skipped,
whatever the lane. It orchestrates; each phase's own skill does the work. The skill is portable;
auto-starting it from the first message is an optional session
hook (see [`hooks/`](hooks/)) — one env-sniffing script that serves Claude Code, Cursor, and
SDK-standard harnesses — off by default.

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
their tradeoffs and a recommendation. The output is the reasoning: `detail/design.md` plus the brief's
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
resting on the `detail/design.md` that `shaping-specs` already wrote. It reads the shaped design
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

Point it at an approved `spec.md`. It reads the requirements, the contracts, and the success criteria, and
builds one FR-group slice at a time — test-first, watching each success criterion's test fail before making
it pass — verifying each slice before the next rather than coding everything and testing at the end. It builds
on an isolated branch (a worktree where the setup supports one), never the live mainline, and hands the
finishing decision — PR, merge, or discard — back to the human. It keeps a slice ledger so a session
death is recoverable — which slice is done — while the design's *Approach* carries the high-level shape across
the gap, so a resume rebuilds intent from the design rather than `git log`, and the spec never carries HOW. It carries a faked-done anti-patterns catalog and a self-review
rubric that mirrors the audit's checks, and has a root-cause debugging escape hatch for a slice that won't go
green (reproduce first, one hypothesis at a time, and when the contract is the bug, route it to `amend-spec`
rather than reinterpret it). On a subagent-capable harness, and a spec with three or more
FR-groups, it can run an optional orchestrated build (a fresh implementer per group, a review gate, a fix
loop, a compaction-proof progress ledger), driven by three ready-to-use dispatch prompts it ships
(`implementer-prompt.md`, `reviewer-prompt.md`, `fixer-prompt.md`); the single-agent path is the portable default. For the deeper
implementation middle — mature TDD, `systematic-debugging`, worktrees — [`docs/interop.md`](docs/interop.md)
shows how to hand off to superpowers.

#### `auditing-specs`

Point it at an implemented `spec.md`. It traces every requirement to code, runs the spec's own
verification, and reports COMPLIANT or NON_COMPLIANT with `file:line` evidence, tagging each deviation
fix-code, amend-spec, or amend-project-spec. Report-only by default; on request it can run an opt-in
fix-and-re-audit loop that applies only `fix-code` fixes and leaves contract changes for a human.

### The spec

A spec is three documents, one per reader. `spec.md` carries the decision brief: the reviewer
approves or rejects from that page alone. `detail/contract.md` carries the binding sections
(requirements, contracts, verification commands, the worked case): the implementer and auditor load
it whole, with no review-time material diluting their context. `detail/design.md` carries the
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
  The human's explicit go-ahead is the gate — the agent may record `approved` for them, but never decides
  it, reads it into silence, or nudges them toward it. Portable, and no hook required.
- **Right-size the ceremony.** The full flow is for work that earns it. `running-lifecycle` triages each
  work item first and sends a trivial slice down a fast lane (skip shaping, a light contract, skip a
  cosmetic audit); the approval gate still stands. A one- or two-line change doesn't need a spec at all, and
  a throwaway with no shared architecture doesn't need a project spec.
- **Harness-specific glue lives outside the skills.** The skills are plain, portable Markdown that names
  actions, never tools. Anything that needs a hook or a subagent — the optional multi-harness auto-start
  (the env-sniffing bootstrap in [`hooks/`](hooks/)), the opt-in orchestrated build, the fix-and-re-audit
  loop — is optional and sits outside `skills/` or behind a capability check. The per-harness translation
  from action words to real tools lives in [`docs/harness-tools/`](docs/harness-tools/).

### Tooling

[`tools/spec-lint.py`](tools/spec-lint.py) rides the parse contract to settle the mechanical checks — unfilled
placeholders, `FR`↔`SC` pairing, ID uniqueness, dangling `INV-NNN` citations, `parent` resolution, status and
`profile` values, and a missing gate record (an `approved` spec with no `approved_by`) — that a script does
faster and cheaper than an LLM reviewer. Stdlib Python, no install, exits nonzero on error so it drops into
CI. `python3 tools/spec-lint.py --status docs/specs` adds a roll-up: every spec's kind, profile, status, and
gate in one table, so work-item state isn't scattered across frontmatter. It judges no engineering; that stays
with `reviewing-specs`. See [`tools/README.md`](tools/README.md).

**Ready-to-use dispatch prompts.** For a subagent-orchestrated build, `implementing-specs` ships three
fill-in-the-slots prompt files — `implementer-prompt.md`, `reviewer-prompt.md`, `fixer-prompt.md` (under
`plugins/spec-monkey/skills/implementing-specs/references/`). You paste and dispatch; you don't re-derive the
brief each time. They point at `contract.md` by path rather than pasting FR/SC text, and the reviewer runs a
three-verdict gate (spec compliance, code quality, cited invariants).

**Behavioral evidence.** The pressure scenarios in [`tests/`](tests/) ship with a reproducible runner
protocol ([`tests/harness.md`](tests/harness.md)) and genuine recorded runs ([`tests/RESULTS.md`](tests/RESULTS.md)) —
control-vs-skill, real observed output, never asserted or fabricated. The recorded runs show the gate holding
under four escalating "just approve it" nudges and the WHAT/WHEN altitude holding on a HOW-soaked brief, each
across a no-skill control.

**Three version numbers, on purpose.** The package version (`plugin.json` + `marketplace.json`), each skill's
own `version`, and a spec's `spec_monkey:` format version answer three different questions — which release,
which skill revision, which document schema — so they don't move in lockstep. A spec you write today reads
`spec_monkey: "1.4.0"` even at plugin 1.8.0 because it records the schema it was authored against, not the
plugin. The full rule is in [`AGENTS.md`](AGENTS.md) ("Version — three numbers, three questions").

### Composing with superpowers

spec-monkey owns the front half (ground, shape, review-design, write, review-spec) and the back half (audit); it composes with
[superpowers](https://github.com/obra/superpowers) for the implementation middle, since a spec-monkey
`contract.md` (WHAT/WHEN) can feed a superpowers plan (HOW) without either system breaking its rules. Who owns
what, and the one seam that matters, is in [`docs/interop.md`](docs/interop.md).

