# 2026-07-23 · Workflow repository comparison

## Question

How should Engineering Ownership become immediately usable without expanding
into another full planning, TDD, review, or autonomous-agent framework?

## Findings and decisions

| Reference | Useful pattern | Adopted | Deliberately not adopted |
| --- | --- | --- | --- |
| [gstack](https://github.com/garrytan/gstack) | Obvious first action, scenario-led onboarding, setup diagnostics | One router, one-sentence start, tutorial, doctor | Auto-update, telemetry, full shipping workflow |
| [Superpowers](https://github.com/obra/superpowers) | Skills selected by intent; disciplined planning, TDD, debugging, verification | Broad R1+ trigger and progressive references | Reimplementation of its development skills |
| [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) | Continuous plan/work/review/compound loop and transferable handoff | Lifecycle routing and handoff pointers | Treating learned solutions as architectural decisions |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | Change-scoped proposal/design/tasks and archive | Stable change IDs and links to canonical artifacts | A duplicate spec lifecycle |
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files) | Durable task state for session recovery | Resume from files rather than chat memory | Per-tool hooks and duplicated task state |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Concise setup and user-facing skill entry points | Small router with detailed references on demand | Multiple public commands for one ownership lifecycle |
| [ECC](https://github.com/affaan-m/ECC) | Broad host adapters and automation surface | Confirmation that portability matters | Large multi-host adapter matrix |
| [loopy](https://github.com/Forward-Future/loopy) | Bounded feedback loops and explicit stopping conditions | Risk gates and finite verification/handoff | Autonomous recursive execution |

## Resulting boundary

Engineering Ownership owns:

- why a consequential implementation decision exists;
- which exact diff was verified;
- which operating, recovery, and security knowledge must survive;
- how another session resumes without reconstructing chat.

Planning, TDD, browser QA, product review, and learned-solution capture remain
owned by the framework that produced them. The Brief links those artifacts
instead of copying them.

## Hook decision

Session hooks are useful only as bounded reminders. They are packaged for
Codex and Claude but default to no-op at the repository contract. In `remind`
mode, SessionStart reports current/stale context and Stop reports advise-only
check output. They never block, write, execute verification, use the network,
or send telemetry.

## Reconsideration conditions

Revisit the single-router boundary only if repeated real projects show that
users cannot complete setup-to-handoff without separate entry points. Revisit
additional hosts only after Codex and Claude installations are stable and a
maintainer can own host-specific security behavior.
