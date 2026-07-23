# 2026-07-23 · v0.1.0 public release

Change ID: `v0-1-0-public-release`
Created: `2026-07-23T09:57:33+00:00`

## Signals and alerts

Treat manifest validation failure, checksum mismatch, unexpected network
activity, evidence containing logs or home paths, command execution during
installation, or a write outside the repository as a release-blocking signal.

## Safe diagnosis

Reproduce in a disposable Git repository with no credentials. Inspect the
exact plugin tag, ZIP checksum, contract argv, evidence JSON, and resolved path.
Do not paste private code or full command output into an issue.

## Rollback or repair

Remove the installed clients and CLI:

```bash
codex plugin remove engineering-ownership@engineering-ownership
claude plugin uninstall engineering-ownership@engineering-ownership --scope user
uv tool uninstall engineering-ownership
# or: pipx uninstall engineering-ownership
```

These commands do not delete repository evidence or application code. Restore
the repository contract from reviewed source control. For a migrated v1
contract, copy `.engineering/contract.v1.backup.json` back only after reviewing
the current state. Re-run verification from a trusted checkout and do not reuse
pre-rollback results.

## Escalation and data handling

Use GitHub private vulnerability reporting. Do not commit secrets or exploit
details. Coordinate a patched tag and advisory before public disclosure when
downstream users need time to update.
