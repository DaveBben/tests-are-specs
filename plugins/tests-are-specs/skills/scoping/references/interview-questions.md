# Interview questions

Prompts to pull requirements out of the user, never a script to read aloud, and never a source of requirements you author yourself. Walk every category; skip a whole category only out loud, with why. Within a category, skip or reword individual questions freely, and let each answer reshape the next question. Split the ask into **functional** requirements (what the system does) and **non-functional** requirements (how well it does it).

## Functional requirements

- What problem does this feature solve, and for whom?
- Who are the users/actors? What roles exist?
- Walk me through the ideal user flow, step by step.
- What triggers this feature? What's the entry point?
- What inputs does the user provide? What outputs do they get?
- What are the business rules or validation constraints?
- What happens in edge cases: empty state, invalid input, duplicate action?
- What should happen when it fails? What does the user see?
- What's explicitly out of scope for v1?
- How do we know it worked? What's the success criteria?
- Does this integrate with any existing systems or third parties?
- What permissions or access control apply?

## Non-functional requirements

- **Performance:** How fast should this respond? What's unacceptable? Expected volume (requests/sec, concurrent users, data size)? Peak vs. average load, seasonal spikes?
- **Scalability:** Growth expectation over 6-12 months? Scale horizontally?
- **Availability & reliability:** Uptime needed? Is downtime tolerable, and when? Recovery expectation (RTO/RPO)? Can operations be retried safely? Is data loss ever acceptable?
- **Security & compliance:** Data sensitivity (PII, financial, health)? Authn/authz requirements? Regulatory constraints (GDPR, HIPAA, SOC 2)? Audit logging?
- **Usability & accessibility:** Accessibility standard (WCAG level)? Mobile, desktop, or both? Offline? Localization/i18n?
- **Maintainability & observability:** Metrics/alerts needed? Who supports this after launch? Lifespan: throwaway or long-term?
- **Constraints:** Budget, deadline, team size? Tech stack limits or mandated tools? Dependencies on other teams?

## Technique tips

- **Ask "why" three times:** stated requirements often hide the real need.
- **Use concrete numbers:** "fast" is useless; "under 200ms at p95" is testable.
- **Probe with scenarios:** "What if 10,000 users hit this at once?" surfaces unstated NFRs.
- **Ask what breaks:** "What would make you consider this a failure?"
- **Confirm by playing back a concrete example:** "a cart of $80 with a coupon that expired yesterday charges the full $80, right?" An example forces the numbers a restatement lets slide, and a ratified example becomes a contract test body almost verbatim.
