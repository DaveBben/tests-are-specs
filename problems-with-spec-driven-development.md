# Problems with Spec-Driven Development

A plain list of the documented problems with spec-driven development (SDD) for
AI-assisted / agentic coding. Drawn from hands-on trials, practitioner
sentiment, and the (thin) research. Sources noted per item.


---

## Overhead & ceremony

1. **Reviewing the spec takes longer than reviewing the code.**
   Generated specs are long. One trial produced 2,577 lines of markdown for 689
   lines of code and 3.5 hours of review; the iterative approach did the same
   work ~10x faster. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html), [Marmelab](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html))

2. **Reviewing prose is worse than reviewing code.**
   You end up hunting for mistakes hidden in verbose, expert-sounding markdown
   instead of reading the thing that actually runs. ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

3. **Over-decomposition.**
   A one-line bugfix balloons into multiple user stories and acceptance criteria
   (one tool turned a single bug into 4 stories / 16 criteria). ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

4. **Token cost, and a model floor.**
   The ceremony burns tokens, and the flow often can't be handed to a cheap
   model — a mid-tier model is the effective floor.

## It's waterfall again

5. **Freezing design up front kills iteration speed.**
   SDD pulls you back toward big-design-first, which is the opposite of fast
   agile loops. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html))

6. **You can't spec what you don't understand yet.**
   Understanding emerges from building. Freeze the spec first and you freeze
   your confusion into a contract. ([r/programming, "too confused to write the spec"](https://publish.obsidian.md/deontologician/Posts/Spec-driven+development+doesn't+work+if+you're+too+confused+to+write+the+spec))

7. **Poor fit for legacy / maintenance work.**
   Nearly every framework assumes a greenfield repo and whole-team adoption —
   neither holds for most real backlogs. ([r/ExperiencedDevs, non-greenfield SDD thread](https://www.reddit.com/r/ExperiencedDevs/))

## The spec rots

8. **Specs go stale — and stale specs are worse than stale docs.**
   Agents consume the spec as context and execute it confidently even when it no
   longer matches reality, without flagging the mismatch. ([Augment Code](https://www.augmentcode.com/blog/what-spec-driven-development-gets-wrong))

9. **The spec becomes a second codebase to maintain.**
   Now the spec and the code can disagree, and you have two sources of truth
   instead of one. ([Isoform](https://isoform.ai/blog/the-limits-of-spec-driven-development), r/ExperiencedDevs)

10. **Context pollution.**
    Spec files crowd the agent's context window and can degrade, not improve,
    what it produces.

## It doesn't deliver the rigor it promises

11. **Agents ignore the spec anyway.**
    They skip parts, misinterpret it, or mark tasks done without doing them —
    e.g. marking "verify implementation" complete without writing a single test.
    ([Marmelab](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back.html), r/ClaudeCode)

12. **False sense of rigor.**
    Elaborate templates give the *feeling* of control while agents ignore the
    templates — false control, not control. ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

13. **"Illusion of work."**
    The flow generates a lot of text and conversation that feels productive; you
    surface hours later having talked a lot and shipped little. ([github/spec-kit discussion #1784](https://github.com/github/spec-kit/discussions/1784))

14. **Specs are non-deterministic where code is deterministic.**
    You, your teammate, and the model each read the same spec differently. ([r/ChatGPTCoding, "technical masturbation" thread](https://www.reddit.com/r/ChatGPTCoding/))

15. **Worst of both worlds: MDD + LLMs.**
    Spec-as-source risks combining Model-Driven Development's inflexibility with
    the LLM's non-determinism. ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

## The evidence isn't there

16. **No credible independent evidence it improves outcomes.**
    The pro-SDD numbers are vendor marketing (Kiro, GitHub Spec Kit) with no
    methodology; the academic work is nascent and mostly uncited. The one
    rigorous nearby RCT (METR) found devs *slower* with AI while feeling faster —
    so treat every "3-4x" claim with suspicion. ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/))

---

## The verification signal is hollow

17. **A green spec-check proves conformance, not correctness.**
    A passing test only shows the code matches the spec. If the spec is wrong,
    the agent faithfully ships the wrong thing and it sails through review. ([truefoundry](https://www.truefoundry.com/blog/spec-driven-development-ai-agents))

18. **No code-review gate — SDD reviews the plan, not the code.**
    Iteration stops at the planning phase; design flaws and spec-to-code
    infidelity reach implementation with no adversarial check on the actual
    code. ([ranthebuilder.cloud](https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/))

19. **The ceremony gives no security guarantee.**
    Heavy planning still missed authorization design — tools "trusted
    caller-supplied context" and never flagged it during planning. It reads as
    thorough while leaving real holes unmentioned. ([ranthebuilder.cloud](https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/))

## The spec is corrupted at authoring time (not just later)

20. **Spec generators fabricate requirements you never gave.**
    The tool assumes context and adds rationale for decisions you didn't make —
    injecting phantom requirements and "faux context" into the thing you've
    declared the source of truth. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html), [ranthebuilder.cloud](https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/))

21. **Requirements mutate between pipeline stages.**
    Each artifact (spec → plan → tasks) is an LLM generating from the last LLM's
    output, so decisions silently change: Decision A in the requirements becomes
    a different Decision B by the tasks — before any code exists. ([r/ClaudeCode, thread 1ok1qxf](https://www.reddit.com/r/ClaudeCode/comments/1ok1qxf/))

## Tooling mechanics work against you

22. **Whole-document regeneration destroys diff-based review.**
    Change direction and the tool regenerates the entire document — no diff of
    just what changed — so every iteration forces a full re-review from scratch. ([ranthebuilder.cloud](https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/))

23. **The spec is the highest-leverage, least-governed file.**
    Every downstream agent decision keys off the spec, so one edit silently
    redirects the whole build — yet spec edits rarely get the review rigor a code
    change would. ([truefoundry](https://www.truefoundry.com/blog/spec-driven-development-ai-agents))

## The format drops the most valuable context

24. **Specs record the "what" but never the "why."**
    They can't capture the assumptions, tradeoffs, and rejected alternatives —
    exactly the context the next maintainer or agent needs most. Even a fresh,
    accurate spec has this hole. ([Isoform](https://isoform.ai/blog/the-limits-of-spec-driven-development), [dev.to](https://dev.to/chrisywz/the-limits-of-spec-driven-development-3b16))

25. **Specs have near-zero value after the feature ships.**
    A user story is a point-in-time steering tool you rarely revisit once
    complete — so much of it is a throwaway artifact whose upkeep is pure waste. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html))

## It constrains the model's problem-solving

26. **Over-structuring pigeonholes the model away from a better solution.**
    Locking in an early spec makes the agent force-fit that design instead of
    finding the better approach it would otherwise reach — some report it even
    introduces hallucinations. ([r/ClaudeCode, thread 1ok1qxf](https://www.reddit.com/r/ClaudeCode/comments/1ok1qxf/), [Isoform](https://isoform.ai/blog/the-limits-of-spec-driven-development))

27. **Prompt-scaffolding rots as models improve.**
    The elaborate templates encode today's model weaknesses; as foundation
    models get better, that scaffolding goes stale and the framework starts
    fighting the model rather than helping it. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html))

## The method itself is ill-defined

28. **The functional-vs-technical boundary is unmanageable.**
    People can't reliably tell when to stay at requirements level and when to
    drop into implementation detail — and the profession has no track record of
    doing this well. The tools assume a separation humans can't maintain. ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

29. **"Spec" has suffered semantic diffusion.**
    The word has decayed into a synonym for "detailed prompt," so "spec-driven
    development" no longer names one coherent method — teams think they've aligned
    while meaning different things. ([martinfowler.com](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html))

---

## Sharper angles on problems already listed

- **Rubber-stamping the AI-written spec = vibe coding with extra steps.** Skip a
  critical read of the generated spec and you've added all the ceremony and kept
  none of the benefit. (Sharpens #2.) ([truefoundry](https://www.truefoundry.com/blog/spec-driven-development-ai-agents))
- **The planning phase actively manufactures scope creep.** Not just
  over-decomposing a fixed scope (#3) — it inflates scope: "you end up with a 2k
  tasks.md" and must constantly cut the agent's "nice to haves." ([r/ClaudeCode, thread 1ok1qxf](https://www.reddit.com/r/ClaudeCode/comments/1ok1qxf/))
- **~1-page comprehension ceiling.** Agents reliably follow only about a page of
  spec; beyond that they drift regardless of context-window size — a
  comprehension limit, not just a token limit (#10). ([r/ChatGPTCoding, thread 1o6j1yr](https://www.reddit.com/r/ChatGPTCoding/comments/1o6j1yr/))
- **Undefined bug-fix protocol.** When generated code has an obvious bug, the
  process gives no guidance on whether to patch the code or re-run the spec. ([Scott Logic](https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html))

---

## A note on evidence quality

The hands-on write-ups (Scott Logic, ranthebuilder, Marmelab, Fowler) are the
strongest sources — real trials, not vendor pitches. Two caveats: **truefoundry**
and **Augment Code** are vendors selling adjacent tooling, so treat their framing
as motivated even where the observation is sound. The **Reddit** items are
single-practitioner anecdotes — real signal, but unmeasured. No new independent
empirical study turned up beyond what item 16 already covers: the evidence
*against* heavy SDD is hands-on but small-N, and the evidence *for* it is mostly
marketing.
