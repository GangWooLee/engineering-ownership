from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
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
    contract_version,
    default_contract,
    effective_risk,
    migrate_v1,
    read_contract,
    required_command_ids,
    validate_contract,
)
from .repository import changed_paths, diff_digest, head_revision, repo_root
from .templates import ADR, BRIEF, POINTER, RUNBOOK, THREAT_MODEL


DECISION_REFERENCE = re.compile(
    r"engineering-decision:\s*([a-z0-9][a-z0-9_-]{2,79})\s*\|\s*([^\s]+)"
)


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
    write_repo_text(
        root,
        ".engineering/handoffs/.gitignore",
        "*\n!.gitignore\n",
    )
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


def readable_title(change_id: str) -> str:
    title = " ".join(part for part in re.split(r"[-_]+", change_id) if part)
    return title[:1].upper() + title[1:]


def template_values(record: dict[str, Any]) -> dict[str, str]:
    created_at = record["created_at"]
    try:
        created_date = datetime.fromisoformat(created_at).date().isoformat()
    except ValueError as exc:
        raise EngineeringError("Evidence created_at must be a valid ISO timestamp") from exc
    return {
        "change_id": record["change_id"],
        "title": record.get("title") or readable_title(record["change_id"]),
        "created_at": created_at,
        "date": created_date,
        "risk": record["risk"],
    }


def write_missing_artifacts(
    root: Path,
    record: dict[str, Any],
    required: dict[str, str],
) -> list[str]:
    templates = {
        "brief": BRIEF,
        "decision": ADR,
        "threat_model": THREAT_MODEL,
        "runbook": RUNBOOK,
    }
    created: list[str] = []
    values = template_values(record)
    for kind, path in required.items():
        target = safe_relative_path(root, path, for_write=True)
        if target.exists():
            continue
        write_repo_text(root, path, templates[kind].format(**values))
        created.append(path)
    return created


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
    title = (args.title or readable_title(change_id)).strip()
    if not title or len(title) > 160:
        raise EngineeringError("title must be 1..160 characters")
    record = new_evidence(
        change_id,
        title,
        args.risk,
        args.competency,
        digest,
        paths,
        artifacts,
        contract.get("review_interval_days", 7),
    )
    write_missing_artifacts(root, record, artifacts)
    save_evidence(root, contract, record, overwrite=False)
    print(f"Started change: {change_id} ({args.risk})")
    for kind, path in artifacts.items():
        print(f"  {kind}: {path}")
    return 0


def command_change_set_risk(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    record = read_evidence(root, contract, args.change_id)
    current = record["risk"]
    target = args.risk
    if RISK_ORDER[target] < RISK_ORDER[current]:
        raise EngineeringError("Risk can only be raised; downward adjustment is unsupported")
    if RISK_ORDER[target] == RISK_ORDER[current]:
        print(f"Risk unchanged: {record['change_id']} remains {current}")
        return 0
    required = artifact_paths(contract, record["change_id"], target)
    created = write_missing_artifacts(root, record, required)
    record["risk"] = target
    record["artifacts"] = {**record.get("artifacts", {}), **required}
    record["updated_at"] = now_iso()
    save_evidence(root, contract, record, overwrite=True)
    print(f"Raised risk: {record['change_id']} {current} -> {target}")
    for path in created:
        print(f"  created: {path}")
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
    detected = effective_risk(contract, paths, recorded=record["risk"])
    if RISK_ORDER[detected] > RISK_ORDER[record["risk"]]:
        raise EngineeringError(
            f"Detected risk {detected} exceeds recorded risk {record['risk']}; "
            f"run `engineering change set-risk {record['change_id']} --risk {detected}` first"
        )
    commands = select_commands(contract, args.id, detected)
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
    if record.get("diff", {}).get("digest") != current_digest:
        gaps.append("evidence diff digest is stale")
    return gaps


def text_paths(root: Path, paths: list[str]) -> list[str]:
    result: list[str] = []
    for relative_path in sorted(set(paths)):
        try:
            path = safe_relative_path(root, relative_path)
        except EngineeringError:
            continue
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            if b"\x00" not in path.read_bytes()[:8192]:
                result.append(relative_path)
        except OSError:
            continue
    return result


def all_repository_paths(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise EngineeringError("Could not enumerate repository files")
    return [
        value.decode("utf-8", errors="surrogateescape")
        for value in completed.stdout.split(b"\0")
        if value
    ]


def implementation_references(text: str) -> list[str]:
    match = re.search(
        r"^## Implementation references\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    paths: list[str] = []
    for line in match.group(1).splitlines():
        item = re.match(r"^\s*-\s+`?([^`\s]+)`?", line)
        if item:
            paths.append(item.group(1).split("::", 1)[0])
    return paths


def decision_is_superseded(text: str) -> bool:
    status = re.search(r"^Status:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if status and "superseded" in status.group(1).lower():
        return True
    replacement = re.search(r"^Superseded by:\s*(.+)$", text, re.MULTILINE)
    return bool(replacement and replacement.group(1).strip().lower() not in {"", "none"})


def reference_gaps(
    root: Path,
    contract: dict[str, Any],
    paths: list[str],
    *,
    change_id: str | None = None,
) -> list[str]:
    gaps: list[str] = []
    records = {record["change_id"]: record for record in list_evidence(root, contract)}
    markers: list[tuple[str, str, str]] = []
    for relative_path in text_paths(root, paths):
        path = safe_relative_path(root, relative_path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in DECISION_REFERENCE.finditer(text):
            marker_id, marker_path = match.groups()
            if change_id and marker_id != change_id:
                continue
            markers.append((relative_path, marker_id, marker_path))

    for source_path, marker_id, marker_path in markers:
        record = records.get(marker_id)
        if not record:
            gaps.append(f"{source_path}: decision reference '{marker_id}' has no evidence")
            continue
        canonical = record.get("artifacts", {}).get("decision")
        if not canonical:
            gaps.append(f"{source_path}: decision reference '{marker_id}' has no ADR")
            continue
        if marker_path != canonical:
            gaps.append(
                f"{source_path}: decision reference path must be canonical ADR '{canonical}'"
            )
            continue
        try:
            adr_path = safe_relative_path(root, canonical)
        except EngineeringError as exc:
            gaps.append(str(exc))
            continue
        if not adr_path.is_file():
            gaps.append(f"{source_path}: referenced ADR is missing: {canonical}")
            continue
        adr_text = adr_path.read_text(encoding="utf-8", errors="replace")
        if decision_is_superseded(adr_text):
            gaps.append(f"{source_path}: decision '{marker_id}' is superseded")

    selected_records = (
        [records[change_id]] if change_id and change_id in records else list(records.values())
    )
    referenced_ids = {marker_id for _, marker_id, _ in markers}
    for record in selected_records:
        if change_id is None and record["change_id"] not in referenced_ids:
            continue
        decision = record.get("artifacts", {}).get("decision")
        if not decision:
            continue
        try:
            adr_path = safe_relative_path(root, decision)
        except EngineeringError as exc:
            gaps.append(str(exc))
            continue
        if not adr_path.is_file():
            continue
        for implementation_path in implementation_references(
            adr_path.read_text(encoding="utf-8", errors="replace")
        ):
            try:
                target = safe_relative_path(root, implementation_path)
            except EngineeringError as exc:
                gaps.append(f"{decision}: {exc}")
                continue
            if not target.is_file():
                gaps.append(
                    f"{decision}: implementation reference is missing: {implementation_path}"
                )
    return sorted(set(gaps))


def command_refs_check(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    if args.change:
        read_evidence(root, contract, args.change)
    paths = all_repository_paths(root) if args.all else changed_paths(root)
    gaps = reference_gaps(root, contract, paths, change_id=args.change)
    print(f"Decision references checked: {len(text_paths(root, paths))} file(s)")
    for gap in gaps:
        print(f"GAP: {gap}")
    print("RESULT: PASS" if not gaps else "RESULT: BLOCKED")
    return 1 if gaps else 0


def command_check(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    digest, paths = diff_digest(root)
    gaps: list[str] = []
    record: dict[str, Any] | None = None
    if args.change and contract_version(contract) == 2:
        record = read_evidence(root, contract, args.change)
    risk = effective_risk(
        contract,
        paths,
        explicit=args.risk,
        recorded=record["risk"] if record else None,
    )
    if contract_version(contract) == 1:
        gaps.append("contract v1 is read-only compatible; migrate before enforce")
    elif risk != "R0":
        records = list_evidence(root, contract)
        if not args.change:
            matching = [item for item in records if item.get("diff", {}).get("digest") == digest]
            if len(matching) == 1:
                record = matching[0]
            elif not matching:
                gaps.append("no change evidence is bound to the current diff")
            else:
                gaps.append("multiple evidence records match; pass --change")
        if record:
            if RISK_ORDER[record["risk"]] < RISK_ORDER[risk]:
                gaps.append(
                    f"recorded risk {record['risk']} is lower than effective risk {risk}; "
                    f"run `engineering change set-risk {record['change_id']} --risk {risk}`"
                )
            gaps.extend(evidence_gaps(root, contract, record, digest))
            gaps.extend(reference_gaps(root, contract, paths, change_id=record["change_id"]))
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
    print(f"Optional decision review for {record['change_id']} ({record['risk']})")
    print("Read the canonical records:")
    for kind, path in record.get("artifacts", {}).items():
        print(f"  {kind}: {path}")
    print("Use these prompts when revisiting the change:")
    for question in EXPLAIN_QUESTIONS:
        print(question)
    print(
        "This review records retained understanding or learning gaps; "
        "it is not a default completion gate."
    )
    return 0


def command_change_review(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    contract = read_contract(root)
    record = read_evidence(root, contract, args.change_id)
    gaps = [redact(item.strip()) for item in args.gap if item.strip()]
    status = args.status
    review_days = (
        args.review_days
        if args.review_days is not None
        else contract.get("review_interval_days", 7)
    )
    if not 1 <= review_days <= 365:
        raise EngineeringError("revisit-days must be between 1 and 365")
    if status == "reviewed" and gaps:
        raise EngineeringError("A reviewed state cannot include gaps")
    record["understanding"] = {
        "status": status,
        "gaps": gaps,
        "reviewed_at": now_iso(),
        "revisit_after": (
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
        understanding = record.get("understanding", {})
        due = understanding.get("revisit_after")
        if args.due and (not due or due > today):
            continue
        stale = record.get("diff", {}).get("digest") != digest
        print(
            f"{record['change_id']}: {record['risk']} "
            f"understanding={understanding.get('status', 'not-reviewed')} "
            f"revisit_after={due or '-'} "
            f"current_diff={'no' if stale else 'yes'}"
        )
        for kind, path in record.get("artifacts", {}).items():
            print(f"  {kind}: {path}")
        if record.get("competencies"):
            print(f"  competencies: {', '.join(record['competencies'])}")
        current_gaps = evidence_gaps(root, contract, record, digest)
        for gap in current_gaps:
            print(f"  gap: {redact(str(gap))}")
        for gap in understanding.get("gaps", []):
            print(f"  understanding gap: {redact(str(gap))}")
        shown += 1
    if not shown:
        print("No matching change records.")
    return 0


def local_plugin_state(executable: str, argv: list[str]) -> str:
    if shutil.which(executable) is None:
        return "unavailable"
    try:
        result = subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
            check=False,
            env=minimal_subprocess_env({}),
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    output = (result.stdout + result.stderr).lower()
    if "engineering-ownership" not in output:
        return "not-detected"
    if any(token in output for token in ("enabled", "installed", "active")):
        return "detected"
    return "detected"


def doctor_payload(root: Path) -> dict[str, Any]:
    contract_path = root / ".engineering" / "contract.json"
    contract: dict[str, Any] | None = None
    contract_status = "missing"
    command_checks: list[dict[str, str]] = []
    if contract_path.is_file():
        try:
            contract = read_contract(root)
            contract_status = f"v{contract_version(contract)}"
        except EngineeringError:
            contract_status = "invalid"
    if contract and contract_version(contract) == 2:
        for command in contract.get("verification", []):
            executable = command["argv"][0]
            available = (
                Path(executable).is_file()
                if Path(executable).is_absolute()
                else shutil.which(executable) is not None
            )
            command_checks.append(
                {"id": command["id"], "executable": "available" if available else "missing"}
            )
    pointers = {}
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = root / name
        pointers[name] = (
            path.is_file()
            and "<!-- engineering-ownership:start -->" in path.read_text(
                encoding="utf-8", errors="replace"
            )
        )
    hooks = (
        contract.get("automation", {}).get("session_hooks", "off")
        if contract
        else "unknown"
    )
    return {
        "git": "available" if shutil.which("git") else "missing",
        "cli": {"version": __version__},
        "plugins": {
            "codex": local_plugin_state("codex", ["codex", "plugin", "list"]),
            "claude": local_plugin_state("claude", ["claude", "plugin", "list"]),
        },
        "contract": contract_status,
        "agent_pointers": pointers,
        "verification_commands": command_checks,
        "session_hooks": hooks,
    }


def command_doctor(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    payload = doctor_payload(root)
    if args.format == "json":
        print(json_text(payload), end="")
        return 0
    print("Engineering doctor")
    print(f"  git: {payload['git']}")
    print(f"  cli: {payload['cli']['version']}")
    print(f"  contract: {payload['contract']}")
    print(f"  Codex plugin: {payload['plugins']['codex']}")
    print(f"  Claude plugin: {payload['plugins']['claude']}")
    for name, present in payload["agent_pointers"].items():
        print(f"  {name} pointer: {'present' if present else 'missing'}")
    for command in payload["verification_commands"]:
        print(f"  verify {command['id']}: {command['executable']}")
    print(f"  session hooks: {payload['session_hooks']}")
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
        understanding = record.get("understanding", {})
        lines.append(
            f"- `{record['change_id']}`: risk {record['risk']}; "
            f"understanding {understanding.get('status', 'not-reviewed')}; "
            f"revisit after {understanding.get('revisit_after', '-')}"
        )
        if record.get("artifacts"):
            lines.append("  - canonical records:")
            for kind, path in record["artifacts"].items():
                lines.append(f"    - {kind}: `{path}`")
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
        for gap in understanding.get("gaps", []):
            lines.append(f"  - understanding gap: {redact(str(gap))}")
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
    if args.save:
        handoff_dir = contract.get("artifacts", {}).get(
            "handoffs", ".engineering/handoffs"
        )
        change_id = validate_change_id(args.change) if args.change else "repository"
        stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
        relative_path = f"{handoff_dir}/{stamp}-{change_id}.md"
        ignore = subprocess.run(
            ["git", "check-ignore", "-q", "--", relative_path],
            cwd=root,
            check=False,
        )
        if ignore.returncode != 0:
            raise EngineeringError(
                f"{handoff_dir} must ignore generated handoffs before --save"
            )
        path = write_repo_text(root, relative_path, output)
        print(f"Wrote {relative(root, path)}")
    elif args.output:
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

    doctor = sub.add_parser("doctor", help="Diagnose local setup without network calls")
    doctor.add_argument("--format", choices=("text", "json"), default="text")
    doctor.set_defaults(func=command_doctor)

    change = sub.add_parser("change", help="Manage a change evidence record")
    change_sub = change.add_subparsers(dest="change_command", required=True)
    start = change_sub.add_parser("start")
    start.add_argument("change_id")
    start.add_argument("--risk", choices=tuple(RISK_ORDER), required=True)
    start.add_argument("--title")
    start.add_argument(
        "--competency",
        action="append",
        default=[],
        choices=sorted(COMPETENCIES),
    )
    start.set_defaults(func=command_change_start)
    set_risk = change_sub.add_parser("set-risk")
    set_risk.add_argument("change_id")
    set_risk.add_argument("--risk", choices=("R2", "R3"), required=True)
    set_risk.set_defaults(func=command_change_set_risk)
    review = change_sub.add_parser("review")
    review.add_argument("change_id")
    review.add_argument("--status", choices=("reviewed", "gaps"), required=True)
    review.add_argument("--gap", action="append", default=[])
    review.add_argument("--revisit-days", type=int, dest="review_days")
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

    refs = sub.add_parser("refs", help="Validate engineering decision references")
    refs_sub = refs.add_subparsers(dest="refs_command", required=True)
    refs_check = refs_sub.add_parser("check")
    refs_check.add_argument("--change")
    refs_check.add_argument("--all", action="store_true")
    refs_check.set_defaults(func=command_refs_check)

    explain = sub.add_parser(
        "explain", help="Print records and optional decision-review questions"
    )
    explain.add_argument("change_id")
    explain.set_defaults(func=command_explain)

    status = sub.add_parser("status", help="Show open evidence and review obligations")
    status.add_argument("--due", action="store_true")
    status.set_defaults(func=command_status)

    handoff = sub.add_parser("handoff", help="Create a conversation-independent handoff")
    handoff.add_argument("--change")
    handoff_output = handoff.add_mutually_exclusive_group()
    handoff_output.add_argument("--output")
    handoff_output.add_argument("--save", action="store_true")
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
