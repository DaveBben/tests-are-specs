# Spec-Driven Development — Research Dump

Compiled 2026-06-19/20 from web + Reddit research, as the evidence base behind the v3
spec-format overhaul. This is the *why* behind `spec_overhaul_plan.md`. The distilled,
operational form is the **A–P rubric** in §1 — that is what the review agents scored against.

---

## 1. The A–P rubric (the operational distillation)

A model spec for an AI coding agent should embody all of these:

- **A. What/Why vs How separation** — requirements (user needs, acceptance criteria, success
  metrics, NO tech choices) separated from the plan (architecture, contracts). Why is
  outcome-oriented.
- **B. Executable, testable EARS criteria** — `WHEN <trigger> THE SYSTEM SHALL <response>`,
  precise enough to generate property-based tests. No untestable "shall".
- **C. Constitution / non-negotiable principles** — explicit project principles gate the
  work; the spec shows compliance.
- **D. Living-artifact / anti-drift** — the spec states how it stays in sync; no assertions
  that silently rot. "A stale spec is worse than no spec."
- **E. The six areas (Addy Osmani)** — Commands (full flags), Testing (framework/location/
  how-to-run/coverage), Project structure, Code style (shown via a real snippet), Git
  workflow, Boundaries (what to never touch).
- **F. Boundaries as three tiers** — ✅ always / ⚠️ ask-first / 🚫 never (not a flat list).
- **G. Concrete examples over description** — at least one real input→output / payload
  example. "One example beats three paragraphs."
- **H. Ambiguity handling** — explicit `[NEEDS CLARIFICATION]` markers, not silent guesses;
  inject domain-knowledge pitfalls an expert would know.
- **I. Self-verification** — instructions for the agent to re-check its output vs the spec.
- **J. Context hygiene** — exact files/symbols named so the agent needn't grep; hierarchical
  summary for long specs; only relevant context.
- **K. Types / data-model first** — types and contracts pinned precisely; procedural detail
  left loose (don't over-specify).
- **L. Alignment-before-speed** — evidence the human was interrogated about edge cases /
  failure modes / open questions before code.
- **M. Task decomposition** — PR-sized, single-concern, dependency-ordered; parallelizable
  steps marked; small enough to dodge the context "dumb zone".
- **N. Verification rigor** — error paths required; anti-tautological tests (don't derive the
  expected value from the constant under test); name the "seams" where a test could cheat.
- **O. Right-sizing / anti-ceremony** — spec weight matches the change; nothing padded.
- **P. Internal consistency** — no contradictions in identifiers/URLs/paths/values. A
  self-contradiction is "lethal" — the agent does exactly what's written and breaks things.

---

## 2. Sources & core findings

### GitHub Spec Kit — `Spec → Plan → Tasks → Implement`
- Inverts development: the spec is the source of truth, code is a regenerable output.
- A `constitution.md` holds non-negotiable principles (library-first, CLI-interface,
  test-first, simplicity, anti-abstraction, integration-first) that gate every phase.
- Spec = what/why (user stories, acceptance criteria, `[NEEDS CLARIFICATION]` markers, no
  tech). Plan = how (architecture, data model, contracts, research). Tasks = dependency-
  ordered list, `[P]` for parallel, tests-first ordering. Code last.
- Templates force completeness via checklists; `[NEEDS CLARIFICATION]` forces marking
  ambiguity rather than guessing.
- Criticism: verbose boilerplate; reads 20–40 files per run (token-hungry).

### AWS Kiro — `requirements.md → design.md → tasks.md`
- Signature: **EARS** acceptance criteria — `WHEN <trigger> THE SYSTEM SHALL <response>`.
- Extracts correctness properties and generates property-based tests from the spec.
- Requirements-first vs design-first variants; tasks run in dependency "waves".

### Addy Osmani — "How to write a good spec for AI agents" (2,500+ config-file study)
- The **six areas** (rubric E). Boundaries was the highest-value area; "never commit secrets"
  the single most valuable constraint found.
- **Boundaries as three tiers** (rubric F): ✅ always / ⚠️ ask-first / 🚫 never.
- **Concrete examples beat description** (rubric G): one snippet > three paragraphs.
- Context hygiene: name the exact files; hierarchical summary/extended-TOC for long specs;
  give each subagent only its slice.
- Self-verification: embed "re-check your output against the requirements" instructions.
- Spec is a living artifact, kept in git; update on discovery, then resync the agent.

### Red Hat — "How spec-driven development improves AI coding quality"
- Vibe coding = fast but brittle. SDD targets "95%+ first-pass accuracy."
- Layered specs: functional ("what") → language-agnostic ("how") → language-specific.
- LLM-as-judge for subjective quality; log a `LessonsLearned.md` and feed it back.
- Hybrid drift control: regenerate from spec vs hand-edit — propose interactively, approve,
  log, keep traceability.

---

## 3. Tooling landscape (community verdicts)

- **Spec Kit** — solid, "ADR-like" plan/research build trust; verbose, token-hungry.
- **Kiro** — originated the requirements/design/tasks UX; proprietary.
- **OpenSpec** — deliberately lightweight; good for existing codebases; no PRD required.
- **BMAD** — most thorough/"enterprise"; widely called overkill + token-hungry ceremony
  ("8 hours for a landing page", "feels productive because there's a lot of conversation").
- **Taskmaster** — best recursive task decomposition (needs a PRD).
- **Agent OS** — sits between OpenSpec and BMAD.
- **superpowers / GSD / Spec Kitty / specs.md (AI-DLC)** — various community harnesses.
- Dominant sentiment: **for a solo dev, the lightest thing that works wins.** "The more
  layers we add, the worse the result." Many roll their own 2–3 slash commands.

---

## 4. Practitioner & critical findings (Reddit)

- **Output quality ∝ spec specificity + the code-style/architecture docs it refers to.**
- **Drift is the #1 failure mode** — specs and code diverge; context resets between sessions;
  lessons don't carry forward.
- **Hidden contradictions are lethal** — "the AI makes the spec gap visible immediately
  instead of letting it hide for two weeks."
- **PR-sized, single-concern tasks**; keep each session out of the **"dumb zone"** (the last
  ~60% of a context window where models degrade) — nuke and restart with clean context.
- **Sub-agents are for context, not role-play** — read N files, return a one-line summary.
- **Types/data-model first** — pin types precisely; review only the data model + signatures;
  let procedural code be loose (a 990k-LOC practitioner's core method).
- **Alignment before speed** — Matt Pocock's "Grill Me" skill (13k stars): the AI interviews
  *you* (40–100 Qs) before coding; "spec-then-generate" without interrogation is "vibe coding
  in disguise." (We chose adaptive ~8 questions, preserved in a Clarifications table.)
- **Token cost is real** — naming files/symbols up front beats letting the agent grep.
- **SDD predates AI** — API-first / contract-first from ~2016; skeptics call heavyweight
  versions "waterfall renamed."
- **It fails / is overkill** when the spec has hidden contradictions, or for trivial changes.

---

## 5. Meta-lessons from the three review rounds (the embedder example)

Three blind Opus reviews scored the evolving example **6.5 → 7.5 → 7.5** (FULL principles
6 → 9 → 10). Lessons that shaped the format and the linter:

1. **Drift is the killer, and structural lints miss it.** Round 1 (codebase-aware) found a
   wrong constant name and a deleted-file reference that passed structure/content/manifest
   checks. → Added the **symbol-resolution** lint.
2. **Documentary discipline is a separate axis from engineering rigor.** Round 2 (research-
   only) found the format strong on rigor (types, tasks, seams) but weak on surfaced open
   questions, self-verification, visible principles, internal consistency. → Added Principles,
   tiered Boundaries, Self-check, Clarifications, de-laundered Assumptions.
3. **The DRY-constitution choice has a ceiling.** A slice that references `standards.md`
   always leaves C (constitution) and E (six areas: commands/git) "partial" under an
   *isolation* review. That caps an isolation score ~8. The missing points are intentional
   tradeoffs, confirmed across all three rounds.
4. **LLM-as-judge scoring is noisy (~±1 pt).** Two reviewers marked identical, unchanged text
   FULL then PARTIAL (M, O). → **Track the scorecard shape across runs, not the integer.**
   Stable-FULL core: B, F, G, H, I, J, K, L, N, D.
5. **Even a hand-crafted "model" spec hid a value-level self-contradiction.** A worked example
   built its mock as `range(768)`, violating its own seam ("don't derive the mock length from
   the constant under test"). No structural lint caught it. → Rules: worked examples must not
   source their dimensions from the constant under test; unify identifiers (one model-name /
   URL form). Consistency-lint candidates. This is principle P being "lethal" in miniature.

---

## 6. Source links

- Addy Osmani — How to write a good spec for AI agents: https://addyosmani.com/blog/good-spec/
- GitHub Spec Kit — spec-driven.md: https://github.com/github/spec-kit/blob/main/spec-driven.md
- GitHub blog announcement: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- Kiro — Specs docs (EARS): https://kiro.dev/docs/specs/
- Red Hat — SDD improves AI coding quality: https://developers.redhat.com/articles/2025/10/22/how-spec-driven-development-improves-ai-coding-quality
- Structure Beats Prose: https://medium.com/@stefanvanegmond/structure-beats-prose-specs-for-coding-agents-that-actually-work-e035929b0f3d
- Reddit: r/ClaudeCode SpecKit/OpenSpec/BMAD comparison — https://reddit.com/r/ClaudeCode/comments/1pba1ud/
- Reddit: Why we shifted to SDD — https://reddit.com/r/ClaudeCode/comments/1op8b6i/
- Reddit: 'Grill Me' alignment-before-code — https://reddit.com/r/vibecoding/comments/1swyadr/
- Reddit: SDD skeptic thread — https://reddit.com/r/ExperiencedDevs/comments/1reiro1/
- Reddit: 990k-LOC agentic engineering guide — https://reddit.com/r/ClaudeCode/comments/1qthtij/
- Reddit: multi-repo/multi-team SDD — https://reddit.com/r/SpecDrivenDevelopment/comments/1szzfwz/
- Reddit: Spec Kit eating tokens — https://reddit.com/r/GithubCopilot/comments/1sus656/
