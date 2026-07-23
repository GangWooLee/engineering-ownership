BRIEF = """# Engineering change: {change_id}

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

ADR = """# Decision: {change_id}

Status: Proposed

## Context

<!-- engineering-ownership:fill-required -->
## Options considered

## Decision

## Consequences and reversal

## Supersession

Supersedes: None
Superseded by: None
"""

RUNBOOK = """# Runbook: {change_id}

## Signals and alerts

<!-- engineering-ownership:fill-required -->
## Safe diagnosis

## Rollback or repair

## Escalation and data handling
"""

THREAT_MODEL = """# Threat model: {change_id}

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
