BRIEF = """# {date} · {title}

Change ID: `{change_id}`
Created: `{created_at}`
Risk: {risk}
Status: In progress

## Problem and intended outcome

<!-- engineering-ownership:fill-required -->
Describe the user or operational problem, desired outcome, constraints,
invariants, and initial approach before asking AI to implement it.

## Success and non-goals

## Existing responsibilities searched

State what was reused and why. If similar code was not reused, record why.

## System and data flow

## Decisions and trade-offs

Link any architecturally significant decision record. State which alternative
was rejected and why.

## Failure, security, and recovery

## Verification evidence

## Known limits and learning gaps

## References

Link issues, ADRs, commits, pull requests, and relevant external constraints.
"""

ADR = """# {date} · {title}

Change ID: `{change_id}`
Created: `{created_at}`
Status: Proposed

## Context

<!-- engineering-ownership:fill-required -->
## Options considered

## Decision

## Consequences and reversal

## Implementation references

List repository-relative implementation paths that enforce this decision.
Leave this section empty when the decision is not enforced in code.

## Supersession

Supersedes: None
Superseded by: None
"""

RUNBOOK = """# {date} · {title}

Change ID: `{change_id}`
Created: `{created_at}`
## Signals and alerts

<!-- engineering-ownership:fill-required -->
## Safe diagnosis

## Rollback or repair

## Escalation and data handling
"""

THREAT_MODEL = """# {date} · {title}

Change ID: `{change_id}`
Created: `{created_at}`
## Assets and trust boundaries

<!-- engineering-ownership:fill-required -->
## Attacker-controlled inputs

## Security invariants

## Abuse and failure cases

## Mitigations and residual risk
"""

POINTER = """<!-- engineering-ownership:start -->
## Engineering Ownership

For non-trivial software changes, use the installed `engineering-ownership`
skill and this repository's `.engineering/contract.json`. Repository rules may
strengthen these gates, but durable decision records and current verification
cannot be waived.
<!-- engineering-ownership:end -->
"""
