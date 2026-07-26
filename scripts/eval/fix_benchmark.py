#!/usr/bin/env python3
"""Correct the vendored aggregator's output in place.

The vendored aggregate_benchmark.py labels a character count as tokens (its
timing fallback never fires for this runner, which always embeds timing into
grading.json) and hardcodes runs_per_configuration to 3. Per vendor/PROVENANCE.md
the vendored file is never edited; this post-pass runs after it and corrects
benchmark.json and benchmark.md from the per-run timing.json records.

Usage: python3 fix_benchmark.py <iteration-dir> [note ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from aggregate_benchmark import calculate_stats, generate_markdown


def main() -> int:
    iteration = Path(sys.argv[1])
    benchmark = json.loads((iteration / "benchmark.json").read_text(encoding="utf-8"))

    tokens: dict[str, list[int]] = {}
    run_counts: dict[tuple[int, str], set[int]] = {}
    for entry in benchmark["runs"]:
        run_dir = (
            iteration
            / f"eval-{entry['eval_id']}"
            / entry["configuration"]
            / f"run-{entry['run_number']}"
        )
        timing = json.loads((run_dir / "timing.json").read_text(encoding="utf-8"))
        entry["result"]["tokens"] = timing["total_tokens"]
        tokens.setdefault(entry["configuration"], []).append(timing["total_tokens"])
        key = (entry["eval_id"], entry["configuration"])
        run_counts.setdefault(key, set()).add(entry["run_number"])

    configs = [name for name in benchmark["run_summary"] if name != "delta"]
    for config in configs:
        benchmark["run_summary"][config]["tokens"] = calculate_stats(tokens.get(config, [0]))
    if len(configs) >= 2:
        primary = benchmark["run_summary"][configs[0]]["tokens"]["mean"]
        baseline = benchmark["run_summary"][configs[1]]["tokens"]["mean"]
        benchmark["run_summary"]["delta"]["tokens"] = f"{primary - baseline:+.0f}"

    counted = sorted({len(numbers) for numbers in run_counts.values()})
    benchmark["metadata"]["runs_per_configuration"] = (
        counted[0] if len(counted) == 1 else counted
    )
    benchmark["metadata"]["corrected"] = "tokens from timing.json; runs counted, not assumed"
    for note in sys.argv[2:]:
        if note not in benchmark["notes"]:
            benchmark["notes"].append(note)

    (iteration / "benchmark.json").write_text(
        json.dumps(benchmark, indent=2) + "\n", encoding="utf-8"
    )
    (iteration / "benchmark.md").write_text(generate_markdown(benchmark) + "\n", encoding="utf-8")
    print(f"corrected {iteration / 'benchmark.json'} and benchmark.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
