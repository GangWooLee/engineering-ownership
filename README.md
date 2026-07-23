# Engineering Ownership

[한국어](README.ko.md)

Engineering Ownership is an evidence layer for people who build software with
AI but still want to understand, explain, operate, and maintain what ships.

It connects four things that often drift apart:

1. the human's initial reasoning;
2. the system and data-flow decision;
3. verification run against the exact current diff;
4. a no-AI teach-back and future review date.

It is not a best-practices encyclopedia, code generator, autonomous reviewer,
agent framework, or productivity score. It does not claim that more documents
mean more competence.

## What v0.1 includes

- A tool-neutral R0–R3 risk model and eight evidence tags.
- A Python 3.11+ standard-library CLI.
- One shared [Agent Skill](https://agentskills.io/specification).
- Codex and Claude Code plugin manifests and marketplace catalogs.
- Local `advise` and explicit CI `enforce` modes.
- No hooks, MCP server, telemetry, dashboard, or network transmission.

## Install

### Codex

```bash
codex plugin marketplace add GangWooLee/engineering-ownership
codex plugin add engineering-ownership@engineering-ownership
```

Start a new session after installation. The plugin contributes the
`engineering-ownership` skill.

### Claude Code

```text
/plugin marketplace add GangWooLee/engineering-ownership
/plugin install engineering-ownership@engineering-ownership
```

For local development:

```bash
claude --plugin-dir ./plugins/engineering-ownership
```

### CLI from GitHub

```bash
uv tool install git+https://github.com/GangWooLee/engineering-ownership.git
# or
pipx install git+https://github.com/GangWooLee/engineering-ownership.git
```

For contributors:

```bash
uv tool install --editable .
```

### Uninstall or roll back

Removing the tools does not delete repository evidence or application code:

```bash
codex plugin remove engineering-ownership@engineering-ownership
claude plugin uninstall engineering-ownership@engineering-ownership --scope user
uv tool uninstall engineering-ownership
# or, when installed with pipx:
pipx uninstall engineering-ownership
```

Restore a tracked `.engineering/contract.json` from reviewed source control. If
v1 was migrated, review and restore
`.engineering/contract.v1.backup.json`, then verify again from a trusted
checkout. Do not reuse old verification results after rollback.

## Quick start

```bash
engineering init
# Review .engineering/contract.json and replace the sample argv command.

engineering change start refresh-session \
  --risk R3 \
  --competency security-privacy \
  --competency testing-debugging

engineering verify refresh-session
engineering check --mode advise --change refresh-session
engineering explain refresh-session
engineering change review refresh-session --status passed
engineering handoff --change refresh-session
```

`engineering init` only creates the contract. It edits `AGENTS.md` and
`CLAUDE.md` only when `--agent-pointers` is explicitly supplied.

## Evidence, not scores

The eight tags are:

- problem framing and requirements;
- system and data-flow design;
- responsibility, reuse, and code design;
- testing and debugging;
- security and privacy;
- reliability, observability, and recovery;
- Git, delivery, and change management;
- explanation, review, and handoff.

`engineering status` shows what was exercised, what remains unexplained, and
what is due for review. It never produces a maturity score.

## Safety model

- Contract commands are argv arrays executed with `shell=False`, bounded
  timeouts, and a limited environment.
- `verify` is always an explicit action; installing the plugin runs nothing.
- Evidence contains command IDs and outcomes, never full logs or environment
  values.
- Writes are repository-relative and reject path traversal and symlink paths.
- Passing verification is tied to the current working-tree digest.
- Contract v1 is readable but must be explicitly migrated before execution.

Read [SECURITY.md](SECURITY.md) and the
[repository threat model](docs/security/threat-model.md) before changing command
execution or path handling.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_distribution.py
claude plugin validate --strict .
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Workflow-principle changes require a
real case, before/after behavior, and evaluation evidence.

## Standards and references

- [Agent Skills specification](https://agentskills.io/specification)
- [Codex plugin structure](https://developers.openai.com/codex/plugins/build)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)

## License

MIT
