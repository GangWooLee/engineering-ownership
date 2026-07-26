# 2026-07-25 · Close quoting evasions in the judge-visible action log

Change ID: `fix-blinding-redaction`
Created: `2026-07-25T23:47:42+09:00`
Status: Accepted

## Context

The action log is the only narrative of a run the judge sees. The runner's own
directory name identifies the configuration, so the log must never carry it. The
existing defense normalized path-looking tokens, but shell quoting produced
token shapes the normalizer did not recognize, and each newly discovered shape
had been patched one at a time — bare tilde was caught, quoted tilde was not.

## Options considered

1. Keep enumerating token shapes (strip quotes, handle `$HOME`, …) and rely on
   the enumeration being complete. Rejected alone: this incident is the second
   time an unanticipated shape got through; enumeration has no completeness
   proof.
2. Replace the whole token pass with a single name-based scrub. Rejected alone:
   the token pass produces useful fixture-relative targets; collapsing to a
   scrub-only approach would degrade every target to opaque strings.
3. Both: extend the token pass for the known shapes (quotes stripped before the
   check, `$`-prefix treated as outside), and add a final backstop that replaces
   any surviving occurrence of `ROOT.name` in a target. Chosen.

## Decision

Option 3. The token pass stays the primary mechanism and keeps targets readable;
the backstop guarantees that whatever shape evades it, the one string that
identifies the configuration cannot reach the log.

The backstop lives in `action_target`, not `redact()`: `redact()` also processes
transcripts, responses, and fixture deltas, where replacing the repository name
would silently rewrite agent-authored content. Judge-visible *metadata* is
scrubbed; agent-authored *material* is instead policed by the grader's
leak-refusal check.

## Consequences and reversal

Targets that would have leaked now read `(outside the repository)`. A target
legitimately naming a fixture file that happens to contain the runner's name is
scrubbed too — acceptable, since such a file identifies the configuration by
construction. Reversal is a single revert of `action_target`; the regression
test will fail loudly if the backstop is removed without a replacement.

## Implementation references

- `scripts/eval/run_skill_evals.py`
- `tests/test_evals.py`

## Supersession

Supersedes: None
Superseded by: None
