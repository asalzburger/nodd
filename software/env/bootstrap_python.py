"""Create a build-owned Python environment using the active Spack interpreter."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--venv", type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
requirements = Path(__file__).with_name("requirements.txt")
codegen = root / "software/submodules/acts/codegen"
if not (codegen / "requirements.txt").is_file():
    p.error("Initialise the ACTS submodule first")
inputs = [requirements, codegen / "requirements.txt", codegen / "pyproject.toml",
          *sorted(codegen.rglob("*.py"))]
fingerprint = hashlib.sha256(b"".join(f.read_bytes() for f in inputs) + sys.version.encode()).hexdigest()
stamp = a.venv / "nodd-bootstrap.json"
if stamp.exists() and json.loads(stamp.read_text())["inputs_sha256"] == fingerprint:
    print("Build-owned Python environment is current")
    raise SystemExit(0)
if not (a.venv / "bin/python").exists():
    subprocess.run([sys.executable, "-m", "venv", str(a.venv)], check=True)
# Use upstream's pinned generator dependencies and its own local codegen package.
# The unrelated PyPI package named codegen is not an ACTS dependency.
lock = a.venv / "requirements.lock"
subprocess.run(["uv", "pip", "compile", "--python", str(a.venv / "bin/python"),
                str(requirements), str(codegen / "requirements.txt"), "-o", str(lock)], check=True)
subprocess.run(["uv", "pip", "sync", "--python", str(a.venv / "bin/python"), str(lock)], check=True)
subprocess.run(["uv", "pip", "install", "--python", str(a.venv / "bin/python"),
                "--no-build-isolation", "--no-deps", "--reinstall", str(codegen)], check=True)
stamp.write_text(json.dumps({"inputs_sha256": fingerprint, "python": sys.version}, indent=2) + "\n")
