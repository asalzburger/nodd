import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import launchd
import poll


CONFIG = {"repository": "example/test", "label": "agent_task", "reviewers": ["reviewer"],
          "hostname": "test-mac", "base_branch": "main", "timeout_seconds": 10}


def event(event_id=10, kind="labeled", actor="reviewer", label="agent_task"):
    return {"id": event_id, "event": kind, "actor": {"login": actor}, "label": {"name": label}}


def issue(number=1, pr=False):
    data = {"number": number, "state": "open", "title": "Test task",
            "body": "Fix the example", "labels": [{"name": "agent_task"}]}
    if pr:
        data["pull_request"] = {}
    return data


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.state = self.root / "state"
        self.repo.mkdir()
        self.host = patch("poll.socket.gethostname", return_value="test-mac.example.org")
        self.host.start()
        self.addCleanup(self.host.stop)
        self.addCleanup(self.temporary.cleanup)

    def fake_api(self, endpoint, paginate=False):
        if "/events?" in endpoint:
            return [event()]
        if "/issues?" in endpoint:
            return [issue()]
        if "/comments?" in endpoint:
            return []
        if endpoint.endswith("/issues/1"):
            return issue()
        self.fail(f"Unexpected API call: {endpoint}")

    def test_latest_label_application_survives_remove_readd_between_polls(self):
        events = [event(12), event(10), event(11, "unlabeled"), event(13, label="other")]
        self.assertEqual(poll.latest_request(events, "agent_task")["id"], 12)
        self.assertIsNone(poll.latest_request([event(), event(11, "unlabeled")], "agent_task"))

    def test_allowlist_and_attempt_history_filter_candidates(self):
        for actor, attempts, expected in [("reviewer", {}, 1), ("REVIEWER", {}, 1),
                                          ("outsider", {}, 0), ("reviewer", {"1-10": {}}, 0)]:
            def response(endpoint, paginate=False):
                return [issue()] if "/issues?" in endpoint else [event(actor=actor)]
            with self.subTest(actor=actor, attempts=attempts), patch("poll.api", side_effect=response):
                self.assertEqual(len(list(poll.candidates(CONFIG, attempts))), expected)

    def test_api_flattens_all_pages(self):
        with patch("poll.command", return_value='[[{"number": 1}], [{"number": 101}]]') as run:
            self.assertEqual(poll.api("repos/example/test/issues", True), [{"number": 1}, {"number": 101}])
            self.assertIn("--paginate", run.call_args.args[0])
            self.assertIn("--slurp", run.call_args.args[0])

    def test_recheck_skips_closed_unlabeled_or_requeued_tasks(self):
        for current, events in [(dict(issue(), state="closed"), [event()]),
                                (dict(issue(), labels=[]), [event()]),
                                (issue(), [event(11)]), (issue(), [event(11, "unlabeled")])]:
            with self.subTest(current=current, events=events), patch("poll.api", side_effect=[current, events]):
                self.assertIsNone(poll.snapshot(CONFIG, issue(), event()))

    def test_pr_context_and_fork_filter(self):
        for repo_name in ["example/test", "fork/test"]:
            pr = {"state": "open", "head": {"sha": "a" * 40, "repo": {"full_name": repo_name}}}
            responses = [issue(pr=True), [event()], [], pr]
            if repo_name == "example/test":
                responses += [[{"body": "Review"}], [{"body": "Inline"}]]
            with self.subTest(repo=repo_name), patch("poll.api", side_effect=responses):
                data = poll.snapshot(CONFIG, issue(pr=True), event())
                if repo_name == "example/test":
                    self.assertEqual(data["review_comments"][0]["body"], "Inline")
                else:
                    self.assertIsNone(data)

    def test_claim_persists_before_execution_and_suppresses_second_pickup(self):
        def execute(*args):
            saved = json.loads((self.state / "state.json").read_text())
            self.assertEqual(saved["attempts"]["1-10"]["status"], "started")
            return {"status": "completed", "exit_code": 0,
                    "draft_pr_url": "https://github.com/example/test/pull/7"}
        with patch("poll.verify_origin"), patch("poll.api", side_effect=self.fake_api), \
                patch("poll.execute", side_effect=execute) as run:
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 0)
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 0)
            self.assertEqual(run.call_count, 1)

    def test_failed_execution_is_not_retried(self):
        with patch("poll.verify_origin"), patch("poll.api", side_effect=self.fake_api), \
                patch("poll.execute", side_effect=RuntimeError("test failure")) as run:
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 1)
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 0)
            self.assertEqual(run.call_count, 1)
        self.assertEqual(json.loads((self.state / "state.json").read_text())["attempts"]["1-10"]["status"], "failed")

    def test_successful_agent_without_a_draft_is_not_complete(self):
        with patch("poll.verify_origin"), patch("poll.api", side_effect=self.fake_api), \
                patch("poll.execute", return_value={"status": "completed", "exit_code": 0}):
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 1)
        result = json.loads((self.state / "state.json").read_text())["attempts"]["1-10"]
        self.assertEqual(result["status"], "failed")
        self.assertIn("draft PR", result["error"])

    def test_publication_error_retains_existing_draft_link(self):
        def fail(*args):
            run_dir = self.state / "runs/1-10"
            run_dir.mkdir(parents=True)
            poll.save(run_dir / "publication.json", {"draft_pr_url": "https://github.com/example/test/pull/7"})
            raise RuntimeError("ledger push failed")
        with patch("poll.verify_origin"), patch("poll.api", side_effect=self.fake_api), \
                patch("poll.execute", side_effect=fail):
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex"), 1)
        result = json.loads((self.state / "state.json").read_text())["attempts"]["1-10"]
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["draft_pr_url"], "https://github.com/example/test/pull/7")

    def test_dry_run_does_not_claim_or_execute(self):
        with patch("poll.verify_origin"), patch("poll.api", side_effect=self.fake_api), \
                patch("poll.execute") as run:
            self.assertEqual(poll.poll(CONFIG, self.repo, self.state, "codex", True), 0)
            run.assert_not_called()
        self.assertFalse((self.state / "state.json").exists())

    def test_api_failure_does_not_consume_request(self):
        with patch("poll.verify_origin"), patch("poll.api", side_effect=RuntimeError("offline")), \
                self.assertRaisesRegex(RuntimeError, "offline"):
            poll.poll(CONFIG, self.repo, self.state, "codex")
        self.assertFalse((self.state / "state.json").exists())

    def test_wrong_host_and_origin_fail_before_api(self):
        with patch("poll.api") as api, patch("poll.socket.gethostname", return_value="other-mac"), \
                self.assertRaisesRegex(ValueError, "restricted"):
            poll.poll(CONFIG, self.repo, self.state, "codex")
        api.assert_not_called()
        with patch("poll.command", return_value="git@github.com:other/test.git"), \
                self.assertRaisesRegex(ValueError, "origin"):
            poll.verify_origin(self.repo, CONFIG)

    def test_local_lock_blocks_overlapping_runs(self):
        with poll.locked_state(self.state):
            with self.assertRaisesRegex(ValueError, "already running"), poll.locked_state(self.state):
                self.fail("second lock acquired")
        with poll.locked_state(self.state):
            pass

    def test_config_and_state_identity_fail_closed(self):
        for changed in [{"reviewers": []}, {"reviewers": "reviewer"}, {"repository": "../bad"},
                        {"timeout_seconds": -1}]:
            config_file = self.root / "config.json"
            config_file.write_text(json.dumps(dict(CONFIG, **changed)))
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                poll.load_config(config_file)
        self.state.mkdir()
        poll.save(self.state / "state.json", {"repository": "other/repo", "attempts": {}})
        with patch("poll.verify_origin"), self.assertRaisesRegex(ValueError, "another repository"):
            poll.poll(CONFIG, self.repo, self.state, "codex")
        with patch("poll.verify_origin"), self.assertRaisesRegex(ValueError, "outside"):
            poll.poll(CONFIG, self.repo, self.repo / "state", "codex")

    def test_real_git_worktree_and_fake_codex_execution(self):
        poll.command(["git", "init", "-b", "main", str(self.repo)])
        (self.repo / "example.txt").write_text("before\n")
        poll.command(["git", "add", "."], self.repo)
        poll.command(["git", "-c", "user.name=Test", "-c", "user.email=test@example.org",
                      "commit", "-m", "fixture"], self.repo)
        origin = self.root / "origin.git"
        poll.command(["git", "clone", "--bare", str(self.repo), str(origin)])
        poll.command(["git", "remote", "add", "origin", str(origin)], self.repo)
        codex = self.root / "fake-codex"
        codex.write_text('#!/bin/sh\ncat >/dev/null\nprintf "fake Codex result\\n"\n')
        codex.chmod(0o755)
        self.state.mkdir()
        data = {"issue": issue(), "request": event(), "comments": []}
        with patch("poll.publish_draft", return_value={"draft_pr_url": "https://github.com/example/test/pull/7"}) as publish:
            result = poll.execute(CONFIG, self.repo, self.state, "1-10", data, str(codex))
            self.assertEqual(publish.call_args.args[4]["input_revision"], result["revision"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual((self.state / "runs/1-10/result.json").read_text(), "fake Codex result\n")
        self.assertEqual((Path(result["worktree"]) / "example.txt").read_text(), "before\n")
        self.assertEqual(poll.command(["git", "status", "--porcelain"], self.repo), "")
        # A stale captured PR head must never execute the agent.
        poll.command(["git", "--git-dir", str(origin), "update-ref", "refs/pull/1/head", result["revision"]])
        data["pull_request"] = {"head": {"sha": "b" * 40}}
        with self.assertRaisesRegex(ValueError, "head changed"):
            poll.execute(CONFIG, self.repo, self.state, "1-11", data, str(codex))

    def test_timeout_terminates_task_group(self):
        process = unittest.mock.Mock(pid=123, returncode=-15)
        process.communicate.side_effect = subprocess.TimeoutExpired("codex", 1)
        with patch("poll.command", side_effect=["", "a" * 40, ""]), \
                patch("poll.subprocess.Popen", return_value=process), patch("poll.os.killpg") as kill:
            with self.assertRaises(subprocess.TimeoutExpired):
                poll.execute(CONFIG, self.repo, self.state, "1-10", {"issue": issue()}, "codex")
            kill.assert_called_once_with(123, poll.signal.SIGTERM)
            process.wait.assert_called_once_with(timeout=10)

    def test_plist_roundtrip_keeps_paths_as_arguments(self):
        data = launchd.make_plist(self.repo / "with spaces", self.state, self.root / "config.json",
                                 "/test/python3", "/test/codex", "/test/bin:/usr/bin")
        data = plistlib.loads(plistlib.dumps(data))
        self.assertEqual(data["StartCalendarInterval"], {"Minute": 7})
        self.assertTrue(data["RunAtLoad"])
        self.assertFalse(data.get("KeepAlive", False))
        self.assertEqual(data["ProgramArguments"][2], str(self.repo / "with spaces/tools/agent_tasks/poll.py"))
        self.assertEqual(data["EnvironmentVariables"]["GIT_TERMINAL_PROMPT"], "0")


if __name__ == "__main__":
    unittest.main()
