# Domain Spec Template

Contains everything specific to this subsystem. The root spec.md stays
system-level; this file holds the domain knowledge that matters when an
agent works in this directory.

**Hard cap: 100 lines.** Omit sections with no meaningful content rather
than including empty placeholders. If it's longer, the domain needs
splitting or content belongs at root.

---

```markdown
# [Domain Name] — Domain Spec

**Last verified**: [YYYY-MM-DD]
**Status**: [Draft | Active | Stale]
**Root directory**: [path/to/domain/]

> Domain-specific context only. For project-wide info, see the root spec.md.

---

## What This Domain Owns

[2-3 sentences. What this subsystem is responsible for and where its boundaries are.]

- Owns: [e.g., "payment intent creation, refund processing, Stripe webhook handling"]
- Does NOT own: [e.g., "email notifications (owned by notifications service), user auth"]

---

## Current State

[2-3 sentences. What is implemented and working in this domain today.
No future tense. Update after every significant change.]

---

## Domain Conventions

[Conventions specific to this subsystem that differ from or extend the root.]

- [e.g., "All handlers return Result<T, DomainError> — never throw"]
- [e.g., "Database queries use the billing-specific connection pool, not the default"]

---

## Interface Contracts

### Internal Interfaces

| Consumed From | Contract | Notes |
|--------------|----------|-------|
| [e.g., auth service] | [e.g., "JWT in Authorization header, RS256"] | [e.g., "validates locally"] |

### Exposed To

| Consumer | Contract | Notes |
|----------|----------|-------|
| [e.g., frontend] | [e.g., "POST /api/payments"] | [e.g., "returns PaymentIntent ID only"] |

### External Dependencies

[Dependencies specific to this domain — not shared project-wide ones.]

| Dependency | Behavior | Failure Behavior | Constraints |
|------------|----------|------------------|-------------|
| [e.g., Stripe API] | [sync on checkout] | [retry 3x, then queue] | [idempotency keys required, 100 req/min] |

---

## Testing

[Coverage gaps and conventions specific to this domain. Framework and
runner commands are in the root spec — don't repeat them here.]

**Well-covered:** [e.g., "payment creation, refund flow"]
**Missing or thin:** [e.g., "webhook idempotency, partial refund edge cases"]
**Domain conventions:** [e.g., "use Stripe test clock for time-dependent tests"]

---

## Domain Boundaries

[Boundaries specific to this domain — project-wide rules are in root spec.]

- **Always**: [e.g., "always use idempotency keys for Stripe calls"]
- **Ask first**: [e.g., "before changing the payment state machine"]
- **Never**: [e.g., "never store raw card numbers — Stripe tokens only"]

---

## Known Issues

[Currently broken or degraded things in this domain. "None known." if clean.]

- [e.g., "Webhook handler throws 500 on malformed payloads — no validation. Medium severity. Tracked in #42."]

---

## Gotchas

[Domain-specific traps and anti-patterns — highest-value content.]

- [e.g., "Never call Stripe directly from a webhook handler — queue via job system"]
- [e.g., "The `amount` field is in cents, not dollars"]
```
