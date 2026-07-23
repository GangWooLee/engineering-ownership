# Operating model

## Risk gates

| Risk | Required before completion |
| --- | --- |
| R0 | Relevant static check when one exists; clear diff |
| R1 | Change brief, relevant fresh verification, change-flow explanation |
| R2 | Detailed brief, significant decision record, integration or runtime seam, failure observation, rollback |
| R3 | R2 plus repository threat model, runbook, recovery or failure-injection evidence, staged application |

An exploratory prototype may begin at R0 or R1. Reclassify it when real users,
money, credentials, sensitive data, or irreversible state become involved.

## Work phases

1. **Intent** — preserve the user's problem, outcome, constraints, and initial view.
2. **Responsibility search** — locate canonical owners and prior decisions.
3. **Design** — map boundaries, data, alternatives, failure, security, and recovery.
4. **Implementation** — make small changes with a reproducible test seam.
5. **Verification** — bind fresh command results to the exact working-tree diff.
6. **Knowledge preservation** — link canonical decisions and record unresolved understanding gaps.
7. **Handoff** — persist enough state for a session with no conversation history.

`advise` reports missing evidence but does not block. `enforce` exits non-zero
and should be adopted deliberately in CI, not silently imposed by the plugin.
Optional understanding review and revisit dates remain visible but do not block
completion unless the repository deliberately adds a stricter local policy.
