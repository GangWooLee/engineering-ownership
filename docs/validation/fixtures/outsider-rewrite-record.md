# Instrument fixture · An outsider-facing rewrite of `add-record-index`

This file documents no new work. It restates the change already recorded in
`docs/engineering/changes/add-record-index.md`, with the same facts, the same
decisions and the same numbers, written for a reader who has never seen this
project. It exists to answer one question the record-quality runs could not:
when D3 fails on 23 of 29 real records, is that because the corpus writes for
insiders, or because D3's bar is not clearable at normal length?

Only the glossing was changed. Nothing was shortened to make a dimension easier,
because a previous finding was that the rubric over-penalizes legible thinness.
Graded blind, twice, so a verdict can be told apart from a re-roll.

## Success and non-goals

This project keeps one Markdown record per change in `docs/engineering/`, plus a
JSON file per change under `.engineering/` holding its metadata. Fifty-two such
documents existed and nothing listed them.

Success: a generated index at `docs/engineering/README.md` lists every change
with its title, risk tier, closed state and links to each document it produced;
the top-level `README.md` links it; adding a record without regenerating fails
the test suite; every link resolves from the index's own directory.

Not attempted: rewriting the existing records, which a separate readability
review covered; a glossary, which that review argued against because the
definitions already exist in this project's reference documents and need linking
rather than copying; and narrowing `status` to open work only, which stays.

## Existing responsibilities searched

Nothing new was invented.

`list_evidence` (`evidence.py:136`) already returns each change's identifier,
title, risk tier, closed state and document paths, so the index needs no new
stored field and no new entry in `.engineering/contract.json`, this project's
per-repository configuration file. `handoff_text` (`cli.py:794`) already renders
Markdown and writes it to a path. `command_status` (`cli.py:658`) already walks
the same records and handles the closed case.

The test keeping the index honest follows `ValidationRecordCase` and
`CommittedArtifactCase` in `tests/test_evals.py`, each of which holds a
different generated list current by regenerating it during the test and failing
on any difference. This is the third use of that pattern, not a new mechanism.

## System and data flow

`index_rows` reads every per-change JSON file, then separately scans the
decision-document directory for files no change claims. `index_text` renders
those rows as one line per change or as a Markdown table, rewriting each link
relative to the index's own directory via `link_from`. `command_index` prints,
or writes when `--write` is given. Two existing `status` flags, `--due` and
`--all`, gained help text they never had.

The scan for unclaimed files exists because of a failure this project produced
during the audit that prompted the work, and the risk tiers are needed to
explain it. Every change is assigned a tier from R0 to R3 at the start; the tier
judges how much could go wrong and decides which documents the change must
produce — R0 and R1 a brief only, R2 a decision record naming the rejected
alternative, R3 also a runbook and a threat model. `artifact_paths` turns a tier
into the document paths that change is allowed to have.

During the audit a decision record was written for a change classified R1.
Because `artifact_paths` allocates a decision document only from R2 upward, that
file had no slot in its own change's document set: it existed on disk and no
command could name it — not the one that explains a change, not the one that
checks cross-references, not the one that lists status. Fifty-one of fifty-two
documents were reachable from the stored metadata; that one was not. An index
built only from that metadata would have reproduced the blind spot it was
written to remove.

## Failure, security, and recovery

The failure that matters is an index that has fallen behind and still passes,
because a stale list that looks maintained is worse than an obviously missing
one. The test regenerates the index during the run and compares it to the
committed file, so a change since closed cannot go on being listed as open.

This reads and writes only inside the repository and adds no network access, no
new configuration and no new stored data, so it opens no new path for untrusted
input. Recovery from a bad index is regenerating it; nothing depends on the
file's contents except readers.

## Verification evidence

- `python3 -m unittest discover -s tests`: 88 tests pass, up from 83, with five
  added and none modified.
- The guard was proved by breaking it. A decision document that no change claims
  was added to `docs/engineering/decisions/`; the suite failed, naming the file.
  Removing it made the suite pass again.
- All 58 links in the generated index were resolved from the directory the index
  lives in. All 58 resolved.
- The four commands this repository declares as its verification contract were
  run through `engineering verify` and all four passed.

## Known limits and learning gaps

The index has a row per change and a row per unclaimed decision document. A
runbook or a threat model appears only as a link inside its change's row. So an
orphaned runbook — one belonging to no change — would be caught by the guard
that checks every document is named, but would have no row of its own. No such
file can currently exist, because the risk tiers only allocate a runbook to an
R3 change, which by definition has a change record to hang it from. That is an
argument from the current tier rules, not a guarantee: if a future tier allocated
a runbook without a record, this gap would open.

The guard checks that every change is named in the index and that regenerating
the index changes nothing. It does not check that a row is *correct* beyond
that. A title that misdescribes its own change passes.
