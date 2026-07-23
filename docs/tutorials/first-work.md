# First work: from installation to handoff

## 1. Ask in natural language

```text
$engineering-ownership add an AI analysis cache
```

The agent routes the request. You do not run a memorized CLI sequence.

## 2. Approve setup once

If the repository has no contract, the agent inspects CI, package scripts,
instructions, and sensitive paths. It previews the proposed contract, agent
pointers, and optional reminder setting. No file changes before approval.

After approval, it applies the setup and runs `engineering doctor`. Doctor
checks local availability only; it never executes project verification.

## 3. Start a risk-proportional change

The agent selects a stable ID, title, and highest risk. The resulting record
begins like this:

```markdown
# 2026-07-23 · AI analysis cache policy

Change ID: `cache-ai-analysis`
Created: `2026-07-23T20:15:32+09:00`
```

The Brief captures the original problem and constraints. An ADR is added only
if the cache policy changes architecture or is expensive to reverse.

## 4. Link, do not duplicate

If gstack or Superpowers already produced a plan or test result, the Brief
links it. An OpenSpec proposal remains canonical in OpenSpec. Engineering
Ownership records the selected ownership decision and verification pointer.

## 5. Implement with traceable rationale

The agent searches existing responsibility before adding code. Only a
non-obvious enforcement point gets a marker:

```text
engineering-decision: cache-ai-analysis | docs/engineering/decisions/cache-ai-analysis.md
```

Readable code does not receive ceremonial comments.

## 6. Verify the exact diff

Reviewed argv commands run through `engineering verify`. Results are stored
without logs or secrets and bound to the current diff digest. If a sensitive
path raises R2 to R3, verification stops until `change set-risk` creates the
missing operational records.

## 7. Check and hand off

Before merge, the agent checks document completeness, decision references, and
fresh verification. A saved handoff is Git-ignored, so creating it cannot make
the verification stale. A new session reads the contract, current diff,
evidence, linked records, and handoff before continuing.
