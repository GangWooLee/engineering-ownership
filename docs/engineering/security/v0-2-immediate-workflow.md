# 2026-07-23 · Engineering Ownership v0.2 immediate workflow

Change ID: `v0-2-immediate-workflow`
Created: `2026-07-23T11:43:43+00:00`

## Assets and trust boundaries

Assets are user source, uncommitted diffs, credentials available to developer
processes, evidence integrity, and the user's decision to trust/enable hooks.
Boundaries are repository input to CLI, host event JSON to hook, contract to
child verification process, and installed plugin to source release.

## Attacker-controlled inputs

Repository files, contract JSON, evidence, decision markers, paths, symlinks,
verification argv, hook stdin, current working directory, and plugin caches.

## Security invariants

- No shell execution or secret-like contract environment values.
- No project verification from install, doctor, SessionStart, or Stop.
- Hooks are no-op unless the validated contract says `remind`.
- Hooks exit zero and never block host termination.
- Writes remain inside the repository and reject symlink/path escape.
- Diagnostics and evidence exclude full logs, environment values, and absolute
  home paths.

## Abuse and failure cases

A malicious marker could escape the repository, a crafted contract could
activate hooks or execute a shell, a Stop hook could loop the agent, doctor
could leak CLI output, or a handoff could alter the diff. A sensitive path
could also appear after an R2 record and silently reuse weaker gates.

## Mitigations and residual risk

Canonical safe-path checks cover markers and implementation references.
Contract enums restrict hook activation. The hook supports only SessionStart
and Stop, is read-only, bounded to 20 lines, offline, and always non-blocking.
Doctor returns normalized local states rather than raw host output. Handoffs
must be ignored before save. Effective risk blocks verification until the
record is explicitly escalated.

Residual risk remains that an explicitly reviewed verification executable can
still be malicious, evidence can be manually edited, and host hook semantics
can change. CI and release validation detect known interface drift.
