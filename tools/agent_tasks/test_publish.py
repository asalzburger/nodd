import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import publish


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "task"
        self.run_dir = self.root / "run"
        self.run_dir.mkdir()
        self.control = self.root / "control"
        self.origin = self.root / "origin.git"
        self.git("init", "-b", "main", str(self.repo), cwd=self.root)
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.org")
        (self.repo / "file.txt").write_text("before\n")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.revision = self.git("rev-parse", "HEAD")
        self.git("clone", "--bare", str(self.repo), str(self.origin), cwd=self.root)
        self.git("remote", "add", "origin", "https://github.com/example/test.git")
        # URL validation uses the real configured origin; pushes are rewritten locally for this fixture.
        self.git("config", f"url.{self.origin}.insteadOf", "https://github.com/example/test.git")
        self.git("checkout", "-b", "codex/agent-task-1-10")
        (self.repo / "file.txt").write_text("after\n")
        (self.run_dir / "result.json").write_text(json.dumps({"title": "Infrastructure: test task", "body": "Changed the fixture. Tests passed."}))
        self.data = {"issue": {"number": 1}, "input_revision": self.revision}
        for tool in ["session_logging/session_log.py", "interactions/ledger.py"]:
            path = self.control / "tools" / tool
            path.parent.mkdir(parents=True)
            path.write_text('''import pathlib, sys
if 'capture' in sys.argv:
    root=pathlib.Path(sys.argv[sys.argv.index('--repo')+1])
    number=int(sys.argv[sys.argv.index('--pr')+1])
    p=root/'interactions'/f'pr-{number:04d}.json'
    p.parent.mkdir(exist_ok=True)
    p.write_text('{"fixture":true}\\n')
''')
        self.bin = self.root / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(f"#!{sys.executable}\n" + '''import json, os, pathlib, subprocess, sys
a=sys.argv[1:]
store=pathlib.Path(os.environ['FAKE_GH_STORE'])
s=json.loads(store.read_text()) if store.exists() else {}
if a[:2]==['pr','list']:
    print(json.dumps([{'number':7}] if s else []))
elif a[:2]==['pr','create']:
    assert '--draft' in a
    s={'base':a[a.index('--base')+1], 'head':a[a.index('--head')+1], 'creates':s.get('creates',0)+1}
    store.write_text(json.dumps(s))
    if os.environ.get('FAKE_GH_LOST_RESPONSE')=='1': sys.exit(1)
    print('https://github.com/example/test/pull/7')
elif a[0]=='api':
    if a[-1].endswith('/pulls/1'):
        print(json.dumps({'state':'open','head':{'ref':'source-branch','sha':os.environ.get('FAKE_GH_SOURCE_SHA','changed')}}))
    else:
        sha=subprocess.check_output(['git','--git-dir',os.environ['FAKE_GH_ORIGIN'],'rev-parse','refs/heads/'+s['head']],text=True).strip()
        reported=sha
        if os.environ.get('FAKE_GH_ALWAYS_OLD'):
            reported=os.environ['FAKE_GH_ALWAYS_OLD']
        elif os.environ.get('FAKE_GH_DELAY_FINAL')=='1' and s.get('confirmed_sha') and s['confirmed_sha']!=sha and not s.get('stale_head_returned'):
            reported=s['confirmed_sha']
            s['stale_head_returned']=True
        s['confirmed_sha']=reported
        store.write_text(json.dumps(s))
        print(json.dumps({'state':'open','draft':os.environ.get('FAKE_GH_READY')!='1','head':{'ref':s['head'],'sha':reported},'base':{'ref':s['base']}}))
else: sys.exit(2)
''')
        gh.chmod(0o755)
        self.env = patch.dict(os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                                           "FAKE_GH_STORE": str(self.root / "gh.json"),
                                           "FAKE_GH_ORIGIN": str(self.origin)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def git(self, *args, cwd=None):
        return subprocess.check_output(["git", *args], cwd=cwd or self.repo,
                                       stderr=subprocess.PIPE, text=True).strip()

    def publish(self):
        # remote get-url expands insteadOf; preserve the configured URL for the validation check.
        real = publish.checked
        def checked(args, cwd=None):
            if args == ["git", "remote", "get-url", "origin"]:
                return "https://github.com/example/test.git"
            return real(args, cwd)
        with patch("publish.checked", side_effect=checked):
            return publish.publish_draft({"repository": "example/test", "base_branch": "main"},
                                         self.repo, self.run_dir, "1-10", self.data, self.control)

    def test_real_commit_push_draft_and_interaction_followup_are_idempotent(self):
        result = self.publish()
        self.assertEqual(result["draft_pr_url"], "https://github.com/example/test/pull/7")
        self.assertIn(result["draft_pr_url"], (self.run_dir / "result.md").read_text())
        self.assertTrue((self.repo / "interactions/pr-0007.json").exists())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.git("--git-dir", str(self.origin), "rev-parse", "refs/heads/codex/agent-task-1-10", cwd=self.root), self.git("rev-parse", "HEAD"))
        self.publish()
        self.assertEqual(json.loads((self.root / "gh.json").read_text())["creates"], 1)
        self.assertEqual(self.git("--git-dir", str(self.origin), "rev-parse", "main", cwd=self.root), self.revision)

    def test_lost_creation_response_recovers_without_second_pr(self):
        with patch.dict(os.environ, {"FAKE_GH_LOST_RESPONSE": "1"}):
            with self.assertRaises(subprocess.CalledProcessError):
                self.publish()
        self.publish()
        self.assertEqual(json.loads((self.root / "gh.json").read_text())["creates"], 1)

    def test_final_push_can_wait_for_a_stale_github_head(self):
        with patch.dict(os.environ, {"FAKE_GH_DELAY_FINAL": "1"}), patch("publish.time.sleep") as pause:
            result = self.publish()
        self.assertEqual(result["draft_pr_number"], 7)
        pause.assert_called_once_with(0.5)
        self.assertTrue(json.loads((self.root / "gh.json").read_text())["stale_head_returned"])

    def test_persistent_wrong_head_still_fails_with_diagnostics(self):
        with patch.dict(os.environ, {"FAKE_GH_ALWAYS_OLD": self.revision}), patch("publish.time.sleep") as pause:
            with self.assertRaisesRegex(ValueError, "has not confirmed published revision"):
                self.publish()
        self.assertEqual(pause.call_count, 4)
        self.assertFalse((self.run_dir / "result.md").exists())

    def test_existing_ready_pr_cannot_count_as_completed_draft(self):
        self.publish()
        remote_before = self.git("--git-dir", str(self.origin), "rev-parse", "refs/heads/codex/agent-task-1-10", cwd=self.root)
        (self.repo / "file.txt").write_text("extra local change\n")
        with patch.dict(os.environ, {"FAKE_GH_READY": "1"}), self.assertRaisesRegex(ValueError, "open draft"):
            self.publish()
        self.assertEqual(self.git("--git-dir", str(self.origin), "rev-parse", "refs/heads/codex/agent-task-1-10", cwd=self.root), remote_before)

    def test_pr_task_targets_the_captured_source_branch(self):
        self.data["pull_request"] = {"head": {"sha": self.revision}}
        self.git("--git-dir", str(self.origin), "update-ref", "refs/heads/source-branch", self.revision, cwd=self.root)
        with patch.dict(os.environ, {"FAKE_GH_SOURCE_SHA": self.revision}):
            self.publish()
        self.assertEqual(json.loads((self.root / "gh.json").read_text())["base"], "source-branch")

    def test_source_pr_moving_stops_publication(self):
        self.data["pull_request"] = {"head": {"sha": self.revision}}
        with self.assertRaisesRegex(ValueError, "source PR changed"):
            self.publish()
        self.assertFalse((self.root / "gh.json").exists())

    def test_large_file_cannot_enter_pushed_history(self):
        (self.repo / "large.npz").write_bytes(b"0" * (publish.MAX_BLOB_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "5 MiB"):
            self.publish()
        self.assertFalse((self.root / "gh.json").exists())

    def test_committed_then_deleted_large_blob_still_blocks_push(self):
        path = self.repo / "large.npz"
        path.write_bytes(b"0" * (publish.MAX_BLOB_BYTES + 1))
        self.git("add", ".")
        self.git("commit", "-m", "large fixture")
        path.unlink()
        self.git("add", ".")
        self.git("commit", "-m", "remove large fixture")
        with self.assertRaisesRegex(ValueError, "new Git blob"):
            self.publish()
        self.assertFalse((self.root / "gh.json").exists())

    def test_bad_metadata_and_credentials_stop_before_push(self):
        (self.run_dir / "result.json").write_text(json.dumps({"title": "Wrong title", "body": "Test"}))
        with self.assertRaisesRegex(ValueError, "valid repository PR title"):
            self.publish()
        (self.run_dir / "result.json").write_text(json.dumps({"title": "Infrastructure: test", "body": "Test"}))
        (self.repo / "auth.json").write_text('{"fixture":true}')
        with self.assertRaisesRegex(ValueError, "credential"):
            self.publish()
        self.assertFalse((self.root / "gh.json").exists())


if __name__ == "__main__":
    unittest.main()
