# tests — behavioral pressure scenarios

Not part of the portable plugin. These are the control-first pressure scenarios the maintainer method in [`docs/testing-skill-changes.md`](../docs/testing-skill-changes.md) demands: inputs that put a skill's discipline under the exact pressure that breaks it, so a skill edit is tested against behavior instead of read for clarity.

## What is here, and what is not

Each file is a **scenario**: a setup, the pressure the user applies, what a no-skill control tends to do, and the pass/fail signals to watch for. That is the durable, checkable artifact. Two files support running them: [`harness.md`](harness.md) is the reproducible control-vs-skill protocol (why there is no shell script, and two ways to dispatch the two arms), and [`RESULTS.md`](RESULTS.md) records the runs we have actually done, with genuine observed output — never asserted or fabricated.

A behavioral *result* is a transcript of a real run, not a claim. This directory ships the scenarios plus the runs we can honestly stand behind; it does not ship a pass count for runs nobody made. Claiming a skill "passes" without running it would be exactly the faked-done the audit hunts. Run the scenario to earn the claim, and record it in `RESULTS.md`.

## How to run one (the method, condensed)

1. **Control first.** Run the scenario against a fresh agent that does **not** have the skill. If it already does the right thing, the wording has nothing to fix — don't credit the skill for behavior the base model already has.
2. **Then with the skill loaded.** Same scenario, same pressure.
3. **Repeat 5+ times each.** These behaviors are probabilistic; one run proves nothing. Read every transcript, not just the last line.
4. **Score against the file's pass/fail signals.** A skill earns its wording only when it moves behavior across the control on repeated runs.

The scenarios target the discipline-critical behaviors — the ones where an agent under pressure fakes the gate, fakes the test, or drops the thinking. Those are where wording has to hold and where a regression is worst.

| Scenario | Skill under test | The pressure |
|---|---|---|
| [`gate-integrity.md`](gate-integrity.md) | writing-specs | user pushes the agent to approve for them |
| [`faked-done.md`](faked-done.md) | implementing-specs | a slice won't go green; ship it anyway |
| [`how-leak.md`](how-leak.md) | writing-specs | a source doc full of file paths and code |
| [`interview-shortcut.md`](interview-shortcut.md) | shaping-specs | impatient user says skip the questions |
| [`brief-ingestion.md`](brief-ingestion.md) | shaping-specs | a confident PRD with unstated assumptions |
| [`invariant-break.md`](invariant-break.md) | implementing-specs | green is one broken invariant away |
