#!/usr/bin/env python3
"""Generate local, ignored ODD single-particle samples for issue #117."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ODD_REVISION = "d70556f33b1c36abdf101a07ad8cf57eb56fbdf1"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--odd-source", type=Path, required=True)
    parser.add_argument("--odd-library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--energies", type=float, nargs="+", default=[5, 20, 50])
    parser.add_argument("--etas", type=float, nargs="+", default=[0, 1.5])
    parser.add_argument("--particles", nargs="+", default=["e-", "gamma"])
    parser.add_argument("--seed", type=int, default=117000)
    args = parser.parse_args()
    source = args.odd_source.resolve()
    library = args.odd_library.resolve()
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != ODD_REVISION:
        parser.error(f"Requires ODD {ODD_REVISION}, got {revision}")
    subprocess.run(["git", "-C", str(source), "diff", "--quiet", "HEAD"], check=True)
    if args.events < 1 or not library.is_file():
        parser.error("Positive event count and existing ODD library required")
    ddsim = shutil.which("ddsim")
    if not ddsim:
        parser.error("Activate DD4hep/Geant4 first")
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for name in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[name] = str(library.parent) + os.pathsep + env.get(name, "")
    samples = []
    for particle in args.particles:
        if particle not in ("e-", "gamma", "mu-"):
            parser.error("Supported particles: e-, gamma, mu-")
        for energy in args.energies:
            for eta in args.etas:
                if energy <= 0 or not math.isfinite(energy) or not math.isfinite(eta):
                    parser.error("Finite eta and positive finite energy required")
                tag = f"{particle}_E{energy:g}_eta{eta:g}"
                directory = args.output / tag
                directory.mkdir(exist_ok=True)
                output = directory.resolve() / "sim.edm4hep.root"
                if output.exists():
                    parser.error(f"Refusing to overwrite {output}")
                theta = 2 * math.atan(math.exp(-eta))
                seed = args.seed + len(samples)
                command = [sys.executable, ddsim, "--enableGun", "--numberOfEvents", str(args.events),
                           "--gun.energy", f"{energy:g}*GeV", "--gun.particle", particle,
                           "--gun.thetaMin", repr(theta), "--gun.thetaMax", repr(theta),
                           "--gun.phiMin", "0.123", "--gun.phiMax", "0.123",
                           "--gun.distribution", "uniform", "--compactFile", str(source / "xml/OpenDataDetector.xml"),
                           "--outputFile", str(output), "--outputConfig.forceEDM4HEP",
                           "--random.seed", str(seed), "--physics.list", "FTFP_BERT", "--printLevel", "WARNING"]
                started = time.monotonic()
                with (directory / "ddsim.log").open("w") as log:
                    result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
                sample = dict(particle=particle, energy_GeV=energy, eta=eta, phi_rad=0.123,
                              requested_events=args.events, seed=seed, command=command,
                              elapsed_seconds=time.monotonic() - started, exit_code=result.returncode,
                              path=str(output), sha256=sha256(output) if output.exists() else None)
                samples.append(sample)
                manifest = dict(status="PROTOTYPE characterization", odd_revision=revision,
                                odd_library_sha256=sha256(library), generator_sha256=sha256(Path(__file__)),
                                python=sys.version, samples=samples,
                                limitations=["Sparse signal-cell digitization does not establish full-detector noise occupancy.",
                                              "Visible silicon deposit / beam energy is not passive-plus-active sampling fraction."])
                (args.output / "samples.json").write_text(json.dumps(manifest, indent=2) + "\n")
                print(f"{tag}: exit {result.returncode}, {sample['elapsed_seconds']:.1f} s", flush=True)
                if result.returncode:
                    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
