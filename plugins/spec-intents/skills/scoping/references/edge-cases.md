# Edge-case discovery

Edge-case discovery is mostly systematic: you walk known dimensions rather than hoping someone remembers the weird one.

## Along each input
- What if it's empty, null, or missing entirely?
- What's the minimum and maximum? What's one past each?
- What if it's the wrong type, wrong format, or wrong encoding?
- What if it's enormous: a 500-character name, a 2GB upload, 10,000 line items?
- What about whitespace, emoji, RTL text, or characters that break your parser?
- What if the value is technically valid but nonsensical: a birthdate in 2087, a negative quantity?

## Along quantity (the 0/1/many rule)
- Zero of the thing: empty list, no results, first-time user with no history
- Exactly one: does the UI still make sense? Does pagination break?
- Many: what happens at 10,000? Does the page render? Does the query time out?
- Too many: is there a cap? What does hitting it look like?

## Along time
- What if two people do this at the same time? Who wins?
- What if the user double-clicks? Is the operation idempotent?
- What if they hit back, refresh, or open two tabs?
- What if the session expires mid-flow? Or their token refreshes?
- Daylight saving transitions, leap years, timezone boundaries, month-end?
- What if step 3 fails after step 2 already committed? Is there a rollback?

## Along state
- What if the entity was deleted while the user was looking at it?
- What if the user's permissions changed mid-session?
- What if the record is already in the target state (approve an approved thing)?
- What if a required upstream record doesn't exist yet?
- What state transitions are *illegal*, and what happens if someone attempts one?

## Along failure
- Network drops mid-request: did it commit or not?
- Third-party API is slow, down, or returns garbage. What's the timeout? The fallback?
- What's retryable and what isn't? Will retries duplicate anything?
- Partial success: 8 of 10 items processed. Now what?

## Along the human
- What's the *malicious* version of this flow? What would someone abuse?
- What's the *confused* version: what will people do by accident?
- What happens with a screen reader, keyboard-only, or 200% zoom?
- What does the error message actually tell them to do next?

## Questions that surface the unknown unknowns
Worth asking out loud in the interview:
- "What's the weirdest case you've seen in production?"
- "Which customer breaks every assumption you have?"
- "What did the last version of this get wrong?"
- "Where do support tickets cluster today?"
- "What's the thing you'd be embarrassed if this got wrong?"
- "If this feature made the news for a bad reason, what happened?"

## Techniques
- **Boundary value analysis:** test at, just below, and just above every limit.
- **Equivalence partitioning:** group inputs into classes that should behave identically, then test one from each class plus the boundaries between them.
- **Decision tables:** enumerate every combination of conditions. The empty cells are your gaps.
- **State transition diagrams:** draw the states, then draw every arrow that *shouldn't* exist and ask what happens.
- **Pre-mortem:** "It's six months from now and this feature failed badly. Write the postmortem." Surfaces risks people won't volunteer directly.

## One process note
Edge cases surface late because stakeholders describe the happy path by default; they're picturing the demo, not the incident. Two habits help: sketch the flow visually during the interview so gaps become literal blank space, and follow up with people who *aren't* the requester. Support, ops, and QA carry the edge-case knowledge; the person who requested the feature usually doesn't.
