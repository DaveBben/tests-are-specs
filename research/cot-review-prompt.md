# CoT Reasoning Review Prompt

Give this prompt to a new Claude instance along with the skill files to review.

---

## Task

You are reviewing Claude Code skills (markdown files that instruct an AI coding agent how to perform multi-step tasks). Your job is to:

1. **Identify every reasoning step** in the skill — every point where the AI must make a judgment, classify, synthesize, evaluate, compare, or generate something non-trivial. Exclude mechanical steps (template filling, arithmetic, rule lookup, file I/O, waiting for user input).

2. **For each reasoning step, evaluate whether a Chain-of-Thought prompting technique would strengthen it.** Answer Yes or No with a specific explanation.

3. **For Yes answers, state which technique, where it goes, and why it helps this specific step.**

Look at my skills:
- think
- plan
- execute
- deep-review
- onboard
- bug

---

## What counts as a reasoning step

A reasoning step is any point where the AI must exercise judgment rather than follow a deterministic rule. Examples:

- Synthesizing findings from multiple sources into a coherent output
- Classifying something where the categories have fuzzy boundaries
- Generating questions, approaches, or alternatives tailored to a specific context
- Evaluating evidence quality or resolving contradictions
- Deciding whether a threshold condition is met when the threshold is qualitative
- Writing acceptance criteria, failure modes, or boundary definitions

NOT reasoning steps:
- Reading a file, running a command, writing to disk
- Applying an explicit rule ("if X > 3, do Y")
- Waiting for user input
- Template filling with known values
- Counting or arithmetic

---

## CoT Techniques Reference

Use this reference to evaluate each reasoning step. Do not force-fit techniques — most reasoning steps should get "No."

### Chain-of-Verification (CoVe)
The model generates an output, then generates verification questions about its own output *from the original spec* (not from the output itself), answers those questions independently by reading source material, and fixes contradictions.

**Best for:** Self-review of generated artifacts (code, plans, criteria) where the model's own reasoning may be self-consistently wrong. Breaks the bias where a model reviews its own work with the same reasoning that produced errors.

**Not useful for:** Creative generation, classification, presentation, or steps where a human immediately reviews the output.

### Tree-of-Thought (ToT)
Generate 2-3 alternative approaches, evaluate each against explicit criteria, select the best. Think BFS/DFS over reasoning paths.

**Best for:** Decision points where the first plausible answer isn't necessarily the best and early commitments cascade (task decomposition, architectural choices, slice boundary decisions). Must have evaluable criteria — if you can't score the alternatives, ToT is just "think of options."

**Not useful for:** Steps with clear rules, single-correct-answer problems, or steps where the model already generates alternatives (e.g., presenting 2-3 approaches to a user).

### Self-Consistency
Run the same reasoning multiple times (or through different frames/agents) and take the intersection/union/majority vote.

**Best for:** High-consequence identification tasks where a single pass may miss items (failure modes, at-risk tests, security surfaces). Most effective when the same task can be framed from genuinely different angles that surface different items.

**Not useful for:** Steps where the model already uses multiple agents/frames, or where the output is creative rather than identification-based.

### Step-Back Prompting
Before tackling the specific problem, reason about the higher-level category or principle first, then apply it.

**Best for:** Steps where the model jumps straight to specifics without first framing "what kind of problem is this?" Classification that anchors subsequent reasoning (e.g., "is this change additive or modificative?" before identifying failure modes).

**Not useful for:** Steps that are already specific by design, or where the high-level frame is obvious from context.

### Self-Ask (Decomposed Sub-Questions)
Break a complex judgment into explicit sub-questions, answer each, then compose.

**Best for:** Complex judgments where the model might skip intermediate reasoning (contradiction resolution, discrepancy detection, multi-factor evaluation). The sub-questions must be answerable independently.

**Not useful for:** Simple judgments, binary decisions with clear criteria, or steps where the skill already provides a decomposed checklist.

### Contrastive Chain-of-Thought
Explain why wrong answers are wrong alongside the correct reasoning.

**Best for:** Classification tasks where common misclassifications are known and the model needs to explicitly rule them out.

**Not useful for:** Most skill steps — the overhead of generating wrong answers usually isn't justified unless there's a specific known failure pattern.

### Few-Shot CoT
Provide 2-3 worked examples showing the desired reasoning trace.

**Best for:** Tasks where the *structure* of reasoning matters and the model reliably mimics demonstrated patterns.

**Not useful for:** Skills operating on arbitrary codebases where examples would be domain-specific. Research shows architectural reasoning doesn't transfer from examples — agents copy form, not reasoning.

---

## Decision Framework

For each reasoning step, ask these questions in order:

1. **Is this a high-consequence step?** If the model gets this wrong, does it cascade into downstream errors that are expensive to fix? If low-consequence or immediately human-reviewed, answer No.

2. **Is the model's default reasoning likely sufficient?** Some steps are within the model's core competency (natural language comprehension, pattern matching over structured data, code generation). If the model handles this well by default, adding a technique adds token overhead for no gain. Answer No.

3. **Does a specific technique address a known failure mode of this step?** The technique must target something the model *actually gets wrong*, not a theoretical risk. Known failure modes from research:
   - Self-review confirms own reasoning rather than checking against spec (CoVe fixes this)
   - First plausible decomposition isn't optimal (ToT fixes this)
   - Single-pass identification misses items visible from a different angle (Self-Consistency fixes this)
   - Jumping to specifics without framing produces inconsistent downstream reasoning (Step-Back fixes this)
   - Complex judgments skip intermediate reasoning (Self-Ask fixes this)
   - Agents predict 77% success when achieving 22% (overconfidence — CoVe partially addresses)

4. **Is the cost justified?** Each technique adds tokens and/or turns. CoVe adds 3-5 verification questions per artifact. ToT adds 2-3x the generation for the exploration step. Self-Consistency requires multiple passes or agents. The step must be consequential enough to justify the cost.

If all four answers are Yes, recommend the technique. Otherwise, No.

---

## Research Context

The following empirical findings should inform your evaluation. Reference them when explaining why a technique would or wouldn't help.

### Context and instruction quality
- Wrong context is WORSE than no context: incorrect retrieval drops resolution 4 points BELOW no-context baseline
- Context types interfere: best pair scored 36.5%, adding third type dropped to 19.6% — worse than no retrieval
- Frontier models degrade on coding tasks above ~32K tokens; sweet spot is 6-10 relevant files
- Verbose instructions actively harm: reducing 107→20 lines quadrupled resolution 12%→50%
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

## Previously Applied Techniques

The following techniques have already been applied to these skills. Note them so you don't recommend duplicates, but DO evaluate whether they're well-placed and sufficient:

### think skill
- **Step-Back** (synthesis): classify change as additive/modificative/extractive before producing outputs
- **Self-Consistency** (at-risk tests): convergence check across 3 agents — 2+ agents = confirmed, 1 agent = uncertain
- **Self-Consistency** (failure modes): dual framing — "what breaks silently?" + "what's irreversible?" — take union
- **Predict-before-reveal** (Batches 2 and 3): ask human first, then present AI findings

### plan skill
- **Tree-of-Thought** (Step 5 decomposition): generate 2-3 candidate decompositions, evaluate against criteria, select best
- **CoVe** (Step 5 acceptance criteria): "Could I implement from only these criteria? Does each test one observable behavior?"

### execute skill
- **Explicit pass/fail check** (trust-but-verify): check exit code AND scan for failure/skip keywords

### code-implementor agent
- **CoVe** (self-review): generate verification questions from spec before looking at code, answer by reading code, fix contradictions
- **Self-Ask** (discrepancy detection): decompose "is this a real discrepancy?" into 3 sub-questions about expectations, reality, and predecessor explanations

### bug skill
- **Self-Consistency** (root cause): trace backward from symptom + trace forward from suspected cause, check convergence
- **CoVe** (reproduction test): verify test exercises exact code path and asserts expected behavior before running
- **CoVe** (acceptance criteria): same as plan skill

### deep-review skill
- **Self-Ask** (cross-agent contradictions): 4-question decomposition for resolving agent disagreements
- **Step-Back** (actionability filtering): anchor "would a developer act?" to change type from Step 2

### onboard skill
- **Self-Ask** (technical domain identification): 3-question evaluation per candidate directory pair
- **Step-Back** (decision-gap check): classify project type before generating risk questions

---

## Output Format

For each skill, produce:

### [Skill Name]

**Reasoning steps:**
1. [Step name] — [one-sentence description of the judgment]
2. ...

**Technique evaluation:**

| # | Step | Technique? | Explanation |
|---|------|-----------|-------------|
| 1 | [name] | No | [why not — be specific] |
| 2 | [name] | Yes — [technique] | [why — reference research finding or known failure mode] |

**New recommendations** (if any):
- **[Step]**: [Technique] — [What to add, where, and why. One paragraph max.]

**Previously applied — assessment:**
- **[Technique at step]**: [Well-placed / Misplaced / Insufficient — and why]

End with a pipeline-wide summary: are there any cross-skill patterns or gaps?
