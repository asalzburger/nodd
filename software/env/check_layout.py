"""Check software gitlinks without initialising optional sources or dependencies."""
import configparser
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
modules = configparser.ConfigParser()
modules.read(root / ".gitmodules")
paths = {modules[s]["path"]: modules[s]["url"] for s in modules.sections()}
for name in ("acts", "IdRes", "nodehammer", "OpenDataDetector"):
    path = "software/submodules/" + name
    assert path in paths, f"Missing submodule: {path}"
    entry = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "--", path], text=True)
    assert entry.startswith("160000 "), f"Not a gitlink: {path}"
for path in ("source/ActsExamples", "source/detectors", "source/EDM", "running", "analysis"):
    assert (root / "software" / path).is_dir(), f"Missing software directory: {path}"
print("Software directory and gitlink checks passed")
