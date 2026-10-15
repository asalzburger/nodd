"""Run two bounded DES036 saved-hit checks in the verified DD4hep environment."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run(directory, library):
    from transport import check
    directory, library = directory.resolve(), library.resolve()
    ddsim = shutil.which("ddsim")
    if not ddsim or not library.is_file():
        raise RuntimeError("activate the verified node runtime and build the isolated factory first")
    data = json.loads((directory / "expected.json").read_text())
    environment = os.environ.copy()
    for variable in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        environment[variable] = str(library.parent) + os.pathsep + environment.get(variable, "")
    commands = []
    for module in (0, 1):
        tile = next(p for p in data["parts"] if p["role"] == "sensitive" and p["module"] == module and p["sensor"] == 0)
        x, y, _ = tile["center_mm"]
        stem = directory / ("module" + str(module) + "-smoke")
        command = [sys.executable, ddsim, "--compactFile", str(directory / "readout.xml"),
                   "--runType", "batch", "--numberOfEvents", "1", "--enableGun",
                   "--gun.particle", "mu-", "--gun.energy", "10*GeV",
                   f"--gun.position={x} {y} -50", "--gun.direction", "0 0 1",
                   "--random.seed", "42", "--physics.list", "FTFP_BERT",
                   "--part.userParticleHandler", "", "--outputFile", str(stem.with_suffix(".root"))]
        with stem.with_suffix(".log").open("w") as log:
            result = subprocess.run(command, env=environment, stdout=log, stderr=subprocess.STDOUT)
        commands.append({"module": module, "command": command, "exit_code": result.returncode})
        (directory / "smoke-commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        if result.returncode:
            raise RuntimeError(f"module {module} DDSim failed with {result.returncode}; see {stem.with_suffix('.log')}")
    return check(directory, directory / "transport.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.directory, args.library))
