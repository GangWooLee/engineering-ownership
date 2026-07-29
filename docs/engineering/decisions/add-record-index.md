# 2026-07-29 · Give the engineering records an entry point

Change ID: `add-record-index`
Created: `2026-07-29T16:11:56+09:00`
Status: Accepted

## Context

Records only pay for themselves when they are read. Fifty-two exist here and
the only way in is to already know a change id, which inverts the point: the
person who needs a record is the one who does not know it exists. Twenty was
survivable, fifty is not, and the cost of building the entry point rises with
every record added.

Two facts decided the shape. This repository already keeps two indexes —
`docs/validation/README.md` and the evaluation workspace's — and both are held
current by a test rather than by anyone's discipline. And it already has proof
that the other approach fails: `README.ko.md` is a hand-kept document that fell
three days and one breaking release behind without anyone noticing.

## Options considered

1. **Hand-written index.** Cheapest today, wrong by next week. `README.ko.md`
   is the evidence, in this repository, for this failure mode. Rejected.
2. **Generated on demand, not committed.** No staleness by construction, and
   no entry point either — a reader who has not cloned and run the CLI sees
   nothing, and the audit's working journey succeeded precisely because a
   committed document named another committed document. Rejected.
3. **Generated, committed, and guarded.** Chosen. The generator makes being
   right cheap; the guard makes being wrong expensive; the committed file is
   what a reader on the web actually lands on.

## Decision

`engineering index` derives the table from the evidence records, which already
carry every field it needs. The output is committed at
`docs/engineering/README.md`, linked from `README.md`, and four tests hold it:
every evidence record named, every document under `docs/engineering/` named,
every link resolving from the index's own directory, and regeneration being a
no-op.

Two details are decisions rather than mechanics. The index prints **titles**,
because the audit's second journey failed at a guess between four ids while the
disambiguating title sat unused in every record. And it scans for **decision
documents no record claims**, because an ADR written under an R1 record has
nowhere to live in that record's artifact map — this repository produced exactly
such an orphan during the audit, and an index walking only the evidence would
have inherited the blind spot.

## Consequences and reversal

Adding a record now requires regenerating the index, enforced rather than
remembered. The failure mode moves from "the index is quietly wrong" to "the
suite fails until you run one command", which is the trade this project makes
everywhere else.

The index also becomes a public surface: it names every change, its risk tier,
and whether it closed. That is the intent, and it is why nothing sensitive
belongs in a change id or title.

Reversal is deleting the command, the test file, and the generated document;
nothing else reads them.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `tests/test_docs.py`

## Supersession

Supersedes: None
Superseded by: None
