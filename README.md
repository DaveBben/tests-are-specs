# Spec Monkey

A pipeline that attempts to ground its design choices in empirical research, keeping humans in architectural decisions while AI handles investigation and implementation.

## Installation

Install as a Claude Code plugin:

```bash
# Add the marketplace
/plugin marketplace add DaveBben/claude-kiss

# Install the plugin
/plugin install spec-monkey@spec-monkey-marketplace
```

Or test locally:

```bash
claude --plugin-dir ./plugins/spec-monkey
```

All skills are namespaced under `spec-monkey:` (e.g., `/spec-monkey:create-spec`, `/spec-monkey:execute-spec`).

---

## Routing

```
Is this a new codebase or one you haven't onboarded yet (brownfield)?
  └── Yes → /spec-monkey:onboard  (creates CLAUDE.md + spec.md)

Can the change be understood by a single diff?
  └── Yes → Use vanilla Claude Code with plan mode. No skills needed.

Is it a bug?
  └── Yes → /spec-monkey:bug → produces bug spec → /spec-monkey:execute-spec

Want to think through a change before implementing?
  └── Yes → /spec-monkey:create-spec → then plan mode

Ready to implement (you already have a spec or clear prompt)?
  └── Yes → Plan mode directly, or /spec-monkey:execute-spec

Want a second set of eyes on what you're writing?
  └── Yes → ask Claude to run the spec-monkey-staff-reviewer agent (multi-pass review — never writes code)
```

---

## Skills

| Skill | What it does | Artifacts produced |
|---|---|---|
| `/spec-monkey:onboard` | Sets up context for a new or existing codebase | `CLAUDE.md`, `docs/specs/spec.md`, `docs/specs/subsystems/*/spec.md` |
| `/spec-monkey:create-spec` | Thinking partner + spec producer — challenges your approach, then writes the spec | `docs/specs/features/{slug}/spec.md` |
| `/spec-monkey:execute-spec` | Reads a spec, implements changes, verifies, then runs parallel staff + QA reviews | Branch, commits |
| `/spec-monkey:bug` | Investigates a bug symptom, traces root cause, produces a bug spec | `docs/specs/bugs/{slug}/spec.md` |

---

## Skill Details

### `/spec-monkey:onboard`

Run this first on any codebase — new or existing. The skill reads the repository, asks targeted questions about purpose, tech stack, conventions, and constraints, then produces:

- **`CLAUDE.md`** — quick-reference context that Claude Code loads on every conversation
- **`spec.md`** — living specification describing what the system does, key decisions, and known constraints

Once onboarded, `/spec-monkey:create-spec` and `/spec-monkey:bug` have rich context to work from, increasing the chances that AI agents implement changes without breaking existing data contracts.

### `/spec-monkey:create-spec`

Thinking partner + spec producer in one conversation. You describe a change, Claude reads the codebase (not just CLAUDE.md/spec.md — the actual source files), challenges your assumptions with specific grounded concerns, then produces a complete spec ready for plan mode.

**Phase 1 — Understand and Challenge:** Claude reads the relevant code and pushes back on your approach using techniques from cognitive science research: pre-mortem ("it shipped and broke — why?"), alternatives analysis, second-order thinking, and operational readiness. It's a conversation with a senior engineer, not an interview.

**Phase 2 — Produce the Spec:** Claude investigates for precise file:line references, symbols, verification commands. Runs the `spec-monkey-spec-reviewer` agent to check for seven evidence-backed failure modes before presenting the spec.

Produces **`docs/specs/features/{slug}/spec.md`** — a contract between the human (who decides what and why) and the AI agent (who implements how). Hand it to plan mode to implement.

### `/spec-monkey:execute-spec`

Reads a spec and implements it:

1. Pre-flight: branch safety, test baseline, validate spec file references, run linters
2. Implement changes following the spec's Approach, Constraints, Edge cases, and Do NOT
3. Before each commit: run linters, type checkers, and the relevant tests — never commit red
4. Run the spec's verification command — not done until it passes
5. Final review in parallel: `spec-monkey-staff-reviewer` (code) + `spec-monkey-qa-reviewer` (tests & edge cases) + `spec-monkey-compliance-reviewer` (spec contract), then full test suite

Does not push or create PRs. Uses subagents for parallel work when the spec involves independent concerns.

### `/spec-monkey:bug`

Bugs start from a symptom, not a change request. Claude reads the code, traces the root cause using dual-frame analysis (backward from symptom + forward from suspected cause), and produces a bug spec with intended/actual behavior, repro steps, root cause, and mitigation approach. Feeds into `/spec-monkey:execute-spec` the same way feature specs do.

---

## Agents

| Agent | Role | Used by |
|---|---|---|
| `spec-monkey-spec-reviewer` | Checks specs for 7 evidence-backed failure modes before presenting to user | `/spec-monkey:create-spec`, `/spec-monkey:bug` |
| `spec-monkey-staff-reviewer` | Multi-pass staff-level review of the full diff (security → correctness → performance → reliability) | `/spec-monkey:execute-spec` final review, or standalone on any diff |
| `spec-monkey-qa-reviewer` | Test quality, test coverage, and edge case handling of the full diff | `/spec-monkey:execute-spec` final review, or standalone |
| `spec-monkey-compliance-reviewer` | End-of-feature check that the implementation matches the spec's contract | `/spec-monkey:execute-spec` final review |

---

## Artifact Storage

Specs live under `docs/specs/`, bug tasks under `.claude/bugs/`:

```
{project-root}/
  docs/
    specs/
      spec.md                          ← project-level spec (produced by /spec-monkey:onboard)
      subsystems/
        {domain-slug}/
          spec.md                      ← subsystem spec (produced by /spec-monkey:onboard)
      features/
        {feature-slug}/
          spec.md                      ← feature/change spec (produced by /spec-monkey:create-spec)
      bugs/
        {bug-slug}/
          spec.md                      ← bug spec (produced by /spec-monkey:bug)
```

The project-level `docs/specs/spec.md` contains a **Spec Index** — a table of contents listing all subsystem and feature specs with descriptions. This is how agents discover related specs without loading every file into context.

Feature specs are persistent artifacts that collectively document how the codebase was built. Each contains: intent, current behavior, constraints, edge cases, approach, rejected alternatives, scope boundaries, file references with symbols, and verification commands.

---

## Design Principles

**Human decides, AI challenges, then AI implements.** `/spec-monkey:create-spec` reads the code and pushes back on assumptions. The human makes the final call. The spec captures the decision.

**The spec is the contract.** One artifact, under 300 words, with everything the implementing agent needs and nothing it doesn't. Every token must earn its place.

**Context density over context volume.** Wrong context is worse than no context. Specs are reviewed by the `spec-monkey-spec-reviewer` agent for seven evidence-backed failure modes before the human sees them.

**Regression prevention is the primary quality metric.** Targeted at-risk tests (human-confirmed, specific) reduce regressions 72%. Generic TDD instructions without targeted context increase them. The pipeline is designed around this finding.

**Skip the skills when you don't need them.** One- or two-line changes do not need a plan file. Use vanilla Claude Code with plan mode.

---

## The Evidence-Based Prompt

Independent of the TPE pipeline, research shows that a well-constructed prompt to a frontier model in plan mode can handle most coding tasks effectively. Based on findings from SWE-bench, METR, ORACLE-SWE, and other benchmarks (see [research.md](research.md) for full citations), here is an example prompt with every element justified by measured evidence.

### Example: Adding webhook retry logic

```
Add exponential backoff retry logic to the webhook delivery system.

**Last updated**: 2026-05-07

## What and why
The webhook dispatcher currently fires once and discards on failure.
Customers lose events when their endpoints have transient outages.
Add retry with exponential backoff so transient failures recover
without manual intervention.

## Current behavior
Webhook dispatch is fire-and-forget: dispatcher.ts:47 sendWebhook()
calls the endpoint, logs on failure, and moves to the next event.
No retry, no status tracking beyond "sent" or "failed".

## Constraints
- Max 5 retries per event, backoff: 1s, 2s, 4s, 8s, 16s
- After final failure, mark event as "dead_letter" (do not delete)
- Retries must not block the main dispatch loop (use the existing
  background job queue in src/jobs/)
- Must not retry on 4xx responses (client errors are permanent)

## Edge cases
- Endpoint returns 429 (rate limited): treat as retryable, not a 4xx client error
- Endpoint times out (>30s): treat as failure, retry
- Event payload exceeds 1MB: skip retry, mark dead_letter immediately
- Webhook URL is unreachable (DNS failure): retryable

## Approach
Use the existing background job queue (src/jobs/queue.ts) to schedule
retries asynchronously. On failure, enqueue a retry job with a
calculated delay rather than blocking the dispatch loop.

## Alternatives rejected
- Inline retry with sleep — rejected because it blocks the dispatch
  loop, delaying delivery to other webhooks
- Separate retry service/process — rejected as over-engineered for
  the current scale; the existing job queue is sufficient

## Do NOT
- Do not add a new database table; use the existing `webhook_events`
  table (add columns if needed via migration)
- Do not refactor the existing WebhookDispatcher class interface;
  callers should not need to change
- Do not add circuit breaker logic; that's a separate concern for later
- Do not modify the webhook registration or configuration endpoints

## Files that matter
- src/webhooks/dispatcher.ts:sendWebhook() — the dispatch method to modify
- src/webhooks/types.ts:WebhookEvent — type definition, needs retry fields
- src/jobs/queue.ts:enqueue() — the method to call for background retries
- src/db/migrations/ — where to add the migration
- tests/webhooks/dispatcher.test.ts — existing tests to keep passing

## Verification
- Run: npm test -- --grep "webhook"
- All existing webhook tests must continue to pass
- New test: dispatching to a consistently-failing endpoint should
  result in exactly 5 retry attempts with increasing delays
- New test: dispatching to an endpoint returning 400 should NOT retry
- After 5 failures, webhook_events row should have status="dead_letter"
  and retry_count=5

Keep going until all tests pass and the verification criteria are met.
If you hit a problem, investigate and fix it rather than stopping.
```

### Why each element is included

| Element | Evidence |
|---------|----------|
| **What and why** | CGO (ECOOP 2025): goal-oriented framing outperforms procedural step-by-step with fewer tokens |
| **Current behavior with location** | ORACLE-SWE: reproduction context is the #1 oracle signal (85.2%). Pinpointing the entry point eliminates 60-80% of agent search cost (Stanford 2026) |
| **Constraints** | Fault Localization Study (2026): precise specs produce 15-17x improvement over vague ones |
| **Edge cases** | "More Than a Score" (AACL-IJCNLP 2025): explicit edge-case handling is a key driver of improvement |
| **Approach** | CGO (ECOOP 2025): goal-oriented framing outperforms procedural. Captures the agreed strategy; prevents agent from choosing a different path |
| **Alternatives rejected** | Google design docs: "Alternatives Considered" unanimously described as the most valuable section. Prevents relitigating settled decisions |
| **Do NOT list** | Practitioner consensus: explicit negation measurably reduces scope creep |
| **Files + symbols** | Fault Localization Study: file + element-level context = 63.4% vs file-only = 54.5% — ~9pp from adding function names |
| **Verification with assertions** | ORACLE-SWE: gap between vague verification (39.4%) and specific reproduction tests (85.2%) is 46pp |
| **Persistence** | OpenAI GPT-4.1: three simple agentic instructions = ~20% improvement on SWE-bench |
| **Plain, short (~250 words)** | Context length degrades performance even with perfect retrieval (EMNLP 2025). Prompt engineering saturates after ~5 hours of work (Softcery 2026) |

### What is deliberately excluded

| Omitted | Why |
|---------|-----|
| "You are an expert" | Negligible on frontier models (literature consensus) |
| Step-by-step instructions | METR (2026): elaborate scaffolding did not beat generic ReAct. Frontier models do CoT internally |
| Impact analysis section | Model handles this internally (Augment Code finding). "Do NOT" list + file list serve the same function with fewer tokens |
| Design option exploration | CGO: direct objectives outperform exploratory prompts. Do design exploration in a separate prior conversation to avoid context degradation (SlopCodeBench) |
| TDD instructions | Net-negative for agentic flows (METR; practitioner consensus) |
| Few-shot examples | No published ablation for agentic coding. High context cost, unmeasured benefit |

Full research with all citations: [research.md](research.md)

---

## Research Foundations

Design choices map to empirical findings on how coding agents fail and how humans lose skill when AI removes friction. 

### Agent effectiveness

| Principle | Key finding | Pipeline response |
|-----------|------------|-------------------|
| **Context precision over volume** | Wrong context is worse than none ([2602.08316](https://arxiv.org/abs/2602.08316)). Context types interfere ([2503.20589](https://arxiv.org/abs/2503.20589)). Structured context degrades review across all models tested ([2603.26130](https://arxiv.org/abs/2603.26130)). | Artifacts capped (brainstorm 200 lines, plan 200, task JSONs per-task only). Every field must earn its place. |
| **Task decomposition** | Highest-ceiling intervention: +10–40pp ([2510.07772](https://arxiv.org/abs/2510.07772), [2311.05772](https://arxiv.org/abs/2311.05772)). Agents collapse from 74% to 11% on feature-level tasks ([2602.10975](https://arxiv.org/abs/2602.10975)). | `/spec-monkey:create-spec` and plan mode decompose into vertical slices, hard max 4 files per task. |
| **Targeted test context** | Test dependency info reduced regressions 72%; generic TDD instructions *increased* them 42% ([2603.17973](https://arxiv.org/abs/2603.17973)). | Human-confirmed at-risk tests, multi-agent triangulated. Never instructs "write tests first." |
| **Single agent** | Matches or beats multi-agent at fraction of cost ([2604.02460](https://arxiv.org/abs/2604.02460), [2505.18286](https://arxiv.org/abs/2505.18286)). Weaker model + strong scaffolding wins ([2512.10398](https://arxiv.org/abs/2512.10398)). | One agent per task. Haiku/Sonnet implements, Opus orchestrates. |
| **Instruction brevity** | Shorter instructions quadrupled resolution ([2603.17973](https://arxiv.org/abs/2603.17973)). Context length alone degrades performance even with perfect retrieval ([2510.05381](https://arxiv.org/abs/2510.05381)). | Task JSONs carry intent, not procedures. |
| **Agent overconfidence** | Agents predict 77% success at 22% actual ([2602.06948](https://arxiv.org/abs/2602.06948)). | Trust-but-verify: orchestrator runs `regressionCheck`, never trusts agent self-report. |
| **Instruction fade-out** | System instructions lose influence as context fills ([2603.05344](https://arxiv.org/abs/2603.05344)). | Re-surfaces constraints before each verification; pauses every 6 tasks. |
| **Quality erosion** | Code quality eroded in 80% of trajectories ([2603.24755](https://arxiv.org/abs/2603.24755)). Security vulnerabilities increased 37.6% after 5 iterations ([2506.11022](https://arxiv.org/abs/2506.11022)). | Per-task commits, handoff checks, size/drift warnings, human pause gates. |

### Human cognition

| Principle | Key finding | Pipeline response |
|-----------|------------|-------------------|
| **Predict-before-reveal** | Predicting before seeing results improves learning and defends against anchoring ([2410.08922](https://arxiv.org/abs/2410.08922), [SSRN:6097646](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6097646)). | `/spec-monkey:create-spec` asks human to predict at-risk tests and propose approach before revealing findings. |
| **Human decides, AI investigates** | Formulating hypotheses produces deeper learning than following suggestions ([2505.08063](https://arxiv.org/abs/2505.08063)). | AI never recommends. Human chooses approach, confirms boundaries, signs off scope. |
| **Batch reveals** | Most AI interactions stay in a single metacognitive phase, skipping planning and evaluation ([2511.04144](https://arxiv.org/abs/2511.04144)). | Three sequential batches (impact → tests → approach), each gated on human response. |
| **Inquiry over delegation** | Conceptual inquiry builds skill; code delegation erodes it ([2601.20245](https://arxiv.org/abs/2601.20245), [2506.08872](https://arxiv.org/abs/2506.08872)). | `/spec-monkey:create-spec` = inquiry mode (human). `/spec-monkey:execute-spec` = delegation (agent). |

### Cross-cutting

- **Verified context only.** Multi-agent convergence for at-risk tests, grep-verified dependency chains, orchestrator-run regression checks. No stage trusts its inputs blindly ([2602.08316](https://arxiv.org/abs/2602.08316)).
- **Progressive compression.** brainstorm (~200 lines) → plan (~200 lines) → task JSONs (~50–80 lines). Semantic density over token count ([2604.07502](https://arxiv.org/abs/2604.07502)).
- **Human gates at decision points, automation at verification points.** Human chooses approach, approves plan, handles push/PR. Regression checks, reference verification, and handoff validation are mechanical.
