# Resume

Resume from repository evidence, not conversation memory alone.

1. Read the contract and run `engineering status`. Plain `status` lists open
   records only; add `--all` when auditing closed history.
2. Inspect current Git status and diff.
3. Match the diff digest to an evidence record. If several records are
   plausible, ask which change owns the diff rather than merging their history.
4. Read the selected Brief and linked ADR, Threat Model, Runbook, and latest
   saved handoff.
5. Identify stale verification, raised path risk, unresolved decisions, and
   understanding gaps.
6. State the recovered problem, current state, and next safe action before
   writing code.
7. Continue in the same change record unless the intended outcome has changed
   enough to deserve a new change. A closed record never reopens; continuation
   is a new change that references it.

If the handoff's revision does not resolve (`git cat-file -t <rev>` fails or
the commit is not an ancestor of the default branch), do not guess: the
history was likely rewritten or the ref pruned. Fall back to the evidence
record itself — its diff digest, verification entries, and linked Brief/ADR
are revision-independent — state that the handoff's revision is dead, and
record which commit now corresponds to it before continuing. Never resume
work against an unreachable revision.

A planning-with-files state file may explain task progress. Engineering
Ownership records remain canonical for decisions, verification pointers, and
operational risk.
