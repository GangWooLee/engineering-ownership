# Decision: v0-1-0-public-release

## Context

The same ownership model must work across stacks and two agent clients without
copying divergent skills or trusting arbitrary shell strings.

## Decision

Keep one plugin directory containing one Agent Skills-compliant skill and the
CLI source. Place a Codex manifest and Claude manifest alongside it, with
repository-root marketplace catalogs for each client. Use a Python standard
library package for both plugin-bundled and `uv`/`pipx` installation.

Represent commands as argv arrays with bounded timeouts. Bind only command ID,
outcome, duration, and timestamp to the current diff digest. Keep durable
reasoning in Markdown and machine state in JSON. Understanding review is an
optional learning signal, not a default completion gate.

## Alternatives considered

- Separate Codex and Claude implementations: rejected because rules would drift.
- Shell command strings: rejected because quoting and injection cannot be
  bounded safely.
- Automatic hooks: deferred because silent execution violates progressive
  adoption and complicates existing repository tooling.
- A maturity score: rejected because it would imply precision not supported by
  the evidence.

## Consequences and reversal

Plugin manifests and package versions must move together. Users must review and
configure their contract. The CLI can be removed without changing application
code; v1 migration preserves its original JSON for reversal.
