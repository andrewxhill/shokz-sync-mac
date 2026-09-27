---
name: scout
description: Clear an initiative's fog of war and choose what to buy. Use when an initiative is in scout, when new unknowns surface, or when choosing a library, service, or tool.
---

Scout is a loop you drive yourself. The human comes in for decisions, not for steering.

1. **Map the fog.** Read the initiative and its neighbours in `.okf/initiatives/`, then write every unknown between here and a design you would bet on as a Risk with `state: open`, ranked by how hard a wrong guess would force a redesign. Hunt in four places:
   - **External contracts**: APIs, SDKs, and services we depend on. Missing published types, undocumented errors, rate limits, auth, pagination.
   - **Overlap**: whether this shares a data model, cache, or component with an adjacent initiative and can build on it.
   - **Buy**: for each capability, the libraries, services, and tools not yet compared. Building our own is a candidate only once buying is ruled out.
   - **Feasibility**: runtime, performance, scale, and failure behavior we are assuming.

   Show the human the ranked map as you start, for information rather than approval. Completion: each Risk names its question and the cheapest evidence that would settle it.
2. **Settle, cheapest evidence first.** Work the Risks top-down. Read first: docs, source, type definitions, issues, changelogs; sub-agents take independent Risks in parallel. When reading leaves the question open, spike it with the shipyard skill. Record the evidence with the okf skill and set the Risk settled. New unknowns found along the way join the map. Completion: every Risk is settled or waits on a decision only the human can make.
3. **Bring the human the decisions.** Use the grilling skill on what remains: tradeoffs between candidates, building instead of buying (which lands as a Decision), and Risks to accept. Only the human sets a Risk accepted.
4. When every Risk is settled or accepted, set the phase to design.
