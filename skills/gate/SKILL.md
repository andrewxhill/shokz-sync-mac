---
name: gate
description: The gate before production code. Use before implementing, building, or wiring up anything in production paths, and when an initiative's design is ready.
---

Production code for an initiative waits for the human's yes. Agents move faster than a person can review, and the decisions belong to the human, so the gate is where drift gets caught before it ships.

1. Read the whole initiative folder with the okf skill and run the validator. Completion: every concept in the folder is read and validation is clean.
2. Write the human a readiness report:
   - **Settled**: what is known and decided, linking the concepts, including every Risk with `state: settled`.
   - **Fog**: every Risk with `state: open` and every piece of research not done, with why each is safe to carry.
   - **Accepted risks**: every Risk with `state: accepted`, what could still go wrong, and what it would cost.
   - **Build**: every place we write custom code instead of adopting a library, each with its Decision.
   - **Evidence**: each spike and what it showed.
   - **Design**: the design that will freeze.

   End with: "May I start production code for <initiative>?" Completion: every Risk in the folder appears in the report.
3. Answer the human's questions until they give a decision. The gate opens only on an explicit yes from the human in this conversation.
4. On yes: set the Design to `status: stable`, then set the initiative to `phase: production` and append `{ by: human:<id>, at: <now> }` to its `verified`, where `<id>` is `git config user.email` (ask the human if it is unset). Log it and validate. On a no or requested changes: record what the human raised as Risks and set the phase to scout.

The gate reopens when a stable Design must change or production uncovers new fog: set the Design back to draft and the initiative back to scout. Production on that initiative resumes after the next yes; the validator rejects a sign-off older than the Design's last change.
