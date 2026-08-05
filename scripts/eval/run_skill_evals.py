#!/usr/bin/env python3
"""Run the evaluation prompts with and without the skill, and record evidence.

The withdrawn evaluation could not attribute its result to the skill because the
two configurations differed in more than the skill: responses were written in
different languages, the machine already had the plugin installed at user scope,
and the user-level instruction file restates the skill's own rules. This runner
holds all of that constant so that loading the plugin is the only difference
between the two configurations.

It shells out to the same `claude` CLI the repository is developed with, using
the developer's existing session, so evaluating the skill needs no separate API
credential.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from build_fixture import build as build_fixture


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "engineering-ownership"
MANIFEST = PLUGIN / "skills" / "engineering-ownership" / "evals" / "evals.json"
WORKSPACE = ROOT / "engineering-ownership-workspace"

USER_SETTINGS = Path.home() / ".claude" / "settings.json"

# Runs may write. Several expectations are about what survives the session - a
# rationale a successor could act on, a decision recorded where a later reader
# finds it - and none of that is observable if the run cannot produce it. The
# earlier read-only attempt also did not hold: a pilot run edited a file anyway.
#
# The set is identical for both configurations. Giving the treatment a capability
# the baseline lacks would destroy the comparison exactly as the language
# confound destroyed the first one. Nothing here leaves the fixture: no network,
# no push, no package installation.
AVAILABLE_TOOLS = ("Read", "Glob", "Grep", "Write", "Edit", "Bash", "Skill")
ALLOWED_TOOLS = (
    "Read",
    "Glob",
    "Grep",
    "Write",
    "Edit",
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(git show:*)",
    "Bash(git add:*)",
    "Bash(python3 -m unittest:*)",
)

# The judge is shown what a run did, but must not learn which configuration
# produced it. Tool names are normalized to an action vocabulary so that the
# presence of the Skill tool - which only one configuration can use - cannot be
# read off the log.
ACTION_NAMES = {
    "Read": "read",
    "Glob": "search",
    "Grep": "search",
    "Write": "write",
    "Edit": "write",
    "Bash": "run",
}


def disabled_plugins() -> dict[str, bool]:
    """Switch off every user-scope plugin for the run.

    The maintainer's machine has this skill installed at user scope, so a plain
    invocation gives the baseline the very skill it is supposed to lack. Other
    plugins matter too: one of them rewrites the response format, which would
    make both configurations unrepresentative of a default installation. The
    treatment gets the skill back through --plugin-dir and nothing else.
    """
    try:
        settings = json.loads(USER_SETTINGS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {name: False for name in settings.get("enabledPlugins", {})}

LANGUAGE_CONTROL = "\n\nRespond in English."

CONFIGURATIONS = ("with_skill", "without_skill")


def fixture_dir(scratch: Path, overlay: str, index: int) -> Path:
    """Where one run's fixture is built. Deliberately not a function of the arm.

    This directory is the run's working directory. Anything the run reports
    about its own location quotes it, and the host encodes the working directory
    into the per-project paths it keeps under the real home, so the name also
    reaches text that looks home-relative. When the name contained the
    configuration, that made the path a statement of which arm was executing,
    and two graded runs reached their judge with `eval-7-without_skill-1` in the
    action log.

    Not `HOME`. `build_fixture` sets `HOME` to this directory for the git
    subprocess that builds the fixture, so the commit is reproducible and does
    not read the operator's global config; `invoke` runs the model with the real
    environment. An earlier version of this docstring said the run's `HOME` was
    set here and was wrong.

    The redaction pass now scrubs those paths, but scrubbing is a thing that can
    have a hole -- it has had two. A name that never held the answer cannot leak
    it. Both arms of the same run therefore share this path; they execute one
    after the other and `build_fixture.build` clears the destination first, so
    sharing is safe by construction rather than by timing.

    The arm is still recorded, in the output directory the judge never reads.
    """
    return scratch / f"{overlay}-{index}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_manifest() -> list[dict]:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))["evals"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unreadable eval manifest: {exc}") from exc


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def redact(text: str) -> str:
    return text.replace(str(Path.home()), "~")


def invoke(prompt: str, cwd: Path, model: str, with_skill: bool, timeout: int) -> dict:
    argv = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--settings",
        json.dumps({"enabledPlugins": disabled_plugins()}),
        "--tools",
        *AVAILABLE_TOOLS,
        "--allowedTools",
        *ALLOWED_TOOLS,
        "--no-session-persistence",
    ]
    if with_skill:
        argv += ["--plugin-dir", str(PLUGIN)]

    # The user-level CLAUDE.md restates the skill's rules, so it would leak the
    # skill's content into the baseline. Disable it for both configurations.
    env = {**subprocess.os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}
    env.pop("CLAUDECODE", None)

    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "reason": "timeout", "elapsed": timeout}
    elapsed = round(time.monotonic() - started, 3)

    if completed.returncode != 0:
        return {
            "status": "error",
            "reason": f"exit {completed.returncode}",
            "detail": redact(completed.stderr[-400:]),
            "elapsed": elapsed,
        }
    return parse_stream(completed.stdout, elapsed, argv, cwd)


def action_target(name: str, tool_input: dict, cwd: Path) -> str:
    """Describe what a tool call touched, in terms of the fixture."""

    # A path can sit inside a token rather than start it. `D=/abs/path`,
    # `MEMFILE="~/x`, and `--out=/abs/path` all begin with a letter or a dash,
    # so every leading-character test below returns raw and the absolute path
    # reaches the judge. Two live runs were graded with their fixture directory
    # -- which encodes the configuration -- sitting in the log this way.
    EMBEDDED = re.compile(r'(?<=[=:])["\']?(?=[~$/])[^\s"\']+')

    def relative(raw: str) -> str:
        candidate = Path(raw)
        # A path written with a leading tilde or an unexpanded $HOME is outside
        # the fixture just as surely as one written from the root, and it is how
        # the shell reports a home-relative path after redaction. Treating it as
        # relative left the skill's own directory name sitting in the log.
        if raw.startswith(("~", "$")):
            return "(outside the repository)"
        try:
            return candidate.resolve().relative_to(cwd.resolve()).as_posix()
        except (ValueError, OSError):
            if candidate.is_absolute():
                return "(outside the repository)"
            # Not a path itself, but it may carry one. Normalize what it carries
            # rather than returning the token whole.
            return EMBEDDED.sub("(outside the repository)", raw)

    def looks_like_path(token: str) -> bool:
        return "/" in token or token.startswith("~") or token.endswith((".py", ".md", ".json"))

    def scrub(text: str) -> str:
        # Backstop for any token form the pass above did not recognize: nothing
        # that reaches the judge-visible log may carry the runner's own
        # directory name, which identifies the configuration on its own.
        return text.replace(ROOT.name, "(outside the repository)")

    if name in {"Read", "Write", "Edit"}:
        return scrub(relative(str(tool_input.get("file_path", ""))))
    if name in {"Glob", "Grep"}:
        return scrub(str(tool_input.get("pattern", ""))[:120])
    if name == "Bash":
        command = str(tool_input.get("command", "")).strip()
        # Every token that could be a path goes through the same normalization,
        # not just the ones after the first argument. A two-word command puts its
        # path in the second token, which is exactly where the skill's own
        # reference files were being read from. Quoting must not defeat the
        # check: `cat "~/x"` carries the same path as `cat ~/x`.
        parts = []
        for token in command.split():
            bare = token.strip("\"'")
            parts.append(relative(bare) if looks_like_path(bare) else token)
        return scrub(" ".join(parts)[:160])
    return ""


def parse_stream(stdout: str, elapsed: float, argv: list[str], cwd: Path) -> dict:
    events: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    tool_calls: dict[str, int] = {}
    transcript: list[str] = []
    actions: list[dict] = []
    skill_loaded = False
    skill_action_index: int | None = None
    result: dict = {}

    for event in events:
        if event.get("type") == "result":
            result = event
            continue
        message = event.get("message") or {}
        for block in message.get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and block.get("text"):
                transcript.append(block["text"])
            elif block.get("type") == "tool_use":
                name = block.get("name", "unknown")
                tool_calls[name] = tool_calls.get(name, 0) + 1
                # Detect skill use by the Skill tool alone. Matching the skill's
                # name against tool inputs looked reasonable but reported the
                # baseline as having loaded the skill, because the repository
                # directory carries the same name and appears in every absolute
                # path the agent touches.
                if name == "Skill":
                    # Recorded for the run's own metadata, never for the judge:
                    # only one configuration can produce this entry. The position
                    # is kept so a spend cap can be set without the risk of
                    # cutting a run off before the skill would have been reached.
                    if not skill_loaded:
                        skill_action_index = len(actions) + 1
                    skill_loaded = True
                    continue
                if name in ACTION_NAMES:
                    actions.append(
                        {
                            "action": ACTION_NAMES[name],
                            "target": redact(action_target(name, block.get("input") or {}, cwd)),
                        }
                    )

    response = result.get("result") or (transcript[-1] if transcript else "")
    usage = result.get("usage") or {}
    return {
        "status": "ok" if response else "error",
        "reason": "" if response else "empty response",
        "response": response,
        "transcript": "\n\n".join(transcript),
        "actions": actions,
        "tool_calls": tool_calls,
        "skill_loaded": skill_loaded,
        "skill_action_index": skill_action_index,
        "num_turns": result.get("num_turns", 0),
        "duration_ms": result.get("duration_ms", int(elapsed * 1000)),
        "duration_api_ms": result.get("duration_api_ms", 0),
        "total_cost_usd": result.get("total_cost_usd"),
        "usage": usage,
        "argv": [redact(part) for part in argv],
        "elapsed": elapsed,
    }


def total_tokens(usage: dict) -> int:
    keys = (
        "input_tokens",
        "output_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
    )
    return sum(int(usage.get(key) or 0) for key in keys)


def capture_fixture_delta(cwd: Path, expected_dirty: list[str]) -> dict:
    """Record what the run changed, with content, before the fixture is removed.

    A path list says a record was written; it does not say whether the record is
    usable. Expectations about what survives the session need the text.
    """
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout
    present = sorted(line[2:].strip() for line in status.splitlines() if line.strip())
    changed = sorted(set(present) - set(expected_dirty))

    diff = subprocess.run(
        ["git", "diff"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout

    created: dict[str, str] = {}
    for relative_path in changed:
        path = cwd / relative_path
        if not path.is_file() or path.stat().st_size > 40_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        created[relative_path] = redact(text[:8000])

    return {
        "paths_changed_by_run": changed,
        "tracked_diff": redact(diff[:20_000]),
        "file_contents": created,
    }


def record_run(run_dir: Path, item: dict, configuration: str, outcome: dict, fixture: dict) -> None:
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    if outcome["status"] != "ok":
        write_json(run_dir / "outputs" / "error.json", outcome)
        return

    # AGENTS.md forbids storing home paths, and these artifacts are committed.
    # AGENTS.md forbids storing home paths, and these artifacts are committed.
    (outputs / "response.md").write_text(redact(outcome["response"]), encoding="utf-8")
    (outputs / "transcript.md").write_text(redact(outcome["transcript"]), encoding="utf-8")
    # The ordered record of what the run did. This is what the judge sees in
    # place of the transcript, which names the skill in one configuration only.
    write_json(outputs / "actions.json", {"actions": outcome["actions"]})

    write_json(
        run_dir / "timing.json",
        {
            "total_tokens": total_tokens(outcome["usage"]),
            "duration_ms": outcome["duration_ms"],
            "total_duration_seconds": round(outcome["duration_ms"] / 1000, 3),
            "api_duration_seconds": round(outcome["duration_api_ms"] / 1000, 3),
            "wall_clock_seconds": outcome["elapsed"],
        },
    )
    write_json(
        outputs / "metrics.json",
        {
            "tool_calls": outcome["tool_calls"],
            "total_tool_calls": sum(outcome["tool_calls"].values()),
            "total_steps": outcome["num_turns"],
            "files_created": [],
            "errors_encountered": 0,
            "output_chars": len(outcome["response"]),
            "transcript_chars": len(outcome["transcript"]),
        },
    )
    write_json(
        outputs / "run_meta.json",
        {
            "configuration": configuration,
            "eval_id": item["id"],
            "skill_loaded": outcome["skill_loaded"],
            "skill_action_index": outcome.get("skill_action_index"),
            "num_turns": outcome["num_turns"],
            "total_cost_usd": outcome["total_cost_usd"],
            "usage": outcome["usage"],
            "fixture_commit": fixture["commit"],
            "user_plugins_disabled": sorted(disabled_plugins()),
            "argv": outcome["argv"],
            "recorded_at": now(),
        },
    )


def preflight(model: str, cwd: Path, timeout: int) -> dict:
    """Prove the two configurations differ in skill availability and nothing else."""
    probe = (
        "List the names of any Agent Skills available to you related to "
        "engineering ownership. If none, reply exactly: NONE"
    )
    findings = {}
    for configuration in CONFIGURATIONS:
        outcome = invoke(probe, cwd, model, configuration == "with_skill", timeout)
        findings[configuration] = {
            "status": outcome["status"],
            "answer": (outcome.get("response") or outcome.get("reason", ""))[:300],
        }
    baseline = findings["without_skill"]["answer"].strip().upper()
    treatment = findings["with_skill"]["answer"]
    findings["baseline_clean"] = baseline.startswith("NONE")
    findings["treatment_has_skill"] = "engineering-ownership" in treatment
    findings["checked_at"] = now()
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="exact model id, not an alias")
    parser.add_argument("--iteration", default="iteration-2")
    parser.add_argument("--eval", action="append", type=int, dest="eval_ids", default=[])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--pause", type=int, default=15, help="seconds between runs")
    parser.add_argument("--resume", action="store_true", help="skip runs already recorded")
    args = parser.parse_args()

    if args.runs < 1:
        raise SystemExit("runs must be at least 1")

    items = read_manifest()
    if args.eval_ids:
        items = [item for item in items if item["id"] in set(args.eval_ids)]
    if not items:
        raise SystemExit("no evals selected")

    iteration = WORKSPACE / args.iteration
    iteration.mkdir(parents=True, exist_ok=True)
    # Fixtures live outside the repository: a working directory under a
    # folder named after the skill leaks that name into every absolute path
    # the agent sees, and it would also be picked up by the parent repo.
    scratch = Path(tempfile.mkdtemp(prefix="engo-eval-"))

    if not args.skip_preflight:
        scratch.mkdir(parents=True, exist_ok=True)
        probe_dir = scratch / "preflight"
        fixture = build_fixture("eval-6", probe_dir)
        findings = preflight(args.model, probe_dir, args.timeout)
        findings["fixture_commit"] = fixture["commit"]
        findings["model"] = args.model
        write_json(iteration / "preflight.json", findings)
        if not findings["baseline_clean"]:
            raise SystemExit(
                "baseline is contaminated: it still reports an engineering-ownership skill"
            )
        if not findings["treatment_has_skill"]:
            raise SystemExit("treatment did not load the skill; --plugin-dir had no effect")
        print("preflight passed: baseline clean, treatment loaded the skill")

    overlays = json.loads(
        (ROOT / "scripts" / "eval" / "fixtures" / "recipe.json").read_text(encoding="utf-8")
    )["overlays"]

    completed = 0
    for item in items:
        overlay = f"eval-{item['id']}"
        if overlay not in overlays:
            print(f"skipping eval {item['id']}: no fixture overlay yet")
            continue
        eval_dir = iteration / overlay
        write_json(
            eval_dir / "eval_metadata.json",
            {
                "eval_id": item["id"],
                "eval_name": item["name"],
                "prompt": item["prompt"],
                "expectations": item["expectations"],
            },
        )
        prompt = item["prompt"] + LANGUAGE_CONTROL
        (eval_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

        for index in range(1, args.runs + 1):
            for configuration in CONFIGURATIONS:
                run_dir = eval_dir / configuration / f"run-{index}"
                # A full sweep takes hours. Losing it to one interruption, or
                # paying for it twice, is avoidable: a run that already produced
                # a response is done.
                if args.resume and (run_dir / "outputs" / "response.md").is_file():
                    print(f"skipping {overlay} {configuration} run-{index}: already recorded")
                    continue
                cwd = fixture_dir(scratch, overlay, index)
                fixture = build_fixture(overlay, cwd)
                print(f"running {overlay} {configuration} run-{index} ...")
                outcome = invoke(
                    prompt, cwd, args.model, configuration == "with_skill", args.timeout
                )
                record_run(run_dir, item, configuration, outcome, fixture)
                delta = capture_fixture_delta(cwd, fixture["dirty_paths"])
                write_json(run_dir / "outputs" / "fixture_delta.json", delta)
                if delta["paths_changed_by_run"]:
                    print(f"  the run changed {len(delta['paths_changed_by_run'])} path(s)")
                print(f"  {outcome['status']} ({outcome.get('elapsed', 0)}s)")
                completed += 1
                shutil.rmtree(cwd, ignore_errors=True)
                # Eight consecutive runs were once rejected three seconds apart
                # while working runs were fifteen to twenty seconds apart. A
                # pause costs little against a run that takes minutes, and a
                # truncated tail costs a whole condition.
                time.sleep(args.pause)

    shutil.rmtree(scratch, ignore_errors=True)
    print(f"completed {completed} run(s) into {iteration.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
