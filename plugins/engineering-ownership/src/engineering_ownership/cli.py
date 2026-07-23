from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from . import __version__
from .errors import EngineeringError
from .evidence import (
    list_evidence,
    new_evidence,
    now_iso,
    read_evidence,
    save_evidence,
    validate_change_id,
)
from .io import json_text, minimal_subprocess_env, redact, safe_relative_path, write_repo_text
from .model import (
    COMPETENCIES,
    RISK_ORDER,
    classify_risk,
    contract_version,
    default_contract,
    migrate_v1,
    read_contract,
    required_command_ids,
    validate_contract,
)
from .repository import changed_paths, diff_digest, head_revision, repo_root
from .templates import ADR, BRIEF, POINTER, RUNBOOK, THREAT_MODEL


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def ensure_pointer(root: Path, relative_path: str) -> bool:
    path = safe_relative_path(root, relative_path, for_write=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if "<!-- engineering-ownership:start -->" in existing:
        return False
    separator = "" if not existing else "\n" if existing.endswith("\n") else "\n\n"
    write_repo_text(root, relative_path, existing + separator + POINTER, overwrite=path.exists())
    return True


def command_init(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract_path = root / ".engineering" / "contract.json"
    if contract_path.exists():
        raise EngineeringError("Contract already exists; init is intentionally non-destructive")
    contract = default_contract(root.name)
    contract["project"]["kind"] = args.kind
    contract["project"]["status"] = args.status
    write_repo_text(root, ".engineering/contract.json", json_text(contract))
    if args.agent_pointers:
        for pointer in ("AGENTS.md", "CLAUDE.md"):
            if ensure_pointer(root, pointer):
                print(f"Added pointer: {pointer}")
    print("Created .engineering/contract.json")
    print("Review the generated argv commands before running engineering verify.")
    return 0


def audit_payload(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    version = contract_version(contract)
    digest, paths = diff_digest(root)
    records = list_evidence(root, contract) if version == 2 else []
    signals: list[str] = []
    gaps: list[str] = []
    signals.append(f"contract-v{version}")
    if records:
        signals.append(f"{len(records)} evidence record(s)")
    else:
        gaps.append("no evidence records")
    if version == 1:
        gaps.append("contract v1 is read-only compatible; migrate before verify")
    if paths:
        signals.append(f"{len(paths)} changed path(s)")
    else:
        signals.append("clean working tree")
    if version == 2 and not contract.get("verification"):
        gaps.append("no verification commands configured")
    return {
        "repository": root.name,
        "revision": head_revision(root)[:12],
        "contract_version": version,
        "current_diff_digest": digest,
        "changed_paths": paths,
        "signals": signals,
        "gaps": gaps,
    }


def command_audit(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract_path = root / ".engineering" / "contract.json"
    if not contract_path.exists():
        payload = {
            "repository": root.name,
            "contract_version": None,
            "signals": [],
            "gaps": ["missing .engineering/contract.json"],
        }
    else:
        payload = audit_payload(root, read_contract(root))
    if args.format == "json":
        print(json_text(payload), end="")
    else:
        print(f"Engineering audit: {payload['repository']}")
        for item in payload["signals"]:
            print(f"  signal: {item}")
        for item in payload["gaps"]:
            print(f"  gap: {item}")
    return 0


def artifact_paths(contract: dict[str, Any], change_id: str, risk: str) -> dict[str, str]:
    artifacts = contract["artifacts"]
    result = {
        "brief": f"{artifacts['changes']}/{change_id}.md",
    }
    if RISK_ORDER[risk] >= RISK_ORDER["R2"]:
        result["decision"] = f"{artifacts['decisions']}/{change_id}.md"
    if risk == "R3":
        result["threat_model"] = f"{artifacts['threat_models']}/{change_id}.md"
        result["runbook"] = f"{artifacts['runbooks']}/{change_id}.md"
    return result


def command_change_start(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    if contract_version(contract) != 2:
        raise EngineeringError("Run `engineering contract migrate --write` before change start")
    change_id = validate_change_id(args.change_id)
    evidence_file = Path(contract["artifacts"]["evidence"]) / f"{change_id}.json"
    if safe_relative_path(root, evidence_file, for_write=True).exists():
        raise EngineeringError(f"Change already exists: {change_id}")
    digest, paths = diff_digest(root)
    artifacts = artifact_paths(contract, change_id, args.risk)
    write_repo_text(root, artifacts["brief"], BRIEF.format(change_id=change_id, risk=args.risk))
    if "decision" in artifacts:
        write_repo_text(root, artifacts["decision"], ADR.format(change_id=change_id))
    if "threat_model" in artifacts:
        write_repo_text(root, artifacts["threat_model"], THREAT_MODEL.format(change_id=change_id))
    if "runbook" in artifacts:
        write_repo_text(root, artifacts["runbook"], RUNBOOK.format(change_id=change_id))
    record = new_evidence(
        change_id,
        args.risk,
        args.competency,
        digest,
        paths,
        artifacts,
        contract.get("review_interval_days", 7),
    )
    save_evidence(root, contract, record, overwrite=False)
    print(f"Started change: {change_id} ({args.risk})")
    for kind, path in artifacts.items():
        print(f"  {kind}: {path}")
    return 0


def select_commands(
    contract: dict[str, Any], ids: list[str], risk: str | None
) -> list[dict[str, Any]]:
    commands = contract["verification"]
    if ids:
        by_id = {command["id"]: command for command in commands}
        missing = sorted(set(ids) - set(by_id))
        if missing:
            raise EngineeringError(f"Unknown verification command(s): {', '.join(missing)}")
        return [by_id[command_id] for command_id in ids]
    if risk:
        wanted = set(required_command_ids(contract, risk))
        return [command for command in commands if command["id"] in wanted]
    return commands


def command_verify(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    if contract_version(contract) != 2:
        raise EngineeringError("Contract v1 cannot execute commands; migrate explicitly first")
    record = read_evidence(root, contract, args.change_id)
    digest, paths = diff_digest(root)
    commands = select_commands(contract, args.id, record["risk"])
    if not commands:
        raise EngineeringError("No verification commands selected")
    results: list[dict[str, Any]] = []
    failed = False
    for command in commands:
        command_id = command["id"]
        print(f"Running {command_id} ...")
        started = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(
                command["argv"],
                cwd=root,
                env=minimal_subprocess_env(command.get("env", {})),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                timeout=command.get("timeout_seconds", 300),
                check=False,
            )
            exit_code: int | None = completed.returncode
            success = exit_code == 0
            if not success:
                print(
                    "  child output was not retained; rerun the reviewed command "
                    "directly if detailed logs are safe to inspect",
                    file=sys.stderr,
                )
        except subprocess.TimeoutExpired:
            exit_code = None
            success = False
            timed_out = True
        except OSError:
            exit_code = None
            success = False
            print(
                "  command could not be started; no operating-system detail was retained",
                file=sys.stderr,
            )
        duration_ms = round((time.monotonic() - started) * 1000)
        print(f"  {'passed' if success else 'failed'} ({duration_ms} ms)")
        results.append(
            {
                "command_id": command_id,
                "status": "passed" if success else "failed",
                "exit_code": exit_code,
                "timed_out": timed_out,
                "duration_ms": duration_ms,
                "diff_digest": digest,
                "verified_at": now_iso(),
            }
        )
        failed = failed or not success
    retained = [
        item for item in record.get("verification", [])
        if item.get("command_id") not in {new["command_id"] for new in results}
    ]
    record["verification"] = retained + results
    record["diff"] = {"digest": digest, "paths": paths}
    record["updated_at"] = now_iso()
    save_evidence(root, contract, record, overwrite=True)
    return 1 if failed else 0


def evidence_gaps(
    root: Path,
    contract: dict[str, Any],
    record: dict[str, Any],
    current_digest: str,
) -> list[str]:
    gaps: list[str] = []
    risk = record["risk"]
    for kind, path in record.get("artifacts", {}).items():
        try:
            target = safe_relative_path(root, path)
        except EngineeringError as exc:
            gaps.append(str(exc))
            continue
        if not target.is_file() or target.stat().st_size < 20:
            gaps.append(f"missing or empty {kind}: {path}")
        elif "<!-- engineering-ownership:fill-required -->" in target.read_text(
            encoding="utf-8", errors="replace"
        ):
            gaps.append(f"unfilled {kind}: {path}")
    required = required_command_ids(contract, risk)
    passing = {
        item.get("command_id")
        for item in record.get("verification", [])
        if item.get("status") == "passed" and item.get("diff_digest") == current_digest
    }
    for command_id in required:
        if command_id not in passing:
            gaps.append(f"verification '{command_id}' has no passing result for current diff")
    if RISK_ORDER[risk] >= RISK_ORDER["R2"] and record.get("teach_back", {}).get("status") != "passed":
        gaps.append("teach-back review has not passed")
    if record.get("diff", {}).get("digest") != current_digest:
        gaps.append("evidence diff digest is stale")
    return gaps


def command_check(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    digest, paths = diff_digest(root)
    risk = classify_risk(contract, paths, args.risk)
    gaps: list[str] = []
    record: dict[str, Any] | None = None
    if contract_version(contract) == 1:
        gaps.append("contract v1 is read-only compatible; migrate before enforce")
    elif risk != "R0":
        records = list_evidence(root, contract)
        if args.change:
            record = read_evidence(root, contract, args.change)
        else:
            matching = [item for item in records if item.get("diff", {}).get("digest") == digest]
            if len(matching) == 1:
                record = matching[0]
            elif not matching:
                gaps.append("no change evidence is bound to the current diff")
            else:
                gaps.append("multiple evidence records match; pass --change")
        if record:
            if RISK_ORDER[record["risk"]] < RISK_ORDER[risk]:
                gaps.append(f"recorded risk {record['risk']} is lower than detected risk {risk}")
            gaps.extend(evidence_gaps(root, contract, record, digest))
    print(f"Risk: {risk}")
    print(f"Changed paths: {len(paths)}")
    if gaps:
        for gap in gaps:
            print(f"GAP: {gap}")
        print(f"RESULT: {'BLOCKED' if args.mode == 'enforce' else 'ADVISE'}")
        return 1 if args.mode == "enforce" else 0
    print("RESULT: PASS")
    return 0


EXPLAIN_QUESTIONS = (
    "1. What problem and user value does this change address?",
    "2. What is the entry point, data/state flow, and persistent or external effect?",
    "3. Why was this design chosen, and which alternative was rejected?",
    "4. Where can it fail, and how will that failure be observed?",
    "5. What evidence shows the current diff works in tests and the real runtime seam?",
    "6. How can this change be rolled back, repaired, or safely disabled?",
)


def command_explain(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    record = read_evidence(root, contract, args.change_id)
    print(f"Teach-back for {record['change_id']} ({record['risk']})")
    print("Answer without AI supplying the content:")
    for question in EXPLAIN_QUESTIONS:
        print(question)
    return 0


def command_change_review(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    record = read_evidence(root, contract, args.change_id)
    gaps = [redact(item.strip()) for item in args.gap if item.strip()]
    status = args.status
    review_days = args.review_days or contract.get("review_interval_days", 7)
    if not 1 <= review_days <= 365:
        raise EngineeringError("review-days must be between 1 and 365")
    if status == "passed" and gaps:
        raise EngineeringError("A passed review cannot include gaps")
    record["teach_back"] = {
        "status": status,
        "gaps": gaps,
        "reviewed_at": now_iso(),
        "review_due": (
            date.today() + timedelta(days=review_days)
        ).isoformat(),
        "self_attested": True,
    }
    record["updated_at"] = now_iso()
    save_evidence(root, contract, record, overwrite=True)
    print(f"Recorded self-review: {record['change_id']} -> {status}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    if contract_version(contract) == 1:
        print("Contract v1: audit and check are available; migrate for evidence status.")
        return 0
    digest, _ = diff_digest(root)
    records = list_evidence(root, contract)
    today = date.today().isoformat()
    shown = 0
    for record in records:
        teach_back = record.get("teach_back", {})
        due = teach_back.get("review_due")
        if args.due and (not due or due > today):
            continue
        stale = record.get("diff", {}).get("digest") != digest
        print(
            f"{record['change_id']}: {record['risk']} "
            f"review={teach_back.get('status', 'pending')} due={due or '-'} "
            f"current_diff={'no' if stale else 'yes'}"
        )
        if record.get("competencies"):
            print(f"  competencies: {', '.join(record['competencies'])}")
        current_gaps = evidence_gaps(root, contract, record, digest)
        for gap in current_gaps:
            print(f"  gap: {redact(str(gap))}")
        shown += 1
    if not shown:
        print("No matching change records.")
    return 0


def handoff_text(root: Path, contract: dict[str, Any], change: str | None) -> str:
    digest, paths = diff_digest(root)
    records = list_evidence(root, contract) if contract_version(contract) == 2 else []
    if change:
        records = [read_evidence(root, contract, change)]
    lines = [
        "# Engineering handoff",
        "",
        f"- Repository: `{root.name}`",
        f"- Revision: `{head_revision(root)[:12]}`",
        f"- Current diff digest: `{digest}`",
        "",
        "## Changed paths",
        "",
    ]
    lines.extend(f"- `{path}`" for path in paths)
    if not paths:
        lines.append("- Clean working tree")
    lines.extend(["", "## Change records", ""])
    for record in records:
        review = record.get("teach_back", {})
        lines.append(
            f"- `{record['change_id']}`: risk {record['risk']}; "
            f"teach-back {review.get('status', 'pending')}; "
            f"review due {review.get('review_due', '-')}"
        )
        if record.get("competencies"):
            lines.append(
                "  - competencies: " + ", ".join(record["competencies"])
            )
        if record.get("verification"):
            for result in record["verification"]:
                current = result.get("diff_digest") == digest
                lines.append(
                    f"  - verification `{result.get('command_id', '?')}`: "
                    f"{result.get('status', 'unknown')} "
                    f"({'current' if current else 'stale'} diff)"
                )
        for gap in review.get("gaps", []):
            lines.append(f"  - gap: {redact(str(gap))}")
    if not records:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Resume safely",
            "",
            "1. Read `.engineering/contract.json` and the referenced change documents.",
            "2. Compare the current diff digest with verification evidence.",
            "3. Re-run stale verification and preserve unresolved learning gaps.",
            "",
        ]
    )
    return "\n".join(lines)


def command_handoff(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    output = handoff_text(root, contract, args.change)
    if args.output:
        path = write_repo_text(root, args.output, output, overwrite=args.overwrite)
        print(f"Wrote {relative(root, path)}")
    else:
        print(output, end="")
    return 0


def command_contract_migrate(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    path = root / ".engineering" / "contract.json"
    current = read_contract(root)
    if contract_version(current) != 1:
        print("Contract is already v2.")
        return 0
    migrated = validate_contract(migrate_v1(current), allow_v1=False)
    if not args.write:
        print(json_text(migrated), end="")
        print("Preview only. Re-run with --write after reviewing argv and env.", file=sys.stderr)
        return 0
    backup = root / ".engineering" / "contract.v1.backup.json"
    if backup.exists():
        raise EngineeringError("Refusing migration because contract.v1.backup.json already exists")
    write_repo_text(root, ".engineering/contract.v1.backup.json", json_text(current))
    write_repo_text(root, ".engineering/contract.json", json_text(migrated), overwrite=True)
    print("Migrated contract v1 to v2 and preserved .engineering/contract.v1.backup.json")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="engineering")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--repo", help="Path inside a Git repository")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a non-destructive v2 contract")
    init.add_argument("--kind", choices=("product", "prototype", "library"), default="product")
    init.add_argument("--status", choices=("active", "portfolio", "coursework", "archived"), default="active")
    init.add_argument("--agent-pointers", action="store_true")
    init.set_defaults(func=command_init)

    audit = sub.add_parser("audit", help="Show evidence signals and gaps without scores")
    audit.add_argument("--format", choices=("text", "json"), default="text")
    audit.set_defaults(func=command_audit)

    change = sub.add_parser("change", help="Manage a change evidence record")
    change_sub = change.add_subparsers(dest="change_command", required=True)
    start = change_sub.add_parser("start")
    start.add_argument("change_id")
    start.add_argument("--risk", choices=tuple(RISK_ORDER), required=True)
    start.add_argument(
        "--competency",
        action="append",
        default=[],
        choices=sorted(COMPETENCIES),
    )
    start.set_defaults(func=command_change_start)
    review = change_sub.add_parser("review")
    review.add_argument("change_id")
    review.add_argument("--status", choices=("passed", "gaps"), required=True)
    review.add_argument("--gap", action="append", default=[])
    review.add_argument("--review-days", type=int)
    review.set_defaults(func=command_change_review)

    verify = sub.add_parser("verify", help="Execute argv verification and bind results to the diff")
    verify.add_argument("change_id")
    verify.add_argument("--id", action="append", default=[])
    verify.set_defaults(func=command_verify)

    check = sub.add_parser("check", help="Evaluate current evidence gates")
    check.add_argument("--mode", choices=("advise", "enforce"), default="advise")
    check.add_argument("--risk", choices=tuple(RISK_ORDER))
    check.add_argument("--change")
    check.set_defaults(func=command_check)

    explain = sub.add_parser("explain", help="Print no-AI teach-back questions")
    explain.add_argument("change_id")
    explain.set_defaults(func=command_explain)

    status = sub.add_parser("status", help="Show open evidence and review obligations")
    status.add_argument("--due", action="store_true")
    status.set_defaults(func=command_status)

    handoff = sub.add_parser("handoff", help="Create a conversation-independent handoff")
    handoff.add_argument("--change")
    handoff.add_argument("--output")
    handoff.add_argument("--overwrite", action="store_true")
    handoff.set_defaults(func=command_handoff)

    contract = sub.add_parser("contract", help="Manage the repository contract")
    contract_sub = contract.add_subparsers(dest="contract_command", required=True)
    migrate = contract_sub.add_parser("migrate")
    migrate.add_argument("--write", action="store_true")
    migrate.set_defaults(func=command_contract_migrate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except EngineeringError as exc:
        print(f"engineering: {redact(str(exc))}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("engineering: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
