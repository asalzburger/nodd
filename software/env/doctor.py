"""Verify actual node-bound dependencies rather than relying on setup guards."""
import hashlib
import json
from pathlib import Path
import subprocess
import dd4hep
import DDG4

def run(*args):
    return subprocess.check_output(args, text=True).strip()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

print(json.dumps({
    "hostname": run("hostname"),
    "spack_environment": run("spack", "env", "status"),
    "packages": run("spack", "find", "--format", "{name}@{version} /{hash}", "dd4hep", "geant4"),
    "setup_sha256": digest("/Users/salzburg/cernbox/configs/acts/acts_setup.sh"),
    "spack_lock_sha256": digest("/Users/salzburg/Documents/work/externals/ci-dependencies/spack.lock"),
    "dd4hep_ddg4_imports": True,
    "geant4_version": run("geant4-config", "--version"),
    "datasets": run("geant4-config", "--check-datasets"),
}, indent=2))
