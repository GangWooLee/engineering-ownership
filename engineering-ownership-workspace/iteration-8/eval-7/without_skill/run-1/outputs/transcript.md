I'll check memory for context, then look at the repo to find the proposal and implementation plan.

No memory file yet. Let me look for the proposal and implementation plan documents in the repo.

Let me look at the existing tracking artifacts for the prior change to understand the convention this repo uses.

This repo uses the **engineering-ownership** tracking system (contract.json + docs/engineering/changes + decisions + evidence). There's a matching plugin installed locally with a CLI — let me check it so I use it correctly rather than hand-rolling the artifacts.

This matches exactly. Let me read the "start" and "resume" reference docs since this is a new change that already has proposal/plan and one step in progress.

It's on PATH as `engineering`. Let's check `engineering status` and `engineering change --help` for exact usage before starting the change record.

Now let's look at the generated templates and fill them in with the actual proposal/plan content.

Now let me fill in the Brief and ADR with the actual content from the proposal and plan.

Now let's run verification (unit tests) and bind it to this change's evidence, then check overall status.

The tracking record is fully set up and passing. Let's review the final diff before deciding what (if anything) to commit.

Tracking is now set up using this repo's engineering-ownership workflow (the same one used for the earlier `partner-settlement-rounding` change):

- Started change record `settlement-currency` (risk R2) via `engineering change start`
- Filled in the **Brief** (`docs/engineering/changes/settlement-currency.md`) with the problem, success criteria, the rejected per-partner-table alternative, and the 5-step status from `plans/settlement-currency.md` (steps 1 & 3 in progress, 2/4/5 not started — flagging that step 4/5's reporting path doesn't exist yet in this repo)
- Filled in the **ADR** (`docs/engineering/decisions/settlement-currency.md`) recording the accepted decision and rejected alternative from the proposal
- Ran the unit tests and bound a passing verification to the current diff via `engineering verify settlement-currency`
- `engineering check --mode advise --change settlement-currency` → **PASS**

These three new files plus the already-modified `src/db/schema.py` are staged in the working tree but not committed — let me know if you'd like me to commit them.