"""Issue 131: repeat the retained 100-electron timing pilot after PR129.

Adapted from the local pilot recipe described by
logs/codex/SESSION-2026-11-10-siw-ecal-compute-pilot.md.
All generated inputs, events and full logs belong in ignored build storage.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import platform
import socket
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare(directory, baseline):
    manifest = json.loads((baseline / "baseline.json").read_text())
    source_xml = baseline / "detector.xml"
    source_materials = baseline / "materials.xml"
    assert sha(source_xml) == manifest["compact_sha256"]
    assert sha(source_materials) == manifest["materials_sha256"]
    compact = ET.parse(source_xml)
    root = compact.getroot()
    assert root.find("fields") is None
    detectors = root.find("detectors")
    assert {int(node.get("id")) for node in detectors} == set(range(10))
    for node in list(detectors):
        if int(node.get("id")) not in (8, 9):
            detectors.remove(node)
    assert all(node.find("wedge_envelope") is not None for node in detectors)
    readouts = root.find("readouts")
    for node in list(readouts):
        if node.get("name") not in {"BARRELHits", "EDGEHits"}:
            readouts.remove(node)
    assert {node.get("name") for node in detectors} == {"BARREL", "EDGE"}
    assert {node.get("name") for node in readouts} == {"BARRELHits", "EDGEHits"}
    root.find("info").attrib.update(name="LAYOUT-001-ECAL-only", title="Issue 131: post-PR129 SiW ECAL timing pilot")
    compact.write(directory / "detector.xml", encoding="utf-8", xml_declaration=True)
    shutil.copyfile(source_materials, directory / "materials.xml")
    samples = []
    commands = ["/gun/position 0 0 0 mm", "/gun/particle e-"]
    for index, eta in enumerate((0.5, 1.45, 2.0, 3.0)):
        phi = 0.123
        p = 50 * math.cosh(eta)
        direction = (math.cos(phi) / math.cosh(eta), math.sin(phi) / math.cosh(eta), math.tanh(eta))
        name = f"eta-{eta:.2f}"
        samples.append(dict(name=name, eta=eta, phi=phi, p_GeV=p, events=25, seeds=[220100 + index, 1220103 + index]))
        commands.extend([
            f"/ddg4/EDM4hepOutput/Output {name}.root",
            f"/gun/momentumAmp {p:.17g} GeV",
            "/gun/direction " + " ".join(format(x, ".17g") for x in direction),
            f"/random/setSeeds {220100 + index} {1220103 + index}",
            f"/i118/saveRandomState random-state-{index}.json",
            f"/control/echo ECAL_TIMING_BEGIN_{index}",
            "/run/beamOn 25",
            f"/control/echo ECAL_TIMING_END_{index}",
        ])
    (directory / "pilot.mac").write_text("\n".join(commands) + "\n")
    return samples


def run(directory, baseline, library, steering):
    if not library.is_file() or not steering.is_file():
        raise FileNotFoundError("Factory library and transport steering must exist")
    directory.mkdir(parents=True, exist_ok=False)
    samples = prepare(directory, baseline)
    environment = os.environ.copy()
    for key in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        environment[key] = str(library.parent) + os.pathsep + environment.get(key, "")
    environment["I118_TRANSPORT_AUDIT"] = str(directory / "native-transport-audit.json")
    command = [
        sys.executable, "-u", shutil.which("ddsim"), "--compactFile", str(directory / "detector.xml"),
        "--steeringFile", str(steering), "--runType", "run", "--enableG4Gun",
        "--macroFile", str(directory / "pilot.mac"), "--numberOfThreads", "1",
        "--random.seed", "22019999", "--physics.list", "FTFP_BERT", "--physics.rangecut", "0.7",
        "--part.userParticleHandler", "", "--outputConfig.forceEDM4HEP",
        "--outputFile", str(directory / "unused.root"),
    ]
    markers = {}
    problems = []
    repository = Path(__file__).resolve().parents[3]
    metadata = dict(
        source_revision=subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip(),
        hostname=socket.gethostname(), platform=platform.platform(), python=sys.version,
        packages=subprocess.check_output(["spack", "find", "--format", "{name}@{version} /{hash}",
                                          "dd4hep", "geant4", "root", "podio", "edm4hep"], text=True).strip(),
        root_version=subprocess.check_output(["root-config", "--version"], text=True).strip(),
        setup_sha256=sha(Path("/Users/salzburg/cernbox/configs/acts/acts_setup.sh")),
        spack_lock_sha256=sha(Path("/Users/salzburg/Documents/work/externals/ci-dependencies/spack.lock")),
    )
    before_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    print("Starting DDSim", flush=True)
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    with (directory / "transport.log").open("w", buffering=1) as log:
        with subprocess.Popen(command, env=environment, cwd=directory, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, errors="replace") as child:
            for line in child.stdout:
                elapsed = time.monotonic() - started
                log.write(f"[{elapsed:10.3f}] {line}")
                marker = line.strip()
                if marker.startswith("ECAL_TIMING_"):
                    if marker in markers:
                        raise RuntimeError(f"Duplicate marker {marker}")
                    markers[marker] = elapsed
                    print(f"{elapsed:.2f}s {marker}", flush=True)
                if any(p in line for p in ("COMMAND NOT FOUND", "Batch is interrupted", "Command aborted")):
                    problems.append(line.strip())
            code = child.wait()
    elapsed = time.monotonic() - started
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(environment=metadata, started_at=started_at, ended_at=datetime.now(timezone.utc).isoformat(), command=command, exit_code=code, elapsed_seconds=elapsed,
                   cpu_user_seconds=usage.ru_utime - before_usage.ru_utime,
                   cpu_system_seconds=usage.ru_stime - before_usage.ru_stime,
                   peak_rss_bytes=usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024), markers=markers, macro_errors=problems,
                   samples=samples, sha256={path.name: sha(path) for path in (
                       directory / "detector.xml", directory / "materials.xml", directory / "pilot.mac",
                       directory / "transport.log", library, steering, Path(__file__).resolve(),
                       baseline / "baseline.json",
                   )})
    (directory / "timing.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if code or problems or len(markers) != 8:
        raise RuntimeError(f"DDSim failed timing checks, see {directory / 'transport.log'}")
    print(f"DDSim completed in {elapsed:.2f}s", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("Usage: run_pilot.py NEW_RUN_DIRECTORY BASELINE LIBRARY STEERING")
    if not __debug__:
        raise SystemExit("Run without Python optimization; input assertions are mandatory")
    run(*(Path(arg).resolve() for arg in sys.argv[1:]))
