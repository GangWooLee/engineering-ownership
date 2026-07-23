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

After the public repository was added to the user's normal Codex marketplace:

- the plugin installed and remained enabled as version `0.1.0`;
- a fresh `codex exec` session named the `engineering-ownership` skill and
  summarized its evidence-based change and review purpose without reading
  repository files.

The earlier isolated-home model probe could not sample because that temporary
home had no OpenAI authentication. The authenticated normal-home probe is the
runtime discovery result.

## Claude Code

In an isolated `CLAUDE_CONFIG_DIR`:

- the local marketplace loaded and the plugin installed as version `0.1.0`;
- `claude plugin validate --strict .` passed;
- `claude plugin details` found exactly one skill,
  `engineering-ownership`;
- the inventory contained zero agents, hooks, MCP servers, and LSP servers.

After the public repository was added to the user's normal Claude marketplace:

- the plugin installed and remained enabled at user scope as version `0.1.0`;
- `claude plugin details` again found one skill and zero agents, hooks, MCP
  servers, and LSP servers.

A fresh model-backed Claude probe could not sample because the existing OAuth
session had expired and could not be refreshed. Component discovery and strict
validation passed, but model invocation remains explicitly unverified until
Claude authentication is renewed.
