# Framework integrations

Engineering Ownership is the decision, verification, and operational
accountability layer. Other frameworks keep their own canonical artifacts.

| Framework | Keep canonical there | Link from Engineering Ownership |
| --- | --- | --- |
| gstack | planning, review, browser QA, shipping output | Brief references and verification evidence |
| Superpowers | brainstorming, plan, TDD, debugging, verification workflow | chosen plan/test evidence, not copied prose |
| OpenSpec | proposal, design, tasks, change archive | Brief references and affected decision |
| Compound Engineering | `docs/solutions` learned patterns | learning reference; never treat it as an ADR |
| planning-with-files | task progress and session state | handoff points to it; does not duplicate state |

Rules:

- Do not require any framework as a dependency.
- Do not create a second copy of a plan, proposal, test report, or solution.
- Record the ownership decision made from those artifacts and link the source.
- Keep gstack/Superpowers responsible for how work is planned or tested.
- Keep Engineering Ownership responsible for why the selected design exists,
  what current diff was verified, and how it is operated or recovered.
