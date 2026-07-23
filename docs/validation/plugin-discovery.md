# Plugin and skill discovery

Checked on 2026-07-23.

## Agent Skills

The shared skill passed the official `skills-ref validate` command using
`agentskills/agentskills` commit
`38a2ff82958afee88dadf4831509e6f7e9d8ef4e`.

## Codex

In an isolated `CODEX_HOME`:

- the local repository marketplace loaded successfully;
- `engineering-ownership@engineering-ownership` installed as version `0.1.0`;
- `codex plugin list` reported it enabled.

A model-backed `codex exec` probe reached session startup but could not sample
because the isolated home had no OpenAI authentication. This is an
authentication limitation, not a claimed runtime discovery pass.

## Claude Code

In an isolated `CLAUDE_CONFIG_DIR`:

- the local marketplace loaded and the plugin installed as version `0.1.0`;
- `claude plugin validate --strict .` passed;
- `claude plugin details` found exactly one skill,
  `engineering-ownership`;
- the inventory contained zero agents, hooks, MCP servers, and LSP servers.

