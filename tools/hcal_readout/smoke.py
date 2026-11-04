"""Run two bounded DES036 saved-hit checks in the verified DD4hep environment."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def run(directory, library):
    from transport import check, sha
    directory, library = directory.resolve(), library.resolve()
    ddsim = shutil.which("ddsim")
    if not ddsim or not library.is_file():
        raise RuntimeError("activate the verified node runtime and build the isolated factory first")
    data = json.loads((directory / "expected.json").read_text())
    environment = os.environ.copy()
    for variable in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        environment[variable] = str(library.parent) + os.pathsep + environment.get(variable, "")
    commands = []
    inputs = {name: {"path": str(path.resolve()), "sha256": sha(path)} for name, path in {
        "expected": directory / "expected.json", "compact": directory / "readout.xml",
        "materials": directory / "materials.xml", "library": library,
        "ddsim": Path(ddsim), "runner": Path(__file__), "python_executable": Path(sys.executable),
    }.items()}
    repository = Path(__file__).resolve().parents[2]
    execution = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip(),
                 "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=repository, text=True))}
    for module in (0, 1):
        tile = next(p for p in data["parts"] if p["role"] == "sensitive" and p["module"] == module and p["sensor"] == 0)
        x, y, _ = tile["center_mm"]
        stem = directory / ("module" + str(module) + "-smoke")
        command = [inputs["python_executable"]["path"], inputs["ddsim"]["path"], "--compactFile", str(directory / "readout.xml"),
                   "--runType", "batch", "--numberOfEvents", "1", "--enableGun",
                   "--gun.particle", "mu-", "--gun.energy", "10*GeV",
                   f"--gun.position={x} {y} -50", "--gun.direction", "0 0 1",
                   "--random.seed", "42", "--physics.list", "FTFP_BERT",
                   "--part.userParticleHandler", "", "--outputFile", str(stem.with_suffix(".root"))]
        record = {"schema_version": 1, "module": module, "command": command,
                  "inputs": inputs, "python": platform.python_version(), "execution": execution,
                  "factory_search_prefix": str(library.parent),
                  "started_at": datetime.now(timezone.utc).isoformat(), "exit_code": None,
                  "settings": {"events": 1, "particle": "mu-", "gun_energy_argument": "10*GeV",
                               "position_mm": [x, y, -50], "direction": [0, 0, 1],
                               "seed": 42, "physics_list": "FTFP_BERT",
                               "field_definition": "absent from compact; no field CLI override"}}
        commands.append(record)
        metadata = directory / "smoke-commands.json"
        metadata.write_text(json.dumps(commands, indent=2) + "\n")
        with stem.with_suffix(".log").open("w") as log:
            result = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT)
        record.update(exit_code=result.returncode, finished_at=datetime.now(timezone.utc).isoformat(),
                      outputs={kind: {"path": str(stem.with_suffix(suffix)),
                                      "sha256": sha(stem.with_suffix(suffix)) if stem.with_suffix(suffix).is_file() else None}
                               for kind, suffix in (("root", ".root"), ("log", ".log"))})
        metadata.write_text(json.dumps(commands, indent=2) + "\n")
        if result.returncode:
            raise RuntimeError(f"module {module} DDSim failed with {result.returncode}; see {stem.with_suffix('.log')}")
    return check(directory, directory / "transport.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.directory, args.library))
