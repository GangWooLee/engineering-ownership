# Contributing

Thank you for helping people retain engineering judgment while using AI.

## Before opening a pull request

1. Open an issue for a new workflow principle or public data-interface change.
2. Explain the real case that exposed the gap.
3. Show before/after behavior and the failure the change prevents.
4. Add or update automated tests.
5. For skill behavior, include paired skill/baseline evaluation evidence.
6. Keep code and documentation changes small enough to review.

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_distribution.py
```

Do not add telemetry, network calls, automatic hooks, secret collection, shell
execution, or path writes outside the repository.

## Principle changes

General rules have a high cost when they are wrong. A proposal must include:

- a concrete user scenario;
- the old failure and new expected behavior;
- evidence that the rule helps and does not overburden R0 work;
- limitations and a removal or revision condition.

One anecdote may justify an experiment. Promote a principle only after it
survives repeated use.

## Commit format

```text
<type>(<scope>): <specific outcome>

Why:
Decision:
Verification:
Limitations:
Refs:
```

By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

