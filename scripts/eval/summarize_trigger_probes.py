#!/usr/bin/env python3
"""Report whether the skill is consulted when it should be, and left alone otherwise.

The earlier summary reported a rate over positives only. That measures recall and
nothing else, so a description that fired on every request would have scored
perfectly. This reads the probe labels and reports both directions, each with an
interval, because the interesting results here are 0/n and n/n where a point
estimate reads as far more settled than the sample supports.

Runs are grouped by the digest of the description they were taken against. A
trigger rate is a property of a description, and pooling runs from either side of
a rewrite would answer a question nobody asked.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from summarize_trigger_rate import clopper_pearson


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "engineering-ownership-workspace"

# Fixed before the runs, so the bar could not be chosen to suit the result. The
# improvement bar is the upper end of the interval measured before this work
# began: 0/7 engagements on an unmanaged repository gave [0, 0.41].
PRIOR_UPPER_BOUND = 0.41
OVER_TRIGGER_LIMIT = 0.5


def load(iteration: str) -> list[dict]:
    directory = WORKSPACE / iteration / "triggers"
    if not directory.is_dir():
        raise SystemExit(f"no trigger runs recorded for {iteration}")
    records: list[dict] = []
    for path in sorted(directory.glob("*/runs-*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8")).get("records", []))
    if not records:
        raise SystemExit(f"no runs found under {directory}")
    return records


def tally(runs: list[dict]) -> dict:
    usable = [r for r in runs if r.get("status") == "ok"]
    engaged = sum(1 for r in usable if r.get("skill_loaded"))
    lower, upper = clopper_pearson(engaged, len(usable)) if usable else (0.0, 1.0)
    return {
        "attempted": len(runs),
        "usable": len(usable),
        "engaged": engaged,
        "rate": round(engaged / len(usable), 3) if usable else None,
        "ci95": (round(lower, 3), round(upper, 3)),
    }


def verdict(label: str, stats: dict) -> str:
    if not stats["usable"]:
        return "no usable runs"
    lower, upper = stats["ci95"]
    if label == "trigger":
        if lower > PRIOR_UPPER_BOUND:
            return f"improved: interval clears the prior bound of {PRIOR_UPPER_BOUND}"
        if upper <= PRIOR_UPPER_BOUND:
            return "no improvement: interval sits at or below the prior bound"
        return "inconclusive at this sample size"
    if label == "no-trigger":
        if upper < OVER_TRIGGER_LIMIT:
            return f"no over-triggering: interval stays under {OVER_TRIGGER_LIMIT}"
        return "over-triggering not ruled out"
    return "recorded, not scored"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration")
    parser.add_argument("--split", choices=("train", "test", "all"), default="all")
    args = parser.parse_args()

    records = load(args.iteration)
    if args.split != "all":
        records = [r for r in records if r.get("split") == args.split]
        if not records:
            raise SystemExit(f"no runs in split '{args.split}'")

    by_description: dict[str, list[dict]] = {}
    for record in records:
        by_description.setdefault(record.get("description_sha", "unknown"), []).append(record)

    for digest, group in sorted(by_description.items()):
        bases = sorted({r.get("base", "?") for r in group})
        print(f"\ndescription {digest}   split={args.split}   base(s)={', '.join(bases)}")
        print(f"  {'class':<12} {'base':<10} {'engaged':>9}  {'rate':>6}  {'95% CI':>14}  verdict")
        print("  " + "-" * 84)
        for base in bases:
            for label in ("trigger", "no-trigger", "unscored"):
                runs = [
                    r for r in group if r.get("expect") == label and r.get("base") == base
                ]
                if not runs:
                    continue
                stats = tally(runs)
                interval = f"[{stats['ci95'][0]:.2f}, {stats['ci95'][1]:.2f}]"
                rate = "n/a" if stats["rate"] is None else f"{stats['rate']:.2f}"
                print(
                    f"  {label:<12} {base:<10} {stats['engaged']:>4}/{stats['usable']:<4} "
                    f"{rate:>6}  {interval:>14}  {verdict(label, stats)}"
                )
                if stats["attempted"] != stats["usable"]:
                    unusable = stats["attempted"] - stats["usable"]
                    print(f"  {'':<12} {'':<10} {unusable} run(s) produced no result")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
