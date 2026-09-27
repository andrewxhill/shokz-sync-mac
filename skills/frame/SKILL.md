---
name: frame
description: Frame a new project or initiative by grilling its creator. Use when starting a project or a new piece of work.
---

Use the grilling skill. The tree is the scope: the problem, who it serves, what done looks like, the constraints, and what is out of scope.

For a new project, the tree is the whole product, and its leaves are the capabilities it needs. Write the project-wide knowledge at the `.okf/` root and each capability as an initiative stub: `.okf/initiatives/<name>/initiative.md` in phase frame with a one-line description. Then frame each initiative in its own pass, starting with the one the creator picks.

For an initiative, write each settled branch into its `initiative.md` with the okf skill. Unknowns that surface while grilling become Risks with `state: open`, left for scout to settle. When the frontier is empty, set the phase to scout.
