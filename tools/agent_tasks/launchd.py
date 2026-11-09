#!/usr/bin/env python3
"""Render a user LaunchAgent. Loading it is a separate, explicit deployment step."""

import argparse
import os
from pathlib import Path
import plistlib
import shutil
import sys

from poll import CONFIG, ROOT, load_config, verify_host, verify_origin


LABEL = "org.nodd.agent-tasks"


def executable(name):
    path = shutil.which(name)
    if not path:
        raise ValueError(f"required executable is missing: {name}")
    return str(Path(path).absolute())


def make_plist(repo, state_dir, config_path, python, codex, search_path):
    return {
        "Label": LABEL,
        "ProgramArguments": [python, "-B", str(repo / "tools/agent_tasks/poll.py"),
                             "--repo", str(repo), "--config", str(config_path),
                             "--state-dir", str(state_dir), "--codex", codex],
        "WorkingDirectory": str(repo),
        "EnvironmentVariables": {"PATH": search_path, "PYTHONUNBUFFERED": "1",
                                 "GH_PROMPT_DISABLED": "1", "GIT_TERMINAL_PROMPT": "0"},
        # A calendar schedule coalesces missed wakeups after sleep; it does not wake the Mac.
        "StartCalendarInterval": {"Minute": 7},
        "RunAtLoad": True,
        "ProcessType": "Background",
        "StandardOutPath": str(state_dir / "launchd.stdout.log"),
        "StandardErrorPath": str(state_dir / "launchd.stderr.log"),
        "Umask": 0o077,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--state-dir", type=Path,
                        default=Path.home() / "Library/Application Support/nodd-agent-tasks")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        repo, state_dir, config_path = (p.resolve() for p in (args.repo, args.state_dir, args.config))
        config = load_config(config_path)
        verify_host(config)
        verify_origin(repo, config)
        python, codex = executable("python3"), executable("codex")
        executable("git")
        executable("gh")
        if state_dir.is_relative_to(repo):
            raise ValueError("state directory must be outside the repository")
        data = make_plist(repo, state_dir, config_path, python, codex, os.environ["PATH"])
        # Never overwrite an installed scheduler accidentally. Re-render elsewhere for upgrades.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as handle:
            plistlib.dump(data, handle)
        args.output.chmod(0o600)
        state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        print(f"Wrote {args.output}; not loaded. See tools/agent_tasks/README.md for deployment.")
        return 0
    except (ValueError, OSError) as error:
        print(f"LaunchAgent generation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
