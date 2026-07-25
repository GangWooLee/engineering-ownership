# Changelog

## Unreleased

### Changed

- Withdraw the published skill evaluation result. The "16 / 16 versus 5 / 16"
  comparison is retracted: the two configurations differed in language as well
  as skill availability, the grader matched on the skill's own vocabulary so no
  baseline could pass on merit, only four of eight evals were graded, four
  checks emitted a fixed evidence string regardless of outcome, there was one
  run per configuration, and the largest reported separation was credited to a
  mandatory teach-back that `documentation-first-workflow` removed. The number
  and its defects are preserved in `docs/validation/skill-evaluation.md`. The
  project publishes no quantitative efficacy claim until a defensible one
  exists.
- Give `docs/validation/` a status and supersession convention mirroring the one
  used for decision records, with an index at `docs/validation/README.md`.
  `plugin-discovery.md` is marked superseded by the v0.2 host validation.

### Removed

- `scripts/grade_skill_evals.py`. It could not run (it pointed at a workspace
  directory that does not exist), covered four of eight evals and raised for the
  rest, and graded by substring-matching the skill's own vocabulary.

### Added

- `tests/test_evals.py`, enforcing that the eval manifest stays English-only and
  internally consistent, that no grader hardcodes eval names or matches on the
  skill's private vocabulary, that every validation document declares a status,
  and that no efficacy number can be published without a committed artifact
  whose means match it.

### Fixed

- Record previously unlogged post-0.2.0 work: the versioned release-notes path
  fix, and the Git attribution rewrite with its verification.

## 0.2.0 - 2026-07-23

- Rework the shared skill into a single setup/start/resume/check/handoff/study
  router with progressive references and scenario-first onboarding.
- Add `doctor`, titled and dated change records, upward-only risk escalation,
  decision-reference integrity checks, and Git-ignored saved handoffs.
- Make declared evidence risk a floor and block verification when changed paths
  require an explicit higher risk.
- Add opt-in, non-blocking Codex and Claude reminder hooks that are no-op by
  default and never write, run verification, use the network, or block exit.
- Document zero-copy integration with gstack, Superpowers, Compound
  Engineering, OpenSpec, and planning-with-files.

## 0.1.0 - 2026-07-23

- Introduce the R0–R3 ownership workflow and eight competency evidence tags.
- Add the standard-library CLI with contracts, diff-bound verification,
  durable decision records, optional understanding reviews, status, handoff,
  and v1 migration.
- Read pre-release `teach_back` evidence and normalize it to optional
  `understanding` state on the next write.
- Add shared Codex and Claude Code plugin packaging.
- Add security, governance, contribution, CI, and release foundations.
