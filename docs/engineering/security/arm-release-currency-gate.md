# 2026-07-26 · Fail a tag whose release notes predate shipped content

Change ID: `arm-release-currency-gate`
Created: `2026-07-26T10:52:39+09:00`
## Assets and trust boundaries

The published release (notes + attested archive) is the asset — it is the one
surface external users consume without reading the repository. The gate runs
inside the existing release job with the permissions it already had; no new
token, secret, or permission is introduced. `fetch-depth: 0` widens what the
job reads (full history), not what it can write.

## Attacker-controlled inputs

The tag name (existing input, already validated against `pyproject.toml`) and
commit timestamps. An author can trivially defeat the timestamp comparison by
touching the notes file without updating it — the gate raises the cost of
publishing a stale document from zero to a deliberate act, which is the
realistic threat here (drift, not malice).

## Security invariants

- The gate can only block a release, never alter its contents.
- `subprocess` is invoked with a fixed argv and no shell, matching the
  repository's execution policy.
- A degraded environment (shallow clone, missing git) passes rather than
  producing a spurious hard failure that would invite a manual bypass — the
  manual bypass being exactly how v0.2.0 got hand-published.

## Abuse and failure cases

- Backdated commits could sneak stale notes past the comparison: accepted;
  the threat model is accidental drift by the author, not self-deception via
  history forgery, which no local check can prevent.
- A blocked legitimate release: recover by amending notes and re-tagging;
  nothing is published in the blocked state.

## Mitigations and residual risk

Residual risk is the untested stale-refusal branch (see the Brief's known
limits) and the touch-without-updating bypass above. Both fail toward "author
must act deliberately," which is the intended posture.
