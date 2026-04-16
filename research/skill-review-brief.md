# Skill Review Brief: think / plan / act

## PURPOSE
Review three Claude Code skills (think, plan, act/execute) for gaps against:
1. Empirical research on AI coding agent performance
2. Internal design goals of the think→plan→act pipeline
3. Data contract consistency across the three skills

Do NOT rewrite the skills. Return a structured gap report only.

---

## DESIGN GOALS (what this pipeline is trying to achieve)

- Human makes architectural decisions BEFORE AI plans or implements
- AI investigates and surfaces consequences; human chooses approach
- brainstorm.md (think output) → plan.md + task JSONs (plan output) → executed code (act output)
- Each skill hands off a verified artifact to the next; no skill re-does prior skill's work
- Regression prevention is the primary quality metric, not resolution rate alone
- Context density over context volume: every token in a task JSON must earn its place

---

## KEY RESEARCH FINDINGS (evaluate skills against these)

### Context
- Wrong context is WORSE than no context: incorrect retrieval drops resolution 4pts BELOW no-context baseline (SWE Context Bench)
- Context types interfere: best pair scored 36.5%, adding third type dropped to 19.6% — worse than no retrieval (2503.20589)
- Frontier models degrade on coding tasks above ~32K tokens; sweet spot is 6-10 relevant files (LongCodeBench, fault localization paper)
- Verbose instructions actively harm: reducing 107→20 lines quadrupled resolution 12%→50% (TDAD paper)
- Human-authored context helps; LLM-generated context hurts (-0.5 to -3% resolution, +20% cost)

### Regression prevention
- Targeted at-risk test context reduced regressions 72% (6.08%→1.82%) — highest single intervention
- Generic TDD instructions WITHOUT targeted context INCREASED regressions 42%
- Agents predict 77% success when achieving 22% — do not trust self-assessment
- >75% of maintenance attempts introduce regressions with current models (except Claude Opus)

### Anchoring / human review
- Exposure to poor AI suggestions reduces human engagement and increases acceptance of wrong answers (n=2784 RCT)
- When reviewer reasons from the same spec as the generator, correlated errors amplify rather than cancel
- Predict-before-reveal: asking human for their approach before presenting AI synthesis prevents anchoring

### Task scope
- Resolution drops 63 percentage points from single-file bugs to multi-file features (74%→11%)
- NameError is the dominant failure mode on multi-file tasks — agents edit locally without re-establishing cross-file references
- Task decomposition: +10 to +40 percentage point improvement (highest ceiling intervention)
- Vertical slices outperform horizontal layers: mixed class+function modifications worst at 8-15% vs 25-40% for single-class

### Reference patterns
- Surface patterns (naming, API, formatting) transfer well from reference implementations
- Architectural reasoning does NOT transfer — agents copy form, not reasoning
- Anti-pattern amplification: agents amplify anti-patterns from reference code over iterations (80% erosion rate)
- One reference is sufficient; multiple references risk interference

### Multi-turn / iteration
- Code erodes in 80% of trajectories without human checkpoints
- Security vulnerabilities increase 37.6% after 5 iterations of self-refinement
- Observation masking after completed tasks prevents stale context crowding

---

## DATA CONTRACTS (verify these are consistent across skills)

### brainstorm.md (think → plan)
Required fields plan must be able to read:
- Status: must be "Approved" before plan proceeds
- What and Why
- Scope: In / Out / Constraints
- Impact Surface: table of files + concern groups
- Dependency Chain: entry point → target (3-5 hops)
- At-Risk Tests: table with path, symbol, reason — all human-confirmed, none [unverified]
- Chosen Approach: name + why chosen + rejected alternatives
- Do NOT: explicit boundaries
- Failure Modes Decided: human decisions on irreversible/silent-break scenarios
- Open Questions: [TBD] items (plan blocks if >3)

### task_{N}.json (plan → act)
Current schema fields (post-refactor):
```
id, slice, repository, title, status, implementer
intent           — why (not what), one sentence
files            — 1-4 paths, hard max 4
symbol           — specific function/type
reference        — SINGLE file:line (one entry only)
dependencyChain  — 3-5 hops, verified against codebase
relevantFiles    — [{path, action: create|modify}] mirrors files
blockedBy        — task IDs
atRiskTests      — [{path, symbol, reason}] human-confirmed from brainstorm.md
doNot            — at least one boundary
acceptanceCriteria — GIVEN/WHEN/THEN
verificationCommand — single runnable command
regressionCheck  — command for atRiskTests; empty iff atRiskTests empty
doneWhen         — mechanically verifiable; includes "regressionCheck passes" when atRiskTests non-empty
scopeBoundaries  — what this task owns vs adjacent tasks
```

REMOVED fields (do not reference these anywhere):
- testContext — merged into atRiskTests
- implementationContext — removed (context interference risk)
- evidence.md — replaced by brainstorm.md for complex tasks

### plan.json (plan → act)
```
date, status ("Approved"), featureSlug, featureDescription
whatWeAreBuilding, whyThisExists
scope: {in[], out[], constraints[]}
knownRisks[], criticalReminders[]
totalTasks, repositories[], totalSlices
slices: [{id, description, files[]}]
```

---

## SKILL: think
```
PHASES:
  Phase 1 — Intent: clarify what+why, ask 3 scope questions
  Phase 2 — Impact: 3 parallel Explore agents (blast radius / patterns / data shapes), synthesize in main session
  Phase 3 — Decisions: confirm boundaries, failure modes + reversibility questions
  Phase 4 — Write brainstorm.md

AGENTS:
  Agent 1 — Blast radius: entry point files, test files, import chain
  Agent 2 — Existing patterns: similar code, TODOs/FIXMEs, closest analogous change
  Agent 3 — Data shapes: type definitions, external callers, serialization boundaries

SYNTHESIS (main session, not delegated):
  - Concern groups from blast radius
  - 2-3 implementation approaches grounded in findings
  - Load-bearing types/interfaces from data shapes
  - 2-3 highest-consequence failure modes
  - Security flag if blast radius includes auth/validation/external endpoints

USER INTERACTION SEQUENCE:
  Batch 1: impact surface (grouped by concern) → wait for surprise check
  Batch 2: at-risk tests → REQUIRES human confirmation before writing to brainstorm.md
  Batch 3: ask human approach first → then present AI approaches → human decides (no AI recommendation)

BRAINSTORM.MD HARD RULES:
  - Under 200 lines
  - Only confirmed decisions (unresolved = [TBD])
  - Unconfirmed tests = [unverified]
  - Every file:line verified on disk
  - No implementation details (code goes in plan.md)
  - Status set to "Approved" only after user explicitly approves
```

---

## SKILL: plan
```
STEPS:
  1 — Load + validate brainstorm.md (hard stops: not Approved, [unverified] tests, >3 [TBD])
  2 — Deepen investigation (targeted reads only, each read must produce a plan.md citation)
  3 — Write plan.md (real code, omit empty sections, max 2 pattern references, 100-200 lines)
  4 — Verify via plan-verifier agent (apply all @FIX before proceeding)
  5 — Decompose to task JSONs (re-anchor first, vertical slices, validate each JSON)
  6 — Single review pass (one revision; second revision triggers "return to think" warning)

KEY CONSTRAINTS:
  - No user interaction except review pass (think already made decisions)
  - Spec freshness check before investigation (warn if >30 days old)
  - plan-verifier note: ignore missing testContext/implementationContext output (fields removed)
  - reference field: SINGLE entry only
  - atRiskTests populated from brainstorm.md confirmed list — not re-derived
```

---

## SKILL: act (execute)
```
FLOW:
  Input resolution → pre-flight → [fast path ≤3 tasks] → task loop → post-implementation → finalize

PRE-FLIGHT:
  Branch safety, validate task JSONs (relevantFiles paths), test baseline, spec freshness, gate check

TASK LOOP:
  Complexity tier → pre-task check → dispatch code-implementor → trust-but-verify regressionCheck → size check → drift check → status update → observation masking

COMPLEXITY TIERS:
  Simple:  1 file, clear reference, no interface changes → haiku, maxTurns:20
  Standard: 2-3 files or interface changes → sonnet, maxTurns:50
  Complex: 4 files or shared interfaces → sonnet, maxTurns:75, also pass brainstorm.md path

CONTEXT MANAGEMENT:
  Observation masking: after each task retain only 1-line summary; keep last 2 full
  Context pause gate: every 6 tasks, pause and report progress
  Spec freshness: warn if spec.md >30 days AND plan >7 days old

POST-IMPLEMENTATION:
  Full test suite + lint, update spec.md if capabilities changed

PER-TASK COMMIT: after trust-but-verify passes, commit with message "task_{N}: {title}" for rollback granularity
HANDOFF CHECK: if next task has blockedBy on this task, dispatch task-handoff-checker subagent (haiku)
  - checks export/import consistency between completed and dependent task
  - runs dependent task's atRiskTests before dependent task starts
  - returns single line: PASS or BLOCKED — [reason]
  - skipped entirely when no task depends on the completed one

DOES NOT: push, create PR
```

---

## CODE-IMPLEMENTOR AGENT (dispatched by act)
```
INPUT: task JSON path, plan JSON path, plan constraints verbatim, known-failures baseline
       brainstorm.md path (complex tasks only — read Chosen Approach + Constraints sections)

BEFORE WRITING:
  1. Read task JSON (acceptanceCriteria, files, doNot)
  2. Read targeted extracts only (grep for symbol, read surrounding function — NOT full files)
  3. Read atRiskTests entries: import block + test symbol to understand what must not break
  4. Read single reference entry (grep for symbol, surrounding function only)
  5. Verify dependencyChain import boundaries
  6. Dynamic discovery: one level deep from relevantFiles imports; check for post-task API changes

SELF-REVIEW (required): correctness, logic errors, security (OWASP top 10), over-abstraction, false DRY, framework bypass

HARD STOPS: ambiguous requirements, task contradicts codebase, file missing, scope >200 lines, reference/dependencyChain mismatch

VERIFICATION: atRiskTests first → full verificationCommand → all criteria met → no regressions vs baseline

DOES NOT: modify test files, commit, plan, make product decisions
```

---

## SKILL: bug
```
WHY A SEPARATE SKILL (not just /think):
  - Bugs start from a SYMPTOM, not a change request. Think's Phase 1 asks
    "what is the concrete change?" — for bugs the answer is unknown.
  - Reproduction (writing a failing test) is the highest-value bug-specific
    step with no feature equivalent. Features use existing atRiskTests;
    bugs CREATE the test that proves the problem exists.
  - Research supports the distinction: SWE-bench Verified (bug fixes) has
    74% resolution vs FeatureBench (features) at 11%. Bugs are naturally
    scoped — forcing them through think→plan→act adds overhead without
    value for the high-resolution-rate case.

PHASES:
  Phase 1 — Capture: symptom (not diagnosis), repro steps, severity
  Phase 2 — Investigate: 2 parallel Explore agents (code path + blast radius),
             then reproduce programmatically (write draft failing test)
  Phase 3 — Confirm: present root cause hypothesis, at-risk tests, boundaries
             for human confirmation
  Phase 4 — Task JSONs: produce tasks directly (no plan.md intermediate)

AGENTS:
  Agent 1 — Code path: trace repro steps through code, find existing tests,
            check git log for recent changes
  Agent 2 — Blast radius: other callers of affected function, shared state,
            working patterns elsewhere in codebase

REPRODUCTION:
  - Draft reproduction test saved to .claude/bugs/{slug}/repro-test.[ext]
  - NOT committed — used as starting point for task_0's acceptance criteria
  - Result recorded as RED (confirmed), GREEN (did not reproduce), or ERROR

TASK STRUCTURE (2-4 tasks, natural bug fix order):
  task_0: reproduction test (write test that fails on bug)
  task_1: fix (blockedBy task_0, doneWhen repro test goes GREEN + regressionCheck passes)
  task_2: edge case tests (optional, only if investigation found related scenarios)

SAME TASK JSON SCHEMA AS FEATURES:
  id, slice, repository, title, status, implementer
  intent, files, symbol, reference, dependencyChain, relevantFiles,
  blockedBy, atRiskTests, doNot, acceptanceCriteria,
  verificationCommand, regressionCheck, doneWhen, scopeBoundaries

  No testContext, no implementationContext (removed fields).
  /act does not need to know whether it's executing a bug or feature.

WHAT WAS REMOVED FROM THE OLD BUG SKILL AND WHY:
  - research.md (LLM-generated context file — research shows these hurt -0.5 to -3% resolution)
  - impact-map.md (redundant with task JSON's files + atRiskTests)
  - plan.md (overhead for 2-4 task bugs; task JSONs go straight to /act)
  - annotation cycle (anchoring risk; one confirmation pass in Phase 3 instead)
  - human-plan-synthesizer agent (unnecessary overhead)
  - symptom-capture.md (227 lines → inlined as 30 lines; verbose instructions harm performance)
  - 10 exploration questions (reduced to 6 targeted agent questions across 2 agents)

FEEDS INTO: /act (same as features, same task JSON contract)
DOES NOT: commit, push, create PR, produce plan.md
```

---

## REVIEW QUESTIONS — answer for each skill and the pipeline as a whole

1. DATA CONTRACT GAPS: Are there fields that think produces but plan does not read? Fields plan produces that act does not validate? Fields act passes to code-implementor that no longer exist?

2. RESEARCH VIOLATIONS: Does any step instruct the AI to do something the research shows actively harms performance? (Examples: accumulate context beyond the 6-10 file sweet spot, provide context that isn't verifiable, give procedural instructions that consume tokens without informing decisions)

3. MISSING HIGH-VALUE INTERVENTIONS: The research identifies these as highest-impact. Is each present?
   - Targeted at-risk test context (human-confirmed, specific) ✓ in think/plan
   - Dependency chain per task ✓ in plan
   - Single reference implementation per task ✓ in plan
   - Observation masking ✓ in act
   - Instruction brevity / no verbose procedural prompts — CHECK each skill
   - Vertical decomposition ✓ in plan
   - Trust-but-verify regression check ✓ in act

4. ANCHORING RISKS: Does any step present AI proposals before asking for human input? Does any step give the human context that was generated by the same AI that will later be reviewed?

5. WRONG-CONTEXT RISKS: Are there places where AI-generated, unverified, or potentially stale content could flow into a downstream task JSON without human validation?

6. RESUMPTION: If a user interrupts mid-think, mid-plan, or mid-act and resumes later, what state is lost and what is preserved? Is the resumption path clearly defined?

7. INSTRUCTION BLOAT: Are there sections that instruct the AI how to do something it already knows (language conventions, standard code quality), consuming tokens without informing decisions specific to this pipeline?

8. PIPELINE BREAKS: What happens if the user runs plan without think, or act without plan? Are the guard conditions sufficient and the error messages actionable?

9. BUG VS FEATURE BOUNDARY: Is the boundary between /bug and /think clear? Could a user reasonably be confused about which to use? Are there cases where a "bug" is actually a multi-file change that should go through think→plan→act instead?

10. BUG DATA CONTRACT: Does /bug produce task JSONs that /act can consume without modification? Are there any bug-specific fields in plan.json that /act doesn't read or validate? Does the reproduction test draft flow correctly into task_0's acceptance criteria?
