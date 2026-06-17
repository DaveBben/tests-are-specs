# Writing style — readable specs and docs

Read this when you write the prose sections of a spec or a generated doc. In a spec that means Why, Summary, Current behavior, Approach, Things to consider, and the Edge-case descriptions. The goal is one linear read, with no backtracking.

**The principle.** Every time the reader holds a clause open while reading ahead, you spend their working memory. Close each loop as fast as you can. Every rule below is one way to close a loop sooner. Users are busy and have low-working memory

This is measured, not stylistic. Readability tracks the cognitive load a reader actually feels. Spend that load only where precision demands it.

---

## Level 1 — the sentence

- **One idea per sentence.** Aim for ~15–20 words. Two claims become two sentences. A sentence that needs an "and … , since … , which …" chain is two or three sentences wearing one coat.
- **Lead with the actor and the action.** Concrete subject, active verb, object: "PHP drops every field past the 1000th," not "truncation of fields beyond the limit occurs." Prefer verbs to noun-forms — "decide," not "make a decision."
- **Conclusion first, then support.** The first sentence states the result. The rest explains it. A reader who stops after sentence one still has the answer.
- **Concrete, familiar words.** Plain words decode automatically and free capacity for meaning. Keep a genuinely load-bearing term — a real API name, a number, a constraint — and define it once on first use.
- **Tighten.** Omit needless words. Put the word that carries the point at the end of the sentence, where it lands and is remembered.
- **Put it in positive form.** Say what is, not what isn't. "The parser rejects empty rows," not "the parser does not accept rows that aren't populated." A negation makes the reader compute "not X" and hold it; the positive form lands directly. A scope-boundary constraint is the deliberate exception — a prohibition (what must NOT change) belongs in the contract's Constraints, stated plainly.

## Level 2 — across sentences (don't make the reader look backward)

- **One condition per sentence.** Replace "if X, unless Y, but when Z" with separate statements. Each caveat or exception gets its own sentence. Never inject a qualifier mid-clause with dashes or parentheses.
- **Don't embed a clause inside another.** Keep each subject next to its verb. Put background before the main clause or after it, never inside it.
- **Repeat the noun.** Avoid "it," "the former," "this," and "as mentioned above" — each forces the reader to search backward. Say the noun again.
- **Make each sentence self-contained.** Understanding one should not depend on perfectly remembering the last three.
- **One path at a time.** Don't fan out parallel options or stacked caveats inside a single thought.

## Level 3 — the page (offload memory onto layout)

- **Chunk.** Short paragraphs (2–3 sentences), labeled sections, lists. Each piece gets processed and filed away before the next.
- **Make structure visible.** Numbered steps for sequences, bold for key terms, consistent formatting, white space. Visual structure moves organizing work off the reader and onto the page.
- **Keep parallel items parallel.** Co-ordinate ideas take the same grammatical shape — "condition: expected behavior" for every edge case, a verb-first phrase for every constraint. The reader learns the pattern once, then reads the rest on autopilot instead of re-parsing each item.

---

## What this does NOT touch

The implementation contract — Constraints, Files that matter, Verification — stays dense, identifier-rich, and deliberately redundant. There, packing identifiers and numbers is load-bearing; readability is for the prose. Keep all the precision everywhere (names, numbers, `file:line`). This is about sentence *shape* and page *layout*, never about dropping detail.

## The "if wrong → what changes" pattern

A spec deliberately pairs each load-bearing assumption with its failure path. Keep the pattern — defended decisions are the point — but render it readably. This is just Level 2 applied: state the assumption as one sentence, the consequence as the next.

- Hard to read: "Per-article marking is worth ~2,000 extra POSTs/night for the narrowest crash-loss window (accepted by you); if wrong → switch to end-of-run batch, which reintroduces the PHP max_input_vars=1000 chunking constraint."
- Readable: "Per-article marking costs ~2,000 extra POSTs a night. You accepted that for the smaller crash-loss window. If it's wrong, we switch to an end-of-run batch — and that brings back the PHP 1000-field chunking limit."

Same facts, same precision, a fraction of the working-memory load.
