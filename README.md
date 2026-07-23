# Engineering Ownership

[한국어](README.ko.md)

AI can produce code faster than people can build a mental model of it.
Engineering Ownership keeps the decisions, verification, operating knowledge,
and handoff needed to understand, explain, maintain, and safely change what
ships.

It is an accountability layer, not another planning, TDD, review, or agent
framework. It links those tools' outputs instead of copying them.

## Install

### Codex

```bash
codex plugin marketplace add GangWooLee/engineering-ownership
codex plugin add engineering-ownership@engineering-ownership
```

Codex asks you to review plugin hooks. The hooks are reminders only and are a
complete no-op unless a repository explicitly sets `session_hooks: remind`.

### Claude Code

```text
/plugin marketplace add GangWooLee/engineering-ownership
/plugin install engineering-ownership@engineering-ownership
```

Claude can also invoke the skill as
`/engineering-ownership:engineering-ownership`. Natural-language implicit use
is the primary workflow.

The plugin bundles its CLI for the skill to invoke directly; it does not need
to be globally on your shell `PATH`. Separate CLI-only installation is
optional:

```bash
uv tool install git+https://github.com/GangWooLee/engineering-ownership.git
# or
pipx install git+https://github.com/GangWooLee/engineering-ownership.git
```

## Start in one sentence

```text
$engineering-ownership work on this feature
$engineering-ownership continue the previous work
$engineering-ownership check this before merge
```

The skill routes setup, new work, resume, check, handoff, and optional study.
You do not need to memorize the CLI.

## A real first-work scenario

You ask: `$engineering-ownership add session revocation`.

1. The skill sees that the repository is not configured. It inspects CI,
   package scripts, sensitive paths, and agent instructions, then shows one
   setup preview. Nothing is written before your approval.
2. After approval, it creates the repository contract and pointers, then runs
   `engineering doctor` without executing project tests.
3. Authentication makes the change R3. A dated Brief, ADR, Threat Model, and
   Runbook preserve the problem, alternatives, failure modes, and recovery.
4. The agent implements in reviewable units. A code comment links the ADR only
   where a non-obvious security invariant is enforced.
5. Reviewed test commands run explicitly. Their results are bound to the exact
   current diff; an old green result cannot pass.
6. Before merge, reference integrity and risk-proportional evidence are checked.
7. A saved handoff lets a new session resume from repository state rather than
   reconstructed chat memory.

See the complete [first-work tutorial](docs/tutorials/first-work.md).

## What v0.2 includes

- One Agent Skill router for setup, start, resume, check, handoff, and study.
- A tool-neutral R0–R3 risk model; declared risk is always a floor.
- Dated Briefs, ADRs, Threat Models, and Runbooks.
- Optional code-to-ADR references with integrity checking.
- Current-diff verification using reviewed argv arrays and no shell.
- `doctor`, risk escalation, ignored saved handoffs, and non-blocking reminders.
- Codex and Claude plugin packages using one shared skill and bundled CLI.

R0 documentation corrections remain lightweight. Local checks default to
`advise`; only explicitly configured CI should use `enforce`.

## Low-level CLI

```text
engineering doctor
engineering change start <id> --risk R1|R2|R3 --title "<title>"
engineering change set-risk <id> --risk R2|R3
engineering verify <id>
engineering refs check --change <id>
engineering check --mode advise --change <id>
engineering handoff --change <id> --save
```

The full interface is in the
[CLI reference](plugins/engineering-ownership/skills/engineering-ownership/references/cli.md).

## Evidence, not scores

Eight tags describe exercised work: requirements, system/data flow, code
responsibility and reuse, testing/debugging, security/privacy,
reliability/recovery, delivery/change management, and explanation/handoff.
They are not a maturity or competence score.

Canonical knowledge remains separated:

- change Brief: one change's intent, flow, trade-offs, evidence, and limits;
- ADR: a significant, long-lived decision and its supersession;
- code comment: a non-obvious local invariant and ADR pointer;
- Runbook: signals, diagnosis, mitigation, and recovery;
- handoff: current state and links, not another design document.

## Safety

- Installing the plugin runs no project command.
- Optional hooks perform no work unless the repository opts into `remind`.
- Reminder hooks never block, modify files, run verification, use the network,
  or send telemetry.
- Verification is explicit, uses `shell=False`, bounded timeouts, and a limited
  environment.
- Evidence never stores full command output or environment values.
- Writes are repository-relative and reject traversal and symlink paths.

Read [SECURITY.md](SECURITY.md) and the
[threat model](docs/security/threat-model.md).

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_distribution.py
claude plugin validate --strict .
```

See [CONTRIBUTING.md](CONTRIBUTING.md), the
[workflow comparison](docs/research/2026-07-23-workflow-comparison.md), and the
[integration rules](plugins/engineering-ownership/skills/engineering-ownership/references/integrations.md).

## License

MIT
