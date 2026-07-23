# Engineering change: v0-1-0-public-release

Risk: R3

## User reasoning

AI can produce working code faster than a developer can build a durable mental
model. The project must preserve the human's problem framing, system decisions,
fresh verification, explanation, and recovery knowledge without turning those
signals into a false maturity score or a mandatory oral examination.

The first release must be tool-neutral, usable from Codex and Claude, and safe
to run in an untrusted repository. It may execute only explicitly requested,
reviewed argv commands, must keep writes in the repository, and must not retain
logs, secrets, environment values, or absolute home paths.

## Success and non-goals

Success means the public repository installs as a Python 3.11+ CLI and as both
plugin formats; R0 remains lightweight; R2/R3 enforce missing current-diff
evidence; v1 stays readable and migrates only with an explicit write.

PyPI, official marketplace submission, hooks, MCP, telemetry, dashboards, and
competency scores are excluded from v0.1.

## Existing responsibilities searched

The private prototype supplied the risk vocabulary and understanding-review model.
Its monolithic CLI, string shell commands, score-like audit, default agent-file
editing, and test-file-presence gate were not reused. Agent Skills, current
Codex plugin, and Claude plugin structures are used as external interface
standards rather than duplicated conventions.

## System and data flow

The repository contract declares command IDs, argv, literal safe environment,
timeouts, risk paths, and artifact locations. A change record binds reasoning,
artifacts, command outcomes, and optional understanding state to a digest of
the current working tree. `check` compares the live digest to stored evidence;
`handoff` renders only repository-relative state and canonical document links.

## Alternatives and trade-offs

A hosted service would centralize analytics but require network access,
identity, privacy policy, and data retention. A pure Markdown workflow would be
portable but could not prove that verification ran on the current diff. The
selected local CLI keeps evidence inspectable and offline while accepting that
self-attested understanding still requires reviewer judgment.

## Failure, security, and recovery

Primary risks are repository-controlled command execution, path or symlink
escape, secret leakage from logs or environment, stale evidence, prompt
injection through repository instructions, and compromised release artifacts.
Controls are documented in the repository threat model and exercised by tests.
Recovery is removal of the plugin/CLI, restoration of the v1 backup, and
re-verification from a trusted checkout.

## Verification plan

Run unit/integration tests on Python 3.11–3.13 and macOS/Ubuntu, validate both
manifests, build a deterministic ZIP and SHA-256, exercise paired skill/baseline
evaluations, test fresh Codex/Claude discovery, and run read-only v1
audit/checks against KeyBox, COOA, and Undrew.

## Known limits and learning gaps

The digest represents the local working tree rather than the runtime artifact.
Understanding review is optional and self-attested. Claude and Codex discovery
can change between client versions. GitHub attestation proves workflow
provenance, not semantic correctness. These limits are visible rather than
converted into a score.
