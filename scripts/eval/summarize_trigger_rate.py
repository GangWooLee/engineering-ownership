#!/usr/bin/env python3
"""Report how often the skill actually engaged, per eval and configuration.

A single run cannot tell an under-triggering skill apart from one unlucky
sample. This reads the run records an iteration already wrote and turns them
into a rate with an interval, so that "the skill did not engage" is stated with
the denominator it was measured against.

Engagement is read from `skill_loaded`, which the runner sets from a `Skill`
tool call and nothing else. An earlier version of that detection matched the
skill's name against tool inputs and reported the baseline as having loaded the
skill, because the repository directory carries the same name and appears in
every absolute path. Do not widen the signal here.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "engineering-ownership-workspace"

CONFIDENCE = 0.95


def binomial_at_most(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p**i * (1.0 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, confidence: float = CONFIDENCE) -> tuple[float, float]:
    """Exact binomial interval, by bisection so the standard library suffices.

    Reported because the interesting results here are 0/n and n/n, where a
    point estimate alone reads as far more settled than the sample supports.
    """
    if n == 0:
        return (0.0, 1.0)
    alpha = (1.0 - confidence) / 2.0

    def solve(target: float, at_most_k: int) -> float:
        low, high = 0.0, 1.0
        for _ in range(200):
            mid = (low + high) / 2.0
            # P(X <= at_most_k) decreases as p grows.
            if binomial_at_most(at_most_k, n, mid) > target:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0

    lower = 0.0 if k == 0 else solve(1.0 - alpha, k - 1)
    upper = 1.0 if k == n else solve(alpha, k)
    return (lower, upper)


def collect(iteration_dir: Path) -> list[dict]:
    """One record per run directory, including runs that never produced a result.

    A run that errored writes `error.json` and no `run_meta.json`. Globbing only
    for `run_meta.json` would drop it from the denominator and quietly raise the
    rate, so an unusable run is carried through as `status: "error"`.
    """
    records: list[dict] = []
    for run_dir in sorted(iteration_dir.glob("eval-*/*/run-*")):
        outputs = run_dir / "outputs"
        meta_path = outputs / "run_meta.json"
        record = {
            "eval": run_dir.parents[1].name,
            "configuration": run_dir.parent.name,
            "run": run_dir.name,
        }
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            record.update(
                status="ok",
                skill_loaded=bool(meta.get("skill_loaded")),
                num_turns=meta.get("num_turns"),
                total_cost_usd=meta.get("total_cost_usd"),
                fixture_commit=(meta.get("fixture_commit") or "")[:12],
            )
        elif (outputs / "error.json").is_file():
            error = json.loads((outputs / "error.json").read_text(encoding="utf-8"))
            record.update(status="error", reason=error.get("reason", ""), skill_loaded=None)
        else:
            record.update(status="missing", skill_loaded=None)
        records.append(record)
    return records


def verdict(usable: int, lower: float, upper: float) -> str:
    """Decide what this sample supports about under-triggering.

    The rule was fixed before iteration-5's runs finished, so that the bar could
    not be chosen to suit the result: the 95% interval must exclude a coin-flip
    trigger rate. It is stated per row, but only the pooled row is the decision
    - three runs cannot clear this bar in either direction, and reading a
    per-scenario row as a verdict is the error the rule exists to prevent.
    """
    if usable == 0:
        return "no usable runs"
    if upper < 0.5:
        return "under-triggering reproduced"
    if lower > 0.5:
        return "triggers reliably"
    return "inconclusive at this sample size"


def unmanaged_evals() -> dict[str, str]:
    """Overlays that start from a repository this skill does not manage.

    Returns the commit each one currently builds to, not just its name. The
    recipe describes the fixture as it is now, while a run records the fixture
    it actually used: `iteration-3` ran eval-9 against the managed base, and
    reading today's recipe alone would pool that run as an unmanaged-base
    result and quietly answer a different question than the one asked.

    Read from the recipe rather than listed here, so that adding an
    unmanaged-base scenario cannot silently leave it out of the pooled sample.
    """
    recipe = json.loads(
        (ROOT / "scripts" / "eval" / "fixtures" / "recipe.json").read_text(encoding="utf-8")
    )
    names = [
        name
        for name, overlay in recipe.get("overlays", {}).items()
        if overlay.get("base", "base") == "unmanaged"
    ]

    from build_fixture import build as build_fixture

    commits: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="engo-summary-") as scratch:
        for name in names:
            commits[name] = build_fixture(name, Path(scratch) / name)["commit"][:12]
    return commits


def tally(runs: list[dict], eval_name: str, configuration: str) -> dict:
    usable = [r for r in runs if r["status"] == "ok"]
    unusable = [r for r in runs if r["status"] != "ok"]
    triggered = sum(1 for r in usable if r["skill_loaded"])
    lower, upper = clopper_pearson(triggered, len(usable))
    return {
        "eval": eval_name,
        "configuration": configuration,
        "runs_attempted": len(runs),
        "runs_usable": len(usable),
        "runs_unusable": len(unusable),
        "skill_loaded_true": triggered,
        "rate": round(triggered / len(usable), 3) if usable else None,
        "ci95_lower": round(lower, 3),
        "ci95_upper": round(upper, 3),
        "verdict": verdict(len(usable), lower, upper),
        "fixture_commits": sorted({r.get("fixture_commit", "") for r in usable}),
    }


def summarize(records: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for record in records:
        groups.setdefault((record["eval"], record["configuration"]), []).append(record)

    rows = [
        tally(runs, eval_name, configuration)
        for (eval_name, configuration), runs in sorted(groups.items())
    ]

    # The pre-registered decision: the treatment runs on every unmanaged-base
    # scenario, read as one sample. Three runs cannot settle anything on their
    # own, and the hypothesis under test is about the kind of repository rather
    # than about either scenario.
    #
    # A run joins the pool only if the fixture it recorded is the one the
    # current recipe builds for that overlay. A run of the same eval against an
    # older fixture is a different experiment.
    expected = unmanaged_evals()
    pooled_runs = [
        record
        for record in records
        if record["configuration"] == "with_skill"
        and expected.get(record["eval"]) == record.get("fixture_commit")
    ]
    excluded = [
        record
        for record in records
        if record["configuration"] == "with_skill"
        and record["eval"] in expected
        and expected.get(record["eval"]) != record.get("fixture_commit")
    ]
    if pooled_runs:
        pooled = tally(pooled_runs, "POOLED", "with_skill (unmanaged base)")
        pooled["excluded_stale_fixture"] = len(excluded)
        rows.append(pooled)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("iterations", nargs="+", help="iteration directory names")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args()

    payload: dict[str, list[dict]] = {}
    for name in args.iterations:
        iteration_dir = WORKSPACE / name
        if not iteration_dir.is_dir():
            raise SystemExit(f"no such iteration: {name}")
        payload[name] = summarize(collect(iteration_dir))

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    for name, rows in payload.items():
        print(f"\n{name}")
        header = f"  {'eval':<8} {'configuration':<28} {'engaged':>9}  {'rate':>6}  {'95% CI':>14}  verdict"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for row in rows:
            if row["eval"] == "POOLED":
                print("  " + "-" * (len(header) - 2))
            engaged = f"{row['skill_loaded_true']}/{row['runs_usable']}"
            rate = "n/a" if row["rate"] is None else f"{row['rate']:.2f}"
            interval = f"[{row['ci95_lower']:.2f}, {row['ci95_upper']:.2f}]"
            print(
                f"  {row['eval']:<8} {row['configuration']:<28} {engaged:>9}  "
                f"{rate:>6}  {interval:>14}  {row['verdict']}"
            )
            if row["runs_unusable"]:
                print(f"  {'':<8} {'':<28} {row['runs_unusable']} run(s) produced no result")
            if row.get("excluded_stale_fixture"):
                print(
                    f"  {'':<8} {'':<28} {row['excluded_stale_fixture']} run(s) excluded: "
                    "recorded a fixture the current recipe no longer builds"
                )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
