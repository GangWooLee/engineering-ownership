#!/usr/bin/env python3
"""Grade recorded evaluation responses with a blinded independent judge.

The withdrawn evaluation graded by substring-matching the skill's own terms, so
a baseline that had never seen the skill could not pass regardless of how well
it reasoned. This driver replaces that with a judge that reads the response and
decides whether the described behaviour occurred.

Blinding is structural rather than promised. The judge receives the response
inline and is given no tools, so it cannot read the directory name that encodes
the configuration, cannot open the skill, and cannot see the other condition's
answer. It is never told that two configurations exist.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VENDOR = HERE / "vendor"
WORKSPACE = ROOT / "engineering-ownership-workspace"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def evidence_section(run_dir: Path) -> str:
    """Assemble what the responder did, with nothing that identifies the run.

    Several expectations concern acts of inspection or what was left behind, and
    a response asserting "I checked the diff" is indistinguishable from having
    checked it. The obvious fix - hand over the transcript - is the wrong one:
    it is written by the model under test and names this skill in one
    configuration and never in the other. The action log is derived from tool
    calls instead, with entries the treatment alone can produce removed.
    """
    parts: list[str] = []

    actions_path = run_dir / "outputs" / "actions.json"
    if actions_path.is_file():
        actions = json.loads(actions_path.read_text(encoding="utf-8")).get("actions", [])
        if actions:
            lines = "\n".join(
                f"{index}. {item.get('action', '?')}: {item.get('target', '')}".rstrip()
                for index, item in enumerate(actions, 1)
            )
            parts.append(
                "## What the responder did, in order\n\n"
                "Each line is one recorded step. If an act an expectation "
                "requires does not appear here, it did not happen.\n\n"
                f"{lines}"
            )

    delta_path = run_dir / "outputs" / "fixture_delta.json"
    if delta_path.is_file():
        delta = json.loads(delta_path.read_text(encoding="utf-8"))
        changed = delta.get("paths_changed_by_run") or []
        if changed:
            body = "\n".join(f"- {path}" for path in changed)
            parts.append(f"## Files the responder changed or created\n\n{body}")
        contents = delta.get("file_contents") or {}
        for path, text in list(contents.items())[:6]:
            parts.append(f"### Contents of `{path}`\n\n```\n{text}\n```")
        diff = (delta.get("tracked_diff") or "").strip()
        if diff:
            parts.append(f"### Changes to files that already existed\n\n```diff\n{diff}\n```")

    if not parts:
        return (
            "## What the responder did\n\n"
            "No steps were recorded. Treat any expectation that requires an act "
            "as unmet."
        )
    return "\n\n".join(parts)


# Anything that names this project identifies the configuration, because only one
# of the two can produce it. The response itself is exempt: it is the artifact
# under review and cannot be altered without changing what is being judged. That
# residual leak is disclosed rather than silently tolerated.
#
# The arm names are here because they were not, and that omission is how two
# graded runs reached a judge with `eval-7-without_skill-1` in the log: the
# fixture directory encodes the configuration, a shell token carried it, and the
# only predicate that could have objected was not looking for it. A tell list
# that omits the thing being hidden is a list that cannot fail.
BLINDING_TELLS = (
    "engineering-ownership",
    "--plugin-dir",
    "plugin-dir",
    "skill-creator",
    "with_skill",
    "without_skill",
    "with-skill",
    "without-skill",
)


def blinding_leaks(bundle: str) -> list[str]:
    lowered = bundle.lower()
    return sorted({tell for tell in BLINDING_TELLS if tell in lowered})


def compose_prompt(task: str, expectations: list[str], response: str, run_dir: Path) -> str:
    instructions = (VENDOR / "grader.md").read_text(encoding="utf-8")
    appendix = (HERE / "judge_appendix.md").read_text(encoding="utf-8")
    listed = "\n".join(f"{index}. {text}" for index, text in enumerate(expectations, 1))
    return (
        f"{instructions}\n\n---\n\n{appendix}\n\n---\n\n"
        "You are grading one response. You have no tools; everything you need is "
        "below.\n\n"
        f"## The task the response was answering\n\n{task}\n\n"
        f"## Expectations to judge\n\n{listed}\n\n"
        "## Response under review\n\n"
        "<response>\n"
        f"{response}\n"
        "</response>\n\n"
        f"{evidence_section(run_dir)}\n\n"
        "Return only the JSON object described above."
    )


def extract_json(text: str) -> dict | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("```")[1]
        if stripped.startswith("json"):
            stripped = stripped[4:]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(stripped[start : end + 1])
    except json.JSONDecodeError:
        return None


def judge(
    task: str, expectations: list[str], response: str, run_dir: Path, model: str, timeout: int
) -> dict:
    prompt = compose_prompt(task, expectations, response, run_dir)
    env = {**subprocess.os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}
    env.pop("CLAUDECODE", None)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--model",
                model,
                "--output-format",
                "json",
                "--tools",
                "",
                "--no-session-persistence",
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": "judge timed out"}
    elapsed = round(time.monotonic() - started, 3)
    if completed.returncode != 0:
        return {"error": f"judge exited {completed.returncode}"}
    try:
        envelope = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"error": "judge returned unparseable output"}
    verdict = extract_json(envelope.get("result", ""))
    if verdict is None:
        return {"error": "judge returned no JSON object"}
    verdict["_elapsed"] = elapsed
    verdict["_raw"] = envelope.get("result", "")[:4000]
    return verdict


def other_script_characters(text: str) -> int:
    """Count characters from writing systems other than the Latin alphabet.

    The language control exists because the withdrawn evaluation compared Korean
    responses against English ones. Checking for non-ASCII was the obvious test
    and the wrong one: ordinary English prose contains typographic characters
    such as a dash, an arrow, or a currency sign, and rejecting those discarded
    every valid run. Detect the writing system instead.
    """
    ranges = (
        (0xAC00, 0xD7AF),  # Hangul syllables
        (0x1100, 0x11FF),  # Hangul jamo
        (0x3040, 0x30FF),  # Hiragana and katakana
        (0x4E00, 0x9FFF),  # CJK unified ideographs
        (0x0400, 0x04FF),  # Cyrillic
        (0x0600, 0x06FF),  # Arabic
    )
    return sum(
        1 for ch in text if any(low <= ord(ch) <= high for low, high in ranges)
    )


def validity_gate(response: str) -> str:
    """Reject a run before judging when the response cannot be graded fairly."""
    if len(response.strip()) < 200:
        return "response is too short to grade"
    foreign = other_script_characters(response)
    if foreign:
        return f"response contains {foreign} non-Latin characters; the language control did not hold"
    return ""


def grade_run(
    run_dir: Path,
    task: str,
    expectations: list[str],
    model: str,
    timeout: int,
    resume: bool = False,
) -> dict:
    # Grading a full sweep is one judge call per run. Redoing the ones already
    # judged pays twice for the same verdict.
    if resume and (run_dir / "grading.json").is_file():
        existing = json.loads((run_dir / "grading.json").read_text(encoding="utf-8"))
        summary = existing.get("summary", {})
        return {"passed": summary.get("passed", 0), "total": summary.get("total", 0), "cached": True}
    response_path = run_dir / "outputs" / "response.md"
    if not response_path.is_file():
        return {"skipped": "no response recorded"}
    response = response_path.read_text(encoding="utf-8")

    invalid = validity_gate(response)
    if invalid:
        write_json(
            run_dir / "grading.json",
            {
                "expectations": [],
                "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0},
                "status": "invalid",
                "reason": invalid,
                "graded_at": now(),
            },
        )
        return {"invalid": invalid}

    leaks = blinding_leaks(evidence_section(run_dir))
    if leaks:
        # Refuse rather than grade. A judge that can infer the configuration is
        # not blinded, and a verdict from it would look exactly like a valid one.
        write_json(
            run_dir / "grading.json",
            {
                "expectations": [],
                "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0},
                "status": "invalid",
                "reason": f"evidence identifies the configuration: {', '.join(leaks)}",
                "graded_at": now(),
            },
        )
        return {"invalid": f"blinding leak: {', '.join(leaks)}"}

    verdict = judge(task, expectations, response, run_dir, model, timeout)
    if "error" in verdict:
        return {"error": verdict["error"]}

    graded = verdict.get("expectations") or []
    if len(graded) != len(expectations):
        return {"error": f"judge returned {len(graded)} verdicts for {len(expectations)}"}

    entries = []
    for expectation, item in zip(expectations, graded, strict=True):
        entries.append(
            {
                "text": expectation,
                "passed": bool(item.get("passed")),
                "evidence": str(item.get("evidence", "")).strip(),
            }
        )
    passed = sum(1 for entry in entries if entry["passed"])
    total = len(entries)

    metrics_path = run_dir / "outputs" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.is_file() else {}
    timing_path = run_dir / "timing.json"
    timing = json.loads(timing_path.read_text(encoding="utf-8")) if timing_path.is_file() else {}

    write_json(
        run_dir / "grading.json",
        {
            "expectations": entries,
            "summary": {
                "passed": passed,
                "failed": total - passed,
                "total": total,
                "pass_rate": round(passed / total, 4) if total else 0.0,
            },
            "execution_metrics": metrics,
            "timing": timing,
            "eval_feedback": {"overall": str(verdict.get("eval_feedback", "")).strip()},
            "judge_model": model,
            "graded_at": now(),
        },
    )
    write_json(run_dir / "judge_raw.json", {"raw": verdict.get("_raw", ""), "model": model})
    return {"passed": passed, "total": total}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="judge model id, pinned")
    parser.add_argument("--iteration", default="iteration-2")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--resume", action="store_true", help="skip runs already graded")
    args = parser.parse_args()

    iteration = WORKSPACE / args.iteration
    if not iteration.is_dir():
        raise SystemExit(f"no such iteration: {args.iteration}")

    graded = 0
    for eval_dir in sorted(iteration.glob("eval-*")):
        metadata_path = eval_dir / "eval_metadata.json"
        if not metadata_path.is_file():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        task = metadata["prompt"]
        expectations = metadata["expectations"]
        for config_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                outcome = grade_run(
                    run_dir, task, expectations, args.model, args.timeout, args.resume
                )
                label = run_dir.relative_to(iteration)
                if "passed" in outcome:
                    mark = " (cached)" if outcome.get("cached") else ""
                    print(f"{label}: {outcome['passed']}/{outcome['total']}{mark}")
                    graded += 1
                else:
                    reason = outcome.get("error") or outcome.get("invalid") or outcome.get("skipped")
                    print(f"{label}: not graded ({reason})")

    if not graded:
        raise SystemExit("no runs were graded")
    print(f"graded {graded} run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
