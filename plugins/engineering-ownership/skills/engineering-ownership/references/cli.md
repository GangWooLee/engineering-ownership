# CLI reference

```text
engineering init [--agent-pointers]
engineering audit [--format text|json]
engineering doctor [--format text|json]
engineering change start <id> --risk R1|R2|R3 [--title <title>] [--competency <tag>]
engineering change set-risk <id> --risk R2|R3
engineering verify <id> [--id <command-id>]
engineering check [--mode advise|enforce] [--change <id>]
engineering refs check [--change <id>] [--all]
engineering explain <id>
engineering change review <id> --status reviewed|gaps [--gap <text>] [--revisit-days <days>]
engineering status [--due]
engineering handoff [--change <id>] [--save|--output <repo-relative-path>]
engineering contract migrate [--write]
```

The CLI writes only within the current Git repository, rejects symlink and path
escapes, stores no full command output, and sends no telemetry or network data.
Review contract commands before invoking `verify`.

`doctor` performs local presence and executable checks only. It does not run
verification commands or make network calls. `handoff --save` requires the
configured handoff directory to be ignored by Git.

`explain` and `change review` support optional study and retained-understanding
checks. Default `check` gates reasoning artifacts and current verification, not
the review status.
