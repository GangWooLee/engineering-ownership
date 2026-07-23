BRIEF = """# Engineering change: {change_id}

Risk: {risk}

## User reasoning

<!-- engineering-ownership:fill-required -->
Describe the problem, desired outcome, constraints, invariants, and your initial
approach before asking AI to implement it.

## Success and non-goals

## Existing responsibilities searched

State what was reused and why. If similar code was not reused, record why.

## System and data flow

## Alternatives and trade-offs

## Failure, security, and recovery

## Verification plan

## Known limits and learning gaps
"""

ADR = """# Decision: {change_id}

## Context

<!-- engineering-ownership:fill-required -->
## Decision

## Alternatives considered

## Consequences and reversal
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
strengthen these gates, but verification evidence and human explainability
cannot be waived.
<!-- engineering-ownership:end -->
"""
