"""Synthetic counter fixtures test accounting, not actual client usage."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import build


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        source = self.root / "tools/session_logging"
        source.mkdir(parents=True)
        for name in ("session_log.py", "session.schema.json"):
            shutil.copy(build.ROOT / "tools/session_logging" / name, source / name)
        (self.root / "project").mkdir()
        (self.root / "logs/usage").mkdir(parents=True)
        shutil.copy(build.ROOT / "logs/TEMPLATE.md", self.root / "logs/TEMPLATE.md")
        (self.root / "project/token-milestones.json").write_text(
            '{"schema_version":1,"features":[]}'
        )
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "-c",
                "user.name=Synthetic fixture",
                "-c",
                "user.email=fixture@example.invalid",
                "commit",
                "--allow-empty",
                "-qm",
                "Synthetic baseline",
            ],
            check=True,
        )
        self.logger = build.journal_module(self.root)
        self.add_record(
            "SESSION-2026-09-16-one", "turn-one", 100, 20, 80, 5, "2026-09-16T12:00:00Z"
        )

    def add_record(self, sid, turn, input_tokens, output_tokens, cached, reasoning, at):
        self.logger.new_record(
            self.root, sid, "Synthetic counter fixture", "codex", "M0"
        )
        path = self.root / "logs/codex" / f"{sid}.json"
        record = json.loads(path.read_text())
        entry = {
            "client_thread_id": "synthetic-thread",
            "turn_id": turn,
            "model": None,
            "source": "Synthetic counters, not measured usage",
            "limitations": ["Synthetic model intentionally unknown."],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_input_tokens": cached,
            "reasoning_output_tokens": reasoning,
            "total_tokens": (
                input_tokens + output_tokens
                if input_tokens is not None and output_tokens is not None
                else None
            ),
        }
        record["usage"] = [entry]
        path.write_text(json.dumps(record))
        if at:
            evidence = {
                "completed_turns": [
                    {
                        "thread_id": entry["client_thread_id"],
                        "turn_id": turn,
                        "status": "completed",
                        "closed": True,
                        "completed_at": at,
                        "tokens": {k: entry[k] for k in build.FIELDS},
                        "usage_entry": entry,
                    }
                ]
            }
            (self.root / "logs/usage" / f"{turn}.json").write_text(json.dumps(evidence))
        return path

    def test_cumulative_totals_subsets_and_replayed_evidence(self):
        self.add_record(
            "SESSION-2026-09-17-two",
            "turn-two",
            200,
            40,
            180,
            10,
            "2026-09-17T12:00:00Z",
        )
        shutil.copy(
            self.root / "logs/usage/turn-one.json",
            self.root / "logs/usage/replayed.json",
        )
        data = build.collect(self.root)
        self.assertEqual(data["summary"]["usage_turns"], 2)
        self.assertEqual(
            [r["cumulative"]["total_tokens"] for r in data["series"]], [120, 360]
        )
        self.assertEqual(data["summary"]["tokens"]["cached_input_tokens"]["sum"], 260)
        self.assertEqual(data["summary"]["tokens"]["total_tokens"]["sum"], 360)

    def test_counter_or_timestamp_conflict_fails(self):
        original = json.loads((self.root / "logs/usage/turn-one.json").read_text())
        for change in ("counter", "time"):
            value = copy.deepcopy(original)
            if change == "counter":
                value["completed_turns"][0]["tokens"]["input_tokens"] = 101
            else:
                value["completed_turns"][0]["completed_at"] = "2026-09-17T12:00:00Z"
            (self.root / "logs/usage/conflict.json").write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "conflicting"):
                build.collect(self.root)

    def test_duplicate_canonical_ownership_is_rejected(self):
        path = self.add_record(
            "SESSION-2026-09-17-two", "different-turn", 200, 40, 180, 10, None
        )
        record = json.loads(path.read_text())
        record["usage"][0] = json.loads(
            (self.root / "logs/codex/SESSION-2026-09-16-one.json").read_text()
        )["usage"][0]
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "duplicate usage turn"):
            build.collect(self.root)

    def test_unknown_counters_and_dates_are_not_zero_or_inferred(self):
        (self.root / "logs/usage/turn-one.json").unlink()
        path = self.root / "logs/codex/SESSION-2026-09-16-one.json"
        record = json.loads(path.read_text())
        for field in ("output_tokens", "reasoning_output_tokens", "total_tokens"):
            record["usage"][0][field] = None
        record["usage"][0]["limitations"].append(
            "Synthetic output counters unavailable."
        )
        path.write_text(json.dumps(record))
        data = build.collect(self.root)
        self.assertIsNone(data["summary"]["tokens"]["total_tokens"]["sum"])
        self.assertEqual(data["dated_turns"], 0)
        self.assertEqual(data["undated_turns"], 1)
        self.assertEqual(data["series"], [])
        result = build.build(
            self.root, self.root / "_site/empty", "2026-10-12T10:00:00Z"
        )
        html = (self.root / "_site/empty/index.html").read_text()
        self.assertIn("Unknown", html)
        self.assertIn("No dated observations", html)
        self.assertEqual(result["undated_tokens"]["input_tokens"]["sum"], 100)

    def test_interrupted_closed_turn_counts_but_active_boundary_fails(self):
        path = self.root / "logs/usage/turn-one.json"
        value = json.loads(path.read_text())
        value["completed_turns"][0]["status"] = "interrupted"
        path.write_text(json.dumps(value))
        self.assertEqual(build.collect(self.root)["dated_turns"], 1)
        value["completed_turns"][0]["closed"] = False
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "unclosed"):
            build.collect(self.root)

    def test_escaping_and_feature_evidence(self):
        revision = subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True
        ).strip()
        feature = {
            "id": "PR-999",
            "label": "<script>alert(1)</script>",
            "at": "2026-09-16T15:00:00Z",
            "revision": revision,
            "url": build.REPOSITORY + "/pull/999",
        }
        manifest = self.root / "project/token-milestones.json"
        manifest.write_text(json.dumps({"schema_version": 1, "features": [feature]}))
        build.build(self.root, self.root / "_site/test", "2026-10-12T10:00:00Z")
        page = (self.root / "_site/test/index.html").read_text()
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("2026-09-16", page)
        self.assertIn("aria-label", page)
        feature["url"] = "javascript:alert(1)"
        manifest.write_text(json.dumps({"schema_version": 1, "features": [feature]}))
        with self.assertRaisesRegex(ValueError, "URL"):
            build.collect(self.root)

    def test_determinism_allowlist_and_source_preservation(self):
        first = self.root / "_site/first"
        second = self.root / "_site/second"
        build.build(self.root, first, "2026-10-12T10:00:00Z")
        build.build(self.root, second, "2026-10-12T10:00:00Z")
        self.assertEqual(
            {p.name for p in first.iterdir()},
            {"index.html", "style.css", "app.js", "usage.json", ".nojekyll"},
        )
        for path in first.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
        with self.assertRaisesRegex(ValueError, "under _site"):
            build.build(self.root, self.root / "project", "2026-10-12T10:00:00Z")
        (first / "stale.txt").write_text("Synthetic stale artifact")
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            build.build(self.root, first, "2026-10-12T10:00:00Z")

    def test_real_journal_timeline_reconciles_all_fields(self):
        data = build.collect(build.ROOT)
        for field in build.FIELDS:
            plotted = data["series"][-1]["cumulative"][field] or 0
            undated = data["undated_tokens"][field]["sum"] or 0
            self.assertEqual(plotted + undated, data["summary"]["tokens"][field]["sum"])
        self.assertEqual(
            data["dated_turns"] + data["undated_turns"], data["summary"]["usage_turns"]
        )


if __name__ == "__main__":
    unittest.main()
