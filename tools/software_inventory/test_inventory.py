"""Synthetic repositories exercise inventory maintenance failures without runtimes."""
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.write(".gitignore", "build/\nsoftware/build/\n")
        self.write("tools/test_fixture/run.py", "# Arbitrary test fixture; no detector parameters.\n")
        self.write("tools/test_fixture/README.md", "# Synthetic test software\n")
        self.write("CMakeLists.txt", "# Synthetic fixture build recipe\n")
        self.data = {
            "schema_version": 1, "updated": "2026-11-06",
            "source_revision": "1" * 40,
            "components": [{
                "id": "TEST-FIXTURE", "name": "Synthetic fixture", "category": "cross-validation",
                "usage": "test only", "integration": "source added to test repository",
                "version": "test value", "installation": "none",
                "paths": ["tools/test_fixture"], "evidence": ["tools/test_fixture/README.md"], "prs": [],
            }],
            "checked_inputs": {}, "source_pins": {},
        }
        self.write("docs/.keep", "")
        self.save()
        self.assertEqual(self.run_command("refresh")[0], 0)
        self.data = json.loads((self.root / inventory.DATA).read_text())

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    def save(self):
        self.write(inventory.DATA, json.dumps(self.data))

    def run_command(self, command):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = inventory.main([command, "--root", str(self.root)])
        return code, output.getvalue()

    def fails(self, command, message):
        code, output = self.run_command(command)
        self.assertEqual(code, 1, output)
        self.assertIn(message, output)

    def test_checkout_without_initialized_submodules_and_ignored_builds(self):
        self.write("build/generated.py", "# Ignored generated test file\n")
        self.write("software/build/venv/installed.py", "# Ignored installed test package\n")
        self.assertEqual(self.run_command("check")[0], 0)

    def test_new_code_family_cannot_be_acknowledged_without_an_entry(self):
        self.write("software/source/ActsExamples/NewTestFixture/Binding.cpp", "// Test only\n")
        before = (self.root / inventory.DATA).read_bytes()
        self.fails("check", "uninventoried code families")
        self.fails("refresh", "uninventoried code families")
        self.assertEqual((self.root / inventory.DATA).read_bytes(), before)

    def test_changed_dependency_in_existing_family_requires_review(self):
        self.write("tools/test_fixture/requirements.txt", "test-package==1.0\n")
        self.fails("check", "review changed dependency/build inputs")
        self.assertEqual(self.run_command("refresh")[0], 0)
        self.write("tools/test_fixture/requirements.txt", "test-package==2.0\n")
        self.fails("check", "tools/test_fixture/requirements.txt")

    def test_removed_manifest_requires_review(self):
        (self.root / "CMakeLists.txt").unlink()
        self.fails("check", "CMakeLists.txt")

    def test_changed_build_recipe_and_ci_recipe_require_review(self):
        self.write("CMakeLists.txt", "# Changed test fixture recipe\n")
        self.fails("check", "CMakeLists.txt")
        self.assertEqual(self.run_command("refresh")[0], 0)
        self.write(".github/workflows/test-fixture.yml", "# Test CI recipe\n")
        self.fails("check", ".github/workflows/test-fixture.yml")

    def test_pin_addition_and_update_without_fetching_source(self):
        path = "software/submodules/test_fixture"
        self.git("update-index", "--add", "--cacheinfo", "160000," + "2" * 40 + "," + path)
        self.fails("check", "uninventoried software submodules")
        entry = copy.deepcopy(self.data["components"][0])
        entry.update(id="TEST-EXTERNAL", paths=[], gitlink=path)
        self.data["components"].append(entry)
        self.save()
        self.assertEqual(self.run_command("refresh")[0], 0)
        self.assertEqual(self.run_command("check")[0], 0)
        self.assertIn("2" * 40, (self.root / inventory.PAGE).read_text())
        self.git("update-index", "--cacheinfo", "160000," + "3" * 40 + "," + path)
        self.fails("check", "source pins changed")

    def test_stale_page_and_description_require_regeneration(self):
        self.write(inventory.PAGE, "# Stale test page\n")
        self.fails("check", "generated inventory page is stale")
        self.data["components"][0]["usage"] = "test pipe | and newline\ncontent"
        self.save()
        self.assertEqual(self.run_command("refresh")[0], 0)
        self.assertIn("test pipe \\| and newline content", (self.root / inventory.PAGE).read_text())

    def test_missing_or_escaping_evidence_is_rejected(self):
        for path in ("missing.md", "../outside.md", "/tmp/outside.md"):
            with self.subTest(path=path):
                self.data["components"][0]["evidence"] = [path]
                self.save()
                self.fails("refresh", "unsafe or missing path")

    def test_duplicate_ownership_and_invalid_pr_are_rejected(self):
        entry = copy.deepcopy(self.data["components"][0])
        entry["id"] = "TEST-DUPLICATE"
        self.data["components"].append(entry)
        self.save()
        self.fails("check", "duplicate family ownership")
        self.data["components"].pop()
        self.data["components"][0]["prs"] = ["https://example.invalid/pull/123"]
        self.save()
        self.fails("check", "invalid PR URL")

    def test_removed_family_is_not_silently_retained(self):
        (self.root / "tools/test_fixture/run.py").unlink()
        self.fails("check", "obsolete/unknown code family")


if __name__ == "__main__":
    unittest.main()
