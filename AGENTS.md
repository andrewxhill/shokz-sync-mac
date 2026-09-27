# AGENTS.md

This repository builds a project from zero to one with production code last. Every unknown is settled first, in knowledge, design, and throwaway spikes, so production code is written once, from settled ground.

## The loop

Each piece of work is an initiative in `.okf/initiatives/` with its own phase. Initiatives move independently: one can be in production while another is still in scout.

```
frame → scout ⇄ shipyard → design → gate → production
          ↑                  │               │
          └──── new fog ─────┴───────────────┘
```

Agents drive scout and shipyard on their own: read first, spike when reading leaves a question open, and bring the human only the decisions.

At the start of every session, read `.okf/index.md` and each initiative's phase with the okf skill, then continue where the phases point.

| Skill | When |
|---|---|
| frame | A new project, or a new piece of work on an existing one |
| scout | An initiative in scout: mapping unknowns and settling them, cheapest evidence first |
| shipyard | An unknown that only running code can answer |
| design | An initiative in design: the fog is clear |
| gate | Before any production code, every time |
| okf | Reading or recording any project knowledge |
| grilling, grill-me | Stress-testing any plan or decision with the human |
| writing-for-agents | Creating or editing a skill or this file |

## Rules

- Production code is anything outside `.okf/` and `.shipyard/` that is meant to ship: source, configuration, scripts, and their test suites. A small helper file counts.
- Production code for an initiative starts only after the gate records the human's yes. Until then, code lives in `.shipyard/`.
- Buy, don't build. Adopt an existing library, service, or tool and derisk it in shipyard. Custom code needs a Decision the human approves at the gate.
- Design comes before code: markdown, mermaid, and ascii, written into `.okf/`.
- All durable knowledge lives in `.okf/`, including designs. `docs/` is gitignored, so anything a tool writes there is lost: move it into `.okf/`.
- Checks run locally. CI stays out of this repo until the user changes this rule.
- Finish any change to `.okf/` with `uv run skills/okf/validate.py` clean.

## In production

Code follows the frozen design and the Decisions. When reality diverges from the design or a new unknown appears, pause that part: record a Risk, set the initiative back to scout, and return through the gate. When the initiative's definition of done is met and the human confirms, set its phase to done.

## Skills

Install external skills with gh skill, once per agent (`--agent` takes one value per run):

```bash
gh skill install <owner/repo> <skill> --agent claude-code
gh skill install <owner/repo> <skill> --agent universal
```

Update them with `gh skill update --all`.

Local skills live in `skills/<name>/`, the one source of truth. Expose each to both agents with symlinks:

```bash
ln -s ../../skills/<name> .claude/skills/<name>
ln -s ../../skills/<name> .agents/skills/<name>
```

`CLAUDE.md` is a symlink to this file.
