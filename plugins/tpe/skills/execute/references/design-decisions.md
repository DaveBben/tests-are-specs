# Design Decisions

## Why a Single Agent Per Task

The research is clear — multi-agent systems underperform single-agent
systems due to hallucination propagation, context saturation from
coordination tokens, and information loss during handoffs (Comprehensive
Agent Framework Evaluation). The task JSON already contains everything
the agent needs: `acceptanceCriteria` (the spec), `reference` (the
pattern), `atRiskTests` (regression targets), `doNot` (boundaries). One
agent reads all of this and implements.

## Why Opus Orchestrates, Sonnet Implements

The orchestrator (execute skill) runs on Opus — it makes sequencing
decisions, interprets review findings, and handles error recovery. The
code-implementor agent runs on Sonnet — it works within bounded task
constraints where the decisions are already made. CCA research showed a
weaker model with strong scaffolding (task JSON, reference patterns,
explicit boundaries) outperforms a stronger model with weaker scaffolding
on SWE-Bench-Pro. The task JSON is the strong scaffolding that makes
Sonnet viable. Specialized routing (cheap models for bounded execution,
frontier for coordination) offers better cost-performance than uniform
model selection.

## Why No Separate Test-Writing Phase

Agent-generated tests don't improve outcomes — agents write observational
debugging rather than real assertions, and increasing test-writing volume
has no effect on resolution rates (Rethinking the Value of
Agent-Generated Tests). The `acceptanceCriteria` and
`verificationCommand` are the contract. The `atRiskTests` field tells
the agent which existing tests to protect.

## Why 6-Task Context Pause Gate

The Focus Agent research found compression every 10-15 tool calls
achieves optimal token savings. At ~5-10 tool calls per task, 6 tasks
puts the orchestrator at 30-60 tool calls — well into the range where
context degradation is measurable. Shorter intervals (e.g. 4) add
unnecessary human interruption for small plans. Longer intervals
(e.g. 10) risk significant fade-out of plan constraints and
accumulation of stale observation tokens.

## Why Sequential Task Execution

Tasks within a slice often have `blockedBy` dependencies — task 3
consumes a type created by task 2. Even for unblocked tasks, parallel
execution means two agents editing the same codebase simultaneously,
creating merge conflicts and state inconsistency. The error
amplification tax from multi-agent coordination (17.2× for independent
agents, 4.4× even with centralization) outweighs the wall-clock savings
of parallelism. Sequential execution with fast feedback (inline code review
per task) catches problems early before they compound.

## Why a Fast Path for Small Plans

ADaPT research showed +27-33 pp improvement from reactive decomposition
— trying the task whole first, decomposing only on failure. For plans
with ≤2 tasks and <200 total lines, the per-task overhead (dispatch,
commit, review, status update) is disproportionate to the actual work.
The fast path tries a single-agent approach first, falling back to
task-by-task only if the agent STOPs or exceeds size limits.

## Why Complexity Tiers

Not all tasks need the same agent configuration. CCA research
demonstrated that scaffolding quality matters more than model capability
— a 1-file task with a clear reference pattern doesn't need frontier
model reasoning. Haiku with strong task JSON scaffolding handles simple
pattern-following. Sonnet handles standard multi-file work. Complex
tasks (4 files, interface changes) get higher turn limits and additional
context (brainstorm.md, full interface files) because the ~60 pp
performance collapse from single-file to multi-file tasks is primarily
a context problem, not a model capability problem.
