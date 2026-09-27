---
name: shipyard
description: >-
  Route uncertain implementation work into a disposable `.shipyard/` spike
  before production code exists. Use when feasibility, library or API
  behavior, data types, caching, integration boundaries, or another material
  implementation detail is unresolved.
---

# Shipyard

A shipyard is a throwaway learning canvas: a small spike, probe, demo, or
validation project used to remove uncertainty before production implementation.
It is not a second production source tree.

## Operating rule

Keep production space clean. Production code, configuration, and production test
suites contain work intended to ship or to support something that ships.

When a material implementation question is still open, work in
`.shipyard/<initiative>/<risk>/` first. Do not put prototype, demo, exploratory,
or learning code in the production paths merely to discover whether an approach
works.

Do not create a shipyard when the approach is already sufficiently understood;
the skill is a gate against avoidable slop, not a ceremony for routine work.

## Workflow

### 1. Name the risk

Every spike settles a Risk in the initiative. Create the Risk with the okf skill
if it is missing, and state the question that must be answered, such as:

- What data types does this API actually return?
- What is the correct pagination, retry, or caching behavior?
- Does the library we plan to adopt meet the requirement, and where does it fall short?
- Can this integration run inside the target runtime?
- Which approach has the required performance or failure behavior?

Create `.shipyard/<initiative>/<risk>/` for it, where `<risk>` matches the
Risk's file slug. Keep the risk name descriptive and narrow. The directory
existing is the signal that the work is exploratory.

Completion criterion: the Risk exists in OKF, states the question, and names its
shipyard location.

### 2. Derisk with the smallest useful spike

Build only what answers the question. Prefer a probe, fixture, script, or tiny
vertical slice over an application-shaped prototype. When the plan is to adopt a
library, the spike exercises that library at the edges we depend on. Keep
dependencies, configuration, credentials, and generated artifacts local to the
shipyard when possible.

The spike may be rough. It may be deleted. It must not become a runtime
dependency of production code, and production code must not import from it.

Completion criterion: the spike produces observable evidence, or clearly shows
that the question remains unanswered.

### 3. Record durable findings in OKF

Update the Risk with the okf skill: its `state`, the answer, evidence, assumptions,
constraints, rejected alternatives, and any follow-up risks that matter later. A
choice between options becomes a Decision. Keep the spike itself out of the OKF
knowledge documents unless a path is useful as provenance.

Validate the OKF bundle with the deterministic validator.

Completion criterion: the Risk reflects the evidence and validation is clean.

### 4. Hand back

Return to scout, where the evidence reshapes the fog of war, or to design if
that is where the question came from. Production code waits for the gate.

Once the gate opens, start the production implementation from the recorded
findings. Design the production code for its real interfaces, error paths,
tests, and operational constraints. Do not blindly move or copy the shipyard
into a production path. Copy only useful evidence or small snippets when that is
genuinely clearer than rewriting them.

Completion criterion: before the gate, the initiative is back in scout or
design with the Risk updated. After it, production code no longer depends on
`.shipyard/`, and its behavior is covered by the appropriate production checks.

### 5. Retire the canvas

After the findings are captured and production work is complete, leave the
spike for historical context or delete it when it has no remaining value.
Either way, it remains disposable and non-production. Do not spend effort
maintaining it as if it were a product.

## Shape

Use whatever files make the spike easy to run and understand:

```text
.shipyard/<initiative>/<risk>/
├── README.md          # optional: question, run command, result
├── spike.*
├── fixtures/          # optional
└── output/            # optional, disposable
```

The only durable record is the validated OKF knowledge that the spike produced.
