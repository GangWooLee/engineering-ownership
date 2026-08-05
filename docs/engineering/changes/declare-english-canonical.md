# 2026-07-29 · Declare English canonical for records, Korean as summary

Change ID: `declare-english-canonical`
Created: `2026-07-29T16:00:15+09:00`
Risk: R1
Corrected: 2026-08-05 — the motivating harm never occurred. This record and its
ADR said the Korean README still described the competency tag subsystem after
it was deleted. It did not: `README.ko.md` dropped that text on 2026-07-23,
three days before the subsystem was removed, so on the date cited it was ahead
of the English README rather than behind it. The decision stands on the fact
that no file declared which language governs.

## Problem and intended outcome

This repository holds documents in two languages and says nowhere which one is
authoritative. The English `README.md` was last changed 2026-07-26, the Korean
`README.ko.md` on 2026-07-23. Nothing tells a reader which of the two governs,
so a reader who lands on the Korean file has no way to know whether it is
current. A translation that can silently fall behind is worse than no
translation precisely because nothing claims either file is the source.

(Corrected 2026-08-05: this paragraph said the Korean README was "three days and
a breaking release behind, still describing the competency tag subsystem that
`remove-competency-tags` deleted". It was not describing it. `README.ko.md`
carried `--competency security-privacy` until `03ec6d1` on 2026-07-23, which
removed it — three days *before* `remove-competency-tags` deleted the subsystem
on 2026-07-26. So on the date this record cites, the Korean file had already
dropped the text and the English one had not; the example runs the wrong way.
`remove-competency-tags` then touched `README.md` alone, because there was
nothing left to remove from the Korean file, and that was the only English
README change in the window, so the two had not diverged in content.

The timestamp gap was real. The divergence was not, and the verification cited
for this paragraph was `git log -1 --format=%ci` on each file, which establishes
dates and cannot establish content. The decision does not rest on it: no file
declared which language governs, which is true and is the reason that stands.

A second correction, same day: the first version of this note said
`README.ko.md` "never described the competency tags" and cited a single
revision. Three earlier revisions did. Checking one commit is not checking a
history.)

Intended outcome: one stated canonical language, and Korean documents that
declare themselves summaries pointing at it.

## Success and non-goals

Success: the decision is recorded; `README.ko.md` and `first-work.ko.md` each
open by naming their English source and their status as a summary; nothing in
either claims to be complete.

Non-goals: retranslating the Korean documents to match the current English
(a separate, larger job — this change makes the staleness visible rather than
hiding it); translating the engineering records; changing the language of
conversation with the owner, which stays Korean.

## Existing responsibilities searched

No prior statement of language policy exists — `grep -i "canonical\|번역\|translation"`
across `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, and
`GOVERNANCE.md` returns nothing about which language governs. `README.ko.md:3`
already links `[English](README.md)`, but as a sibling link, not as a source.

## System and data flow

Documentation only. No code, no contract, no test touches language choice —
except indirectly: `tests/test_evals.py` requires eval prompts, expectations,
and the skill description to be ASCII, so the evaluated surface is already
English by enforcement rather than by decision. This change states out loud
what that enforcement already assumes.

## Decisions and trade-offs

See `docs/engineering/decisions/declare-english-canonical.md`.

## Failure, security, and recovery

The failure this addresses is a reader trusting a stale document. Recovery is
the header itself: a summary that names its source lets the reader check.
Reversal is deleting two headers and the ADR.

## Verification evidence

- `git log -1 --format=%ci` on each README pair, showing the three-day drift
  quoted above.
- `python3 -m unittest discover -s tests`: suite green.
- `python3 scripts/validate_distribution.py`: passes.

## Known limits and learning gaps

Nothing enforces the summaries staying summaries. A guard could assert that
each `*.ko.md` names its English source, but the drift this change documents is
about content, not headers, and no cheap check catches that — a test that
compared the two would fail permanently by design. Left as a stated limit
rather than a false gate.

**A product gap this change ran into.** The decision here deserved an ADR, but
`artifact_paths` (`cli.py:135-145`) allocates a decision document only at R2 and
above, so the ADR exists on disk while the evidence record's `artifacts` map
lists only the Brief. `engineering explain declare-english-canonical` will not
mention it. The tier is meant to be a floor on required artifacts, not a ceiling
on judgement, and raising the risk to R2 purely to obtain a file would have been
the tail wagging the dog. Recorded here rather than worked around.

## References

- `docs/engineering/decisions/declare-english-canonical.md`
- `README.ko.md`, `docs/tutorials/first-work.ko.md`
