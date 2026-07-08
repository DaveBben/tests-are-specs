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

Skills are namespaced under `spec-monkey:`, so you get `/spec-monkey:creating-specs`,
`/spec-monkey:reviewing-specs`, `/spec-monkey:implementing-specs`, and `/spec-monkey:auditing-specs`.

**Any agent (Skills CLI):**

```bash
npx skills add DaveBben/spec-monkey
```

Installs all four skills into whatever skills-compatible agent you have — Claude Code, Cursor,
Codex, opencode, and others. Target one explicitly with `-a`, e.g. `npx skills add DaveBben/spec-monkey -a claude-code`.

**Test locally:**

```bash
claude --plugin-dir ./plugins/spec-monkey
```

### The four skills

| Skill | What it does | Produces |
|---|---|---|
| `creating-specs` | An interactive plain-text interview that turns a rough request into an approved spec. The template's questions ARE the discovery: orientation, clarifying interrogation, and five risk lenses. Gates on the human typing `approve`. | `docs/specs/{slug}/spec.md` (the default; a user-named path wins) |
| `reviewing-specs` | A skeptical, report-only critique of a drafted spec: soundness, grounding against the real code, edge-case coverage, traceability, weak success criteria, and any HOW that leaked past design altitude. Returns findings + an APPROVE / REVISE verdict. | A review report (never edits the spec) |
| `implementing-specs` | Takes an approved spec and builds it: works out the HOW from the spec and the real code, then verifies against the spec's own success criteria and commands. Stops before pushing or opening a PR. | Working code + a commit that points back to the spec |
| `auditing-specs` | Audits a finished implementation against the approved spec: traces every requirement to code, runs the spec's own verification, and confirms the success criteria, data contracts, constraints, and scope boundaries actually hold. Report-only. | A COMPLIANT / NON_COMPLIANT report with evidence |

The natural flow is create → review → implement → audit, but nothing forces it.

#### `creating-specs`

You describe a change; the skill interviews you through a question-driven template, writing
a single `spec.md` directly. Discovery lives in the questions.

- **Orient.** Read the repo constitution (`standards.md` / `CLAUDE.md` / `AGENTS.md`) and
  scan the touched area just enough to ask sharp questions.
- **Interrogate.** Drive ambiguity to near-zero, highest-uncertainty questions first,
  reflecting interpretations back.
- **Worry.** Work five risk lenses (failure & scale, operational readiness, trust boundary,
  implied work, better way); each surfaced risk gets HANDLE / ACCEPT / OUT-OF-SCOPE.
- **Sequence.** A first-class *When it happens* section covers triggers, ordering, rollout
  conditions, and reversibility.

#### `reviewing-specs`

Point it at a `spec.md`. It reads the spec and the codebase and works a nine-part
rubric, and flags any unanswered template question. It returns BLOCKING / SHOULD_FIX / SUGGESTIONS 
findings with a verdict.

#### `implementing-specs`

Point it at an approved `spec.md`. It reads the requirements, the contracts, and
the success criteria, and builds until every requirement holds.

#### `auditing-specs`

Point it at an implemented `spec.md`. It traces every requirement to code, runs the spec's own
verification, and reports COMPLIANT or NON_COMPLIANT with `file:line` evidence, tagging each
deviation fix-code or amend-spec.

### The spec

The full template is the canonical format reference:
[`plugins/spec-monkey/skills/creating-specs/references/spec-template.md`](plugins/spec-monkey/skills/creating-specs/references/spec-template.md).

### Design principles

- **Discovery lives in the questions.** The interview and risk analysis are template sections.
- **Single source of truth.** Each decision lives in one place and is referenced by ID elsewhere.
- **Skip the skills when you don't need them.** A one- or two-line change doesn't need a spec.

