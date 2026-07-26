from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
VENDOR = ROOT / "scripts" / "eval" / "vendor"
SKILL = ROOT / "plugins" / "engineering-ownership" / "skills" / "engineering-ownership"
EVALS = SKILL / "evals" / "evals.json"
VALIDATION = ROOT / "docs" / "validation"
WORKSPACE = ROOT / "engineering-ownership-workspace"

ALLOWED_STATUS = {"Current", "Superseded", "Withdrawn"}

# Tokens that belong to this skill's own vocabulary. An expectation that requires
# them cannot be passed on merit by a baseline that has never seen the skill, so
# neither a grader nor an expectation may depend on them. The risk tiers are
# included as whole words: a baseline can reason about how risky a change is, but
# it cannot produce a letter-and-digit label this skill invented.
# See docs/validation/skill-evaluation.md.
PRIVATE_VOCABULARY = ("teach-back", "engineering-decision:", "runbook")
PRIVATE_TIERS = re.compile(r"\bR[0-3]\b")

# An expectation phrased purely as restraint is satisfied by a response that says
# nothing at all, which is how nine of the withdrawn manifest's expectations
# became free points. Requiring the response to show it made the choice is what
# turns restraint into an observable behavior.
BARE_NEGATIVE = re.compile(
    r"^(does not|do not|avoids|never|refrains|omits)\b", re.IGNORECASE
)
SHOWS_ITS_REASONING = re.compile(
    r"\b(and (says|states|explains|names)|rather than|instead of|because|why)\b",
    re.IGNORECASE,
)

RESULTS_BLOCK = re.compile(r"```json\s*(\{[^`]*?\"with_skill_mean\"[^`]*?\})\s*```", re.DOTALL)
# The withdrawn claim's original form was a markdown table, not a JSON block.
# Any surface that pairs a with/without-skill comparison with score-shaped
# numbers is treated as a published result and held to the same contract.
SKILL_COMPARISON = re.compile(r"(?i)\bwith(?:out)?[ _-]skill")
EFFICACY_SHAPE = re.compile(r"\b\d+\s*/\s*\d+\b|\b\d+(?:\.\d+)?\s*%")
STATUS_LINE = re.compile(r"^Status:\s*(\S+)", re.MULTILINE)
CHECKED_LINE = re.compile(r"^Checked:\s*\d{4}-\d{2}-\d{2}", re.MULTILINE)
SUPERSEDED_LINE = re.compile(r"^Superseded by:\s*\S+", re.MULTILINE)
RETIRED_STATUS = re.compile(r"^Status:\s*(Withdrawn|Superseded)", re.MULTILINE)
DIGEST_ROW = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$", re.MULTILINE)


def load_evals() -> dict:
    return json.loads(EVALS.read_text(encoding="utf-8"))


def validation_documents() -> list[Path]:
    return sorted(path for path in VALIDATION.glob("*.md") if path.name != "README.md")


class EvalManifestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load_evals()
        self.evals = self.data["evals"]

    def test_skill_name_matches_the_skill_it_evaluates(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        declared = re.search(r"^name:\s*(\S+)$", frontmatter, re.MULTILINE)
        self.assertIsNotNone(declared)
        self.assertEqual(self.data["skill_name"], declared.group(1))

    def test_every_eval_declares_the_required_fields(self) -> None:
        self.assertTrue(self.evals)
        for item in self.evals:
            for field in ("id", "name", "prompt", "expected_output", "expectations"):
                self.assertIn(field, item, f"{item.get('name', '?')} is missing {field}")
            self.assertTrue(item["expectations"], f"{item['name']} has no expectations")

    def test_identifiers_are_unique_and_stable(self) -> None:
        names = [item["name"] for item in self.evals]
        identifiers = [item["id"] for item in self.evals]
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(len(set(identifiers)), len(identifiers))
        for name in names:
            self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_every_eval_carries_enough_expectations_to_discriminate(self) -> None:
        # Counts deliberately vary. Requiring a uniform count forced unrelated
        # observations to be bundled into one expectation, which is how twelve of
        # the withdrawn manifest's expectations became unresolvable. The harness
        # computes the denominator, so it does not need them to match.
        for item in self.evals:
            self.assertGreaterEqual(
                len(item["expectations"]),
                3,
                f"{item['name']} has too few expectations to discriminate",
            )

    def test_no_expectation_requires_the_skill_private_vocabulary(self) -> None:
        # The withdrawn grader matched on these terms. Moving the same dependency
        # into the expectation text would reintroduce the defect one layer up:
        # a baseline that has never seen the skill cannot produce them, so it
        # could not pass on merit however well it reasoned.
        for item in self.evals:
            for index, expectation in enumerate(item["expectations"]):
                lowered = expectation.lower()
                for token in PRIVATE_VOCABULARY:
                    self.assertNotIn(
                        token,
                        lowered,
                        f"{item['name']}.expectations[{index}] requires '{token}'",
                    )
                self.assertIsNone(
                    PRIVATE_TIERS.search(expectation),
                    f"{item['name']}.expectations[{index}] requires a risk-tier label",
                )

    def test_no_expectation_is_satisfied_by_silence(self) -> None:
        # A purely negative expectation passes for a response that never raises
        # the subject. Restraint is only observable when the response shows it
        # considered the question and chose.
        for item in self.evals:
            for index, expectation in enumerate(item["expectations"]):
                if BARE_NEGATIVE.match(expectation.strip()) and not SHOWS_ITS_REASONING.search(
                    expectation
                ):
                    self.fail(
                        f"{item['name']}.expectations[{index}] is phrased as bare "
                        "restraint; require the response to show it made the choice"
                    )

    def test_prompts_and_expectations_are_english_only(self) -> None:
        # The withdrawn evaluation compared Korean with-skill responses against
        # English baseline responses, so language and skill availability varied
        # together. Restricting the manifest to ASCII keeps language a constant.
        for item in self.evals:
            for field in ("prompt", "expected_output"):
                self.assertTrue(
                    str(item[field]).isascii(),
                    f"{item['name']}.{field} is not ASCII",
                )
            for index, expectation in enumerate(item["expectations"]):
                self.assertTrue(
                    expectation.isascii(),
                    f"{item['name']}.expectations[{index}] is not ASCII",
                )


class SkillDescriptionCase(unittest.TestCase):
    """The description is the only text that decides whether the skill is consulted."""

    def description(self) -> str:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^description:\s*(.+?)$", text, re.MULTILINE)
        self.assertIsNotNone(match, "SKILL.md declares no description")
        return match.group(1).strip()

    def test_description_fits_the_agent_skills_limits(self) -> None:
        # Rules taken from the reference validator shipped with skill-creator.
        # They are enforced here because a description that fails them is not
        # loaded at all, and nothing else in this repository checks them.
        value = self.description()
        self.assertLessEqual(len(value), 1024, "description exceeds the 1024 character limit")
        self.assertNotIn("<", value, "description cannot contain angle brackets")
        self.assertNotIn(">", value, "description cannot contain angle brackets")
        self.assertTrue(value.isascii(), "description must be ASCII")


class TriggerProbeCase(unittest.TestCase):
    """Probes for whether the skill is consulted, kept separate from what it does."""

    def probes(self) -> list[dict]:
        path = SKILL / "evals" / "triggers.json"
        if not path.is_file():
            self.skipTest("no trigger probes are present")
        return json.loads(path.read_text(encoding="utf-8"))["probes"]

    def test_probes_are_well_formed(self) -> None:
        probes = self.probes()
        identifiers = [p["id"] for p in probes]
        self.assertEqual(len(set(identifiers)), len(identifiers), "probe ids repeat")
        for probe in probes:
            self.assertRegex(probe["id"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertIn(probe["expect"], {"trigger", "no-trigger", "unscored"})
            self.assertIn(probe["split"], {"train", "test"})
            self.assertTrue(probe["query"].strip(), f"{probe['id']} has an empty query")
            self.assertTrue(probe["query"].isascii(), f"{probe['id']} query is not ASCII")

    def test_both_scored_classes_are_represented(self) -> None:
        # With positives alone the measurement has recall and no precision, and a
        # description that fired on everything would score perfectly. That gap is
        # why this file exists.
        probes = self.probes()
        for label in ("trigger", "no-trigger"):
            count = sum(1 for p in probes if p["expect"] == label)
            self.assertGreaterEqual(count, 3, f"too few '{label}' probes to estimate a rate")

    def test_the_split_is_stratified(self) -> None:
        # A split that puts every negative in one half cannot detect over-triggering
        # in the other.
        probes = self.probes()
        for label in ("trigger", "no-trigger"):
            splits = {p["split"] for p in probes if p["expect"] == label}
            self.assertEqual(
                splits,
                {"train", "test"},
                f"'{label}' probes do not appear in both splits",
            )

    def test_failed_probe_runs_keep_their_reason(self) -> None:
        # Eight consecutive runs once failed with nothing recorded but an exit
        # code, and diagnosing them meant reproducing the failures by hand. A
        # recorded run that produced no result has to say why.
        for path in WORKSPACE.rglob("runs-*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for record in payload.get("records", []):
                if record.get("status") == "ok":
                    continue
                self.assertTrue(
                    record.get("reason"),
                    f"{path.name}: {record.get('probe')} run-{record.get('run')} "
                    "failed without recording a reason",
                )

    def test_probe_runs_record_which_description_they_measured(self) -> None:
        # A trigger rate is a property of a description. Without this, runs from
        # either side of a rewrite pool silently.
        for path in WORKSPACE.rglob("runs-*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            digest = payload.get("description_sha")
            self.assertTrue(digest, f"{path.name} does not say which description it measured")
            for record in payload.get("records", []):
                self.assertEqual(
                    record.get("description_sha"),
                    digest,
                    f"{path.name} mixes runs from more than one description",
                )

    def test_probe_queries_are_not_copied_from_the_capability_evals(self) -> None:
        # Reusing an eval prompt would measure the description against text the
        # expectations were already written around.
        prompts = {item["prompt"].strip().lower() for item in load_evals()["evals"]}
        for probe in self.probes():
            self.assertNotIn(
                probe["query"].strip().lower(),
                prompts,
                f"{probe['id']} reuses a capability eval prompt",
            )


class EvalGraderCase(unittest.TestCase):
    """Guard the two grader defects that produced the withdrawn result."""

    def grader_sources(self) -> list[Path]:
        # Grading logic lives in prompt text as well as code, so the markdown the
        # judge is given is scanned by the same guards. Vendored upstream files
        # are excluded: they are covered by the provenance digest instead, and
        # editing them locally is what that check exists to catch.
        candidates = list((ROOT / "scripts").glob("*eval*.py"))
        candidates.extend((ROOT / "scripts" / "eval").glob("*.py"))
        candidates.extend((ROOT / "scripts" / "eval").glob("*.md"))
        return [path for path in candidates if path.is_file()]

    def test_no_grader_hardcodes_individual_eval_names(self) -> None:
        # The withdrawn grader branched on four eval names and raised for the
        # rest, so half the suite was silently ungraded and the denominator was
        # wrong. A grader must iterate the manifest instead.
        names = [item["name"] for item in load_evals()["evals"]]
        for source in self.grader_sources():
            text = source.read_text(encoding="utf-8")
            for name in names:
                self.assertNotIn(
                    name,
                    text,
                    f"{source.name} hardcodes eval '{name}'; iterate evals.json instead",
                )

    def test_no_grader_matches_on_the_skill_private_vocabulary(self) -> None:
        # Matching on the skill's own terms makes the baseline structurally
        # unable to pass, which is what inflated the withdrawn delta.
        for source in self.grader_sources():
            text = source.read_text(encoding="utf-8").lower()
            for token in PRIVATE_VOCABULARY:
                self.assertNotIn(
                    token,
                    text,
                    f"{source.name} matches on private vocabulary '{token}'",
                )

    def test_no_grader_contains_non_ascii_matching_terms(self) -> None:
        for source in self.grader_sources():
            self.assertTrue(
                source.read_text(encoding="utf-8").isascii(),
                f"{source.name} contains non-ASCII terms; grading must be language-neutral",
            )


class JudgeBlindingCase(unittest.TestCase):
    """The judge must not be able to infer which configuration it is grading."""

    def grader(self):
        import importlib.util

        path = ROOT / "scripts" / "eval" / "grade_skill_evals.py"
        if not path.is_file():
            self.skipTest("no grader is present")
        spec = importlib.util.spec_from_file_location("_grader_under_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_evidence_naming_this_project_is_treated_as_a_leak(self) -> None:
        # The action log is derived from paths the run touched. If one of them
        # names this project, the configuration is readable from the bundle.
        grader = self.grader()
        self.assertEqual(grader.blinding_leaks("1. read: src/api/adapter.py"), [])
        self.assertIn(
            "engineering-ownership",
            grader.blinding_leaks("1. read: plugins/engineering-ownership/SKILL.md"),
        )
        self.assertIn("--plugin-dir", grader.blinding_leaks("run: claude --plugin-dir /x"))

    def test_committed_action_logs_do_not_identify_the_configuration(self) -> None:
        grader = self.grader()
        logs = list(WORKSPACE.rglob("actions.json")) if WORKSPACE.is_dir() else []
        if not logs:
            self.skipTest("no action logs are committed yet")
        for path in logs:
            leaks = grader.blinding_leaks(path.read_text(encoding="utf-8"))
            self.assertEqual(
                leaks,
                [],
                f"{path.relative_to(ROOT)} identifies the configuration: {leaks}",
            )

    def test_action_targets_never_carry_the_runner_location(self) -> None:
        # A live sweep recorded `cat ~/engineering-ownership/...` verbatim: the
        # token pass recognized bare tilde paths but not quoted or $HOME forms.
        # Every shell-quoting shape of the runner's own location must leave the
        # judge-visible target, including forms not anticipated here.
        import importlib.util
        import sys

        eval_dir = ROOT / "scripts" / "eval"
        path = eval_dir / "run_skill_evals.py"
        if not path.is_file():
            self.skipTest("no runner is present")
        sys.path.insert(0, str(eval_dir))
        try:
            spec = importlib.util.spec_from_file_location("_runner_under_test", path)
            runner = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner)
        finally:
            sys.path.remove(str(eval_dir))

        marker = ROOT.name
        home = str(Path.home())
        cwd = Path("/tmp/fixture-under-test")
        cases = [
            ("Bash", {"command": f"cat ~/{marker}/plugins/{marker}/references/start.md"}),
            ("Bash", {"command": f'cat "~/{marker}/plugins/x.md"'}),
            ("Bash", {"command": f"cat '$HOME/{marker}/plugins/x.md'"}),
            ("Bash", {"command": f"find {home}/{marker}/src 2>/dev/null"}),
            ("Bash", {"command": f"grep -r ownership ~/{marker}/plugins"}),
            ("Read", {"file_path": f"{home}/{marker}/skills/SKILL.md"}),
            ("Write", {"file_path": f"notes/{marker}-copy.md"}),
            ("Grep", {"pattern": marker}),
        ]
        for name, tool_input in cases:
            target = runner.redact(runner.action_target(name, tool_input, cwd))
            self.assertNotIn(
                marker,
                target,
                f"{name} {tool_input} leaks the runner location: {target!r}",
            )


class FixtureCoverageCase(unittest.TestCase):
    """Fixtures decide which expectations are ever exercised."""

    def recipe(self) -> dict:
        path = ROOT / "scripts" / "eval" / "fixtures" / "recipe.json"
        if not path.is_file():
            self.skipTest("no fixture recipe is present")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_every_fixture_belongs_to_a_declared_eval(self) -> None:
        # An orphaned fixture is a scenario nothing evaluates. The reverse gap -
        # an eval with no fixture - is real and currently large, but the runner
        # skips those and each iteration records which evals it actually ran, so
        # it is reported as evidence rather than hidden behind a red suite.
        declared = {f"eval-{item['id']}" for item in load_evals()["evals"]}
        for overlay in self.recipe().get("overlays", {}):
            self.assertIn(
                overlay,
                declared,
                f"fixture {overlay} does not correspond to any eval in the manifest",
            )

    def test_the_unmanaged_base_carries_none_of_this_skill_artifacts(self) -> None:
        # A scenario asking whether the skill produces this discipline cannot
        # start from a repository that already practises it. The first version of
        # this fixture shipped a decision document that matched this skill's own
        # template section for section, including an empty supersession field -
        # a fill-in-the-blank for the very expectation the scenario grades, and
        # the reason the baseline scored as well as it did.
        base = ROOT / "scripts" / "eval" / "fixtures" / "unmanaged"
        if not base.is_dir():
            self.skipTest("no unmanaged base is present")
        markers = ("Superseded by:", "Supersedes:", "Change ID:", "engineering-decision:")
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            self.assertNotIn(
                ".engineering",
                path.as_posix(),
                "the unmanaged base carries this skill's contract directory",
            )
            if path.suffix not in {".md", ".json", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for marker in markers:
                self.assertNotIn(
                    marker,
                    text,
                    f"{path.relative_to(base)} carries this skill's template field '{marker}'",
                )

    def test_every_eval_has_a_fixture(self) -> None:
        # For most of this work seven of nine scenarios had no fixture, so their
        # expectations were never exercised and the runner skipped them without
        # failing. Now that the gap is closed, hold it closed: an eval added
        # without a repository to run in measures nothing.
        declared = {f"eval-{item['id']}" for item in load_evals()["evals"]}
        have = set(self.recipe().get("overlays", {}))
        self.assertEqual(
            declared - have,
            set(),
            "these evals have no fixture and would be silently skipped",
        )

    def test_overlay_aliases_point_somewhere_real(self) -> None:
        overlays = ROOT / "scripts" / "eval" / "fixtures" / "overlays"
        for name, entry in self.recipe().get("overlays", {}).items():
            alias = entry.get("overlay")
            if alias:
                self.assertTrue(
                    (overlays / alias).is_dir(),
                    f"{name} borrows overlay '{alias}', which does not exist",
                )

    def test_settled_states_referenced_by_the_recipe_exist(self) -> None:
        fixtures = ROOT / "scripts" / "eval" / "fixtures"
        for overlay, entry in self.recipe().get("overlays", {}).items():
            settled = entry.get("settled")
            if settled:
                self.assertTrue(
                    (fixtures / "settled" / settled).is_dir(),
                    f"{overlay} references a settled state that does not exist: {settled}",
                )


class VendoredHarnessCase(unittest.TestCase):
    """Editing a vendored judge prompt is the easiest way to bias grading."""

    def test_vendored_files_match_their_recorded_digests(self) -> None:
        provenance = VENDOR / "PROVENANCE.md"
        if not provenance.is_file():
            self.skipTest("no vendored harness is present")
        recorded = dict(DIGEST_ROW.findall(provenance.read_text(encoding="utf-8")))
        self.assertTrue(recorded, "PROVENANCE.md records no file digests")
        for name, digest in recorded.items():
            path = VENDOR / name
            self.assertTrue(path.is_file(), f"vendored file {name} is missing")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                actual,
                digest,
                f"{name} no longer matches its recorded digest; "
                "re-vendor from upstream or record the change deliberately",
            )

    def test_every_vendored_file_is_accounted_for(self) -> None:
        provenance = VENDOR / "PROVENANCE.md"
        if not provenance.is_file():
            self.skipTest("no vendored harness is present")
        recorded = set(dict(DIGEST_ROW.findall(provenance.read_text(encoding="utf-8"))))
        present = {
            path.name
            for path in VENDOR.iterdir()
            if path.is_file() and path.name not in {"PROVENANCE.md", "LICENSE.apache-2.0.txt"}
        }
        self.assertEqual(
            present - recorded,
            set(),
            "a vendored file has no recorded digest",
        )


class ValidationRecordCase(unittest.TestCase):
    def test_every_validation_document_declares_a_status(self) -> None:
        for path in validation_documents():
            text = path.read_text(encoding="utf-8")
            status = STATUS_LINE.search(text)
            self.assertIsNotNone(status, f"{path.name} has no Status line")
            self.assertIn(status.group(1), ALLOWED_STATUS, f"{path.name} status is unknown")
            self.assertIsNotNone(
                CHECKED_LINE.search(text), f"{path.name} has no dated Checked line"
            )

    def test_superseded_documents_name_their_replacement(self) -> None:
        for path in validation_documents():
            text = path.read_text(encoding="utf-8")
            status = STATUS_LINE.search(text)
            if status is not None and status.group(1) == "Superseded":
                self.assertIsNotNone(
                    SUPERSEDED_LINE.search(text),
                    f"{path.name} is superseded but names no replacement",
                )

    def test_the_index_lists_every_validation_document(self) -> None:
        index = (VALIDATION / "README.md").read_text(encoding="utf-8")
        for path in validation_documents():
            self.assertIn(path.name, index, f"{path.name} is missing from the index")


class CommittedArtifactCase(unittest.TestCase):
    """AGENTS.md forbids storing home paths, and these artifacts are committed."""

    def committed_artifacts(self) -> list[Path]:
        if not WORKSPACE.is_dir():
            return []
        return [
            path
            for path in WORKSPACE.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json", ".txt"}
        ]

    def test_no_artifact_records_a_home_directory(self) -> None:
        for path in self.committed_artifacts():
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn(
                "/Users/",
                text,
                f"{path.relative_to(ROOT)} records an absolute home path",
            )
            self.assertNotIn(
                "/home/",
                text,
                f"{path.relative_to(ROOT)} records an absolute home path",
            )

    def test_every_iteration_declares_what_it_is(self) -> None:
        if not WORKSPACE.is_dir():
            self.skipTest("no evaluation workspace is committed")
        index = WORKSPACE / "README.md"
        self.assertTrue(index.is_file(), "the workspace has no index")
        listed = index.read_text(encoding="utf-8")
        for path in sorted(WORKSPACE.glob("iteration-*")):
            self.assertIn(
                path.name,
                listed,
                f"{path.name} is committed but the index does not say what it is",
            )


class PublishedResultCase(unittest.TestCase):
    """A published number must be backed by a committed artifact."""

    def test_no_efficacy_number_is_published_without_supporting_artifacts(self) -> None:
        document = VALIDATION / "skill-evaluation.md"
        text = document.read_text(encoding="utf-8")
        block = RESULTS_BLOCK.search(text)
        if block is None:
            # No machine-readable result is published. The document must then say
            # so explicitly rather than leaving a bare table for a reader to
            # mistake for a current claim.
            self.assertIsNotNone(
                RETIRED_STATUS.search(text),
                "no results are published, so the document must be marked "
                "Withdrawn or Superseded rather than left ambiguous",
            )
            return

        published = json.loads(block.group(1))
        benchmark = WORKSPACE / published["iteration"] / "benchmark.json"
        self.assertTrue(
            benchmark.is_file(),
            f"published results cite {published['iteration']} but no benchmark.json is committed",
        )
        summary = json.loads(benchmark.read_text(encoding="utf-8"))["run_summary"]
        for configuration in ("with_skill", "without_skill"):
            self.assertAlmostEqual(
                published[f"{configuration}_mean"],
                summary[configuration]["pass_rate"]["mean"],
                places=4,
                msg=f"published {configuration} mean disagrees with the committed benchmark",
            )
        self.assertEqual(
            published["denominator"],
            published["evals"] * published["assertions_per_eval"] * published["n_runs"],
            "published denominator is not the product of its own factors",
        )

    def test_efficacy_shaped_numbers_need_a_results_contract_or_retired_status(self) -> None:
        # The gate above matches only the machine-readable JSON block; the
        # withdrawn claim's original form was a markdown table, which would
        # have slipped past it if republished.
        surfaces = [ROOT / "README.md", ROOT / "README.ko.md"]
        surfaces.extend(sorted(VALIDATION.glob("*.md")))
        for path in surfaces:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if not (SKILL_COMPARISON.search(text) and EFFICACY_SHAPE.search(text)):
                continue
            self.assertTrue(
                RESULTS_BLOCK.search(text) or RETIRED_STATUS.search(text),
                f"{path.relative_to(ROOT)} pairs a with/without-skill comparison "
                "with score-shaped numbers but carries neither a machine-readable "
                "results block nor a Withdrawn/Superseded status",
            )

    def test_committed_benchmarks_report_tokens_from_timing_records(self) -> None:
        # The vendored aggregator falls back to output_chars where tokens
        # belong, and its fallback always fires for this runner. A committed
        # benchmark that skipped the fix_benchmark.py post-pass would publish
        # a character count labelled as tokens — off by three orders of
        # magnitude in the one pilot that hit it.
        benchmarks = list(WORKSPACE.glob("iteration-*/benchmark.json")) if WORKSPACE.is_dir() else []
        if not benchmarks:
            self.skipTest("no benchmarks are committed yet")
        checked = 0
        for path in benchmarks:
            benchmark = json.loads(path.read_text(encoding="utf-8"))
            for entry in benchmark.get("runs", []):
                keys = {"eval_id", "configuration", "run_number", "result"}
                if not keys.issubset(entry):
                    continue
                timing_file = (
                    path.parent
                    / f"eval-{entry['eval_id']}"
                    / entry["configuration"]
                    / f"run-{entry['run_number']}"
                    / "timing.json"
                )
                if not timing_file.is_file():
                    continue
                timing = json.loads(timing_file.read_text(encoding="utf-8"))
                self.assertEqual(
                    entry["result"].get("tokens"),
                    timing.get("total_tokens"),
                    f"{path.relative_to(ROOT)} eval-{entry['eval_id']} "
                    f"{entry['configuration']} run-{entry['run_number']}: the "
                    "benchmark's token figure disagrees with timing.json — run "
                    "scripts/eval/fix_benchmark.py before committing",
                )
                checked += 1
        if not checked:
            self.skipTest("no benchmark entry has a matching timing record")
