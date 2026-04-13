# Design Decisions

## Why a Single Agent Per Task

The research is clear — multi-agent systems underperform single-agent
systems due to hallucination propagation, context saturation from
coordination tokens, and information loss during handoffs (Comprehensive
Agent Framework Evaluation). The task JSON already contains everything
the agent needs: `acceptanceCriteria` (the spec), `reference` (the
pattern), `atRiskTests` (regression targets), `doNot` (boundaries). One
agent reads all of this and implements.

## Why No Separate Test-Writing Phase

Agent-generated tests don't improve outcomes — agents write observational
debugging rather than real assertions, and increasing test-writing volume
has no effect on resolution rates (Rethinking the Value of
Agent-Generated Tests). The `acceptanceCriteria` and
`verificationCommand` are the contract. The `atRiskTests` field tells
the agent which existing tests to protect.
