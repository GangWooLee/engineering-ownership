# Harness validation, not a result

One run per configuration on one scenario. The pass rates in `benchmark.md` are
not a measurement: n=1 gives a standard deviation of zero by construction.

This iteration exists to show the changed harness working: runs may now write,
the judge is shown an ordered record of what each run did instead of the
transcript, and the blinding check found no way to tell the configurations
apart from that record.

It also did its job as a check on the expectations. The judge reported that one
of them bundled two behaviours and created a tension - correct practice for
superseding a decision *requires* editing the earlier record's status, so
"leaves the original intact" read as forbidding the right answer. That
expectation has since been split. The grading here was produced against the
unsplit wording.
