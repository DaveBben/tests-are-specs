# tools — optional spec tooling

Not part of the portable plugin. These are conveniences that ride the spec-monkey **parse contract** (the machine-readable conventions the templates define: frontmatter scalars, `FR`/`SC`/`INV` join keys, canonical section homes). They burn no LLM tokens on checks a script settles better. A skill never depends on them; the flow runs without this directory.

## `spec-lint.py` — mechanical spec checks

Stdlib Python 3, no install. Checks what a parser can settle without judging engineering:

- **Placeholders** — unfilled template slots (`<...>` spans containing a space). A single-token `<id>` in a command is left alone.
- **Frontmatter** — the required scalars (`spec_monkey`, `id`, `kind`, `status`, `created`, `updated`) are present, `status` is a legal value for the `kind` (work-item vs project lifecycle), and `profile` (if set) is `full` or `light`.
- **Gate record** — a spec at `approved` (or beyond) records who granted the gate in `approved_by`. A status flip with an empty `approved_by` is a warning: a gate with no owner, which an audit can't tell from a self-set flip. (A tighter check — that a `draft→approved` flip and a content change never share one commit — needs git history and is left to a CI step, not this file-level linter.)
- **ID uniqueness** — no `FR-NNN` or `SC-NNN` defined twice in a spec.
- **FR↔SC pairing** — every `FR-NNN` carries a success criterion beneath it, or is listed under *Coverage exceptions*. A full spec is paired in `detail/contract.md`; a `profile: light` (trivial-lane) spec keeps its FR/SC in `spec.md`, and the linter pairs it there.
- **Dangling invariants** — every `INV-NNN` a work-item spec cites is actually defined in the project spec.
- **Parent resolution** — a work-item's `parent` resolves to the project spec's `id` (a missing parent is a warning: fine for a genuine one-off).

What it does **not** do: judge soundness, grounding, altitude, or the risk lenses. That is `reviewing-specs`' job and stays with a human-plus-LLM reviewer. The linter clears the mechanical noise so the review spends its attention on judgment.

### Run it

```bash
tools/spec-lint.py                       # lint docs/specs (the default root)
tools/spec-lint.py docs/specs            # explicit root
tools/spec-lint.py docs/specs/my-feature # a single spec folder
tools/spec-lint.py --status docs/specs   # roll up kind/profile/status/gate; never fails
```

The `--status` roll-up is the state view: one row per spec (slug, id, kind, profile, status, `approved_by`), so you can see at a glance which specs are drafted, approved, or shipped without opening each frontmatter. It reports; it does not judge, and always exits `0`.

Exit code is `0` when no `ERROR` was printed and `1` when any was — warnings never fail — so it drops straight into CI or a pre-commit hook:

```yaml
# CI step
- run: python3 tools/spec-lint.py docs/specs
```

Verified clean against the worked example: `tools/spec-lint.py examples/clf-pipeline/docs/specs`.
