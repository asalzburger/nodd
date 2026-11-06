"""Publish one isolated task branch as a draft PR using the host's GitHub login."""

import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


PREFIXES = ("Magnet System", "Tracker", "Calorimeter", "Muon System", "Global",
            "Software", "Documentation", "Infrastructure")
MAX_BLOB_BYTES = 5 * 1024 * 1024


def checked(args, cwd=None):
    process = subprocess.Popen(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    try:
        output, errors = process.communicate(timeout=180)
    except BaseException:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        raise
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, args, output, errors)
    return output.strip()


def metadata(path):
    value = json.loads(path.read_text())
    if (set(value) != {"title", "body"} or not isinstance(value["title"], str)
            or not isinstance(value["body"], str) or not value["body"].strip()
            or "\n" in value["title"] or "\r" in value["title"]
            or not any(value["title"].startswith(prefix + ": ")
                       and value["title"][len(prefix) + 2:].strip() for prefix in PREFIXES)):
        raise ValueError("final response must supply a valid repository PR title and nonempty body")
    return value


def inspect_staged(worktree, run_dir):
    """Retain a reviewable size inventory; reject obvious secrets and large run artifacts."""
    paths = checked(["git", "diff", "--cached", "--diff-filter=ACMRT", "--name-only", "-z"], worktree)
    inventory = []
    for name in filter(None, paths.split("\0")):
        path = Path(name)
        if (any(part in {".ssh", ".aws"} for part in path.parts)
                or path.name in {".env", "auth.json", "credentials"}
                or path.suffix in {".pem", ".key"}):
            raise ValueError(f"refusing to publish a credential/configuration path: {name}")
        size = int(checked(["git", "cat-file", "-s", ":" + name], worktree))
        inventory.append({"path": name, "bytes": size})
        if size > MAX_BLOB_BYTES:
            raise ValueError(f"staged file exceeds the unattended 5 MiB publication limit: {name}")
    report = run_dir / "staged-files.json"
    previous = json.loads(report.read_text()) if report.exists() else []
    combined = {item["path"]: item for item in previous + inventory}
    report.write_text(json.dumps(list(combined.values()), indent=2) + "\n")


def inspect_commits(worktree, run_dir, revision):
    objects = []
    for line in checked(["git", "rev-list", "--objects", f"{revision}..HEAD"], worktree).splitlines():
        sha, _, path = line.partition(" ")
        if checked(["git", "cat-file", "-t", sha], worktree) != "blob":
            continue
        size = int(checked(["git", "cat-file", "-s", sha], worktree))
        if size > MAX_BLOB_BYTES:
            raise ValueError(f"new Git blob exceeds the unattended 5 MiB publication limit: {path}")
        objects.append({"sha": sha, "path": path, "bytes": size})
    (run_dir / "published-objects.json").write_text(json.dumps(objects, indent=2) + "\n")


def publish_draft(config, worktree, run_dir, key, data, control_root):
    value = metadata(run_dir / "result.json")
    branch = f"codex/agent-task-{key}"
    if checked(["git", "branch", "--show-current"], worktree) != branch:
        raise ValueError("task changed its assigned branch; publication stopped")
    origin = checked(["git", "remote", "get-url", "origin"], worktree)
    repo = config["repository"]
    if origin not in {f"git@github.com:{repo}.git", f"https://github.com/{repo}.git",
                      f"https://github.com/{repo}"}:
        raise ValueError("task origin changed; publication stopped")
    base = config["base_branch"]
    if "pull_request" in data:
        source = json.loads(checked(["gh", "api", "--hostname", "github.com",
                                    f"repos/{repo}/pulls/{data['issue']['number']}"]))
        if source["state"] != "open" or source["head"]["sha"] != data["pull_request"]["head"]["sha"]:
            raise ValueError("source PR changed during the task; publication stopped")
        base = source["head"]["ref"]
    # Validate curated records before creating any remote result.
    checked([sys.executable, "-B", str(control_root / "tools/session_logging/session_log.py"),
             "--repo", str(worktree), "validate"])
    checked([sys.executable, "-B", str(control_root / "tools/interactions/ledger.py"),
             "--repo", str(worktree), "validate"])
    checked(["git", "add", "--all"], worktree)
    inspect_staged(worktree, run_dir)
    if checked(["git", "diff", "--cached", "--name-only"], worktree):
        checked(["git", "commit", "-m", value["title"]], worktree)
    if int(checked(["git", "rev-list", "--count", f"{data['input_revision']}..HEAD"], worktree)) == 0:
        raise ValueError("task has no deliverable commit; include its curated session record")
    inspect_commits(worktree, run_dir, data["input_revision"])
    existing = json.loads(checked(["gh", "pr", "list", "--repo", repo, "--head", branch,
                                   "--state", "all", "--limit", "100", "--json", "number"]))
    if len(existing) > 1:
        raise ValueError("multiple PRs already reference the task branch")
    if existing:
        number = existing[0]["number"]
        prior = json.loads(checked(["gh", "api", "--hostname", "github.com", f"repos/{repo}/pulls/{number}"]))
        if (prior["state"] != "open" or not prior["draft"] or prior["head"]["ref"] != branch
                or prior["base"]["ref"] != base):
            raise ValueError("existing task result is not an open draft PR; refusing to update it")
    checked(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], worktree)
    if not existing:
        body = (f"Task request: https://github.com/{repo}/"
                f"{'pull' if 'pull_request' in data else 'issues'}/{data['issue']['number']}\n"
                f"Label request: `{key}`\n\n" + value["body"])
        body_file = run_dir / "pr-body.md"
        body_file.write_text(body + "\n")
        url = checked(["gh", "pr", "create", "--repo", repo, "--head", branch,
                       "--base", base, "--draft", "--title", value["title"],
                       "--body-file", str(body_file)], worktree)
        match = re.fullmatch(r"https://github\.com/" + re.escape(repo) + r"/pull/([0-9]+)", url)
        if not match:
            raise ValueError("GitHub did not return the task draft PR URL")
        number = int(match[1])
    url = f"https://github.com/{repo}/pull/{number}"
    progress = {"draft_pr_url": url, "draft_pr_number": number}
    (run_dir / "publication.json").write_text(json.dumps(progress, indent=2) + "\n")

    def verify():
        pr = json.loads(checked(["gh", "api", "--hostname", "github.com", f"repos/{repo}/pulls/{number}"]))
        if (pr["state"] != "open" or not pr["draft"] or pr["head"]["ref"] != branch
                or pr["base"]["ref"] != base
                or pr["head"]["sha"] != checked(["git", "rev-parse", "HEAD"], worktree)):
            raise ValueError("task result is not an open draft PR at the published revision")

    verify()
    # PR numbers exist only after creation. Add the individual interaction record before completion.
    checked([sys.executable, "-B", str(control_root / "tools/interactions/ledger.py"),
             "--repo", str(worktree), "capture", "--pr", str(number)])
    checked([sys.executable, "-B", str(control_root / "tools/interactions/ledger.py"),
             "--repo", str(worktree), "validate", "--pr", str(number)])
    checked(["git", "add", "--", f"interactions/pr-{number:04d}.json"], worktree)
    inspect_staged(worktree, run_dir)
    if checked(["git", "diff", "--cached", "--name-only"], worktree):
        checked(["git", "commit", "-m", "Infrastructure: record agent task draft PR interactions"], worktree)
        inspect_commits(worktree, run_dir, data["input_revision"])
        checked(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], worktree)
    verify()
    (run_dir / "result.md").write_text(f"Draft PR: {url}\n\n{value['body']}\n")
    return progress
