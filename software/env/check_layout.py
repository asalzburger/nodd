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

if (root / "detector").is_symlink():
    assert (root / "detector").resolve() == root / "software/source/detectors"
    for name, filename in (("short_strip_barrel", "ShortStripBarrel.cpp"),
                           ("short_strip_endcap", "ShortStripEndcap.cpp"),
                           ("long_strip_barrel", "LongStrip.cpp"),
                           ("calorimeter", "Calorimeter.cpp")):
        assert (root / "prototypes" / name / filename).resolve() == root / "software/source/detectors/src" / filename
    print("Detector compatibility paths resolve to their software source owner")
