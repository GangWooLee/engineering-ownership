#!/usr/bin/env python3
"""Measure whether the skill is consulted at all, separately from whether it helps.

The treatment engaged in none of seven runs on a repository that does not carry
this skill's artifacts, while engaging in both runs on one that does. That is a
question about the description, which is the only text a model sees when
deciding whether to consult a skill, and it is worth measuring on its own terms.

Nothing here is graded. A probe run produces a yes or no about invocation;
grading it would produce numbers that read like an efficacy result and are not
one. Only the treatment is run: the baseline cannot invoke a skill it was not
given, which the existing runs already show at 0/7.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from build_fixture import build as build_fixture
from run_skill_evals import LANGUAGE_CONTROL, invoke, redact


ROOT = Path(__file__).resolve().parents[2]
PROBES = (
    ROOT
    / "plugins"
    / "engineering-ownership"
    / "skills"
    / "engineering-ownership"
    / "evals"
    / "triggers.json"
)
WORKSPACE = ROOT / "engineering-ownership-workspace"

# A probe needs a repository to sit in, but not a scenario-specific one: what is
# being measured is the decision to consult, before any work begins.
BASE_OVERLAYS = {"unmanaged": "eval-5", "base": "eval-6"}


def description_digest() -> str:
    """Identify which description a measurement was taken against.

    A trigger rate is a property of a description, not of the repository. Writing
    every run to one file let a second invocation clobber the first, and worse,
    would have allowed runs taken before and after a rewrite to be pooled as
    though they measured the same thing.
    """
    skill = (
        ROOT
        / "plugins"
        / "engineering-ownership"
        / "skills"
        / "engineering-ownership"
        / "SKILL.md"
    )
    match = re.search(r"^description:\s*(.+?)$", skill.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise SystemExit("SKILL.md declares no description")
    return hashlib.sha256(match.group(1).strip().encode("utf-8")).hexdigest()[:12]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_probes(split: str) -> list[dict]:
    try:
        probes = json.loads(PROBES.read_text(encoding="utf-8"))["probes"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unreadable trigger probes: {exc}") from exc
    if split != "all":
        probes = [p for p in probes if p["split"] == split]
    if not probes:
        raise SystemExit(f"no probes in split '{split}'")
    return probes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--iteration", required=True)
    parser.add_argument("--base", choices=sorted(BASE_OVERLAYS), default="unmanaged")
    parser.add_argument("--split", choices=("train", "test", "all"), default="train")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--pause", type=int, default=10, help="seconds between runs")
    parser.add_argument("--probe", action="append", default=[], help="restrict to probe ids")
    args = parser.parse_args()

    probes = read_probes(args.split)
    if args.probe:
        wanted = set(args.probe)
        probes = [p for p in probes if p["id"] in wanted]
        if not probes:
            raise SystemExit("no probes matched")

    digest = description_digest()
    destination = WORKSPACE / args.iteration / "triggers" / args.base
    destination.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="engo-trigger-"))
    overlay = BASE_OVERLAYS[args.base]

    records: list[dict] = []
    try:
        for probe in probes:
            for index in range(1, args.runs + 1):
                cwd = scratch / f"{probe['id']}-{index}"
                fixture = build_fixture(overlay, cwd)
                outcome = invoke(
                    probe["query"] + LANGUAGE_CONTROL,
                    cwd,
                    args.model,
                    True,
                    args.timeout,
                )
                record = {
                    "probe": probe["id"],
                    "expect": probe["expect"],
                    "intent": probe.get("intent", ""),
                    "split": probe["split"],
                    "base": args.base,
                    "run": index,
                    "status": outcome["status"],
                    "fixture_commit": fixture["commit"][:12],
                    "description_sha": digest,
                    "recorded_at": now(),
                }
                if outcome["status"] == "ok":
                    record.update(
                        skill_loaded=outcome["skill_loaded"],
                        skill_action_index=outcome.get("skill_action_index"),
                        num_turns=outcome["num_turns"],
                        total_cost_usd=outcome["total_cost_usd"],
                        response_head=redact(outcome["response"][:400]),
                    )
                    mark = "engaged" if outcome["skill_loaded"] else "did not engage"
                else:
                    record["reason"] = outcome.get("reason", "")
                    record["detail"] = outcome.get("detail", "")
                    mark = f"unusable ({record['reason']})"
                records.append(record)
                print(f"  {probe['id']} run-{index} [{probe['expect']}]: {mark}")
                shutil.rmtree(cwd, ignore_errors=True)
                time.sleep(args.pause)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # Merge rather than replace. Runs against the same description are the same
    # measurement continued, and a second invocation for different probes should
    # add to the sample rather than destroy what came before.
    target = destination / f"runs-{digest}.json"
    merged = list(records)
    if target.is_file():
        keys = {(r["probe"], r["run"]) for r in records}
        previous = json.loads(target.read_text(encoding="utf-8")).get("records", [])
        merged = [r for r in previous if (r["probe"], r["run"]) not in keys] + merged
    write_json(
        target,
        {
            "model": args.model,
            "description_sha": digest,
            "base": args.base,
            "runs_per_probe": args.runs,
            "records": sorted(merged, key=lambda r: (r["probe"], r["run"])),
        },
    )
    usable = [r for r in records if r["status"] == "ok"]
    engaged = sum(1 for r in usable if r.get("skill_loaded"))
    print(
        f"recorded {len(records)} run(s), {len(usable)} usable, "
        f"{engaged} engaged -> {destination.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
