"""Workflow contracts tested against real, isolated Git history."""

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

import workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name).resolve() / "repository with spaces"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Workflow Test")
        self.git("config", "user.email", "workflow-test@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.profiles = self.repo / ".codex/agents"
        self.profiles.mkdir(parents=True)
        for role in workflow.ROLES:
            self.write_profile(role)
        for skill in workflow.SKILLS:
            path = self.repo / f".agents/skills/{skill}/SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                f"---\nname: {json.dumps(skill)}\ndescription: \"Test procedure.\"\n---\n"
                "Read the assigned source and report the result.\n", encoding="utf-8",
            )
        self.source = self.repo / "docs/input.md"
        self.source.parent.mkdir()
        self.original = b"Historical evidence: requirement alpha.\n"
        self.source.write_bytes(self.original)
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture revision")
        self.revision = self.git("rev-parse", "HEAD").decode().strip()
        self.assignment = {
            "id": "TEST-01", "role": "TrackTech", "input_revision": self.revision,
            "inputs": ["docs/input.md"], "mode": "read-only", "writable_paths": [],
            "task": "Assess the requirement in the assigned source.",
            "deliverable": "A short finding with an exact source locator.",
            "completion": "Return the finding and outstanding questions.",
        }

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout

    def write_profile(self, role, **updates):
        fields = {
            "name": role, "description": f"Test responsibility for {role}.",
            "developer_instructions": f"Act as {role}.\nRetain uncertainty; never invent approval.",
        }
        fields.update(updates)
        (self.profiles / f"{role}.toml").write_text(
            "\n".join(f"{key} = {json.dumps(value)}" for key, value in fields.items()) + "\n",
            encoding="utf-8",
        )

    def prepare(self, **updates):
        return workflow.prepare(self.repo, dict(self.assignment, **updates))

    def test_validate_requires_all_exact_roles_and_skills(self):
        self.assertEqual(set(workflow.validate(self.repo)), set(workflow.ROLES))
        profile = self.profiles / "PubDoc.toml"
        profile.rename(self.profiles / "Other.toml")
        with self.assertRaisesRegex(ValueError, "eight nODD"):
            workflow.validate(self.repo)

    def test_profile_mandate_is_required_and_names_are_unique(self):
        self.write_profile("TrackTech", developer_instructions="  ")
        with self.assertRaisesRegex(ValueError, "developer_instructions"):
            workflow.validate(self.repo)
        self.write_profile("TrackTech", name="SysArch")
        with self.assertRaisesRegex(ValueError, "name must match"):
            workflow.validate(self.repo)

    def test_skill_frontmatter_convention_and_nonempty_body(self):
        file = self.repo / ".agents/skills/nodd-coordinate/SKILL.md"
        valid = file.read_text()
        for invalid in (
            valid.replace('name: "nodd-coordinate"', "name: nodd-coordinate"),
            valid.replace("---\nRead", 'extra: "unsupported"\n---\nRead'),
            valid.replace('name: "nodd-coordinate"', 'name: "other"'),
            valid[:valid.index("Read the assigned")],
        ):
            with self.subTest(invalid=invalid):
                file.write_text(invalid)
                with self.assertRaises(ValueError):
                    workflow.validate(self.repo)

    def test_complete_current_mandate_and_assignment_propagate(self):
        mandate = "Current role instruction.\nKeep this precise boundary.\nDo not infer a human review."
        self.write_profile("TrackTech", developer_instructions=mandate)
        prompt = self.prepare()
        self.assertIn(mandate, prompt)
        self.assertIn(json.dumps(self.assignment, indent=2), prompt)
        self.assertIn("working-tree workflow instructions", prompt)
        self.assertIn("does not claim the client has loaded", prompt)
        self.assertIn("do not edit files", prompt)

    def test_historical_source_is_verified_despite_dirty_worktree(self):
        self.source.write_text("Dirty bytes that must not become target evidence.\n")
        source = workflow.pinned_input(self.repo, self.revision, "docs/input.md")
        self.assertEqual(source["sha256"], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(source["blob_oid"], self.git("rev-parse", f"{self.revision}:docs/input.md").decode().strip())
        self.assertEqual(source["locator"], f"{self.revision}:docs/input.md")
        read = subprocess.run(shlex.split(source["show_command"]), check=True, stdout=subprocess.PIPE)
        self.assertEqual(read.stdout, self.original)
        prompt = self.prepare()
        self.assertIn(source["sha256"], prompt)
        self.assertNotIn(self.source.read_text(), prompt)
        self.assertNotIn(self.original.decode(), prompt)

    def test_missing_or_noncommit_revisions_are_rejected(self):
        blob = self.git("rev-parse", f"{self.revision}:docs/input.md").decode().strip()
        for revision in ("HEAD", self.revision[:12], "g" * 40, "0" * 40, blob):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                self.prepare(input_revision=revision)

    def test_source_must_exist_at_assigned_revision(self):
        later = self.repo / "docs/later.md"
        later.write_text("New evidence.\n")
        self.git("add", "docs/later.md")
        self.git("commit", "-qm", "Later source")
        with self.assertRaisesRegex(ValueError, "absent at input_revision"):
            self.prepare(inputs=["docs/later.md"])
        with self.assertRaisesRegex(ValueError, "regular Git file"):
            self.prepare(inputs=["docs"])
        self.assertIn("docs/later.md", self.prepare(
            input_revision=self.git("rev-parse", "HEAD").decode().strip(), inputs=["docs/later.md"],
        ))

    def test_unknown_role_and_malformed_assignment_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown nODD role"):
            self.prepare(role="UnboundedExpert")
        with self.assertRaisesRegex(ValueError, "requires exactly"):
            self.prepare(extra="unexpected")
        missing = dict(self.assignment)
        del missing["completion"]
        with self.assertRaisesRegex(ValueError, "requires exactly"):
            workflow.prepare(self.repo, missing)
        for key in ("id", "task", "deliverable", "completion"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "nonempty string"):
                self.prepare(**{key: " "})
        for inputs in ([], "docs/input.md", [42]):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                self.prepare(inputs=inputs)

    def test_read_only_and_write_ownership_boundaries(self):
        with self.assertRaisesRegex(ValueError, "empty writable_paths"):
            self.prepare(writable_paths=["docs/result.md"])
        with self.assertRaisesRegex(ValueError, "nonempty file ownership"):
            self.prepare(mode="write")
        with self.assertRaisesRegex(ValueError, "individual files"):
            self.prepare(mode="write", writable_paths=["docs"])
        with self.assertRaisesRegex(ValueError, "mode must be"):
            self.prepare(mode="unrestricted")
        with self.assertRaisesRegex(ValueError, "must be a list"):
            self.prepare(writable_paths="docs/result.md")
        prompt = self.prepare(mode="write", writable_paths=["docs/result.md"])
        self.assertIn('"writable_paths": [\n    "docs/result.md"', prompt)
        self.assertFalse((self.repo / "docs/result.md").exists())

    def test_absolute_traversal_and_noncanonical_paths_are_rejected(self):
        for path in ("../outside.md", "/tmp/outside.md", "docs/../input.md", "./docs/input.md",
                     "docs//input.md", "docs/", "C:/outside.md", "docs\\input.md", "\x00"):
            for key in ("inputs", "writable_paths"):
                with self.subTest(path=path, key=key), self.assertRaisesRegex(ValueError, "repository-relative"):
                    updates = {"mode": "write", "writable_paths": ["docs/result.md"]}
                    updates[key] = [path]
                    self.prepare(**updates)

    def test_symlink_escapes_are_rejected_for_sources_and_new_outputs(self):
        outside = self.repo.parent / "outside"
        outside.mkdir()
        (outside / "input.md").write_text("Outside content.")
        self.source.unlink()
        self.source.symlink_to(outside / "input.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.prepare()
        self.source.unlink()
        self.source.write_bytes(self.original)
        (self.repo / "escape").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.prepare(mode="write", writable_paths=["escape/new.md"])

    def test_historical_symlink_is_not_regular_input_evidence(self):
        linked = self.repo / "docs/link.md"
        linked.symlink_to("input.md")
        self.git("add", "docs/link.md")
        self.git("commit", "-qm", "Historical symlink")
        with self.assertRaisesRegex(ValueError, "regular Git file"):
            self.prepare(input_revision=self.git("rev-parse", "HEAD").decode().strip(), inputs=["docs/link.md"])

    def test_duplicate_file_ownership_and_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate paths"):
            self.prepare(inputs=["docs/input.md", "docs/input.md"])
        with self.assertRaisesRegex(ValueError, "duplicate paths"):
            self.prepare(mode="write", writable_paths=["docs/result.md", "docs/result.md"])

    def test_cli_reports_validation_and_concise_failure_without_traceback(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = workflow.main(["validate", "--repo", str(self.repo)])
        self.assertEqual(status, 0)
        self.assertIn("Validated eight", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        assignment_file = self.repo.parent / "assignment.json"
        assignment_file.write_text(json.dumps(dict(self.assignment, input_revision="HEAD")))
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = workflow.main(["prepare", "--repo", str(self.repo), "--assignment", str(assignment_file)])
        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(stderr.getvalue().startswith("error: "))
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
