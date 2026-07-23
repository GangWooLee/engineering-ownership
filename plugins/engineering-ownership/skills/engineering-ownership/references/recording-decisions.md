# Recording engineering decisions

Use one canonical record for each kind of knowledge. Link records instead of
copying the same explanation into every surface.

| Surface | Record | Do not use it for |
| --- | --- | --- |
| Change brief | Problem, constraints, current flow, decisions made during one change, verification, known limits | Permanent cross-system policy |
| ADR | Architecturally significant choice, alternatives, rationale, consequences, status, supersession | Every small implementation detail |
| Code comment | A local invariant, surprising constraint, or why an obvious approach is unsafe | Narrating what readable code already says |
| Commit | One atomic outcome, why it changed, verification, links | A complete design document |
| Pull request | Review map: purpose, scope, risks, how to review, evidence, linked decisions | The only copy of long-lived rationale |
| Runbook | Signals, diagnosis, mitigation, rollback, escalation | Product requirements or design history |
| Handoff | Current state, fresh or stale evidence, unresolved gaps, next safe action | Duplicating the brief and ADR |

## ADR lifecycle

Create an ADR only when a decision changes system structure, a key quality
attribute, a public or data contract, or is expensive to reverse. Use a stable
status such as `Proposed`, `Accepted`, `Deprecated`, or `Superseded`. Do not
rewrite accepted history when the decision changes; write a new ADR and link
the old and new records.

## Commit shape

Keep commits atomic and concise. A useful body is:

```text
Why: <problem or constraint>
Decision: <what this commit establishes>
Verification: <fresh commands or runtime seam>
Refs: <brief, ADR, issue, or PR>
```

The body links to the canonical reasoning rather than copying it. Refactoring
and behavior changes should be separate when practical.

## Comments

Prefer names and structure that make the code explain itself. Add comments for
non-obvious rationale, invariants, external constraints, or rejected obvious
approaches. Remove comments that merely translate code into prose or can drift
without a test or linked decision.

## AI continuation

Before changing an existing responsibility, an agent reads the active brief,
relevant ADRs, runbook, contract, current diff, and handoff. It records whether
the new change follows, supersedes, or invalidates a prior decision. It must not
silently overwrite accepted rationale.

## References

- [Microsoft: maintain an architecture decision record](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record)
- [Google: documentation is the story of your code](https://google.github.io/styleguide/docguide/best_practices.html)
- [Google: small, self-contained changes](https://google.github.io/eng-practices/review/developer/small-cls.html)
- [GitHub: helping others review your changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/helping-others-review-your-changes)
