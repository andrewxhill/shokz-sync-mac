---
name: design
description: Design an initiative in markdown, mermaid, and ascii before any code. Use when an initiative is in design.
---

Use the grilling skill. The tree is this initiative's design: components, interfaces, data flow, failure behavior, and how it will be tested, built on what scout chose to buy. Read the designs and Decisions of adjacent initiatives first, and build on their data models, caches, and components where they fit.

Write it with the okf skill as `design.md` (`type: Design`, `status: draft`) in markdown, with a mermaid or ascii diagram wherever a picture carries structure, flow, sequence, or layout better than prose. The design describes code; the code itself waits for production. A branch that rests on an unknown becomes a Risk with `state: open`, and the initiative goes back to scout to settle it. When the frontier is empty, use the gate skill.
