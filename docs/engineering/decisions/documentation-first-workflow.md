# 2026-07-23 · Documentation-first engineering workflow

Change ID: `documentation-first-workflow`
Created: `2026-07-23T10:37:55+00:00`

Status: Accepted

## Context

The first implementation made a no-AI teach-back a mandatory R2/R3 completion
gate. The owner clarified that the desired system is a durable decision memory:
records written during work should support later understanding, maintenance,
and AI-assisted modification without forcing a quiz before every next task.

## Decision

Make reasoning artifacts and fresh verification the default enforceable
evidence. Replace `teach_back` with optional `understanding` state containing
`not-reviewed`, `reviewed`, or `gaps`, unresolved items, and a suggested
`revisit_after` date. Optional review never passes or fails the software change.

Keep separate records for separate lifetimes:

- change brief: the complete local story of one change;
- ADR: architecturally significant, long-lived decisions and alternatives;
- code comments: non-obvious local rationale and invariants;
- commit/PR: atomic delivery summary and links to canonical records;
- runbook: observation, diagnosis, rollback, and repair;
- handoff: current session state and pointers, not duplicated rationale.

## Alternatives considered

- Mandatory teach-back for every R2/R3 change: rejected because it confuses
  retained recall with safe completion and interrupts the intended workflow.
- Remove understanding review entirely: rejected because explicit gaps and
  revisit reminders are useful for deliberate learning.
- Store all rationale in commits: rejected because architectural decisions
  outlive individual implementation commits and need status and supersession.
- Copy full explanations into every surface: rejected because duplicated
  documentation drifts.

## Consequences and reversal

R2/R3 can complete when required records and current verification are present,
even if the owner has not performed a separate understanding review. Status and
handoff must make that distinction visible. Teams may layer a stricter
teach-back policy on top of the tool-neutral default.

Reversal requires restoring the check gate and legacy evidence vocabulary.
Existing accepted ADRs should not be edited to hide the change; a future
decision should supersede this record.
