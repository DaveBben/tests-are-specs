# Agentic Coding Pipeline Research

## Question

Does a multi-phase think/plan/execute pipeline add value over giving a well-crafted prompt to Claude plan mode directly?

## Current Pipeline (TPE)

- **7 skills**, **8+ subagents**, producing **6 artifact types** across 4-5 phases
- Single feature flow: think (3 parallel explore agents) → plan (plan-verifier agent) → execute (code-implementor agent, task-handoff-checker) → review (4 parallel review agents)
- Potentially **10+ model invocations** before a single line of code ships

## Part 1: Pipeline Complexity vs Simplicity

### Initial Sources (General)

- **SWE-bench** (Princeton) — Top-performing agents use simple architectures: locate relevant code, understand the problem, generate a patch. Multi-phase pipelines don't correlate with higher scores.
- **Cognition/Devin benchmarks** — Their advantage came from tool use and iteration loops, not planning frameworks.
- **Anthropic's own findings** — Claude performs best with a clear specification and the ability to iterate. Plan mode already provides "think before acting" structure.
- **Practitioner consensus** (Addy Osmani, others) — TDD-first in agentic flows actually slows down agentic coding and produces worse results because the model writes tests against its assumptions rather than against working code.

### What Demonstrably Helps

| Technique | Why | Evidence |
|-----------|-----|----------|
| Detailed, specific prompts | Single highest-leverage input | SWE-bench, METR, HumanEval, every benchmark |
| Explicit "do NOT" list | Measurably reduces scope creep | Practitioner consensus |
| File/context scoping | Giving the model the right files matters more than a thinking framework | SWE-bench top performers |
| Iterative feedback loops | Run, fail, read errors, retry outperforms single-shot | Consistent across benchmarks |
| Independent review | Catches blind spots self-review misses | Independent review agents |
| Human decision gates | Humans decide what, AI decides how | Universal |

### What's Questionable on Frontier Models

| Technique | Why It's Questionable |
|-----------|----------------------|
| External "think step by step" scaffolding | Frontier models do CoT internally. External scaffolding restates what the model would do anyway. |
| Impact analysis as a separate phase | Model naturally considers dependencies when given good context. Separate pass is redundant. |
| TDD-first in agentic flows | Net-negative per METR and practitioners. |
| Multi-phase framework scaffolding | No published benchmark shows plan → decompose → analyze → execute outperforms a well-crafted prompt + plan mode. |

### What Should Be Dropped from TPE

| Drop | Why |
|------|-----|
| Separate impact analysis phase | Model does this internally with good prompts |
| Plan-verifier subagent | The model already verified paths when writing the plan |
| Task JSON schema ceremony | Most features are 1-3 tasks; schema overhead exceeds coordination value |
| Multi-candidate decomposition | Almost always produces the same answer at 3x cost |
| At-risk test tracking through pipeline | TDD in agentic flows is net-negative per METR findings |
| Task-handoff-checker subagent | Solves a problem created by the task decomposition complexity |
| brainstorm.md as a separate artifact | Its value is the thinking, not the document |

### The Core Insight

Frameworks that work for *human* development (TDD, impact analysis, decomposition planning) don't transfer directly to agentic coding because they solve human cognitive limitations — limited working memory, attention drift, communication overhead between team members. The model doesn't have those limitations. What it *does* need is clear intent, explicit boundaries, and the ability to iterate.

---

## Part 2: Prompt Quality — What Actually Works (Deep Dive)

### METR Findings (Specific, Citable)

METR has **not** published a dedicated study on prompt quality for agentic coding. Their findings touch on it tangentially:

**1. Elaborate scaffolding does NOT reliably beat generic scaffolds (Feb 2026)**
Claude Code and Codex — "prompted much more elaborately than other scaffolds, including use of to-do lists for long tasks" and "explicitly optimized for their respective model families" — are **not obviously better** than METR's generic scaffolds (ReAct, Triframe). Opus 4.5 with Claude Code beat ReAct in only 50.7% of bootstrap samples. **Not statistically significant.** This is a key negative result: heavily optimized, elaborate prompting did not reliably outperform a generic scaffold.
- Source: [METR: Measuring Time Horizon using Claude Code and Codex](https://metr.org/notes/2026-02-13-measuring-time-horizon-using-claude-code-and-codex/)

**2. Scaffold sensitivity is model-dependent (Mar 2025, updated Jan 2026)**
GPT-4o and o3 had "statistically significantly higher scores under Vivaria than Inspect," meaning scaffold/prompt effects are **model-dependent**, not universal. What works for one model may not matter for another.
- Source: [METR: Time Horizon 1.1](https://metr.org/blog/2026-1-29-time-horizon-1-1/)

**3. "Don't give up" prompting helps moderately (Feb 2026)**
"With minor changes to Claude Code and Codex, such as additional prompting that encourages agents not to give up early on tasks, agents could perform moderately better." Mentioned as observation, not controlled study.

**4. Algorithmic vs holistic scoring gap (Aug 2025)**
AI agents "often implement functionally correct code that cannot be easily used as-is because of issues with test coverage, formatting/linting, or general code quality." Performance drops substantially under manual review vs test-based scoring. Implication: prompts optimized for passing tests may not produce production-quality code.
- Source: [METR: Research Update](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/)

**5. The productivity paradox (Jul 2025)**
16 experienced developers, 246 real tasks, randomized. Developers using AI tools were **19% slower** (95% CI: +2% to +39%), despite *believing* they were 20% faster — a perception-reality gap of ~40 percentage points. Even with frontier models and good prompting tools, integration overhead and verification burden can negate raw generation speed.
- Source: [METR Developer Productivity Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

**6. HCAST: Task duration threshold (Mar 2025)**
Current agents succeed 70-80% on tasks taking humans <1 hour, but <20% on tasks taking >4 hours. Basic scaffold, no prompt variations tested.
- Source: [HCAST](https://arxiv.org/abs/2503.17354)

### Quantified Prompt Engineering Findings (Non-METR)

**OpenAI GPT-4.1: Three simple agentic instructions = ~20% improvement**
Adding persistence reminders ("keep going until resolved"), tool-calling encouragement ("use tools instead of guessing"), and explicit planning instructions increased SWE-bench Verified score by **~20%**. Planning alone = **+4%**. Measured, not theoretical.
- Source: [GPT-4.1 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide)

**Structured CoT (SCoT): Up to +13.79% Pass@1**
Decomposing chain-of-thought into programming constructs (sequence, branch, loop) outperformed standard CoT by up to 13.79% on HumanEval, 12.31% on MBPP. Plain CoT only improved gpt-3.5-turbo by 0.82 points. Ablation showed removing I/O structures decreased Pass@1 by up to 2.37%.
- Source: [SCoT — Li et al., ACM TOSEM 2025](https://arxiv.org/abs/2305.06599)

**Chain of Grounded Objectives (CGO): Same accuracy, fewer tokens**
Concise goal-oriented functional objectives (styled like code comments) instead of step-by-step reasoning. Achieved accuracy **comparable to or better than** existing methods while **using fewer tokens**. Goals outperform procedural steps.
- Source: [CGO, ECOOP 2025](https://arxiv.org/abs/2501.13978)

**Anthropic Context Engineering: Up to +54% from avoiding contradictions**
Up to 54% improvement by ensuring system prompt, tool definitions, conversation history, and injected context don't conflict. This is "context engineering" — curating the smallest set of high-signal tokens.
- Source: [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**SWE-agent: Tool design > prompt text (+10.7pp)**
Custom edit commands + linter guardrails outperformed raw bash by 10.7 percentage points. Removing the linter caused agents to get stuck on syntax error recovery. Action space simplification (specialized commands like `edit`, `find_file`) reduces agent confusion. Fixed output templates remove ambiguity. The interface matters more than the prompt text.
- Source: [SWE-agent, NeurIPS 2024](https://arxiv.org/abs/2405.15793)

**Agentless: Structured prompts beat complex agents**
Hierarchical localization prompts (files → classes/functions → edit locations) achieved 32% on SWE-bench Lite at $0.70/issue — highest open-source at the time. Carefully structured prompts in a fixed pipeline can outperform complex agent scaffolds.
- Source: [Agentless, Jul 2024](https://arxiv.org/abs/2407.01489)

**Augment Code: Foundation model quality dominates**
Achieved #1 open-source SWE-bench Verified (65.4%). Their hierarchy: (1) foundation model quality dominates — prompt optimization "saturates as an axis for improvement", (2) context quality is the most important prompt factor, (3) consistency across all prompt components matters, (4) error recovery via informative tool errors. Things that **did not help**: thinking mode, separate "fix regressions" agent.
- Source: [Augment Code: 11 prompting techniques](https://www.augmentcode.com/blog/how-to-build-your-agent-11-prompting-techniques-for-better-ai-agents)

### The Null Results (What Doesn't Matter)

**Prompt patterns don't affect code quality (EASE 2025)**
Across 7,583 code files, Kruskal-Wallis tests found **no statistically significant differences** among prompt patterns (zero-shot, few-shot, CoT) on maintainability, security, or reliability metrics. Prompt patterns affect *functional correctness* but not *code quality*. Quality is a function of model training, not prompt structure.
- Source: [Palomba et al., EASE 2025](https://dl.acm.org/doi/10.1145/3756681.3756938)

**Formatting is negligible on frontier models**
Claude 3.7 and GPT-4o: performance varies by <1% when whitespace/indentation is removed. Gemini-1.5 is sensitive (4% decline). Smaller models (LLaMA-2-13B) can swing 76 points from formatting alone. For frontier models, formatting doesn't matter.
- Source: [Du et al., 2025](https://arxiv.org/html/2508.13666v1)

**"You are an expert" phrasing is negligible on frontier models**
Literature increasingly treats persona/role phrasing as negligible for frontier models.

### What Matters Most: The Evidence-Based Hierarchy

Based on all published research, the factors that affect agentic coding success, **in priority order**:

1. **Foundation model quality** — dominates everything else; prompt optimization saturates (Augment Code)
2. **Context quality** — *what information* you provide matters most: which files, what errors, what constraints (Augment Code, Anthropic, OpenAI)
3. **Context consistency** — no contradictions between system prompt, tools, and conversation history; up to 54% improvement (Anthropic)
4. **Tool/interface design** — specialized edit commands, linter guardrails, informative errors; +10.7pp (SWE-agent)
5. **Persistence/iteration** — "keep going until resolved"; ~20% improvement from three simple instructions (OpenAI GPT-4.1)
6. **Goal framing over procedural steps** — state objectives, not procedures; same accuracy, fewer tokens (CGO)
7. **Structured decomposition in the prompt** — programming constructs in CoT; up to +13.79% but diminishes with model capability (SCoT)
8. **Prompt text/wording** — minimal impact on frontier models; formatting <1% variance (Du et al.)

### What This Means for Prompt Design

**High-value prompt components (keep):**
- Clear intent: what and why
- Explicit constraints and non-goals ("do NOT")
- Relevant file paths and code context
- Persistence instructions ("keep going until done")
- Verification instructions ("run tests after changes")

**Low-value prompt components (drop):**
- Elaborate step-by-step reasoning scaffolds
- Role/persona phrasing ("you are an expert senior engineer")
- Formatting ceremony (specific markdown structure)
- Separate impact analysis instructions
- Multi-phase decomposition instructions

**The uncomfortable truth:**
The research says the single biggest thing you can do is use the best model. After that, it's about *what context* you feed it, not *how you phrase* the prompt. A well-scoped prompt with the right files and clear constraints on a frontier model will beat an elaborately engineered prompt scaffold almost every time.

---

## Part 3: Context Engineering — The Real Differentiator (Deep Dive)

### The Key Finding: Context Quality > Prompt Quality

The research converges on a surprising conclusion: **what information you give the model matters far more than how you phrase the request.** This is "context engineering" — curating the right tokens in the right order.

### Localization Is the Bottleneck

Agents spend **60-80% of their tokens on finding relevant code**, not on solving the problem. The single biggest differentiator between a 40% agent and a 60%+ agent is how well it locates the right code to modify.

**Measured: File context provides 15-17x improvement (April 2026)**
61 configurations tested on 500 SWE-bench Verified instances (GPT-5-mini):
- No file context at all: 18/500 resolved (3.6%)
- With file-level context: 56-63% resolution rate
- Optimal configuration (LLM-retrieved files + elements + buggy lines): **317/500 (63.4%)**
- Sweet spot: **6-10 relevant files** (~58,273 tokens)
- Source: [Fault Localization Context for LLM-Based Program Repair](https://arxiv.org/abs/2604.05481)

**Measured: Oracle context signals ranked (ORACLE-SWE, April 2026)**
On SWE-bench Verified with GPT-5, injecting individual oracle signals:
- Reproduction Test (oracle): **85.2%** success
- Execution Context (oracle): 57.5%
- Edit Location (oracle): 54.5%
- API Usage (oracle): 51.0%
- Regression Test (oracle): 39.4%
- All five combined: **97%+**
- **Reproduction tests are the single most valuable signal** — more valuable than knowing *where* to edit
- Source: [ORACLE-SWE](https://arxiv.org/abs/2604.07789)

**Measured: Focused context beats full-file context (SWE-bench, ICLR 2024)**
"Oracle-collapsed" context (only the lines edited in the ground-truth fix, +/-15 lines) outperformed full-file oracle context:
- GPT-4: 1.3% → 3.4% (2.6x improvement)
- Claude 2: 4.8% → 5.9% (1.2x improvement)
- Source: [SWE-bench, ICLR 2024](https://arxiv.org/abs/2310.06770)

### More Context Hurts — This Is Measured, Not Opinion

**Context length alone degrades performance (EMNLP 2025 Findings)**
Tested 5 models on math, QA, and coding tasks. Performance degradation: **13.9% to 85%** even with perfect retrieval.

| Model | Task | Baseline | At 30K tokens | Drop |
|-------|------|----------|---------------|------|
| GPT-4o | GSM8K | 87.8% | 80.8% | -7.0pp |
| Claude 3.5 Sonnet | MMLU | 82.2% | 14.6% | -67.6pp |
| Llama-3.1-8B | HumanEval | 57.3% | 9.7% | -47.6pp |

Even when distracting text was replaced with **whitespace tokens**, degradation persisted. Even when irrelevant tokens were **masked entirely** (forced attention only to relevant tokens), performance still dropped. **Context length itself causes degradation, not distraction.**
- Source: [Context Length Alone Hurts, EMNLP 2025](https://arxiv.org/abs/2510.05381)

**Context rot across all frontier models (Chroma, 2025)**
Every model tested exhibited degradation as context grew:
- Claude Sonnet 4 dropped from **99% to 50%** on word replication tasks
- Models performed **better on shuffled haystacks than coherent documents** — structural coherence hurts (counter-intuitive)
- Degradation starts well before maximum context window
- At 1M tokens MRCR v2: Opus 4.6 = 78.3%, GPT-5.4 = 36%, Gemini 3.1 Pro = 26%
- Source: [Context Rot, Chroma 2025](https://www.trychroma.com/research/context-rot)

**Lost in the middle (TACL 2024)**
- Information at position 1 (beginning): ~75% accuracy
- Information at position 20 (end): ~72% accuracy
- Information at position 10 (middle): ~55% accuracy
- **~20pp drop for middle-positioned information** — architectural limitation from RoPE biases
- Source: [Lost in the Middle, TACL 2024](https://aclanthology.org/2024.tacl-1.9/)

**Line-level expansion actively hurts (April 2026)**
Adding more context around identified buggy lines *degraded* performance:
- "Context window lines" expansion: average **-3.1 instances** resolved
- "Code slicing" expansion: average **-3.5 instances** resolved
- Simply providing the buggy lines outperformed expanded code slices
- Source: [Fault Localization Context](https://arxiv.org/abs/2604.05481)

### CLAUDE.md / AGENTS.md — Measured Impact

**Human-curated context files help modestly; LLM-generated ones hurt (Feb 2026)**
ETH Zurich tested 4 agents across 3 conditions on SWE-bench Lite (300 tasks) and AGENTbench (138 tasks):

| Condition | Task Success | Cost Impact |
|-----------|-------------|-------------|
| No context file | baseline | baseline |
| LLM-generated context file | **-0.5 to -2pp** | **+20-23% cost** |
| Developer-written context file | **+4pp** | increased cost |

- LLM-generated files hurt performance in **5 of 8** evaluation settings
- Reasoning tokens increased **+14-22%** with auto-generated files
- **Context file bloat reduces task success** — more rules ≠ better performance
- Source: [Evaluating AGENTS.md, ETH Zurich](https://arxiv.org/abs/2602.11988)

**Separate study: AGENTS.md reduces runtime 28.6% (Jan 2026)**
10 repositories, 124 pull requests: AGENTS.md presence associated with 28.64% lower median runtime and 16.58% reduced output tokens while maintaining comparable completion.
- Source: [Impact of AGENTS.md Files](https://arxiv.org/abs/2601.20404)

### What This Means: The Context Engineering Rules

Based on all measured evidence:

1. **Less context is better than more** — provide the minimum relevant context, not everything you can find
2. **Precise context beats expansive context** — exact buggy lines > code slices > full files
3. **Reproduction information is the highest-value signal** — more valuable than knowing where to edit
4. **6-10 files is the sweet spot** — measured optimal range for file-level context
5. **Put important information at beginning or end, never middle** — 20pp accuracy penalty for middle positioning
6. **Human-curated context files help; auto-generated ones hurt** — quality > quantity
7. **Contradictions in context are catastrophic** — up to 54% improvement from eliminating them

---

## Part 4: What Actually Wins — The SWE-bench Formula

### Current State of the Art (May 2026)

**SWE-bench Verified (now considered contaminated):**

| System | Score |
|--------|-------|
| Claude Mythos Preview | 93.9% |
| GPT-5.3-Codex | 85% |
| Verdent (Claude Sonnet 4.5 + thinking) | 82% pass@1, 88% pass@3 |
| Claude Opus 4.5 | 80.9% |
| Augment Code | 72.0% (standard pass@1) |

**SWE-bench Pro (1,865 multi-language tasks, uncontaminated — the real benchmark):**

| System | Score |
|--------|-------|
| GPT-5.3-Codex (CLI) | 57.0% |
| Claude Code | 55.4% |
| Auggie | 51.8% |
| Cursor | 50.2% |
| Best raw model (standardized scaffold) | 45.9% |

The gap between standardized scaffold (~46%) and custom agent system (~55%) demonstrates **scaffolding adds 5-15pp** beyond raw model capability.

### What Separates 40% Agents from 60%+ Agents

| Factor | ~40% Agent | ~60%+ Agent |
|--------|-----------|-------------|
| **Localization** | Single-pass RAG or simple search | Hierarchical or interactive multi-pass search |
| **Attempts** | Single attempt (pass@1) | Multiple attempts + intelligent selection |
| **Context management** | Naive full-file inclusion | Compressed/selective, token-efficient |
| **Model** | Open-source or older proprietary | Claude 3.5+ Sonnet, GPT-5, Gemini 2.5 Pro |
| **Verification** | Generate patch, submit | Generate patch, run tests, iterate, submit |
| **Planning** | No explicit plan | Lightweight todo list |
| **Tool design** | Generic tool descriptions | Optimized interfaces, absolute paths, string replacement |

### The Five Techniques That Actually Matter (Ranked by Measured Impact)

**1. Inference-time scaling / multi-attempt selection (+5-6pp)**
Generate multiple candidate patches, select the best one using tests or a critic model.
- OpenHands: 60.6% → 66.4% with 5 attempts + critic model
- Moatless + DeepSeek: 56% by sampling 250 candidates
- Verdent: 76.1% pass@1 → 81.2% pass@3
- Source: [OpenHands](https://openhands.dev/blog/sota-on-swe-bench-verified-with-inference-time-scaling-and-critic-model)

**2. Test-based verification loops (doubles precision)**
Generate reproduction test, run candidates against it. Devin: 72% of successful fixes took >10 minutes, indicating iterative test-fix cycles.
- Source: [Cognition/Devin Technical Report](https://cognition.ai/blog/swe-bench-technical-report)

**3. Hierarchical localization (15-17x improvement over no context)**
File → class/function → edit location. Agentless achieved 50%+ with just this technique.
- Source: [Agentless](https://arxiv.org/abs/2407.01489)

**4. Minimal, well-designed tools (+10.7pp)**
Verdent tested directly: SWE-bench succeeds with only `bash`, `read`, `write`, and `edit`. Anthropic spent more time optimizing tool interfaces than the overall prompt. Key: absolute file paths, string replacement (not line-number editing), detailed tool descriptions.
- Source: [SWE-agent, NeurIPS 2024](https://arxiv.org/abs/2405.15793), [Verdent Technical Report](https://www.verdent.ai/blog/swe-bench-verified-technical-report)

**5. Lightweight planning (prevents drift, not heavyweight)**
Structured todo lists improve resolution and reduce wasted tokens. MCTS-based planning gives 23% relative improvement. But **rigid state machines hurt** — flexible transitions + value functions outperform fixed pipelines.
- Source: [SWE-Search](https://arxiv.org/html/2410.20285v1)

### What Does NOT Help (Measured)

- **Thinking mode** — Augment Code found it did not help
- **Separate "fix regressions" agent** — Augment Code found it did not help
- **More tools** — Verdent proved 4 tools is sufficient
- **Multi-agent systems** (under equal compute) — single-agent matches or outperforms when controlling for total tokens (Anthropic-affiliated study, arXiv 2604.02460)
- **LLM-generated context files** — hurt performance by 0.5-2pp, increased cost 20%+ (ETH Zurich)

### The Token Economics

**More tokens ≠ more accuracy (Stanford, 2026)**
- Agentic coding workflows average **1-3.5M tokens per task**
- Runs on the same task differ by **up to 30x** in total tokens
- **Higher token usage does not correlate with higher accuracy**
- **60-80% of tokens go toward locating relevant code**, not solving the problem
- Source: [How Do AI Agents Spend Your Money?](https://arxiv.org/abs/2604.22750)

**Cost-effectiveness comparison:**
- Agentless: ~$0.34/issue
- Full agents: ~$3.34/issue (10x more)
- Agentless-1.5 at 50.8% vs top agents at 79.2% — the last 29pp costs 10x more

### Architecture Diversity, Not Complexity

The "Dissecting SWE-bench Leaderboards" paper (2506.17208) analyzed 80 unique approaches and found **no single architecture dominates**. Both simple (Agentless) and complex (MASAI) approaches appear near the top. Seven architectural groups identified. The common thread is not complexity but:

1. Good localization
2. Verification after patching
3. Model quality
4. Token efficiency

### Scaffolding Matters — But How Much?

**Measured: Same model, different scaffold = 21% spread (Morphllm, 2026)**
The same model scores 17 benchmark problems apart depending on scaffold architecture. This is the strongest evidence that scaffolding adds real value beyond the model alone.

**But: Elaborate scaffolding doesn't beat simple scaffolding**
METR found Claude Code's elaborate scaffold did not reliably beat generic ReAct (50.7% win rate, not significant). The value is in *having* a scaffold, not in *how elaborate* it is.

---

## Part 5: The 2026 Breakthrough Papers (Latest Research)

### The Paradigm Shift: Harness Engineering

The field has converged on a new term and discipline: **Harness Engineering**. The harness is "everything in an AI agent except the model itself." This reframes the question from "what prompt works best" to "what system around the model works best."

**Core equation (Addy Osmani, 2026):** `Agent = Model + Harness`

If you're not building the model, you're building the harness. And the harness is where the measured gains live.

### SlopCodeBench: The Most Sobering Finding (March 2026)

Measures how code quality degrades as agents repeatedly extend their own code. 11 models, 20 problems.

- **No agent solves any problem end-to-end** (highest checkpoint solve rate: 17.2%)
- Agent code is **2.2x more verbose** than maintained human code
- High-complexity functions grew from 4.1 to 37.0 across checkpoints
- Agents **patch rather than refactor** — bad early decisions become permanent foundations
- **Quality-aware prompts (anti-slop, plan-first) reduced initial verbosity by 33-34%, but degradation resumed at identical rates**. The slopes are parallel. Prompting does not fix long-horizon degradation.
- Source: [SlopCodeBench](https://arxiv.org/html/2603.24755v1)

**This is the killer finding for your TPE pipeline question.** Your plan skill's elaborate instructions may produce a better *first* output, but over a long session the quality degrades at the same rate regardless. The fix is architectural (fresh context windows, clean handoffs), not prompt-based.

### Meta Context Engineering: Learnable Harnesses Beat Handcrafted Ones (Feb 2026)

A bi-level optimization framework that co-evolves context engineering skills and context artifacts.

- **89.1% average relative improvement** over base model
- **16.9% improvement** over prior SOTA handcrafted context engineering
- **13.6x faster** than prior methods
- Learned contexts flexibly adjust from 1.5K to 86K tokens per task — no fixed template
- Source: [Meta Context Engineering](https://arxiv.org/abs/2601.21557)

**Implication:** The optimal context is task-dependent and learnable. Fixed templates (like your brainstorm.md → plan.md → task JSON pipeline) are outperformed by adaptive approaches.

### Meta-Harness: Automated Harness Search (March 2026, Stanford)

An outer-loop system that searches over harness code configurations.

- **+7.7 points** over SOTA context management on text classification, using **4x fewer tokens**
- **+4.7 points** average across five held-out models on IMO-level math problems
- Discovered harnesses **outperform best hand-engineered baselines on TerminalBench-2**
- Source: [Meta-Harness](https://arxiv.org/abs/2603.28052)

**Implication:** Even the best hand-engineered harness (which is what GSD, TPE, and all frameworks are) is suboptimal compared to automated harness search. The field is moving toward learned harnesses.

### SWE-Pruner: Less Context = Better Results (Jan 2026, ACL 2026)

A 0.6B parameter neural skimmer that prunes irrelevant code from agent context.

- **23-54% token reduction** while **improving** success rates
- Up to **14.84x compression** on single-turn tasks
- Source: [SWE-Pruner](https://arxiv.org/abs/2601.16746)

**Implication:** Most of what we feed to agents is noise. Aggressive, intelligent pruning improves outcomes.

### Prompt Engineering Saturation: Now Measured (2026)

Softcery's empirical data quantifies the diminishing returns curve:

- First 5 hours of prompt work: **35% improvement**
- Next 20 hours: **5% improvement**
- Next 40 hours: **1% improvement**
- **The 85% accuracy ceiling**: once you hit ~85% with proper foundations, continued prompt iteration yields near-zero gains
- **The 10-iteration rule**: if 10 focused rephrasing attempts don't resolve a failure mode, the issue is architectural

SlopCodeBench corroborates: prompt strategies reduce initial verbosity by 33-34% but degradation resumes at identical rates.

### Codified Context: Real-World Evidence (Feb 2026)

A 70-day study with 283 development sessions (2,801 human prompts, 16,522 autonomous agent turns):

**Three-tier architecture that worked in production:**
1. **Tier 1 (Hot Memory)**: ~660-line constitution loaded every session
2. **Tier 2 (Domain Specialists)**: 19 specialized agent specs (~9,300 lines)
3. **Tier 3 (Cold Memory)**: 34 on-demand specs (~16,250 lines) via MCP retrieval

Context infrastructure totaled **24.2% of the codebase**. Human prompts averaged under 100 words (pre-loaded context replaced explanation). **Zero save-system failures across 74+ sessions.**
- Source: [Codified Context](https://arxiv.org/html/2602.20478v1)

### Harness Engineering Design Framework (Böckeler, martinfowler.com, 2026)

**Two control types:**
- **Guides (feedforward)**: Anticipatory controls that steer before execution
- **Sensors (feedback)**: Observational controls enabling self-correction after generation

**Three regulation categories:**
1. **Maintainability harness** — most mature (linters, formatters, type checkers)
2. **Architecture fitness harness** — fitness functions enforcing constraints
3. **Behaviour harness** — validates functional correctness; "the elephant in the room" with significant unsolved challenges

**The Ratchet Principle (Osmani):** Every agent failure should produce a permanent harness rule. Failures drive constraints, not speculation. Each mistake becomes a permanent signal.

**Measured result:** Viv's team moved a coding agent from **Top 30 to Top 5 on Terminal-Bench by changing only the harness**, not the model.

### GSD vs Alternatives — Still No Head-to-Head

No formal benchmark comparison exists between frameworks. Qualitative differences:

| Framework | Core Insight |
|-----------|-------------|
| **GSD** | Every phase starts with full context budget; clean handoff prevents context rot |
| **Superpowers** | TDD enforcement |
| **GSTACK** | Role-based governance |
| **Spec Kit** | Lightweight spec-driven |

**GSD's key architectural insight** is worth noting: by decomposing into context-window-sized tasks where each sub-agent gets a fresh context, it directly addresses the SlopCodeBench finding that long-horizon quality degrades regardless of prompting. This is solving the right problem — context rot — through architecture rather than prompt engineering.

---

## Part 6: The Definitive Answer (As of May 2026)

### The question: What actually gets the best quality from coding agents?

The evidence now converges clearly enough to give a real answer. Here it is:

### Tier 1: Non-negotiable foundations (without these, nothing else matters)

| Factor | Impact | Evidence |
|--------|--------|----------|
| Best available model | Dominates all other factors | SWE-bench Pro leaderboard; Augment Code |
| Precise, minimal context (6-10 files) | 15-17x improvement over no context; more context actively hurts | Fault Localization Study; Context Length Alone Hurts |
| Verification loop (run tests, iterate) | Doubles precision of patch selection | Devin, OpenHands, Verdent |
| Well-designed tools (bash, read, write, edit) | +10.7pp; 4 tools is sufficient | SWE-agent; Verdent |

### Tier 2: High-value harness components (measurable gains)

| Factor | Impact | Evidence |
|--------|--------|----------|
| Human-curated CLAUDE.md/AGENTS.md | +4pp success, -28.6% runtime, -16.6% tokens | ETH Zurich; AGENTS.md impact study |
| Persistence instructions ("keep going") | ~20% improvement from 3 simple instructions | OpenAI GPT-4.1 guide |
| Fresh context per task (prevent context rot) | Degradation is prompt-resistant; only architecture fixes it | SlopCodeBench; GSD insight |
| Context consistency (no contradictions) | Up to +54% from eliminating contradictions | Anthropic context engineering |
| Lightweight todo list (not heavyweight planning) | Prevents drift, reduces wasted tokens | Verdent; SWE-Search |
| The ratchet principle (failures → permanent rules) | Compound improvement over time | Osmani; practitioner consensus |

### Tier 3: Valuable if you can afford it (diminishing returns)

| Factor | Impact | Evidence |
|--------|--------|----------|
| Multi-attempt + selection | +5-6pp but 2-5x cost | OpenHands; Verdent pass@3 |
| Specialized search subagent (WarpGrep-style) | +2.1pp, -15.6% cost, -28% time | SWE-bench Pro analysis |
| Model ensembling | +3-8pp at proportional cost increase | Augment Code |

### Tier 4: Saturated / not worth additional investment

| Factor | Status | Evidence |
|--------|--------|----------|
| Prompt wording beyond clear intent + constraints | Saturates after ~5 hours of work | Softcery measurement; EASE 2025 null result |
| Elaborate multi-phase scaffolding | Not reliably better than simple scaffolding | METR Feb 2026 |
| Multi-agent under equal compute | Single-agent matches or outperforms | arXiv 2604.02460 |
| TDD-first in agentic flows | Net-negative | METR; practitioners |
| Auto-generated context files | Hurts by 0.5-2pp, costs 20% more | ETH Zurich |
| More than 4 tools | No benefit measured | Verdent |
| Thinking mode | No benefit measured | Augment Code |
| Role/persona phrasing | Negligible on frontier models | Literature consensus |

### What this means for your TPE pipeline

Your pipeline invests heavily in Tier 4 (elaborate multi-phase scaffolding, detailed prompt instructions, multi-agent decomposition) while potentially underinvesting in Tier 1 and 2 (precise context management, fresh context per task, verification loops, the ratchet principle).

The evidence-backed redesign would:
1. **Keep** the human decision gate (think phase's core value)
2. **Keep** clear constraints and non-goals
3. **Add** aggressive context pruning (the research says most context is noise)
4. **Add** fresh context per task segment (GSD's insight, backed by SlopCodeBench)
5. **Add** the ratchet principle (failures → permanent CLAUDE.md rules)
6. **Drop** elaborate prompt scaffolding (266-line skills)
7. **Drop** multi-phase artifact generation (brainstorm.md → plan.md → task JSONs)
8. **Drop** verification subagents (plan-verifier, task-handoff-checker)
9. **Drop** at-risk test tracking through the pipeline

### The formula

```
1. Best model
2. Minimal precise context (6-10 files, pruned aggressively)
3. Clear spec: what, why, constraints, non-goals, verification command
4. Fresh context per task (clean handoff, not accumulated)
5. 4 tools: bash, read, write, edit
6. Persistence: "keep going until resolved, run tests after changes"
7. Ratchet: every failure becomes a permanent harness rule
8. Human approval at intent and review stages
```

That's it. Everything else is in the noise — or actively harmful due to context bloat.

### The honest caveats

1. **SWE-bench ≠ real-world development.** All the evidence comes from well-defined single-repo tasks. Real features involve ambiguity, multi-repo, stakeholder alignment, and multi-day effort. The benchmarks don't cover this.

2. **No framework has been independently benchmarked against alternatives.** GSD, TPE, Spec Kit — none have controlled comparisons. The field lacks this data.

3. **The "think" phase (ambiguity resolution) has no benchmarks.** The value of forcing clear requirements before coding is universally agreed upon but never quantified. Your think phase may be the one part that genuinely adds value — we just can't prove it.

4. **Context rot is real but unsolved.** SlopCodeBench shows prompts don't fix it. GSD's clean-handoff approach is promising but unmeasured on a standard benchmark.

5. **The research is moving fast.** Meta Context Engineering and Meta-Harness suggest the future is *learned* harnesses, not hand-engineered ones. Today's optimal framework may be automated away within a year.

---

## Part 7: The Optimal Workflow — Small Focused Changes

### The conclusion

The optimal workflow for agentic coding is not a framework. It's:

```
1. Human thinks and designs (outside Claude, outside any tool)
2. Human decomposes into small focused changes
3. For each change: fresh session → focused prompt → verify → done
```

### The evidence

**Why small changes win:**

| Factor | Evidence |
|--------|----------|
| Fresh context per change prevents quality degradation | SlopCodeBench: quality degrades over long sessions, prompts can't fix it |
| Verification is tractable | ORACLE-SWE: verification is the #1 signal — only useful when scope is small enough to verify |
| Failure is cheap | A bad small change is thrown away and re-prompted. A bad 15-file change is the METR 19% slowdown scenario. |
| Agents succeed on small tasks | HCAST: 70-80% on tasks <1 hour, <20% on tasks >4 hours |
| SWE-bench winners touch few files | Median successful patch: 1-3 files modified |

**The measured sweet spot:**

| Scope | Range | Source |
|-------|-------|--------|
| Files shown as context | 6-10 | Fault Localization Study |
| Files the agent modifies | 1-3 | SWE-bench median successful patch |
| Hard ceiling before quality drops | ~4 modifications | HCAST, SlopCodeBench |

**When to decompose vs. not:**
- Can a competent developer hold the entire change in their head? → One prompt, one session
- No? → Decompose into pieces that pass that test
- Breaking a 3-file change into three 1-file changes is overhead, not improvement
- Breaking a 15-file feature into five 3-file tasks with fresh contexts is the architecture that wins

**Where the create-spec skill fits:**
- For changes where you already know the files, constraints, and verification → write the prompt directly using the template
- For changes where you know *what* but need codebase investigation to find *where* → the create-spec skill finds the files, symbols, and current behavior

**The human's irreplaceable role:**
The design work — understanding tradeoffs, choosing the right approach, identifying edge cases, decomposing into the right pieces — is the part that has no benchmarks and can't be automated. Every benchmark measures the *implementation* step, not the *thinking* step. The value of the human is in producing the specification that makes implementation tractable.

---

## Part 8: Helping Humans Think Better (Pre-Implementation)

### The problem

The specification is now the bottleneck, not the AI. Developers delegate 60% of work to AI but fully trust only 0-20% without oversight (Anthropic 2026 Trends Report). The quality of the spec determines the quality of the output — yet most developers don't have a structured way to think through tradeoffs, edge cases, and failure modes before coding.

### What the cognitive science says

**The single strongest finding: the pre-mortem.**
Mitchell, Russo, and Pennington (1989) found that "prospective hindsight" — imagining an event has *already occurred* — increases the ability to correctly identify reasons for outcomes by **30%** compared to conventional forecasting. The mechanism: "what could go wrong?" generates possibilities from optimism; "it failed — why?" leverages hindsight bias, making realistic failure scenarios easier to generate.

**Expert vs novice cognition (Klein's RPD model).**
Experts don't analytically compare options — they rapidly pattern-match and generate four outputs simultaneously: expectancies (what will happen), plausible goals, relevant cues, and action scripts. This comes from decades of domain experience. Checklists and structured techniques are most valuable precisely in the areas where intuitive expertise is hardest to develop — namely, architectural decisions with long feedback cycles. You can't pattern-match on architecture if your last architecture decision's consequences took 18 months to materialize.

**The cognitive reframe is the intervention, not the process.**
Across all the research, the pattern is consistent: what works is **changing the question**, not adding more steps.
- Pre-mortem: "what might go wrong?" → "it failed — why?" (+30% risk identification)
- Alternatives Considered: "here's my solution" → "here's why I rejected the others" (forces genuine evaluation)
- Second-order thinking: "what does this do?" → "and then what?" (surfaces cascade effects)

**The Curse of Instructions (Stanford).**
When models are given many simultaneous requirements, adherence to each individual requirement drops significantly. This applies to humans too — a 50-item checklist produces checkbox fatigue. The effective approach is **few, targeted questions** that change the cognitive frame, not exhaustive checklists.

### What the industry says

**The Spec-Driven Development Triangle (Breunig, 2026).**
Spec, code, and tests must stay in sync as a triangle, not a pipeline. The spec is a living document. Key lesson: "Code is cheap; maintenance, support, and security are not."

**"The Specification as Quality Gate" (Zietsman, arXiv 2603.25773).**
Grounding code review in human-authored specifications improved developer adoption of review suggestions by **90.9%** relative to baseline LLM review. Executable specifications convert problems from the complex domain to the complicated domain (Cynefin framework), making them tractable for AI.

**DORA 2026 (1,110 Google engineers).**
Higher AI adoption correlates with *both* higher throughput and higher instability simultaneously. Speed without specification creates fragility.

**Martin Fowler's "On the Loop" model.**
Three models: in the loop (human reviews everything — bottleneck), out of the loop (AI autonomous — risky), **on the loop** (humans design the specifications and harness that guide the agent). The human's job: build and maintain the working loop.

**Cautionary note (Fowler's team).**
Testing three SDD tools (Kiro, spec-kit, Tessl), they found specs were overkill for small tasks, agents still ignored instructions, and verbose upfront specification may contradict "small, iterative steps." Used the German word *Verschlimmbesserung* — making something worse through attempted improvement. The evidence for SDD is enthusiasm, not controlled studies.

### The techniques that work (ranked by evidence strength)

| Technique | Evidence | Mechanism |
|-----------|----------|-----------|
| **Pre-mortem** | 30% improvement in risk identification (controlled study, 1989) | "It failed — why?" reframes from speculative to retrospective |
| **Alternatives Considered** | Google design docs at scale; forces genuine trade-off evaluation | "Why did I reject the others?" prevents anchoring on first idea |
| **Second-order thinking** | Established framework, widely adopted | "And then what?" surfaces cascade effects |
| **Boundary Value Analysis** | Well-established testing methodology | Test outside, on, and inside boundaries systematically |
| **DO-CONFIRM checklists** | Medical evidence (Gawande); anecdotal software evidence | Perform from memory, then verify against list — catches errors of ineptitude |
| **Writing forces clarity** | Unanimous practitioner evidence from Google, Uber, Amazon | Externalizing reasoning surfaces gaps invisible to internal thought |

### Non-Functional Requirements: The Blind Spot

Research shows AI agents **do not handle non-functional requirements unless explicitly told**:

| Finding | Source |
|---------|--------|
| 38% unit test success rate, **0% of PRs mergeable as-is** — failed on test coverage, documentation, code quality | METR Aug 2025 |
| Error handling gaps **2x more common** in AI code; logic issues 75% more common | CodeRabbit (470 PRs, Dec 2025) |
| AI code is **2.2x more verbose**; structural erosion in 80% of trajectories | SlopCodeBench Mar 2026 |
| **37.6% increase in critical vulnerabilities** after 5 iterations | IEEE-ISTAS 2025 |
| **No study found** showing agents spontaneously add monitoring/logging/observability | Research gap |
| Specifying NFRs improves initial quality by **14-30%** | MaintainCoder 2025 |
| But specifying NFRs **does not slow degradation rate** — shifts intercept, not slope | SlopCodeBench |

**Implication for the thinking phase:** Scalability, maintainability, cost, and monitoring concerns must be surfaced by the human and specified in the prompt. If they're not in the spec, they won't be in the code. The pre-mortem naturally surfaces some of these ("it broke in production — why?" may yield "we had no visibility into failures"), but operational readiness needs an explicit prompt for reliability.

**The design choice:** One targeted question ("If this runs in production for a year, what would you wish you'd built in from the start?") rather than four separate questions about scalability, maintainability, cost, and monitoring. The Curse of Instructions (Stanford) shows adherence drops with more simultaneous requirements — one well-framed question surfaces all four concerns without checklist fatigue.

### What a "thinking aid" should do

Based on the evidence, a tool that helps humans think before coding should:

1. **Change the cognitive frame, not add process** — ask 4-5 questions that reframe, not a 50-item checklist
2. **Use the pre-mortem** — "imagine this shipped and broke in production — what went wrong?"
3. **Force alternatives** — "what approach did you reject, and why?" prevents anchoring
4. **Surface second-order effects** — "what does this change make harder or easier later?"
5. **Make edge cases concrete** — "what's the weirdest input this could receive?"
6. **Surface operational readiness** — "if this runs for a year, what would you wish you'd built in?" — because agents don't add monitoring, error handling, or observability unprompted
7. **Be fast** — under 15 minutes, or engineers skip it. Pre-mortems run in 20-30 minutes for teams; solo should be 5-10.
8. **Produce the spec as output** — the thinking process should naturally produce the prompt template inputs (intent, constraints, edge cases, do-not, verification)

### Spec Failure Modes (evidence-backed)

How specs go wrong, ranked by measured impact:

| Failure | Root cause | Measured impact | Prevention |
|---------|-----------|-----------------|------------|
| Too verbose | Including context the agent doesn't need | 13.9-85% degradation (EMNLP 2025) | 300 word cap; every line must change agent behavior |
| Contradictions | Constraint conflicts between sections | Up to 54% improvement from eliminating (Anthropic) | Cross-read all sections before writing |
| Stale references | File/symbol names that are wrong | 0.5-2pp worse than no references (ETH Zurich) | Read actual code, not cached context files |
| Vague constraints | "Good performance" instead of "p99 < 200ms" | 15-17x improvement from precision (Fault Loc.) | Every constraint must be testable |
| Weak verification | "Run tests" instead of specific assertions | 46pp gap between vague and specific (ORACLE-SWE) | Name exact tests + new behavior assertions |
| Untestable NFRs | "Make it maintainable" | No effect on quality metrics (EASE 2025) | Quantify or drop |
| Scope creep | One spec trying to be three changes | Adherence drops with more requirements (Stanford); review effectiveness cliff at 400 lines (multiple studies) | If >4 files modified, >3 concerns, or >400 estimated lines of change, split into multiple specs |

### Code Review: What the Evidence Says

**Bug detection rates are modest.** AI review tools catch 42-48% of real-world runtime bugs (Greptile benchmark, Martian Code Review Bench). Traditional static analyzers catch under 20%. AI review is an improvement, but misses more than half.

**1 general agent beats 4 specialized agents:**
- Microsoft's Azure SRE team built multi-agent specialists, then reversed course. Handoff losses between specialists exceeded specialization gains. Their conclusion: "fewer agents, broader tools."
- Multi-agent review consumes **4-220x more tokens** (UIUC study).
- If all agents use the same model family, errors correlate (ICML 2025: models agree on errors 60% of the time). 4 Claude agents don't give 4 independent opinions — they echo the same blind spots.
- Diffray claims 3x more bugs with multi-agent, but this is vendor self-report without independent replication.

**AI self-review doesn't work:**
- Models **fail to correct errors in their own outputs 64.5% of the time** while successfully correcting identical errors from external sources.
- The same model that wrote the code reviewing it is the worst-case scenario for correlated errors.
- **Spec-grounded review** (reviewing against the specification rather than the code in isolation) improved developer adoption of review suggestions by **90.9%** (SGCR, arXiv 2512.17540).

**Per-change review beats end-of-batch:**
- Review effectiveness drops sharply beyond **400 lines** or **90 minutes** (multiple empirical studies).
- DORA 2025: AI-generated PRs are 51.3% larger — exactly the condition where per-change review has the strongest advantage.

**What to do:**
1. One general review agent, not 4 specialists
2. Review per-change, not at the end
3. Review against the spec — the agent must have the spec to ground its review
4. Use a different model family from the code-writing model if possible
5. Linters and type checkers first — don't burn AI tokens on what deterministic tools catch free
6. Track which review categories developers actually act on — disable the rest

**Sources:**
- [Greptile AI Code Review Benchmarks 2025](https://www.greptile.com/benchmarks)
- [Martian Code Review Bench 2026](https://codereview.withmartian.com/)
- [CodeRabbit Martian Results](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark)
- [Azure SRE Agent Context Engineering](https://techcommunity.microsoft.com/blog/appsonazureblog/context-engineering-lessons-from-building-azure-sre-agent/4481200/)
- [Correlated Errors in LLMs, ICML 2025](https://arxiv.org/abs/2506.07962)
- [SGCR: Spec-Grounded Review, arXiv 2512.17540](https://arxiv.org/abs/2512.17540)
- [The Specification as Quality Gate, arXiv 2603.25773](https://arxiv.org/abs/2603.25773)
- [DORA 2025 Report](https://dora.dev/dora-report-2025/)
- [AI Self-Correction Blind Spot](https://www.augmentedswe.com/p/ai-code-review-security)
- [Google: Modern Code Review Case Study](https://research.google/pubs/modern-code-review-a-case-study-at-google/)


### What it should NOT do

- Exhaustive checklists (checkbox fatigue, Curse of Instructions)
- Impact analysis (the model handles this)
- Architecture documentation for its own sake (ADRs are valuable but separate from pre-implementation thinking)
- Force TDD thinking (net-negative for agentic flows)
- Require team collaboration (solo developer workflow)

---

## Part 9: The Evidence-Based Prompt Template

Based on all research findings, here is what an optimal prompt to a frontier model (Claude Opus 4.7) looks like for a coding task. Every element included has measured evidence supporting its value. Every element excluded was found to be neutral or harmful.

### Example: Adding webhook retry logic to an event system

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

### Why each element is included (with evidence)

| Element | Research justification |
|---------|----------------------|
| **"What and why" (intent, not procedure)** | CGO (ECOOP 2025): goal-oriented framing matches or outperforms procedural step-by-step with fewer tokens. Augment Code: context quality is the #1 prompt factor. |
| **Current behavior (what exists now)** | ORACLE-SWE: reproduction/execution context is the #1 most valuable oracle signal (85.2%). Describing current behavior with a specific location (dispatcher.ts:47) eliminates search time. Stanford (2026): 60-80% of agent tokens go to *locating* code — pinpointing the entry point collapses that cost. |
| **Edge cases (specific behaviors)** | "More Than a Score" (AACL-IJCNLP 2025): explicit I/O specifications and edge-case handling are key drivers of improvement. ORACLE-SWE: execution context (which includes edge case behavior) is the 2nd most valuable signal (57.5%). Edge cases are high-signal tokens, not bloat. |
| **Constraints (specific, technical)** | Fault Localization Study: precise specifications produce 15-17x improvement over vague ones. SWE-bench top performers all provide specific constraints. |
| **Approach (1-3 sentences)** | CGO (ECOOP 2025): goal-oriented framing outperforms procedural. The approach captures the agreed strategy from the thinking conversation — without it, the agent may choose a different path. Google design docs: the "Alternatives Considered" section is unanimously described as the most valuable section because it prevents relitigating settled decisions. |
| **Alternatives rejected** | Google design docs at scale: forces genuine trade-off evaluation by requiring engineers to articulate why other solutions were rejected. Prevents anchoring on first idea and prevents the agent from "helpfully" choosing a rejected approach. ADR research: writing down rejections with reasons is the highest-value part of architecture decision records. |
| **"Do NOT" list** | Practitioner consensus: explicit negation measurably reduces scope creep. Every top SWE-bench agent includes boundary constraints. |
| **Files + symbols (file:function)** | Fault Localization Study (April 2026): file-level context = 54.5% success; file + element-level = 63.4% success — a ~9pp gain from adding function names. 6-10 files is the measured sweet spot. Agentless: hierarchical localization (file → class/function → edit location) is core to all top agents. |
| **Verification with specific assertions** | ORACLE-SWE: reproduction test is the #1 signal (85.2%). The gap between "run tests" (39.4% — regression test oracle) and "these specific behaviors must be tested" (85.2% — reproduction test oracle) is 46pp. Concrete assertions let the model write targeted tests. |
| **Persistence instruction ("keep going")** | OpenAI GPT-4.1 guide: three simple agentic instructions (persistence, tool use, planning) = ~20% improvement on SWE-bench Verified. METR: "don't give up" prompting helps moderately. |
| **Plain, direct language** | Du et al. (2025): formatting has <1% effect on frontier models. EASE 2025: prompt patterns (zero-shot, few-shot, CoT) show no significant difference on code quality. Anthropic: "simple, direct language" recommended. |
| **Short length (~250 words)** | Context Length Alone Hurts (EMNLP 2025): longer context degrades performance even with perfect retrieval. SWE-Pruner: 23-54% token reduction improves results. Softcery: prompt engineering saturates after ~5 hours; the 85% ceiling. Every token must earn its place. |

### Why each omitted element is excluded (with evidence)

| Omitted element | Research justification |
|-----------------|----------------------|
| **"You are an expert senior engineer"** | Literature consensus: role/persona phrasing is negligible on frontier models. Zero measured impact. |
| **Step-by-step reasoning instructions** | METR (Feb 2026): elaborate scaffolding did not reliably beat generic ReAct scaffold (50.7%, not significant). Frontier models do CoT internally. CGO: goals beat procedures. |
| **Impact analysis instructions** | Augment Code: foundation model handles this internally. No benchmark shows separate impact analysis helps. SWE-bench winners don't include it. |
| **Explicit planning instructions ("first plan, then implement")** | OpenAI measured +4% from planning instructions, but Claude already has plan mode built in. External planning instructions for a model that already plans are redundant. CGO shows goals > procedures. |
| **Few-shot examples** | No published ablation found isolating few-shot for agentic coding tasks. METR mentions it as untested hypothesis. Context cost is high, benefit unmeasured. |
| **TDD instructions ("write tests first")** | METR: net-negative for agentic flows. Practitioners (Osmani et al.): model writes tests against its assumptions, not against working code. |
| **Multi-phase decomposition ("first do X, then Y, then Z")** | No benchmark shows multi-phase outperforms single well-crafted prompt + plan mode. METR: elaborate scaffold ≈ generic scaffold. |
| **Formatting ceremony (specific markdown structure)** | Du et al.: <1% variance on frontier models. Irrelevant signal consuming context budget. |
| **Architecture/design discussion** | SlopCodeBench: long context degrades quality. Keep the prompt focused on what to change, not background education. The model can read the code. |
| **Reference to coding standards or style guides** | EASE 2025: prompt patterns don't affect code quality metrics (maintainability, security, reliability). Quality is a function of model training. |

### Disputed elements: deeper analysis

**Edge cases — SHOULD be included (corrected after review)**

Initially omitted due to context-length concerns. This was wrong. The "More Than a Score" study (AACL-IJCNLP 2025) specifically found that explicit I/O specifications and edge-case handling were key drivers of improvement. ORACLE-SWE ranks execution context (which includes edge case behavior) as the 2nd most valuable oracle signal (57.5%). Edge cases are *high-signal* tokens — the constraint isn't "fewer words" but "fewer *low-value* words." Added to the template above.

**Design options exploration — EXCLUDE from implementation prompt, do separately**

CGO (ECOOP 2025): stating objectives directly outperforms exploratory/procedural prompts. SWE-bench top agents all use direct specification, not design exploration. SlopCodeBench (March 2026): longer sessions degrade quality regardless of prompt quality — a design exploration phase extends the session and adds tokens that degrade the subsequent implementation.

However, SWE-bench tasks are well-defined with known solutions. Real-world features often have legitimate design ambiguity. The research can't tell us whether design exploration helps for ambiguous tasks because benchmarks don't test ambiguous tasks.

Recommendation: resolve ambiguity in a *separate, prior conversation* (this is the genuine value of a "think" phase). Then give the coding agent a clear spec in a fresh context. Asking the model to explore options *and* implement in the same session is the worst of both worlds: you pay the context cost of exploration and then implement with a degraded context window.

**Impact analysis — EXCLUDE as separate section, absorb into file list**

Augment Code (65.4% SWE-bench Verified, #1 open-source): the foundation model handles dependency analysis internally. No impact analysis phase in their pipeline. Anthropic's own scaffold: just Bash + Edit, minimal prompt, no impact analysis. They "spent more time optimizing tool interfaces than the overall prompt."

The "Do NOT" list serves the same function more efficiently — instead of asking the model to *analyze* what might be affected (generating tokens about things it won't change), you *tell* it what not to touch. The model reads the files it modifies and discovers dependencies naturally.

The "Files that matter" section already does implicit impact analysis. By naming `types.ts` and `dispatcher.test.ts`, you're saying "these are in the blast radius" without a separate section analyzing why.

Exception: for breaking changes to widely-used interfaces, listing affected callers in the file list has value because the model may not grep exhaustively. In that case, expand the file list:

```
## Files that matter
- src/webhooks/dispatcher.ts — modifying retry logic here
- src/api/routes/events.ts — calls dispatcher.send(), verify still works
- src/api/routes/subscriptions.ts — calls dispatcher.send(), verify still works
```

That's impact analysis compressed into the file list — high-signal, low-token.

## Part 10: Code Review — Full Research

### AI Code Review Tool Benchmarks

| Tool | Catch Rate (Greptile) | Precision (Martian) | Recall (Martian) | False Positives (Greptile) |
|------|----------------------|--------------------|--------------------|---------------------------|
| Greptile | 82% | — | — | 11 per run |
| Bugbot | 58% | — | — | — |
| Copilot | ~55% | — | 36.7% | — |
| CodeRabbit | 44% | 49.2% | 52.5% (highest F1) | 2 per run |
| Graphite | 6% | — | — | — |

AI review catches 42-48% of real-world runtime bugs. Traditional static analyzers catch under 20%. An improvement, but misses more than half.

### Self-Review Doesn't Work (Measured)

- Models **fail to correct errors in their own outputs 64.5%** of the time while successfully correcting identical errors attributed to external sources (across 14 LLMs studied).
- LLMs can repair up to **60% of insecure code from other models** while performing poorly on their own output.
- The "Self-Correction Blind Spot" traces to training data structure: demonstrations rarely include error-correction sequences.
- Source: [AI Self-Correction Blind Spot](https://www.augmentedswe.com/p/ai-code-review-security)

### Correlated Errors in Same-Model Review (Measured)

Kim et al. (arXiv 2506.07962, ICML 2025) studied 350+ LLMs:
- Models agree on errors **60% of the time** when both models err
- Shared architectures and providers drive correlation
- **Larger and more accurate models have MORE correlated errors** — the problem gets worse with better models
- Running 4 Claude agents to review Claude-generated code gives correlated blind spots, not 4 independent opinions
- Source: [Correlated Errors in LLMs, ICML 2025](https://arxiv.org/abs/2506.07962)

### Single Agent vs Multi-Agent for Review

**Microsoft Azure SRE (the strongest production evidence):** Built multi-agent specialists, then reversed course. Handoff losses between agents exceeded specialization gains. Conclusion: "fewer agents, broader tools, and on-demand knowledge replaced brittle routing and rigid boundaries."
- Source: [Azure SRE Agent Context Engineering](https://techcommunity.microsoft.com/blog/appsonazureblog/context-engineering-lessons-from-building-azure-sre-agent/4481200/)

**Multi-agent token cost:** 4-220x more tokens than single-agent (UIUC study).

**Diffray claims:** 87% fewer false positives and 3x more bugs with 10 specialized agents. Vendor self-report, no independent replication.

### Spec-Grounded Review (Measured)

**SGCR (Wang et al., arXiv 2512.17540):** Deployed spec-grounded review in a live industrial environment. Developer adoption of review suggestions improved by **90.9%** relative to baseline LLM review (from 22% to 42% adoption rate).

**The Specification as Quality Gate (Zietsman, arXiv 2603.25773):** Without a spec, AI review is structurally circular — the same model family reviewing code it generated produces correlated errors. With a spec, the review has an external ground truth that breaks the correlation.

### Per-Change vs End-of-Batch Review

- Review effectiveness drops sharply beyond **400 lines** or **90 minutes** (multiple empirical studies)
- Meta found reducing review latency was the single most impactful improvement to their code review process
- DORA 2025: AI-generated PRs are **51.3% larger** — exactly the condition where batch review fails
- Per-change review (small diffs after each commit) keeps reviews under the effectiveness cliff

### DORA 2025: Acceleration Whiplash

The DORA 2025 report (State of AI-Assisted Software Development) is the largest study:
- **90%** AI adoption among software professionals
- **80%+** report enhanced productivity
- But: median PR review time up **441%**, incidents per PR up **242.7%**
- **31% more PRs merging with no review at all**
- Individual output up 21% more tasks, 98% more PRs — but organizational delivery metrics stay flat
- AI acts as an **amplifier**: strengthens high-performing teams, exposes weaknesses in weak teams
- DORA calls this "Acceleration Whiplash": throughput gains at the top, compounding quality costs below
- Source: [DORA 2025 Report](https://dora.dev/dora-report-2025/)

### Automated (Linters) vs AI Review

They catch different things. Layer them, don't choose between them:

| Category | Linters / Type Checkers | AI Review |
|----------|------------------------|-----------|
| Syntax / formatting | Excellent | Redundant — don't waste tokens |
| Type errors | Excellent (with TS/mypy) | Redundant |
| Known vulnerability patterns | Good (SAST) | Overlapping |
| Logic errors | Cannot detect | Moderate (42-48%) |
| Spec compliance | Cannot detect | Good (when spec-grounded) |
| Architectural issues | Cannot detect | Weak without context |
| Business logic errors | Cannot detect | Very weak |
| Consistency across codebase | Limited | Moderate |

**Best practice:** Linters and type checkers as the first pass (free, deterministic, fast). AI review as the second pass for what they can't catch — logic errors, spec compliance, and missed edge cases.

### The Evidence-Backed Review Architecture

Based on all measured findings:

1. **Linters and type checkers first** — deterministic, free, catch style/type/formatting
2. **One general review agent per commit** — not 4 specialists (Microsoft Azure SRE finding)
3. **Spec-grounded** — review against the spec, not in isolation (+90.9% adoption, SGCR)
4. **Fresh context (subagent)** — not self-review by the implementing agent (64.5% self-correction failure)
5. **Per-commit, not end-of-batch** — stay under the 400-line effectiveness cliff
6. **Different model family if possible** — decorrelates errors (ICML 2025)
7. **Track adoption** — disable review categories that developers consistently ignore

---

## Part 11: The Final System Architecture

### What was built (as of May 2026)

Based on all research findings, the TPE pipeline was simplified from 7 skills + 9 agents to 5 skills + 1 agent:

```
/specd:onboard → docs/specs/spec.md (project spec + Spec Index)
                docs/specs/subsystems/{slug}/spec.md (if multi-domain)

/specd:create-spec    → docs/specs/features/{slug}/spec.md (feature/change spec)
                Checked by specd-spec-reviewer agent before presenting

/specd:execute-spec → Reads spec, implements, reviews each commit via
                subagent against the spec, verifies, commits

/specd:review  → Standalone spec-grounded review for ad-hoc use

/specd:bug     → Bug investigation (retained from original pipeline)
```

### What was removed and why

| Removed | Research justification |
|---------|----------------------|
| `/specd:think` (242 lines) | Merged into `/specd:create-spec` — artificial separation dissolved when both need to read code |
| `/specd:plan` (266 lines) | Replaced by spec + plan mode — no benchmark shows multi-phase outperforms a well-crafted prompt |
| `plan-verifier` agent | Replaced by `specd-spec-reviewer` — same function, grounded in the new spec format |
| `code-implementor` agent | execute-spec skill implements directly or uses generic subagents — no need for a dedicated agent |
| `task-handoff-checker` agent | No task decomposition = no handoffs |
| `refactor-opportunities` agent | Augment Code found separate "fix regressions" agents did not help |
| 4 specialized review agents | 1 general reviewer — Microsoft Azure SRE, ICML 2025 correlated errors, 4-220x token waste |

### The spec hierarchy

```
docs/specs/
  spec.md                     ← Project-level (onboard), contains Spec Index
  subsystems/{slug}/spec.md   ← Subsystem specs (onboard, if multi-domain)
  features/{slug}/spec.md     ← Feature/change specs (create-spec skill)
```

The Spec Index in the root spec.md is the discovery mechanism. The create-spec skill reads it to find related specs and updates it after creating/modifying specs.

### Design principles (evidence-mapped)

| Principle | Evidence |
|-----------|----------|
| Small focused changes with fresh context | SlopCodeBench: quality degrades, prompts can't fix it |
| Spec as contract (under 300 words) | Context length degrades performance (EMNLP 2025); SWE-Pruner: less = better |
| Spec-grounded review per commit | SGCR: +90.9% adoption; 400-line effectiveness cliff |
| Review via subagent, not self-review | 64.5% self-correction failure rate; correlated errors (ICML 2025) |
| Linters first, AI review second | Linters catch style/type for free; AI catches logic/compliance |
| Human thinks, AI challenges, AI implements | Pre-mortem +30% risk identification; no benchmark for AI design decisions |
| One agent, not many | Single-agent ≥ multi-agent under equal compute (arXiv 2604.02460); Microsoft Azure SRE |
| Specs are persistent repo documentation | Codified Context study: 24.2% of codebase as context infrastructure, zero failures in 74+ sessions |

---

### The meta-lesson

The prompt above is ~200 words. Your current plan skill is 266 lines of instructions. The research says the 200-word version will perform equivalently or better because:

1. It provides precise context (5 files, not "investigate the codebase")
2. It states goals, not procedures
3. It includes verification as a first-class element
4. It sets explicit boundaries (do NOT)
5. It includes persistence ("keep going")
6. It doesn't bloat the context window with scaffolding the model doesn't need

The value your TPE pipeline adds is in *producing* a prompt like this (clarifying intent, identifying files, setting constraints). The value is not in the 266 lines of instructions about *how* to produce it.

---


### METR
- [Measuring Time Horizon using Claude Code and Codex (Feb 2026)](https://metr.org/notes/2026-02-13-measuring-time-horizon-using-claude-code-and-codex/)
- [Measuring AI Ability to Complete Long Tasks (Mar 2025)](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)
- [Time Horizon 1.1 (Jan 2026)](https://metr.org/blog/2026-1-29-time-horizon-1-1/)
- [Research Update: Algorithmic vs Holistic Evaluation (Aug 2025)](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/)
- [RE-Bench: Evaluating R&D Capabilities (Nov 2024)](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/)
- [HCAST: Human-Calibrated Autonomy Software Tasks (Mar 2025)](https://arxiv.org/abs/2503.17354)
- [Developer Productivity Study (Jul 2025)](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

### Agent Benchmarks & Architecture
- [SWE-agent: Agent-Computer Interfaces, NeurIPS 2024](https://arxiv.org/abs/2405.15793)
- [Agentless: Demystifying LLM-based Software Engineering Agents (Jul 2024)](https://arxiv.org/abs/2407.01489)
- [MetaGPT: Meta Programming for Multi-Agent Framework, ICLR 2024](https://arxiv.org/abs/2308.00352)
- [Augment Code: 11 Prompting Techniques](https://www.augmentcode.com/blog/how-to-build-your-agent-11-prompting-techniques-for-better-ai-agents)
- [Augment Code: #1 Open-Source on SWE-Bench](https://www.augmentcode.com/blog/1-open-source-agent-on-swe-bench-verified-by-combining-claude-3-7-and-o1)
- [Dissecting the SWE-bench Leaderboards (2025)](https://arxiv.org/abs/2506.17208)
- [MASAI: Modular Architecture (2024)](https://arxiv.org/abs/2406.11638)
- [SWE-Search: MCTS for Software Agents (2024)](https://arxiv.org/html/2410.20285v1)
- [OpenHands: Inference-Time Scaling + Critic Model](https://openhands.dev/blog/sota-on-swe-bench-verified-with-inference-time-scaling-and-critic-model)
- [Cognition/Devin SWE-bench Technical Report](https://cognition.ai/blog/swe-bench-technical-report)
- [How Do AI Agents Spend Your Money? (Stanford, 2026)](https://arxiv.org/abs/2604.22750)
- [Single-Agent vs Multi-Agent Under Equal Token Budgets (2026)](https://arxiv.org/abs/2604.02460)
- [Morphllm AI Coding Agent Study (2026)](https://www.morphllm.com/swe-benchmark)

### Context Engineering
- [Effective Context Engineering for AI Agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [ORACLE-SWE: Oracle Information Signals (April 2026)](https://arxiv.org/abs/2604.07789)
- [Fault Localization Context for Program Repair (April 2026)](https://arxiv.org/abs/2604.05481)
- [Context Length Alone Hurts, EMNLP 2025](https://arxiv.org/abs/2510.05381)
- [Context Rot — Chroma, 2025](https://www.trychroma.com/research/context-rot)
- [Lost in the Middle, TACL 2024](https://aclanthology.org/2024.tacl-1.9/)
- [Evaluating AGENTS.md — ETH Zurich (Feb 2026)](https://arxiv.org/abs/2602.11988)
- [Impact of AGENTS.md Files (Jan 2026)](https://arxiv.org/abs/2601.20404)
- [Meta Context Engineering via Agentic Skill Evolution (Feb 2026)](https://arxiv.org/abs/2601.21557)
- [Codified Context: Infrastructure for AI Agents (Feb 2026)](https://arxiv.org/html/2602.20478v1)
- [Context Engineering from Prompts to Multi-Agent Architecture (Mar 2026)](https://arxiv.org/pdf/2603.09619)
- [State of Context Engineering in 2026 (SwirlAI)](https://www.newsletter.swirlai.com/p/state-of-context-engineering-in-2026)

### Harness Engineering (2026)
- [Meta-Harness: End-to-End Optimization of Model Harnesses (Stanford, Mar 2026)](https://arxiv.org/abs/2603.28052)
- [SlopCodeBench: Agent Degradation Over Long-Horizon Tasks (Mar 2026)](https://arxiv.org/html/2603.24755v1)
- [SWE-Pruner: Self-Adaptive Context Pruning (Jan 2026, ACL 2026)](https://arxiv.org/abs/2601.16746)
- [Harness Engineering — Birgitta Böckeler (martinfowler.com, 2026)](https://martinfowler.com/articles/harness-engineering.html)
- [Agent Harness Engineering — Addy Osmani (2026)](https://addyosmani.com/blog/agent-harness-engineering/)
- [Agent Psychometrics (April 2026)](https://arxiv.org/abs/2604.00594)
- [Augment Code on Harness Engineering](https://www.augmentcode.com/guides/harness-engineering-ai-coding-agents)
- [Agent Engineering: Harness Patterns (MorphLLM)](https://www.morphllm.com/agent-engineering)

### Prompt Engineering for Code
- [GPT-4.1 Prompting Guide — OpenAI](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide)
- [Structured CoT Prompting for Code Generation — ACM TOSEM 2025](https://arxiv.org/abs/2305.06599)
- [Chain of Grounded Objectives — ECOOP 2025](https://arxiv.org/abs/2501.13978)
- [EPiC: Evolutionary Prompt Engineering for Code — ACM TOSEM 2025](https://dl.acm.org/doi/10.1145/3805704)
- [Do Prompt Patterns Affect Code Quality? — EASE 2025](https://dl.acm.org/doi/10.1145/3756681.3756938)
- [The Hidden Cost of Readability — Du et al., 2025](https://arxiv.org/html/2508.13666v1)
- [More Than a Score: Prompt Specificity — AACL-IJCNLP 2025](https://arxiv.org/abs/2508.03678)
- [Guidelines to Prompt LLMs for Code Generation (Jan 2026)](https://arxiv.org/abs/2601.13118)
- [Factors Influencing Quality of AI-Generated Code (Mar 2026)](https://arxiv.org/abs/2603.25146)
- [Prompt Engineering Diminishing Returns — Softcery (2026)](https://softcery.com/lab/the-ai-agent-prompt-engineering-trap-diminishing-returns-and-real-solutions)

### Industry Reports & Trend Analysis
- [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/2026-agentic-coding-trends-report)
- [Eight Trends Defining How Software Gets Built — Claude Blog (2026)](https://claude.com/blog/eight-trends-defining-how-software-gets-built-in-2026)
- [10 Lessons for Agentic Coding (May 2026)](https://www.dbreunig.com/2026/05/04/10-lessons-for-agentic-coding.html)
- [Epistemic Grounding in Agentic Coding (April 2026)](https://arxiv.org/abs/2604.21744)

### Vendor Documentation
- [Codex Best Practices — OpenAI](https://developers.openai.com/codex/learn/best-practices)
- [Codex Prompting Guide — OpenAI](https://developers.openai.com/codex/prompting)
- [Claude Code Best Practices — Anthropic](https://code.claude.com/docs/en/best-practices)
- [Claude Prompting Best Practices — Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Verdent SWE-bench Verified Technical Report](https://www.verdent.ai/blog/swe-bench-verified-technical-report)

### Framework Comparisons
- [SWE-bench Pro Leaderboard](https://labs.scale.com/leaderboard/swe_bench_pro_public)
- [SWE-bench Pro Analysis (MorphLLM)](https://www.morphllm.com/swe-bench-pro)
- [Aider LLM Leaderboards](https://aider.chat/docs/leaderboards/)
- [GSD Framework](https://gsd.build/)
- [GSD vs Spec Kit vs OpenSpec vs Taskmaster AI Comparison](https://medium.com/@richardhightower/agentic-coding-gsd-vs-spec-kit-vs-openspec-vs-taskmaster-ai-where-sdd-tools-diverge-0414dcb97e46)
- [GSD/GSTACK Framework Comparison — Pulumi](https://www.pulumi.com/blog/claude-code-orchestration-frameworks/)
- [AI Agentic Programming: A Survey](https://arxiv.org/html/2508.11126v1)
- [Building AI Coding Agents for the Terminal (Mar 2026)](https://arxiv.org/html/2603.05344v1)

### Human Thinking & Specification Quality
- [Pre-mortem: Prospective hindsight increases risk identification by 30% (Mitchell, Russo, Pennington 1989)](https://www.gary-klein.com/premortem)
- [PayPal: Pre-Mortem Working Backwards](https://medium.com/paypal-tech/pre-mortem-technically-working-backwards-1724eafbba02)
- [The Specification as Quality Gate (arXiv 2603.25773)](https://arxiv.org/html/2603.25773)
- [Google Design Docs (Industrial Empathy)](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Software Engineering at Google: Documentation](https://abseil.io/resources/swe-book/html/ch10.html)
- [Martin Fowler: Humans and Agents in Software Engineering Loops](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html)
- [Martin Fowler: Understanding SDD Tools (Kiro, spec-kit, Tessl)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [GitHub Blog: Spec-Driven Development](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Addy Osmani: How to Write a Good Spec for AI Agents](https://addyosmani.com/blog/good-spec/)
- [Addy Osmani: My LLM Coding Workflow Going into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [10 Lessons for Agentic Coding (Breunig, May 2026)](https://www.dbreunig.com/2026/05/04/10-lessons-for-agentic-coding.html)
- [The Spec-Driven Development Triangle (Breunig)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html)
- [Scaling via Writing Things Down: RFCs (Pragmatic Engineer)](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- [Martin Fowler: Architecture Decision Records](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
- [RAND: Assessing the Value of Structured Analytic Techniques](https://www.rand.org/pubs/research_reports/RR1408.html)
- [Doteveryone: Consequence Scanning](https://doteveryone.org.uk/project/consequence-scanning/)
- [Booking.com AI Adoption with DX](https://getdx.com/customers/booking-drives-ai-adoption-with-dx/)
- [DORA 2026 Report / Anthropic Trends Analysis](https://resources.anthropic.com/2026-agentic-coding-trends-report)
- [MIT Missing Semester 2026: Agentic Coding](https://missing.csail.mit.edu/2026/agentic-coding/)
- [Gary Klein: Recognition-Primed Decision Making](https://commoncog.com/putting-mental-models-to-practice/)
- [CodeScene: Agentic AI Coding Best Practice Patterns](https://codescene.com/blog/agentic-ai-coding-best-practice-patterns-for-speed-with-quality)

### Code Review
- [Greptile AI Code Review Benchmarks 2025](https://www.greptile.com/benchmarks)
- [Martian Code Review Bench 2026](https://codereview.withmartian.com/)
- [CodeRabbit Martian Results](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark)
- [CodeAnt Benchmark Summary](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests)
- [Diffray: Single vs Multi-Agent AI Code Review](https://diffray.ai/blog/single-agent-vs-multi-agent-ai/)
- [Azure SRE Agent Context Engineering](https://techcommunity.microsoft.com/blog/appsonazureblog/context-engineering-lessons-from-building-azure-sre-agent/4481200/)
- [Correlated Errors in LLMs, ICML 2025](https://arxiv.org/abs/2506.07962)
- [SGCR: Spec-Grounded Review, arXiv 2512.17540](https://arxiv.org/abs/2512.17540)
- [The Specification as Quality Gate, arXiv 2603.25773](https://arxiv.org/abs/2603.25773)
- [AI Self-Correction Blind Spot](https://www.augmentedswe.com/p/ai-code-review-security)
- [Google: Modern Code Review Case Study](https://research.google/pubs/modern-code-review-a-case-study-at-google/)
- [DORA 2025 Report](https://dora.dev/dora-report-2025/)
- [DORA 2025 Key Takeaways (Faros)](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025)
- [Meta Code Review Time](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/)
- [Review Effectiveness Beyond 400 Lines](https://link.springer.com/article/10.1007/s10664-023-10401-z)

### Non-Functional Requirements & AI Code Quality
- [Quality Assurance of LLM-generated Code — ISO 25010 analysis (arXiv 2511.10271)](https://arxiv.org/html/2511.10271v2)
- [Beyond Functional Correctness: Design Issues in Large-Scale AI Projects (arXiv 2604.06373)](https://arxiv.org/html/2604.06373v1)
- [METR: Many SWE-bench-Passing PRs Would Not Be Merged (Mar 2026)](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)
- [CodeRabbit: AI vs Human Code Generation Report (Dec 2025)](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)
- [MaintainCoder: Structured NFR-aware prompts +14-30% (arXiv 2503.24260)](https://arxiv.org/html/2503.24260v3)
- [Security Degradation in Iterative AI Code Generation — 37.6% increase (IEEE-ISTAS 2025)](https://arxiv.org/html/2506.11022v1)
- [CodeScene: Echoes of AI — EMSE 2025](https://arxiv.org/html/2507.00788v2)
- [Qodo: State of AI Code Quality 2025](https://www.qodo.ai/reports/state-of-ai-code-quality/)
- [GitClear: AI Copilot Code Quality 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)
