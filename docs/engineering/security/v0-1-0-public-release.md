# 2026-07-23 · v0.1.0 public release

Change ID: `v0-1-0-public-release`
Created: `2026-07-23T09:57:33+00:00`

## Assets and trust boundaries

Assets are user source and uncommitted work, repository integrity, credentials
available to development processes, truthful verification evidence, and
release/install integrity. Trust boundaries exist between the user and agent,
repository content and the CLI, the CLI and child verification process, the
working tree and persisted evidence, and source control and plugin consumers.

## Attacker-controlled inputs

Repository contracts, filenames, symlinks, instruction files, command output,
pull requests, and downloaded plugin archives may be attacker controlled.

## Security invariants

Installation runs nothing. Verification is explicit, uses no shell, has a
bounded timeout and limited environment, and stores no output or environment
values. Writes are repository-relative and reject symlink traversal. A stale
digest cannot satisfy a current verification gate.

## Abuse and failure cases

An attacker may place `sh -c`, secret environment keys, path traversal, or
symlinks in a repository; print credentials into command output; edit code
after verification; inject agent instructions; or replace a release asset.

## Mitigations and residual risk

Validation rejects command shells, unsafe environment entries, path traversal,
and symlink paths. Evidence excludes output and absolute home paths. CI pins
actions and releases a SHA-256 plus provenance attestation.

Residual risk remains because any explicitly approved executable can run
arbitrary project code, a human can falsely self-attest understanding, and a
digest does not prove production equivalence.
