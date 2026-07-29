# 2026-07-29 · Give the engineering records an entry point

Change ID: `add-record-index`
Created: `2026-07-29T16:11:56+09:00`
Risk: R3

## Problem and intended outcome

Fifty-two records exist and only someone who already knows a change id can
reach them. An audit ran three reader journeys with real commands and counted
the steps:

- **"Why does the terminal close state exist?"** — no path. `README.md` carries
  eight links and not one reaches `docs/engineering/`. The CLI route is worse
  than absent: `engineering status` prints `No matching change records.`,
  because every record is closed, so the default view of a repository holding
  fifty-two record files says it has none. The escape hatch, `--all`, had no
  help string, and its meaning was written down in exactly one place —
  `references/resume.md:1` — which `README.md` does not link.
- **"Which paths are R3, and why?"** — six steps, one of them a guess between
  four plausible ids, because `status` prints no title. The title is stored in
  every evidence record and no command has ever printed it.
- **"What efficacy number is claimed?"** — three steps, no guess. It works for
  one reason: `CHANGELOG.md` names both the document and its index, and the
  index answers.

The third journey is the specification for the other two.

Intended outcome: a reader who knows no id reaches the record behind any change
in three steps, and the entry point cannot silently fall behind.

## Success and non-goals

Success: `docs/engineering/README.md` lists every change record with its title,
risk, state, and links to its documents; `README.md` links it; adding a record
without regenerating fails the suite; every link resolves from the index's own
directory.

Non-goals: rewriting existing records (a separate readability review produced
its own findings); a glossary — the same review concluded the definitions
already exist in the skill's references and need links, not copies; changing
what `status` shows to open work only, which is deliberate.

## Existing responsibilities searched

Nothing new was invented. `list_evidence` (`evidence.py:136`) already returns
id, title, risk, closed state, and artifact paths — the index needs no new
input and no new contract key. `handoff_text` (`cli.py:794`) already generates
markdown and writes it to a path. `command_status` (`cli.py:658`) already
iterates records and handles the closed case. The guard follows
`ValidationRecordCase` and `CommittedArtifactCase` in `tests/test_evals.py`,
which hold the other two indexes current; this is the third application of that
pattern, not a new mechanism.

## System and data flow

`index_rows` reads every evidence record, then scans the decisions directory
for documents no record claims. `index_text` renders either one line per record
or a markdown table, with every link rewritten relative to the index's own
directory by `link_from`. `command_index` prints, or writes when `--write` is
given. `status --due` and `status --all` gained the help strings they never had.

The orphan scan exists because of a failure this repository produced during the
audit itself: an ADR written under an R1 record has nowhere to live in that
record's artifact map, because `artifact_paths` allocates a decision document
only from R2 up. That file was reachable by `ls` and by nothing else — not
`explain`, not `refs check`, not `status`. Fifty-one of fifty-two documents
could be named from the evidence; that one could not. An index that only walked
the evidence would have reproduced the blind spot it was built to remove.

## Decisions and trade-offs

See `docs/engineering/decisions/add-record-index.md` — generated versus
hand-kept, and why the guard is not optional.

## Failure, security, and recovery

See the linked threat model and runbook. The failure that matters is a stale
index that still passes: covered by regenerating in the test and comparing, so
a closed record cannot keep being listed as open.

## Verification evidence

- `python3 -m unittest discover -s tests`: 88 tests pass (83 before, 5 added).
- Guard proved by breaking it: adding an unlisted document to
  `docs/engineering/decisions/` fails the suite; removing it passes again.
- All 58 links in the generated index resolve from `docs/engineering/`.
- The four contract commands pass via `engineering verify`.

## Known limits and learning gaps

The index lists change records and unclaimed decisions. Runbooks and threat
models appear only as links from their record's row, so an orphan runbook —
which the current risk tiers cannot produce — would be listed by the document
guard but have no row of its own.

The guard checks that every record is named and that regeneration is a no-op.
It does not check that the row is *right* beyond that; a title that misdescribes
its change will pass.

## References

- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `tests/test_docs.py`
- `docs/engineering/decisions/add-record-index.md`
