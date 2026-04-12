# Architecture Anti-Patterns

Quick reference for the `/architecture` skill and `architecture-reviewer`
agent. When you spot one, name it and use the response phrase.

| Anti-Pattern | Signal | Response |
|---|---|---|
| Premature Decomposition | Microservices before domain boundaries are understood, more services than team members | "You haven't discovered your domain boundaries yet. A monolith lets you find them cheaply." |
| Resume-Driven Development | Tech chosen for novelty, no rationale beyond "modern" | "What problem does [tech] solve that simpler alternatives don't?" |
| Over-Engineering | Unnecessary abstraction layers, patterns without problems | "You're solving problems you don't have yet. What's the simplest thing that works?" |
| Architecture-Team Mismatch | More moving parts than people to operate them | "Your team of [N] cannot operate [M] services. Simplify." |
| Distributed Monolith | Services share a database, synchronous call chains, batch deploys | "If services can't deploy independently, they're a monolith with network overhead." |
| Wrong Storage Choice | Choosing DB before understanding access patterns | "How will the data be queried? The access pattern picks the storage." |
| Missing Observability | "We'll add monitoring later" | "If you can't see it, you can't debug it. Observability is day-1." |
| Security as Afterthought | No auth design, "we'll handle security later" | "Security retrofitted costs 10x. What's the auth model?" |
| Vendor Lock-in Without Exit | Deep proprietary dependency with no exit plan | "What happens if [vendor] doubles pricing? What's the migration path?" |
| Solution Without Problem | Technology with no trace to constraints or quality needs | "Which constraint or quality need drives this choice?" |
