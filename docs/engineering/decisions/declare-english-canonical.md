# 2026-07-29 · Declare English canonical for records, Korean as summary

Change ID: `declare-english-canonical`
Created: `2026-07-29T16:00:15+09:00`
Status: Accepted
Corrected: 2026-08-05 — the Context cited a harm that never occurred. The Korean
README never described the deleted competency tag subsystem. The decision is
unchanged; the example supporting it was false.

## Context

The repository carries English and Korean documents with no statement of which
governs. The Korean README was last touched three days before the English one,
and nothing tells a reader whether that matters, because neither file claims to
be the source. The project is written for "anyone who develops with AI"; its
owner works in Korean and its conversations happen in Korean, so the pull toward
Korean documents is real and will not go away.

(Corrected 2026-08-05: this said the Korean README "still describes a subsystem
that has been deleted". It never described it. `README.ko.md` has no mention of
the competency tags in any revision, and the change that removed them touched
`README.md` alone. The two files had not diverged in content during the window
cited. The decision is unchanged and does not depend on that example — the
absence of any statement of which language governs is the reason, and it is
true.)

## Options considered

1. **Korean canonical.** Matches how the owner reasons most precisely, which is
   not a small thing for records whose whole purpose is preserving reasoning.
   Rejected on cost and consistency: twenty existing records would need
   translating, and the evaluation harness already enforces ASCII on the skill
   description, eval prompts, and expectations (`tests/test_evals.py`), so the
   measured surface would stay English regardless — the split would remain, just
   relocated.
2. **Delete the Korean documents.** The cold audit listed them as over-built for
   a project with no users, and deletion removes the drift permanently.
   Rejected: it also removes the only Korean entry point, and the drift is
   fixable by declaring status rather than by deleting the document.
3. **English canonical, Korean as declared summaries.** Chosen. Records, code,
   commits, and the shipped skill stay English. Korean survives as entry-level
   summaries that name their source and do not claim completeness.

## Decision

English is canonical for everything durable: engineering records, ADRs,
runbooks, threat models, commit messages, and the shipped plugin. Korean
documents are summaries. Each opens by naming the English document it
summarizes and stating that the English one governs where they disagree.

Conversation with the owner stays Korean. That is not in tension with this
decision — the records are written for a later reader who may be anyone, while
the conversation has exactly one audience.

## Consequences and reversal

A Korean reader gets an accurate entry point and a truthful signal about where
authority lies, at the cost of the summaries being visibly incomplete rather
than invisibly stale. Nothing enforces the summaries staying current; a test
comparing the two would fail permanently by construction, so none is added and
the limit is stated instead.

Reversal is deleting two headers and this record.

## Implementation references

Leave this section empty when the decision is not enforced in code.

## Supersession

Supersedes: None
Superseded by: None
