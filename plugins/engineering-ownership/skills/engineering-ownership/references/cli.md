# CLI reference

```text
engineering init [--agent-pointers]
engineering audit [--format text|json]
engineering change start <id> --risk R1|R2|R3 [--competency <tag>]
engineering verify <id> [--id <command-id>]
engineering check [--mode advise|enforce] [--change <id>]
engineering explain <id>
engineering change review <id> --status passed|gaps [--gap <text>]
engineering status [--due]
engineering handoff [--change <id>] [--output <repo-relative-path>]
engineering contract migrate [--write]
```

The CLI writes only within the current Git repository, rejects symlink and path
escapes, stores no full command output, and sends no telemetry or network data.
Review contract commands before invoking `verify`.

