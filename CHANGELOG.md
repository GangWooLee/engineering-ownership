# Changelog

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
