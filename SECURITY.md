# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.2.x | Yes |
| 0.1.x | Security fixes only |
| pre-release prototypes | No |

## Report a vulnerability

Please use GitHub's private vulnerability reporting for this repository:

`Security` → `Advisories` → `Report a vulnerability`

Do not include secrets, private source code, or personal data in a public issue.
If private reporting is unavailable, open a public issue containing no exploit
details and ask the maintainer for a private channel.

You should receive acknowledgment within seven days. Release timing depends on
severity and whether downstream installations need coordinated updates.

## Security invariants

- Installing the plugin executes no project verification command.
- Bundled hooks are no-op unless a repository explicitly opts into reminders.
- Reminder hooks never block, write, execute verification, use the network, or
  send telemetry.
- Verification requires an explicit CLI invocation.
- Contract commands use argv arrays with no shell.
- Stored evidence excludes command output, environment values, and absolute
  home paths.
- Writes remain inside the Git repository and reject symlink traversal.
- The project has no telemetry or network transmission in v0.2.

Repository content, contracts, and instruction files are untrusted input. They
cannot override user authorization, system policy, or these invariants.

See [docs/security/threat-model.md](docs/security/threat-model.md).
