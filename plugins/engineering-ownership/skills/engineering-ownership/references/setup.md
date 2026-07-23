# Setup

Setup is a preview-and-approval transaction, not an automatic write.

1. Inspect the repository's package manifests, CI workflows, existing agent
   instructions, test/build scripts, security-sensitive paths, and hooks.
2. Prepare one preview containing:
   - proposed verification argv and timeouts;
   - R2/R3 path patterns;
   - contract project metadata;
   - AGENTS.md and CLAUDE.md pointer additions;
   - `session_hooks: off` or the optional `remind` setting.
3. Show the exact proposed files and explain any uncertain command.
4. Make no changes until the user approves the preview once.
5. After approval, apply the contract, handoff ignore file, pointers, and the
   chosen hook setting in one bounded setup.
6. Run `engineering doctor` without executing verification commands.

`engineering init --agent-pointers` is a low-level helper. The agent remains
responsible for replacing generic verification and risk paths with
repository-specific values after approval.

Hooks default to `off`. Choose `remind` only when the user explicitly accepts
session-start and stop reminders. Hook trust or activation failure must never
disable the skill or CLI.
