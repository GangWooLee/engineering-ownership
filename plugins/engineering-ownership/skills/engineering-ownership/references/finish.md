# Finish and handoff

## Check

1. Inspect the final diff.
2. Confirm the effective risk has not risen above the recorded risk.
3. Fill all required reasoning and operational artifacts.
4. Run `engineering refs check --change <id>` when decision references exist.
5. Run reviewed verification with `engineering verify <id>`.
6. Exercise the real runtime seam where proportionate to risk.
7. Run `engineering check --mode advise --change <id>` locally. CI may use
   `--mode enforce`.
8. Report current evidence separately from unverified or residual risk.

## Handoff

Use `engineering handoff --change <id> --save` when another session must
continue. Saved handoffs live under `.engineering/handoffs/`, are ignored by
Git, and therefore do not invalidate the diff digest.

The handoff points to canonical records and reports:

- changed paths and current digest;
- risk and decision records;
- fresh or stale verification;
- unresolved gaps;
- next safe action.

Do not duplicate the full Brief/ADR, include secrets, or turn the handoff into
a second design document.
