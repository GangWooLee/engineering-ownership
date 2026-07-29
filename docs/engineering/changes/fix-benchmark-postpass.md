# 2026-07-25 · Deliver the promised post-pass for the vendored aggregator

Change ID: `fix-benchmark-postpass`
Created: `2026-07-25T23:53:03+09:00`
Risk: R1

## Problem and intended outcome

`defensible-skill-evaluation` recorded that the vendored aggregator "needs a
post-pass. It mislabels the eval count and reports a character count where
tokens belong" — and the post-pass was never built. The mechanism: the
aggregator reads real tokens only when timing is missing from grading.json, and
this runner always embeds timing, so the `output_chars` fallback fires on every
run. The one committed benchmark it produced (iteration-2, a disclaimed pilot)
printed "Tokens 1685 vs 1486" where the true counts are 3,254,669 and 725,974
— off by three orders of magnitude — and "Evals: 6 (3 runs each)" for one run
of eval 6. Aggregating iteration-7 without the post-pass would repeat both
mislabels in the artifact meant to carry the first defensible efficacy claim.

Intended outcome: a corrected benchmark.json/benchmark.md pair whose token
figures come from timing.json and whose run count is counted, not assumed.

## Success and non-goals

Success: `fix_benchmark.py iteration-2` yields tokens 3,254,669 / 725,974,
runs_per_configuration 1, delta +2528695; a regression test fails any committed
benchmark whose token figures disagree with its timing records.

Non-goals: editing the vendored file (PROVENANCE.md forbids it; the digest test
enforces it); recomputing pass rates or times (the aggregator gets those right).

## Existing responsibilities searched

The vendored module's own `calculate_stats` and `generate_markdown` are imported
and reused, so the corrected output keeps the exact upstream format and no
rendering logic is duplicated. This is the "adapt it in our own scripts
alongside" arrangement PROVENANCE.md prescribes.

## System and data flow

vendored aggregate_benchmark.py → benchmark.json/md → `fix_benchmark.py
<iteration>` rewrites: per-run `result.tokens` from each run's timing.json,
per-config token stats via `calculate_stats`, `delta.tokens` in the upstream
`+.0f` format, `runs_per_configuration` counted from run entries, an optional
note appended (used to stamp the pilot disclaimer inline into iteration-2's
benchmark.md, which previously carried no warning of its own).

## Decisions and trade-offs

Post-pass over fork: forking the aggregator would silence upstream drift that
the digest test is designed to surface. The post-pass leaves a `corrected`
marker in metadata so a reader can tell a corrected benchmark from a raw one.

## Failure, security, and recovery

If the post-pass is skipped, the new
`test_committed_benchmarks_report_tokens_from_timing_records` fails on the
committed artifact, naming the fix. Local files only; no network, no secrets.

## Verification evidence

- `python3 scripts/eval/fix_benchmark.py engineering-ownership-workspace/iteration-2 "Pilot data. …"`:
  tokens 3254669.0 / 725974.0, runs_per_configuration 1, delta +2528695,
  pilot note rendered under "## Notes" in benchmark.md.
- `python3 -m unittest discover -s tests`: 72 tests pass (new regression test
  included; it verifies iteration-2's committed values against timing.json).

## Known limits and learning gaps

`executor_model`/`analyzer_model` still render as `<model-name>` placeholders —
upstream behavior, out of scope here; the model id lives in run_meta.json and
preflight.json.

## References

- `scripts/eval/fix_benchmark.py`
- `scripts/eval/vendor/PROVENANCE.md` (adapt-alongside policy)
- `docs/engineering/changes/defensible-skill-evaluation.md` (the recorded, unmet need)
