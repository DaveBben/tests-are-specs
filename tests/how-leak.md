# Scenario: a source document full of file paths and code

**Skill under test:** writing-specs (WHAT/WHEN-not-HOW altitude), and `shaping-specs/references/ingesting-briefs.md`
**Failure form:** shaping (the spec comes out with HOW in it) → tests a positive recipe, not a prohibition.

## Setup

The user hands the agent a PRD-style doc for a "webhook retry" feature. The doc is written by an engineer and is thick with HOW: it names `retry_worker.py`, a `RetryQueue` class, exact SQL, and a code snippet for the backoff. It also carries the genuine WHAT (retries must be bounded, ordering preserved, no duplicate delivery) mixed in.

## The prompt

"Here's the spec doc — turn it into the formal spec." (The doc is the input; the agent should ingest it.)

## Control expectation

A no-skill agent tends to carry the doc's file names, class names, and code straight into the spec, producing a `contract.md` that reads like a plan — pinning the implementer's HOW and coupling the spec to a design that may change.

## Pass signals (skill working)

- The composed `spec.md` / `detail/contract.md` state WHAT and WHEN: bounded retries, preserved ordering, exactly-once delivery, with success criteria — and **no** file manifest, class names, or typed code block.
- The agent extracts the *intent* behind the doc's HOW rather than transcribing it; the concrete tech becomes an observable requirement, not a named symbol.
- The one allowed exception — the verification commands — may be concrete; nothing else is.
- Guarantee words ("no duplicate delivery") trace to an FR whose check is as strong as the verb.

## Fail signals

- File paths, class/function names, or code fenced blocks in the spec (outside *Verification approach & commands*).
- Requirements written as implementation steps ("call `RetryQueue.enqueue`") instead of observable behavior.
- The doc's assumptions copied in as facts without being marked or confirmed.
