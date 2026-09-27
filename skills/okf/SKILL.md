---
name: okf
description: The project's knowledge bundle in `.okf/`. Use when reading project knowledge, recording a finding or decision, or editing anything under `.okf/`.
---

`.okf/` is an Open Knowledge Format v0.2 bundle: the single source of truth for everything this project knows. That covers scope, research, designs, risks and decisions. The spec is [SPEC.md](SPEC.md). Read §4, §5.1, §5.2, §8, §9 and §11 before your first write in a session.

## Consume

Start at `.okf/index.md` and follow links only into what the task touches. Weigh trust as you read: `status: draft`, a past `stale_after`, or no `verified` entry means confirm before relying on it.

## Produce and maintain

- One concept per file; its path is its ID. `type` is required; add `title` and `description`.
- Stamp every write with `generated: { by: <agent>/<version>, at: <ISO 8601> }`. List what you read in `sources` and footnote each sourced claim with the source's `id`.
- Keep each directory's `index.md` current and add a dated entry, newest first, to `.okf/log.md`.
- Retire knowledge with `status: deprecated` and a log entry, so its history stays.
- `verified: { by: human:<id>, at: <ISO 8601> }` records a person's sign-off. Write it only for words the human gave you in this conversation.

## Initiatives

Each piece of work is a folder with its own phase:

```
.okf/initiatives/<name>/
  index.md
  initiative.md        type: Initiative   phase: frame | scout | design | production | done
  design.md            type: Design       status: draft until the gate freezes it as stable
  risk-<slug>.md       type: Risk         state: open | settled | accepted; the question, the cheapest evidence that settles it, the evidence
  decision-<slug>.md   type: Decision     the choice, the alternatives, why; every buy-or-build lands here
```

Phases advance frame → scout → design. Only the gate sets production; production becomes done when the initiative's definition of done is met. A Risk is settled by evidence and accepted only by the human. A spike for a Risk lives at `.shipyard/<name>/<slug>/`, matching its file.

## Validate

```bash
uv run skills/okf/validate.py
```

Finish with it clean. It checks OKF conformance, every Risk's state, and the initiative rules: a known phase, and for production or done, a human `verified` entry newer than the Design's last change and no draft Design.
