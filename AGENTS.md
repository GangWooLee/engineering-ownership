# Repository instructions

<!-- engineering-ownership:start -->
Use the installed `engineering-ownership` skill and
`.engineering/contract.json` for non-trivial changes.
<!-- engineering-ownership:end -->

This repository is security-sensitive because it executes repository-defined
verification commands and writes evidence. Preserve these project rules:

- Python 3.11+ standard library only at runtime.
- No shell execution, blocking hooks, MCP, telemetry, or network calls.
- Bundled hooks must remain opt-in reminders: no writes, verification,
  termination blocking, network, or telemetry.
- All writes must stay inside the Git repository and reject symlink traversal.
- Do not store full command output, environment values, secrets, or home paths.
- Keep Codex and Claude plugin versions and the package version aligned.
