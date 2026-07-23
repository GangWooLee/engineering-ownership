# Repository instructions

Use the installed `engineering-ownership` skill and
`.engineering/contract.json` for non-trivial changes.

This repository is security-sensitive because it executes repository-defined
verification commands and writes evidence. Preserve these project rules:

- Python 3.11+ standard library only at runtime.
- No shell execution, automatic hooks, MCP, telemetry, or network calls.
- All writes must stay inside the Git repository and reject symlink traversal.
- Do not store full command output, environment values, secrets, or home paths.
- Keep Codex and Claude plugin versions and the package version aligned.

