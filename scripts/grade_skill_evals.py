#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "engineering-ownership-workspace" / "iteration-2"
EVALS = json.loads(
    (
        ROOT
        / "plugins"
        / "engineering-ownership"
        / "skills"
        / "engineering-ownership"
        / "evals"
        / "evals.json"
    ).read_text(encoding="utf-8")
)["evals"]


def contains_all(text: str, groups: list[tuple[str, ...]]) -> tuple[bool, str]:
    lowered = text.lower()
    missing = [
        " or ".join(group)
        for group in groups
        if not any(term.lower() in lowered for term in group)
    ]
    if missing:
        return False, "Missing evidence for: " + "; ".join(missing)
    return True, "Found: " + "; ".join(
        next(term for term in group if term.lower() in lowered) for group in groups
    )


def checks(eval_name: str, text: str) -> list[tuple[bool, str]]:
    lower = text.lower()
    if eval_name == "r0-readme-typo":
        no_heavy = (
            ("brief" not in lower and "adr" not in lower and "runbook" not in lower)
            or any(term in lower for term in ("필요하지", "unnecessary", "not require"))
        )
        no_score_claim = not any(
            term in lower
            for term in ("more documentation proves", "문서량이 역량", "documentation quantity proves")
        )
        return [
            contains_all(text, [("R0",)]),
            (no_heavy, "No heavy artifact is required for the typo-only change."),
            contains_all(text, [("diff",), ("lint", "link", "spell", "검사")]),
            (no_score_claim, "No documentation-volume quality claim appears."),
        ]
    if eval_name == "r3-auth-session-refresh":
        return [
            contains_all(text, [("R3",)]),
            contains_all(text, [("brief",), ("threat", "위협"), ("runbook",)]),
            contains_all(
                text,
                [
                    ("security", "보안", "replay"),
                    ("failure", "실패", "race"),
                    ("rollback", "롤백", "recovery", "복구"),
                    ("current diff", "현재 diff"),
                ],
            ),
            contains_all(
                text,
                [
                    ("brief", "change record", "변경 기록"),
                    ("adr", "decision record", "의사결정 기록"),
                    ("optional", "not block", "not a default", "선택", "차단하지"),
                ],
            ),
        ]
    if eval_name == "r2-db-api-stale-verification":
        at_least_r2 = "r2" in lower or "r3" in lower
        return [
            (at_least_r2, "The response explicitly names R2 or R3."),
            contains_all(text, [("test file", "테스트 파일"), ("earlier", "이전", "previous"), ("not evidence", "증거가 아니")]),
            contains_all(text, [("current diff", "현재 diff", "current working tree"), ("integration", "통합", "runtime")]),
            contains_all(text, [("rollback", "롤백", "recovery", "복구")]),
        ]
    if eval_name == "decision-memory-and-revisit":
        handoff = contains_all(
            text,
            [
                ("handoff",),
                ("decision", "adr", "brief", "결정"),
                ("verification", "검증"),
                ("gap", "risk", "위험"),
                ("next", "다음"),
            ],
        )
        links = contains_all(
            text,
            [
                ("canonical", "source of truth", "정본"),
                ("link", "pointer", "참조"),
            ],
        )
        review = contains_all(
            text,
            [
                ("gap",),
                ("revisit", "review", "복습", "재확인"),
                ("optional", "not block", "선택", "차단하지"),
            ],
        )
        decline = any(
            term in lower
            for term in (
                "score”는 제공하지",
                "score\" is not",
                "decline",
                "점수는 제공하지",
                "not a competence grade",
            )
        )
        return [
            handoff,
            links,
            review,
            (decline, "The response declines a maturity score."),
        ]
    raise ValueError(eval_name)


def stat(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(statistics.mean(values), 4),
        "stddev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def main() -> int:
    runs: list[dict] = []
    for eval_item in EVALS:
        eval_name = eval_item["name"]
        for configuration in ("with_skill", "without_skill"):
            run_dir = WORKSPACE / eval_name / configuration
            response = (run_dir / "outputs" / "response.md").read_text(encoding="utf-8")
            results = checks(eval_name, response)
            expectations = []
            for expectation, (passed, evidence) in zip(eval_item["expectations"], results, strict=True):
                expectations.append(
                    {"text": expectation, "passed": passed, "evidence": evidence}
                )
            passed_count = sum(item["passed"] for item in expectations)
            grading = {
                "expectations": expectations,
                "summary": {
                    "passed": passed_count,
                    "failed": len(expectations) - passed_count,
                    "total": len(expectations),
                    "pass_rate": passed_count / len(expectations),
                },
                "execution_metrics": {
                    "tool_calls": {},
                    "total_tool_calls": 0,
                    "total_steps": 1,
                    "errors_encountered": 0,
                    "output_chars": len(response),
                    "transcript_chars": 0,
                },
                "timing": {
                    "total_duration_seconds": 0.0,
                    "measurement_note": "Subagent timing and token metrics were not exposed by this orchestration surface.",
                },
                "claims": [],
                "user_notes_summary": {
                    "uncertainties": [],
                    "needs_review": [],
                    "workarounds": [],
                },
                "eval_feedback": {
                    "suggestions": [],
                    "overall": "Assertions test risk proportionality, current-diff evidence, recovery, and human ownership.",
                },
            }
            (run_dir / "grading.json").write_text(
                json.dumps(grading, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (run_dir / "timing.json").write_text(
                json.dumps(
                    {
                        "total_tokens": 0,
                        "duration_ms": 0,
                        "total_duration_seconds": 0.0,
                        "measurement_note": "Unavailable from collaboration task notifications.",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            runs.append(
                {
                    "eval_id": eval_item["id"],
                    "eval_name": eval_name,
                    "configuration": configuration,
                    "run_number": 1,
                    "result": {
                        "pass_rate": grading["summary"]["pass_rate"],
                        "passed": grading["summary"]["passed"],
                        "failed": grading["summary"]["failed"],
                        "total": grading["summary"]["total"],
                        "time_seconds": 0.0,
                        "tokens": 0,
                        "tool_calls": 0,
                        "errors": 0,
                    },
                    "expectations": expectations,
                    "notes": [],
                }
            )

    summary: dict[str, dict] = {}
    for configuration in ("with_skill", "without_skill"):
        config_runs = [run for run in runs if run["configuration"] == configuration]
        summary[configuration] = {
            "pass_rate": stat([run["result"]["pass_rate"] for run in config_runs]),
            "time_seconds": stat([0.0 for _ in config_runs]),
            "tokens": stat([0.0 for _ in config_runs]),
        }
    delta = (
        summary["with_skill"]["pass_rate"]["mean"]
        - summary["without_skill"]["pass_rate"]["mean"]
    )
    summary["delta"] = {
        "pass_rate": f"{delta:+.2f}",
        "time_seconds": "n/a",
        "tokens": "n/a",
    }
    with_passed = sum(
        run["result"]["passed"]
        for run in runs
        if run["configuration"] == "with_skill"
    )
    baseline_passed = sum(
        run["result"]["passed"]
        for run in runs
        if run["configuration"] == "without_skill"
    )
    total = sum(
        run["result"]["total"]
        for run in runs
        if run["configuration"] == "with_skill"
    )
    notes = [
        f"With-skill passed {with_passed} of {total} expectations; baseline passed {baseline_passed} of {total}.",
        "The largest intended separation is risk proportionality, durable decision memory, current-diff evidence, recovery, and refusal to turn evidence into a maturity score.",
        "Both configurations handled proportional README verification and rejected stale tests, so those checks alone do not distinguish the skill.",
        "Time and token metrics are intentionally not compared because the orchestration surface did not expose them.",
    ]
    benchmark = {
        "metadata": {
            "skill_name": "engineering-ownership",
            "skill_path": "plugins/engineering-ownership/skills/engineering-ownership",
            "executor_model": "inherited subagent model",
            "analyzer_model": "deterministic assertion grader plus main-agent review",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": [item["id"] for item in EVALS],
            "runs_per_configuration": 1,
        },
        "runs": runs,
        "run_summary": summary,
        "notes": notes,
    }
    (WORKSPACE / "benchmark.json").write_text(
        json.dumps(benchmark, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (WORKSPACE / "benchmark.md").write_text(
        "# Skill benchmark: engineering-ownership\n\n"
        "| Configuration | Expectation pass rate |\n"
        "| --- | ---: |\n"
        f"| With skill | {summary['with_skill']['pass_rate']['mean']:.0%} |\n"
        f"| Without skill | {summary['without_skill']['pass_rate']['mean']:.0%} |\n"
        f"| Delta | {delta:+.0%} |\n\n"
        + "\n".join(f"- {note}" for note in notes)
        + "\n",
        encoding="utf-8",
    )
    print(f"graded {len(runs)} runs; delta={delta:+.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
