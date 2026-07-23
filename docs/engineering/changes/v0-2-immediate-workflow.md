# 2026-07-23 · Engineering Ownership v0.2 immediate workflow

Change ID: `v0-2-immediate-workflow`
Created: `2026-07-23T11:43:43+00:00`

Risk: R3
Status: In progress

## Problem and intended outcome

The v0.1 workflow exposes a correct but CLI-heavy lifecycle. Users must remember
the order of setup, change, verification, check, and handoff commands, and the
workflow does not yet preserve dated titles, upward-only risk escalation,
code-to-decision integrity, or ignored handoffs. The intended result is one
skill entry point that routes the lifecycle while keeping the product limited
to decision, verification, operational ownership, and session recovery.

The user's initial constraints are: preserve contract v2 and evidence v1,
remain independent of gstack/Superpowers/OpenSpec/Compound/planning-with-files,
make hooks opt-in reminders only, keep R0 lightweight, add no MCP, telemetry,
dashboard, auto-update, or broad multi-host framework.

## Success and non-goals

Success means a user can request work, resume it, or check it with the single
skill; setup previews all writes before approval; declared risk never falls;
changed paths can require explicit upward escalation; dated records and
decision references remain valid; a saved handoff does not alter the diff
digest; and doctor/hooks disclose no secrets or home paths.

Non-goals are TDD, planning, product review, automatic releases, autonomous
loops, mandatory comments, or generalized host adapters.

## Existing responsibilities searched

The existing CLI parser, evidence validator, repository-safe write helper,
contract classifier, templates, diff digest, shared Agent Skill, release
builder, and plugin manifests remain their canonical owners. New behavior is
added to those owners rather than creating parallel scripts. Framework outputs
remain canonical in their own repositories and are linked from Briefs.

## System and data flow

Natural-language requests enter the shared skill router and select setup,
start, resume, check, handoff, or study. The bundled CLI reads the validated
contract and evidence, computes effective risk as the maximum of declared,
path-detected, and explicit risk, and writes only repository-relative records.
Verification results remain bound to the current diff digest.

Optional host events invoke one bundled read-only hook. It reads the event cwd,
finds the Git root, validates the contract, and exits immediately unless
`automation.session_hooks` is `remind`. SessionStart reads bounded status; Stop
runs advise-only check. Neither path invokes `verify`.

## Decisions and trade-offs

See [the v0.2 ADR](../decisions/v0-2-immediate-workflow.md). One router with
progressive references was selected over multiple public workflow commands.
Optional no-op hooks were selected over per-tool automation. Evidence v1 gains
only optional fields rather than a migration.

## Failure, security, and recovery

Primary failures are malicious path references, stale verification accepted
after risk changes, hook activation without consent, host termination blocking,
secret leakage from diagnostics, and handoff writes invalidating evidence.
Path validation, upward-only risk, no-op activation, exit-zero hook behavior,
bounded redacted diagnostics, and Git-ignored handoffs address these risks.
Rollback is removal of hook declarations and v0.2-only commands while keeping
existing contract/evidence records readable.

## Verification evidence

The unit suite covers risk floors, escalation, dated titles, canonical and
broken/superseded references, handoff digest stability, doctor redaction, and
hook off/remind behavior. Distribution checks validate the single router,
bundled hook surface, manifests, schemas, and release archive. Host plugin
validation and fresh install checks are required before release.

## Known limits and learning gaps

Plugin hosts may disable or decline trust for hooks; the skill and CLI must
remain sufficient. `doctor` can only report whether host plugin listings expose
the package and does not prove implicit skill selection quality. The setup
preview is agent behavior described by the skill, not an autonomous CLI
configuration detector.

## References

- [Workflow comparison](../../research/2026-07-23-workflow-comparison.md)
- [Codex plugin hooks](https://learn.chatgpt.com/docs/build-plugins)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Agent Skills specification](https://agentskills.io/specification)
