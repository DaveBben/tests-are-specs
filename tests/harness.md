# The runner: control vs. skill, reproducibly

The scenarios in this directory are behavioral tests of an LLM under pressure, so the "runner" is a dispatch protocol, not a shell script — there is no deterministic binary to assert against. This file is the protocol. Anyone can reproduce a run, and [`RESULTS.md`](RESULTS.md) records the ones we have actually run, with their genuine output.

## Why not a shell script

The system under test is a model's judgment ("does it cross the gate under social pressure?"). You cannot unit-test that; you observe it, repeatedly, and compare two arms. A script that pretended to "pass" a scenario would be the exact faked-done the audit hunts (see the README). So the harness ships the method and honest transcripts, not a green checkmark.

## The two arms

For each scenario, run two agents in **fresh, isolated contexts** — nothing about spec-monkey loaded except what each arm is given:

- **Control arm.** The scenario's setup and pressure, and *no skill guidance*. This is the base model's default behavior.
- **Skill arm.** The same setup and pressure, prefixed with the relevant skill's binding wording (the SKILL.md section under test — the gate stance for `gate-integrity`, the WHAT/WHEN-not-HOW rule for `how-leak`, and so on).

The skill earns its wording only when the skill arm moves behavior across the control, on repeated runs. If the control already does the right thing, the wording has nothing to fix — cut it (this is the control-first rule from `docs/testing-skill-changes.md`).

## Two ways to dispatch

Both give each arm a clean context. Use whichever your setup has.

### A. A subagent / Task tool (what RESULTS.md used)

Dispatch each arm as a fresh general-purpose subagent. Give the control arm the scenario; give the skill arm the same scenario with the skill wording pasted in as its instructions. Keep the model identical across the two arms so the only variable is the skill. Read the full returned transcript against the scenario's pass/fail signals.

For an escalating scenario (e.g. `gate-integrity`'s four turns), a single dispatch can list the turns in order and ask the agent to answer each — a single-dispatch approximation of a multi-turn session. It is cheaper and reproducible; a true multi-turn run (below) is stronger and worth doing before you trust a wording change.

### B. Headless `claude -p` (a true multi-turn run)

```bash
# control arm — no skill
claude -p "$(cat tests/gate-integrity.md)  ... <the setup + turn 1>"
# then continue the session for each escalating turn

# skill arm — prepend the skill wording
claude -p "You operate under writing-specs. <paste SKILL.md step 6 + gate stance>
<the same setup + turn 1>"
```

Drive the turns one message at a time so state accumulates the way a real session does. Capture each arm's transcript.

## Scoring

1. Read every transcript in full, not just the last line — a right final answer reached by crossing the gate mid-way still fails.
2. Score against the scenario file's **Pass signals** and **Fail signals**.
3. Repeat 5+ times per arm. These behaviors are probabilistic; one run is a demonstration, not evidence for a wording change. Record what you actually saw.
4. Record genuine output only. If you did not run it, it has no row in `RESULTS.md`.
