# skills-are-all-you-need

A git template for starting a project from zero to one with agents, where production code comes last. Agents grill the creator on scope, research what to adopt instead of build, and settle every unknown with throwaway spikes in `.shipyard/`. They write designs in markdown, mermaid, and ascii, and record all of it in an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) bundle in `.okf/`. Production code starts only after a human approves a readiness report for that piece of work, so it gets written once, from settled ground, without slop. Each piece of work runs this loop on its own, so new work can start in discovery while earlier work is already in production. The skills work in Claude Code, Codex, Cursor, Gemini, and other agents.

Agent: this repository is a template. When a human asks you to start a new project from it, follow these steps. The loop and its rules live in `AGENTS.md`; this file only gets the copy in place.

## 1. Copy the template

Ask the human which way they want it, then run the matching commands. Requires [gh](https://cli.github.com/) 2.95 or later and [uv](https://docs.astral.sh/uv/).

**A new GitHub repo from the template**: the new repo becomes `origin`.

```bash
gh repo create <owner>/<name> --template recallnet/skills-are-all-you-need --private --clone
cd <name>
```

**Local only, no remote**: fresh history, nothing points back at this template.

```bash
git clone --depth 1 git@github.com:recallnet/skills-are-all-you-need.git <name>
cd <name>
rm -rf .git && git init
```

A local copy stays local until the human gives you a remote of their own.

## 2. Make it the new project's

1. Replace this README with a title for the new project and one line pointing at `AGENTS.md`.
2. Replace the entry in `.okf/log.md` with today's date and `* **Initialization**: Created the project from the skills-are-all-you-need template.`
3. Run `uv run skills/okf/validate.py` and confirm it prints `OK`.
4. Commit: `git add -A && git commit -m "Start from skills-are-all-you-need template"`.

Completion criterion: the validator is clean, the commit exists, and in the local-only path `git remote -v` prints nothing.

## 3. Start the loop

Invoke the frame skill and grill the human about the project. From here, `AGENTS.md` leads.
