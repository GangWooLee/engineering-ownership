# 2026-07-23 · Engineering Ownership v0.2 immediate workflow

Change ID: `v0-2-immediate-workflow`
Created: `2026-07-23T11:43:43+00:00`

Status: Accepted

## Context

The project needs an immediate-use entry point and session reminders without
becoming a complete development framework or weakening explicit execution and
path-safety boundaries.

## Options considered

1. Add separate public skills for every lifecycle phase.
2. Build an autonomous framework with per-tool hooks and automatic checks.
3. Keep one router skill, a compatible CLI, and opt-in bounded reminders.

## Decision

Choose option 3. The shared skill routes setup/start/resume/check/handoff/study
and progressively loads phase references. The CLI remains the deterministic
repository adapter. Effective risk is the maximum of declared, detected, and
explicit risk, and can only be raised. Hook code is packaged but executes
meaningful work only for validated `session_hooks: remind`; it cannot block or
write.

## Consequences and reversal

Users get one stable mental model and existing framework artifacts remain
canonical. The cost is a larger shared skill and an additional trusted hook
surface. That surface is constrained to two events and offline read-only
behavior. Reversal removes `hooks/hooks.json` and the automation setting without
invalidating contract v2 or evidence v1.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/model.py`
- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `plugins/engineering-ownership/hooks/ownership_hook.py`
- `plugins/engineering-ownership/skills/engineering-ownership/SKILL.md`

## Supersession

Supersedes: None
Superseded by: None
