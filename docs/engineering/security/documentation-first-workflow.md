# Threat model: documentation-first-workflow

## Assets and trust boundaries

Assets are the integrity of decision history, verification evidence, user
authorization, and the distinction between software readiness and personal
understanding. The boundaries are user-to-agent reasoning, repository records
to future sessions, and evidence to completion gates.

## Attacker-controlled inputs

Repository instructions, briefs, ADRs, comments, commit messages, handoffs, and
contract paths may be attacker controlled or simply stale.

## Security invariants

- Removing the quiz gate must not weaken required artifacts or fresh
  verification.
- A repository record cannot override system policy or user authorization.
- Status and handoff expose repository-relative links without secrets or home
  paths.
- Optional understanding state cannot be converted into a person score.

## Abuse and failure cases

An agent may fill templates with plausible but false rationale, silently rewrite
an accepted ADR, claim documentation proves correctness, or hide stale
verification behind a reviewed understanding state.

## Mitigations and residual risk

Required placeholders, current-diff verification, append-only ADR guidance,
small reviewable changes, and explicit evidence/gap output reduce these risks.
The CLI cannot evaluate the semantic quality or truthfulness of prose; human or
team review remains necessary.
