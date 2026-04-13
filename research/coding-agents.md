# What actually works in AI coding agents: an empirical synthesis

**Context engineering, not scaffolding complexity, is the highest-leverage intervention for improving LLM-based coding agents.** Across 25+ papers from October 2025 through April 2026, the evidence converges on a counterintuitive set of findings: agent-generated tests rarely improve resolution rates, multi-agent architectures lose their edge as models improve, and verbose instructions actively degrade performance. The interventions that work — hierarchical context management, targeted dependency information, concise specifications — share a common thread: they increase the density of decision-relevant information per token. This report synthesizes specific empirical results from peer-reviewed papers and arxiv preprints to answer six questions about agentic software development.

---

## Q1: Focused context helps, but most context files hurt

The evidence on context engineering splits sharply between *what* context is provided and *how*. Developer-written AGENTS.md files reduced median agent runtime by **28.64%** and output token consumption by **16.58%** across 124 pull requests in 10 repositories, without degrading task completion quality (2601.20404). But a larger controlled study from ETH Zurich found that LLM-generated context files **reduced resolution rates by 0.5–3%** while increasing inference costs by over **20%** across SWE-bench Lite and a new 138-instance AGENTbench benchmark (2602.11988). Even developer-written files produced only a **marginal ~4% improvement** on AGENTbench. The reconciliation is straightforward: **minimal, focused context improves efficiency; verbose, kitchen-sink context degrades performance.**

The strongest positive evidence comes from hierarchical context architectures. The Confucius Code Agent's hierarchical working memory with adaptive context compression delivered a **+6.6 percentage point improvement** on a 100-instance SWE-Bench-Pro subset (48.6% vs. 42.0% for Claude Sonnet 4), and its persistent note-taking reduced token usage by over **10%** while adding **+1.4%** to solve rates (2512.10398). The Agentic Context Engineering framework achieved **+10.6%** improvement on agent benchmarks by treating context as evolving "playbooks" rather than static files (2510.04618). A detailed case study of a three-tier context architecture — hot memory (~660 lines, always loaded), specialized agents (~9,300 lines, loaded per-task), and cold memory (~16,250 lines, retrieved on demand) — demonstrated that context infrastructure can scale to **108,000-line codebases**, though it required ~26,000 lines of context infrastructure itself (2602.20478).

**Tiered structures outperform flat files at scale.** The three-tier system explicitly manages context window budget by keeping the always-loaded constitution concise while embedding substantial domain knowledge (>50% of content) in specialized agents loaded only when triggered (2602.20478). This mirrors CCA's approach of adaptive compression that creates structured summaries preserving goals, decisions, and error traces while maintaining a rolling window of recent messages (2512.10398). ContextBench found that all evaluated LLMs achieved block-level F1 scores **below 0.45** on context retrieval, with a consistent "consolidation gap" where agents accessed relevant code during exploration but retained only **50–70%** of it in final context (2602.05892). This evidence gap between explored and utilized context underscores why structured retrieval matters.

Two failure modes of context engineering deserve attention. **Brevity bias** causes iterative optimization to collapse context toward short, generic prompts that lose domain-specific insights (2510.04618). **Context collapse** occurs when iterative rewriting erodes details over time (2510.04618). Both suggest that context files need principled curation, not automated generation.

**Actionable rules:**
- Provide minimal, focused context files with build commands, architecture overview, and conventions — omit exhaustive detail
- Use hierarchical/tiered context structures for projects exceeding ~10K LOC
- Never auto-generate context files with LLMs for production use
- Keep always-loaded context under ~700 lines; load domain knowledge on demand
- Measure both efficiency (tokens, runtime) and resolution rate — context that speeds agents up may not improve correctness

---

## Q2: Agent-generated tests are a habit, not a driver of resolution

The evidence on testing is the most counterintuitive finding in this literature. A study of six frontier LLMs on SWE-bench Verified found that **GPT-5.2 achieves 71.8% resolution while writing tests in only 0.6% of tasks**, whereas Claude-opus-4.5 achieves 74.4% while writing tests in 83% of tasks — a gap of just **2.6 percentage points** despite radically different testing behaviors (2602.07900). Prompt interventions that encouraged or discouraged test writing changed outcomes in only **16.8%** of 500 tasks; **83.2% of tasks produced identical results** regardless of testing policy. The authors conclude that agent-written tests function as a "reproduced habit" — a model-dependent process style rather than a causal driver of success.

The TDAD paper reveals a critical nuance: **procedural TDD instructions without targeted context actively increase regressions.** On 100 SWE-bench Verified instances with Qwen3-Coder 30B, vanilla agents produced a test-level regression rate of **6.08%**, but adding TDD prompting (write tests first, then implement) raised regressions to **9.94%** — a **42% increase** in pass-to-pass test failures (2603.17973). The mechanism is twofold: verbose procedural prompts consume context tokens in smaller models, and TDD-prompted agents attempt more ambitious fixes without knowing which existing tests to protect.

However, **TDD combined with targeted test context dramatically reduces regressions.** When GraphRAG-based impact analysis provided agents with the specific tests affected by their changes, regression rates dropped to **1.82%** — a **72% reduction** from vanilla and an **81% reduction** from TDD-only (2603.17973). The auto-improvement loop demonstrated even more dramatic gains: resolution rose from **12% to 60%** with **0% regression** on a 10-instance subset, and simplifying the instruction file from 107 to 20 lines alone **quadrupled resolution from 12% to 50%**.

The practical implication is that **context about what tests exist matters far more than instructions to write tests.** Tests serve agents primarily as observational feedback channels — print statements and runtime observations appear more often than assertion-based checks in agent test code (2602.07900). When agents do write useful tests, it is because they need to observe system behavior, not because the tests themselves validate correctness.

**Actionable rules:**
- Do not mandate test-writing as a universal policy — it helps some models and hurts others
- Provide agents with dependency-mapped information about which existing tests their changes affect (GraphRAG or similar)
- For regression prevention, targeted test context is the intervention; procedural TDD prompting is counterproductive for smaller models
- Measure regression rate alongside resolution rate — a 31% resolver with 1.82% regression rate is more valuable than a 31% resolver with 9.94% regression
- Keep testing instructions concise; verbose testing procedures consume context budget without proportional benefit

---

## Q3: Agent performance collapses as task scope expands

The relationship between task scope and success rate is the most robustly documented finding across this literature. The same frontier models that resolve **74.4%** of SWE-bench Verified bug fixes achieve only **11.0%** on FeatureBench's feature-level tasks (~790 lines of code, multiple files) — a **6–7× difficulty increase** (2602.10975). On SWE-EVO's software evolution tasks (average 21 files modified, 610 lines edited, 51 functions touched), GPT-5 with OpenHands drops to **21%** versus **65%** on SWE-bench Verified (2512.18470). SWE-Bench Pro's enterprise tasks produce best-case resolution of **43.6%** (2509.16941). The pattern is consistent across every benchmark expansion.

| Benchmark | Task scope | Best model | Resolution |
|-----------|-----------|------------|------------|
| SWE-bench Verified | Single-issue bug fixes, 1–2 files | Claude Opus 4.5 | 74.4% |
| SWE-Bench Pro | Enterprise multi-file tasks | Claude Sonnet 4.5 | 43.6% |
| SWE-EVO | Multi-PR evolution, avg 21 files | GPT-5.4 (OpenHands) | 25% |
| FeatureBench | Feature-level, ~790 LoC | GPT-5.1-Codex | 12.5% |

**Specifications and interface definitions measurably help.** FeatureBench's ablation removing function signatures and call-path annotations from prompts produced significant performance drops, and providing ground-truth unit tests alongside task descriptions significantly improved both success rates and pass rates (2602.10975). Yet SWE-EVO found that providing additional PR/issue context beyond release notes yielded only **modest gains** — agents still struggled even with "detailed and fully specified context" (2512.18470). This suggests **specifications help with understanding but do not solve the execution bottleneck** of multi-file coordination.

Failure mode analysis reveals the mechanism. On FeatureBench, **NameError is the dominant failure** — agents focus on local edits without re-establishing cross-file references (2602.10975). On SWE-EVO, strong models fail primarily on **instruction following (>60% of failures)**, misinterpreting long, nuanced release notes, while weaker models fail on syntax and tool use (2512.18470). The complexity gradient is not just about more code — it is about coordinating changes across dependency boundaries.

**Task decomposition provides the largest measured improvements.** The ACONIC framework's formal complexity-guided decomposition delivered **10–40 percentage point improvements** on combinatorial and database tasks (2510.07772). ADaPT's recursive as-needed decomposition achieved **27–33 percentage point improvements** across ALFWorld, WebShop, and TextCraft (2311.05772). Neither was tested on SWE-bench-family benchmarks, but the magnitude of gains suggests decomposition would be high-impact for multi-file coding tasks. SWE-PolyBench confirmed a **consistent decline in performance as task complexity increases**, with mixed class-and-function modifications producing the worst results at **8–15% pass rate** versus 25–40% for single-class changes (2504.08703).

**Actionable rules:**
- Expect a ~60 percentage point drop in resolution when moving from single-issue to feature-level tasks
- Provide explicit interface specifications (function signatures, call paths, expected behaviors) for complex tasks
- Decompose multi-file features into bounded subtasks with clear interface boundaries
- For evolution-scale tasks, decompose by release-note item rather than presenting the full change set
- Cross-file dependency resolution is the primary bottleneck — prioritize context about import paths and module interfaces

---

## Q4: Single agents beat multi-agent systems under controlled conditions

The scaffolding question has the clearest empirical resolution in recent literature. A Stanford study controlling for thinking token budgets across three model families found that **single-agent systems consistently match or outperform multi-agent systems** on multi-hop reasoning (2604.02460). The theoretical argument invokes the Data Processing Inequality: multi-agent decomposition introduces communication bottlenecks that cause information loss. A broader evaluation confirmed that **MAS consumes 4–220× more input tokens** than single-agent systems, and even with perfect context reuse, MAS still requires **2–12× more tokens** (2505.18286). The key finding: "MAS historically outperforms SAS, but loses its edge as LLMs grow more capable."

A comprehensive evaluation of seven agent frameworks on code-centric tasks quantified the overhead. AgentOrchestra (hierarchical multi-agent) achieved the highest completeness score (**0.86**) but at **$370 total cost** versus GPTswarm's **$16** — a **22× cost premium** (2511.00872). AgentOrchestra averaged **40+ steps per task** with ~45% correction attempt rates, with planning and reflection stages consuming the majority of resources. Single-agent frameworks like OpenHands demonstrated more stable, convergent behavior.

Yet scaffolding design still matters enormously — just not multi-agent orchestration per se. The Confucius Code Agent demonstrated that a **weaker model with strong scaffolding (Claude Sonnet 4.5 + CCA at 52.7%) outperformed a stronger model with weaker scaffolding (Claude Opus 4.5 + Anthropic's scaffold at 52.0%)** on SWE-Bench-Pro (2512.10398). The gains came from context management, not coordination — hierarchical working memory, adaptive compression, and meta-agent-optimized tool use. ContextBench reinforced this: sophisticated retrieval scaffolding yielded **only marginal gains** over a simple baseline using basic shell commands, with all agents achieving block-level F1 below **0.45** (2602.05892).

The OpenDev architecture paper provides the practitioner synthesis: **context engineering is the central design constraint**, more important than model selection in many cases (2603.05344). Their evolution from simple to sophisticated scaffolding was driven by context pressure, not coordination needs — adaptive compaction, lazy tool discovery, dual-memory architecture, and event-driven reminders to counter instruction fade-out.

**Actionable rules:**
- Default to single-agent architectures; add multi-agent coordination only for tasks where single agents demonstrably fail
- Invest scaffolding effort in context management (compression, retrieval, memory hierarchy) rather than agent coordination
- Expect 4–20× token overhead for multi-agent systems with minimal resolution gains on current frontier models
- As models improve, simplify architectures — the benefits of multi-agent coordination are diminishing
- Specialized model routing (cheap models for planning, frontier for execution) offers better cost-performance than multi-agent coordination

---

## Q5: Verbose instructions are actively harmful

The instruction density question has the most actionable evidence. A foundational study demonstrated that **context length alone degrades LLM performance by 13.9–85%** even with perfect retrieval — the degradation persists even when irrelevant tokens are replaced with whitespace or completely masked (2510.05381). At 30,000 tokens, Llama-3.1-8B accuracy dropped **24.2%** despite retrieving evidence with 97% exact match. The degradation is not about distraction; it is an intrinsic property of processing long sequences.

The TDAD paper provides the most striking coding-specific evidence: **reducing a SKILL.md instruction file from 107 to 20 lines quadrupled resolution from 12% to 50%** for a 35B-parameter model (2603.17973). Additional procedural text neither helped nor hurt in isolation; what mattered was eliminating context consumed by instructions that could instead hold problem-relevant information. The ETH Zurich study confirmed this at scale: context files increased trajectory length by an average of **3.92 additional tool steps** and inflated inference costs by **over 20%**, while reducing resolution rates by **0.5–3%** (2602.11988).

The OpenDev paper quantifies the mechanism: a single `read_file` tool output consumes **2,000–3,000 tokens**, and test-runner output can generate thousands of lines (2603.05344). "Left unchecked, verbose results dominate the context window within a few iterations, crowding out the user query and system instructions." Their solution — type-specific compression of tool outputs to **50–200 characters** — addresses the right bottleneck. The paper also documents **instruction fade-out**, where early system instructions lose influence as the context fills, requiring event-driven reminders to maintain behavioral compliance.

Average prompt length grew **nearly fourfold** between 2024 and 2025, from ~1,500 to over 6,000 tokens based on OpenRouter data spanning over 100 trillion tokens (2604.07502). A controlled experiment found that aggressive compression of log formats actually **increased total session cost by 67%** despite reducing input tokens by 17%, because the model spent more reasoning tokens decoding compressed formats (2604.07502). The concept of **semantic density** — the ratio of task-relevant meaning to total tokens — captures the right optimization target. Maximizing semantic density outperforms both verbose instructions and aggressively compressed formats.

**Actionable rules:**
- Keep instruction files under 20–30 lines for models under 70B parameters; scale up cautiously for frontier models
- Compress tool outputs aggressively (50–200 characters per call) using type-specific summarization
- Optimize for semantic density, not raw token count — every token should carry decision-relevant information
- Implement instruction reminders at context boundaries to counter fade-out
- Never add procedural instructions that could instead be embedded in tool behavior

---

## Q6: Resolution rate alone is a dangerously incomplete metric

The regression problem is severe and underreported. SWE-CI evaluated 18 models on 100 code maintenance tasks spanning average **233 days** and **71 consecutive commits** each, finding that **most models achieve a zero-regression rate below 0.25** — meaning they break existing tests in over 75% of maintenance attempts (2603.03823). Only the two Claude Opus models exceeded **0.50** zero-regression rate. Twelve of 20 models showed positive correlation between iteration count and regression rate, suggesting models resort to increasingly risky trial-and-error on harder problems.

The TDAD paper quantifies the gap between resolution and safety: vanilla agents achieved **31% resolution** with a **6.08% test-level regression rate** — 562 pass-to-pass test failures across 100 instances (2603.17973). TDD prompting raised resolution to the same 31% but increased regressions to **9.94%** (799 failures). GraphRAG+TDD maintained **29% resolution** with only **1.82% regression** (155 failures). Critically, **no patches simultaneously resolved the target issue AND introduced regressions** — resolution and regression appear to be independent dimensions, not trade-offs.

SWE-EVO introduced the **Fix Rate** metric, which rewards partial progress on failing tests while assigning a score of zero to any instance where pass-to-pass tests break (2512.18470). This strict regression penalty reveals meaningful differences between models that appear equivalent under binary resolved/unresolved scoring. SWE-Bench Pro enforces a "No Regressions" condition requiring patches to pass all pre-existing tests (2509.16941). The CLEAR framework found that agent performance drops from **60% on single runs to 25% with 8-run consistency**, and agents optimized for accuracy alone cost **4.4–10.8× more** than cost-aware alternatives (2511.14136).

A study of 24,014 merged agentic pull requests found that agent-authored code actually **survives longer** in production than human code, with a hazard ratio of **0.842** (16% lower modification hazard, p < 0.001) (2601.16809). However, agent code shows modestly elevated corrective maintenance rates (**26.3% vs. 23.0%**), suggesting it is somewhat more likely to need bug fixes even if it persists longer (2601.17581). Agentic PRs are smaller and more localized than human PRs, with the largest structural difference in commit count (Cliff's δ = **0.54**, large effect size).

**Actionable rules:**
- Always measure regression rate (pass-to-pass test failures) alongside resolution rate
- Adopt Fix Rate or similar metrics that penalize regressions strictly — resolution rate alone overstates production readiness
- Run the full existing test suite before and after agent patches, not just target tests
- Expect >75% of maintenance attempts to introduce regressions with current models (except Claude Opus)
- Use graph-based impact analysis to identify which tests agent changes are likely to affect

---

## What actually works: interventions ranked by measured impact

The following ranks interventions by the magnitude of empirical evidence supporting them, from largest measured effect to smallest. Each entry specifies the intervention, the measured impact, and the supporting paper(s).

**1. Task decomposition into bounded subtasks** — **+10 to +40 percentage points** on resolution rate. Formal complexity-guided decomposition (ACONIC, 2510.07772) and recursive as-needed decomposition (ADaPT, 2311.05772) both demonstrate large gains. Not yet validated on SWE-bench-family benchmarks, but the magnitude is consistent across multiple task domains. This is the highest-ceiling intervention.

**2. Providing interface specifications and dependency context** — **~60 percentage point gap** between specified and unspecified complex tasks. FeatureBench ablations show significant drops without function signatures and call paths (2602.10975). GraphRAG-based test dependency information reduced regressions by **72%** (2603.17973). SWE-EVO shows even fully specified context is insufficient for evolution tasks, but specifications are necessary if not sufficient (2512.18470).

**3. Hierarchical context management** — **+6.6 percentage points** on SWE-Bench-Pro from CCA's adaptive compression and working memory (2512.10398). **+10.6%** from ACE's evolving playbooks (2510.04618). Three-tier architecture scales to 108K LOC codebases (2602.20478). This is the most consistently beneficial scaffolding investment.

**4. Instruction brevity** — **4× resolution improvement** (12% → 50%) from reducing instruction file from 107 to 20 lines (2603.17973). Context files increase costs by **>20%** while reducing resolution by **0.5–3%** (2602.11988). Context length alone degrades performance **13.9–85%** (2510.05381). Keeping instructions minimal is a zero-cost improvement.

**5. Targeted test context over procedural TDD** — **72% reduction in regressions** (6.08% → 1.82%) from providing graph-based test dependency information versus procedural TDD instructions that increase regressions by 42% (2603.17973). Context about *which* tests to check outperforms instructions about *how* to test.

**6. Single-agent over multi-agent architectures** — Equivalent or superior performance at **4–220× lower token cost** (2604.02460, 2505.18286). **22× cost reduction** versus hierarchical multi-agent with comparable quality (2511.00872). The benefit of simplification grows as models improve.

**7. Developer-written (not LLM-generated) context files** — **28.64% faster runtime** and **16.58% fewer tokens** (2601.20404). **+4% average resolution** on AGENTbench (2602.11988). Modest but consistent, and zero-cost once written. LLM-generated alternatives are counterproductive.

**8. Tool output compression** — Reducing tool outputs to **50–200 characters** prevents context window crowding (2603.05344). Quantified indirectly through the context length degradation findings (2510.05381), but no isolated ablation on resolution rate. High practical value as a default engineering practice.

**Where the evidence is insufficient.** No paper directly compares optimal context window utilization thresholds for coding tasks specifically — the cited "40% utilization" threshold traces to a practitioner blog post, not controlled research (2604.07502). Cross-task context reuse has a benchmark (SWE-ContextBench, 2602.08316) but no published agent results. The interaction between task decomposition and specific SWE-bench-family performance remains untested. And the regression problem lacks standardized measurement — SWE-CI, TDAD, SWE-EVO, and SWE-Bench Pro each define regression differently, making cross-paper comparison difficult. The field urgently needs a unified regression metric adopted across benchmarks.

---
Additional Papers and summaries:

# Paper Summaries

---

# TDAD: Test-Driven Agentic Development — Reducing Code Regressions in AI Coding Agents via Graph-Based Impact Analysis

TDAD tackles one of the more insidious failure modes of AI coding agents: silently breaking existing functionality while fixing a reported issue. The system builds a dependency graph between source code and tests, then delivers a targeted impact-analysis report to the agent as a lightweight static skill file it can query at runtime. On SWE-bench Verified, this reduced regression rates by 70% — from 6.08% down to 1.82% — and simultaneously lifted issue-resolution rates from 24% to 32%. The evaluations ran across two open-weight models (Qwen3-Coder 30B and Qwen3.5-35B-A3B), establishing that the benefit generalizes across model families. The core insight is that agents correct themselves when they have concrete, targeted information about which tests are at risk, not just generic instructions to "be careful."

The most counterintuitive finding is that adding test-driven development instructions *without* the accompanying targeted context actually made things worse — increasing regressions from ~6% to nearly 10% — suggesting that generic procedural guidance can actively mislead agents when it lacks specificity. The evaluation is limited to two open-weight models on a single benchmark, so generalizability to proprietary frontier models or different code domains remains an open question.

---

# Building Effective AI Coding Agents for the Terminal — Scaffolding, Harness, Context Engineering, and Lessons Learned

This paper presents OPENDEV, an open-source, terminal-native CLI coding agent implemented in Rust. Its architecture centers on a compound AI system with workload-specialized model routing and a dual-agent design that separates planning from execution. The terminal-native approach is argued to be a natural fit for software development because it operates directly in the environment where developers manage version control, run builds, and deploy. To combat the known problem of instruction degradation over long agent contexts, OPENDEV uses event-driven system reminders that re-surface critical instructions dynamically. It also features adaptive context compaction that progressively summarizes older observations, lazy tool discovery to reduce upfront context consumption, and automated memory accumulation that persists project-specific knowledge across sessions.

The paper is explicitly marked as a work-in-progress with continuous updates planned, meaning its claims and architecture may not yet reflect a stable, evaluated system. No quantitative benchmarks comparing OPENDEV to other agents (e.g., Claude Code, Aider, or SWE-agent) are presented in the abstract, making it difficult to assess performance claims empirically.

---

# On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents

This study provides the first empirical measurement of how AGENTS.md files — repository-level markdown files containing instructions for AI coding agents — affect agent efficiency in practice. Analyzing 10 GitHub repositories across 124 pull requests, the researchers compared agent runs with and without AGENTS.md files present, using agents including Codex and Claude Code. The presence of AGENTS.md files produced a 28.64% reduction in median runtime and a 16.58% reduction in output token consumption, while task completion rates were maintained. This means that well-crafted repository-level configuration files make agents faster and cheaper without sacrificing the quality of results — a meaningful practical finding for teams deploying agents in CI/CD or automated code-review pipelines.

The study examined only 10 repositories and 124 pull requests, which is a modest sample that may not generalize across the full diversity of codebases, languages, and task types. The research measures efficiency (time, tokens) but does not deeply analyze the quality or correctness of agent outputs beyond completion rates, and the AGENTS.md files used were presumably as-found in the wild — purpose-written, high-quality files might yield even larger improvements.

---

# Rethinking the Value of Agent-Generated Tests for LLM-Based Software Engineering Agents

This paper challenges the intuitive assumption that when AI coding agents write tests during problem-solving, those tests meaningfully improve outcomes. By analyzing agent trajectories from six strong language models on SWE-bench Verified, the researchers found that resolved and unresolved tasks show similar test-writing frequencies — meaning whether the agent wrote tests had little correlation with success. More revealingly, the tests agents wrote predominantly used print statements for observational feedback rather than assertions, functioning more as informal debugging scaffolding than genuine regression guards. A controlled prompt-intervention study with four models confirmed the causality: increasing or decreasing agents' test-writing volume did not significantly change final task resolution rates. The conclusion is stark — current agent testing practices primarily reshape the process and inflate computational costs without delivering proportional improvements in outcomes.

The finding that test writing doesn't improve outcomes is specific to the current generation of agent behavior on SWE-bench Verified; it does not mean tests are valueless in principle, but rather that agents are not yet writing tests well enough (e.g., with proper assertions) to benefit from them. The study uses prompt interventions as a proxy for causal manipulation, which is an indirect method that may not fully separate the effect of test writing from other behavioral changes induced by the same prompts.

---

# Codified Context: Infrastructure for AI Agents in a Complex Codebase

This paper tackles a fundamental problem with LLM-based coding assistants: they have no memory between sessions, causing incoherence and inconsistency as a codebase grows. The author, building a substantial C# distributed system solo, designed and evaluated a three-part "codified context" architecture: (1) a "hot-memory constitution" — a live document encoding conventions, retrieval hooks, and orchestration protocols always in the agent's context window; (2) a fleet of 19 specialized domain-expert agents, each scoped to a subsystem; and (3) a "cold-memory" knowledge base of 34 specification documents retrieved on demand. The system was evaluated across 283 development sessions with four observational case studies demonstrating how the architecture prevented agent failures and maintained cross-session consistency. The paper's central argument is that the real bottleneck for AI in complex codebases is not model capability but context infrastructure — the scaffolding that tells agents what they need to know, when they need to know it.

The study is explicitly single-developer and single-project, making it unknown whether the architecture generalizes to teams, other languages, or simpler domains. Most critically, specification staleness emerges as a silent failure mode — because agents trust documentation absolutely, outdated spec documents cause them to generate code that conflicts with recent refactors.

---

# FeatureBench: Benchmarking Agentic Coding for Complex Feature Development

FeatureBench introduces a benchmark specifically designed to measure AI agent performance on end-to-end feature development — as opposed to the isolated bug fixes that dominate existing benchmarks like SWE-bench. Constructed automatically by analyzing unit test dependencies across 24 open-source repositories, it yields 200 curated evaluation tasks backed by 3,825 executable environments. The headline result is striking: Claude 4.5 Opus achieves a 74.4% resolution rate on SWE-bench but drops to just 11.0% on FeatureBench — a 63-point collapse — revealing a massive gap between agents' ability to fix isolated bugs versus developing coherent multi-file features. The paper diagnoses three persistent failure modes: models struggle with cross-file dependency resolution, exhibit "lazy reasoning" (hallucinating interfaces rather than reading files), and consume over one million input tokens even at this 11% success rate, representing extremely low token efficiency.

The LLM-based classification step that identifies "tested objects" operates at only 81.03% precision, meaning a non-trivial fraction of task boundaries may be mis-drawn in ways that are hard to audit. The performance gap between SWE-bench and FeatureBench partly reflects fundamentally different task types rather than a clean measurement of agent capability regression, so comparisons across benchmarks must be interpreted carefully.

---

# SWE-EVO: Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios

SWE-EVO addresses what existing benchmarks miss by focusing on "software evolution" — the sustained, long-horizon changes a codebase undergoes across releases. Tasks are derived from the release notes of seven mature open-source Python projects, producing 48 carefully validated instances where each task requires multi-step modifications spanning an average of 21 files, validated against test suites averaging 874 tests per instance. The performance gap is stark: the best agent tested (GPT-5.4 with OpenHands) achieves only 25% on SWE-EVO versus 72.80% for GPT-5.2 on SWE-Bench Verified — a ~47-point drop. A particularly insightful failure analysis shows that stronger models fail primarily on "Instruction Following" (60%+ of failures), while weaker models fail on incorrect implementation — suggesting the ceiling for top models is semantic comprehension of specifications, not code mechanics.

The benchmark covers only Python and uses only release notes as the specification format, excluding common real-world evolution drivers like security patches or dependency updates. With just 48 instances, it has limited statistical power for fine-grained model comparisons, and the Fix Rate metric treats all tests as equally weighted regardless of complexity, which may misrepresent partial progress on structurally harder sub-features.

---

# A Comprehensive Empirical Evaluation of Agent Frameworks on Code-Centric Software Engineering Tasks

This study benchmarks seven general-purpose agent frameworks (including OpenHands, AgentOrchestra, GPTswarm, and SE-Agent) across three representative software engineering tasks: software development, vulnerability detection, and program repair. On software development, OpenHands achieves the best quality score (0.47), while GPTswarm leads vulnerability detection at 77% accuracy. A striking cross-cutting finding is that single-agent systems consistently outperform multi-agent systems across all three tasks, despite taking shorter execution paths — attributed to inter-agent hallucination propagation, context window saturation from excessive coordination tokens, and information loss during state handoffs. On cost, software development is the most expensive task overall ($544.90 total under DeepSeek pricing), while GPTswarm is the most economical at $16.29 across all tasks.

All seven frameworks are evaluated exclusively with DeepSeek-v3.1 as the backend LLM, so results may not generalize to other model families with different reasoning styles or context capacities. High correction rates — often read as inefficiency — can actually signal effective self-monitoring rather than poor performance, meaning efficiency metrics require careful interpretation rather than face-value ranking.

---

# How AI Coding Agents Modify Code: A Large-Scale Study of GitHub Pull Requests

Using the MSR 2026 AIDev dataset, this study compares 24,014 merged agent-generated pull requests (440,295 commits) against 5,081 merged human pull requests (23,242 commits) drawn from open-source GitHub repositories. Agent-generated PRs show a large effect-size difference in commit organization (Cliff's delta = 0.54), meaning AI agents consolidate work into far fewer commits and touch fewer files per PR than humans. On description-to-code alignment measured using CodeBERT and GraphCodeBERT semantic embeddings, both human and agent PRs score high, but agent-generated descriptions are slightly more consistent with their actual diffs. Agent tools are not monolithic in behavior: Claude Code and OpenAI Codex produce broader multi-file changes, while GitHub Copilot makes highly localized edits — implying that review strategies cannot be one-size-fits-all.

The dataset covers only open-source GitHub projects, so findings may not extend to private industrial codebases where agent usage patterns and review practices differ. Structural metrics like commit count capture scope but say nothing about code correctness, security, or maintainability — the study explicitly does not measure whether AI-generated changes are higher or lower quality than human ones.

---

# Confucius Code Agent: An Open-Sourced AI Software Engineer at Industrial Scale

The Confucius Code Agent (CCA) is an open-source software engineering agent framework designed to bridge the gap between lightweight research prototypes and the demands of large, real-world codebases. Its architecture organizes around three design perspectives: Agent Experience (what the LLM receives, kept compressed and structured), User Experience (rich instrumented traces for human oversight), and Developer Experience (observability tooling for builders). Key technical contributions include hierarchical memory with adaptive context compression (triggering an "Architect Agent" near token limits), persistent cross-session note-taking that records both solutions and failure modes, and a "meta-agent" that automates the build-test-improve loop for agent configuration itself. On SWE-Bench-Pro (731 real-world tasks), CCA achieves 59% Resolve@1 using GPT-5.2. The central empirical claim is that agent scaffolding — not just raw model capability — is a primary determinant of performance: a weaker model with strong scaffolding can outperform a stronger model with naive scaffolding.

Several ablations were conducted on only 100-example subsets, limiting statistical confidence of those specific comparisons. Performance degrades meaningfully when tasks require modifying five or more files simultaneously, attributed to "cumulative localization uncertainty" — a limitation that matters for large refactoring or architectural tasks.

---

# Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?

This paper delivers a counterintuitive empirical result: context files like AGENTS.md — strongly encouraged by agent developers — tend to *reduce* task success rates compared to providing no repository context at all, while simultaneously inflating inference costs by over 20%. Using both LLM-generated context files on SWE-bench tasks and human-written context files from real repositories, the researchers tested multiple coding agents and found that both machine-generated and developer-authored context files caused agents to engage in broader, costlier exploration behaviors — more file traversal, more test execution — without commensurate accuracy gains. The core culprit is that context files introduce "unnecessary requirements" that make tasks harder rather than easier, suggesting that the intuitive practice of giving agents more context can actively work against them.

The finding is not that all context is harmful — the problem is *poorly scoped* context that adds noise or imposes extra requirements. Repositories that already have AGENTS.md files may attract harder or more complex issues, potentially confounding the comparison. The implication for practitioners is precise: context files should be ruthlessly trimmed to only truly essential, task-relevant information.

---

# ContextBench: A Benchmark for Context Retrieval in Coding Agents

ContextBench introduces a process-oriented evaluation framework — not just judging final outputs, but examining the intermediate steps of how coding agents retrieve and use context during issue resolution. Spanning 1,136 tasks across 66 repositories and 8 programming languages with human-annotated reference contexts, the benchmark reveals three structural weaknesses: sophisticated scaffolding yields only marginal gains in raw context retrieval; LLMs systematically prioritize recall over precision (finding more than they need rather than exactly what they need); and there is a significant gap between what context agents *explore* and what they actually *use* when generating solutions.

The recall-over-precision bias means agents are less likely to miss critical context but routinely over-retrieve, compounding inference costs and potentially introducing noise. The benchmark is process-level, which adds richness but also complexity in how teams should weight intermediate metrics versus end-to-end task success.

---

# SWE Context Bench: A Benchmark for Context Learning in Coding

SWE Context Bench evaluates whether coding agents can *reuse context across related problems* — a capability critical for real-world software work where issues and PRs reference each other. Built on top of SWE-Bench data, it contains 1,100 base tasks with 376 related tasks derived from real dependency and reference relationships on GitHub, spanning 51 repositories and 9 programming languages. The central finding is that correctly selected, summarized prior context improves resolution accuracy and substantially cuts runtime and token cost — especially on harder tasks. However, the benefit flips negative when context is unfiltered or poorly selected, making retrieval quality and representation format (compact summaries vs. full trajectories) the decisive factors.

The heavy qualification — that benefits only materialize with *correctly selected* context — is itself a significant limitation, since the benchmark effectively presupposes a solved retrieval problem in its oracle condition. The dependency between GitHub issues is mined automatically, which may introduce noisy or spurious relationships between "related" tasks.

---

# Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models

This paper introduces ACE (Agentic Context Engineering), a framework that treats agent context — system prompts, memory, instructions — as *living documents* that should evolve and improve through experience rather than static configurations. ACE addresses two failure modes in standard LLM pipelines: brevity bias (models compress rich domain knowledge into lossy short summaries) and context collapse (information degrades through repeated revisions). Through a modular cycle of generation, reflection, and curation, ACE accumulates and refines operational strategies like a "playbook" that grows with experience. Results are substantial: +10.6% on agent benchmarks, +8.6% on finance-specific tasks, with smaller open-source models matching production-level agents on the AppWorld leaderboard — all without requiring labeled supervision, relying instead on natural execution feedback. Accepted to ICLR 2026.

The gains are achieved without labeled supervision, but this means the framework relies on execution feedback signals that may be noisy or misleading in domains where success is hard to measure automatically. The risk of accumulated context becoming its own form of cruft — strategies that worked once but generalize poorly — is an open question the framework must guard against.

---

# Context Length Alone Hurts LLM Performance Despite Perfect Retrieval

This paper challenges the implicit assumption that RAG and retrieval systems fully solve the long-context problem for LLMs. The authors demonstrate that even under *ideal* retrieval conditions — where models have access to all relevant information and irrelevant tokens are masked or replaced with whitespace — model performance still degrades substantially as input length grows. Across 5 models and three task types (math, QA, and coding), degradation ranged from 13.9% to 85%. This means the problem is not just about retrieval quality or distractor noise — the sheer volume of tokens in context is itself harmful, even when those tokens are neutral. The proposed mitigation is elegantly simple: prompt the model to recite the retrieved evidence before attempting to solve the problem, yielding up to 4% gains on GPT-4o. Accepted at EMNLP 2025 Findings.

The "perfect retrieval" condition is a laboratory construct — in practice, retrieval is never perfect, so real-world degradation is likely worse than what this paper measures. The findings vary widely across models (13.9% to 85% degradation range), suggesting some architectures handle length scaling significantly better, though the paper does not fully explain what architectural factors drive that variance.
