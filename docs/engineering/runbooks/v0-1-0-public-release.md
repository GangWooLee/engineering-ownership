# Runbook: v0-1-0-public-release

## Signals and alerts

Treat manifest validation failure, checksum mismatch, unexpected network
activity, evidence containing logs or home paths, command execution during
installation, or a write outside the repository as a release-blocking signal.

## Safe diagnosis

Reproduce in a disposable Git repository with no credentials. Inspect the
exact plugin tag, ZIP checksum, contract argv, evidence JSON, and resolved path.
Do not paste private code or full command output into an issue.

## Rollback or repair

Disable or uninstall the plugin, uninstall the CLI tool, and restore the
repository contract from source control. For a migrated v1 contract, copy
`.engineering/contract.v1.backup.json` back only after reviewing the current
state. Re-run verification from a trusted checkout.

## Escalation and data handling

Use GitHub private vulnerability reporting. Do not commit secrets or exploit
details. Coordinate a patched tag and advisory before public disclosure when
downstream users need time to update.

