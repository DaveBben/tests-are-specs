# Ingesting an existing brief or PRD

The interview is not the only door. When the user already has a written brief, PRD, ticket, design doc, or a page of answers, do not re-interview from scratch — that is the friction that makes people quit before the payoff. Read the document, map what it settles, and interview only the gaps. This is a fast path *into* shaping, not a way around it: the risk lenses and the approach comparison still run.

## When to reach for this

The user hands you, or points you at, a document that already carries some of the thinking: "here's the PRD", "I wrote up what I want in `notes.md`", a pasted spec from another tool, a filled-in answer list. If they only have a sentence, run the normal interview; there is nothing to ingest.

## The moves

1. **Read the whole thing first.** Before a single question, read the document end to end. You are looking for what it decides, what it assumes, and what it leaves open — not for a place to start asking.

2. **Map it onto the shaping structure, don't transcribe it.** For each part of the reasoning — the ask, the current-state facts, the drivers, the risks, the candidate approaches, the decisions — find what the document supplies and restate it in spec terms. A PRD's prose becomes a *Driver*; a stated constraint becomes a fact under *What's true today*; a chosen approach becomes a *Decision to sign off*. Copying the document's words into the spec is not shaping; extracting its decisions is.

3. **Separate what it settles from what you inferred.** A thing the document states is a decision. A thing you filled in to make the document make sense is an **assumption** — mark it as one, and never launder an inference into a fact. This is the discipline that keeps a confident-sounding brief from smuggling unexamined choices into a signed contract. "The PRD implies X" is an assumption to confirm, not a decision to record.

4. **Reflect the extraction back once, in a batch.** Show the user your read of the document: "here is what I take you to have **decided**, what I am **assuming** to fill the gaps, and what the document leaves **open**." This one confirmation pass replaces the one-question-at-a-time interview for everything the document already answers — it is cheaper precisely because the answers exist. Correct the mistakes, promote or kill the assumptions, then move on.

5. **Interview only the residual gaps.** Now run the normal interview, but only over what the document did not settle — highest-uncertainty questions first, one at a time, reflecting each answer back. Skip every question the brief already answers. A ten-question interview may collapse to two.

## What a brief does NOT let you skip

- **The risk lenses.** A brief rarely works all five (failure & scale, operational readiness, trust boundary, implied work, better way). Work the ones it skipped; each surfaced risk still gets HANDLE / ACCEPT / OUT-OF-SCOPE. A PRD that lists features has almost never worked the trust boundary.
- **The approach comparison.** A brief that asserts one approach with no alternatives is a decision to *ratify*, not a reason to skip weighing it. Name the real alternatives, lay out the tradeoff, and put the choice — the brief's or a better one — to the human. If the brief's approach is right, say why; if the comparison changes it, that is the interview earning its keep.
- **The one-decision gate.** A big PRD often bundles several decisions with distinct owners or lifecycles. Split it into sequenced children the same as any other over-large ask; the brief does not buy an exemption.
- **Grounding on the project spec.** The brief's claims still bind to the project spec's `INV-NNN` and shared contracts. A brief that contradicts an invariant routes up to `grounding-specs`, same as any conflict.

## Altitude

A PRD or design doc may name files, symbols, or paste code — that is the author's HOW, useful context but not the spec's content. Ingest the *intent* behind it; leave the file manifest and the typed code to the implementer. The spec you compose stays WHAT + WHEN even when the source document didn't.
