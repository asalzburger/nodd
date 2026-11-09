#!/usr/bin/env python3
"""Frozen, zero-field nODD/ODD transport; full event outputs stay local.

Prepare only after the native integrated-geometry gate. Run one geometry and
population in each fresh process, then index only normally completed groups.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "docs/validation/issue117/nodd-digitization-protocol.md"
ODD_PIN = "d70556f33b1c36abdf101a07ad8cf57eb56fbdf1"
PDG = {"e-": 11, "gamma": 22, "mu-": 13}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def git(*args, directory=ROOT):
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


def referenced_files(path, seen=None):
    seen = set() if seen is None else seen
    path = Path(path).resolve()
    if path in seen:
        return seen
    seen.add(path)
    for node in ET.parse(path).getroot().iter():
        ref = node.get("ref")
        if ref and node.tag in ("include", "gdmlFile"):
            referenced_files(path.parent / ref, seen)
    return seen


def canonical(node, base, drop_fields=False):
    attributes = dict(node.attrib)
    if "ref" in attributes:
        attributes["ref"] = str((base / attributes["ref"]).resolve())
    return (node.tag, attributes, (node.text or "").strip(),
            [canonical(child, base, drop_fields) for child in node
             if not (drop_fields and child.tag == "fields")])


def rows():
    output = []
    for geometry, offset in (("nodd", 0), ("odd-zero", 1000)):
        points = [(p, e, eta) for p in ("e-", "gamma")
                  for e in (5, 20, 50) for eta in (0, 1, 2)]
        points.append(("e-", 20, -2))
        for index, (particle, momentum, eta) in enumerate(points):
            output.append(dict(geometry=geometry, kind="showers", particle=particle,
                               energy_GeV=momentum, eta=eta, requested_events=200,
                               seed=120000 + offset + index))
    for geometry, offset in (("nodd", 0), ("odd-zero", 1000)):
        for index, eta in enumerate((0, 2, -2)):
            output.append(dict(geometry=geometry, kind="muons", particle="mu-",
                               energy_GeV=10, eta=eta, requested_events=250,
                               seed=122000 + offset + index))
    for index, eta in enumerate((0, 1, 2, -2)):
        output.append(dict(geometry="odd-zero", kind="calibration", particle="e-",
                           energy_GeV=20, eta=eta, requested_events=100,
                           seed=124000 + index))
    for row in output:
        row.update(id=f"{row['kind']}-{row['particle']}_E{row['energy_GeV']:g}_eta{row['eta']:g}",
                   phi_rad=.123, seed_pair=[row["seed"], row["seed"] + 1000003])
    return output


def validate_native(baseline, report, libraries):
    """Exact native PASS binding, required before every nODD run and final index."""
    record = json.loads((baseline / "baseline.json").read_text())
    native = json.loads(report.read_text())
    if (record["layout"] != "LAYOUT-001" or native["status"] != "PASS"
            or native["overlap_count"] != 0
            or native["baseline_manifest_sha256"] != sha(baseline / "baseline.json")):
        raise ValueError("Native complete nODD union audit did not pass on this export")
    for name, key in (("detector.xml", "compact_sha256"), ("materials.xml", "materials_sha256")):
        if sha(baseline / name) != record[key] or native[key] != record[key]:
            raise ValueError("Current geometry/material differs from audited native export")
    expected_systems = {m["name"]: m["integrated_system_id"]
                        for component in record["components"] for m in component["system_mapping"]}
    if (native["native_systems"] != expected_systems
            or set(native["native_systems"].values()) != set(range(10))
            or native["overlap_tolerance_mm"] != 1e-5
            or native["native_auditor_sha256"] != sha(ROOT / "tools/calorimeter_baselines/native.py")):
        raise ValueError("Native root/tolerance/auditor identity differs from protocol")
    if {p.name: sha(p) for p in libraries} != native["libraries"]:
        raise ValueError("Factory libraries differ from the native union audit")
    return dict(report_path=str(report.resolve()), report_sha256=sha(report),
                compact_sha256=record["compact_sha256"], materials_sha256=record["materials_sha256"],
                baseline_sha256=sha(baseline / "baseline.json"), libraries=native["libraries"])


def bind_native(work, manifest):
    geom = manifest["geometries"]["nodd"]
    proof = validate_native(Path(geom["baseline_directory"]), Path(manifest["native_report_path"]),
                            [Path(p) for p in geom["libraries"]])
    path = work / "native-pass-binding.json"
    if path.exists() and json.loads(path.read_text()) != proof:
        raise ValueError("Native audit binding changed after the first nODD run")
    if not path.exists():
        save(path, proof)
    return proof


def prepare(args):
    work = args.work.resolve()
    if (work / "manifest.json").exists():
        raise ValueError("Choose a fresh work path; existing evidence is immutable")
    for source in (Path(__file__).resolve(), Path(__file__).with_name('nodd_transport.py').resolve(), PROTOCOL):
        committed = subprocess.check_output(['git','show','HEAD:'+str(source.relative_to(ROOT))],cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != sha(source):
            raise ValueError("Commit the exact protocol and transport producers before preparation")
    if git("rev-parse", "HEAD", directory=args.odd_source) != ODD_PIN or git("status", "--porcelain", directory=args.odd_source):
        raise ValueError("ODD source must match its clean pinned revision")
    baseline = args.nodd_directory.resolve()
    record = json.loads((baseline / "baseline.json").read_text())
    if record["layout"] != "LAYOUT-001":
        raise ValueError("Only the maintained SiW LAYOUT-001 is this study's nODD geometry")
    libraries = [p.resolve() for p in args.library]
    for name, key in (("detector.xml", "compact_sha256"), ("materials.xml", "materials_sha256")):
        if sha(baseline / name) != record[key]:
            raise ValueError("Current export differs from its construction manifest")
    pending = not args.native_report.exists()
    if pending and not args.allow_pending_native:
        raise ValueError("Native report pending; only explicit independent ODD-control preparation is permitted")
    if not pending:
        validate_native(baseline, args.native_report, libraries)
    work.mkdir(parents=True, exist_ok=True)
    original = args.odd_source.resolve() / "xml/OpenDataDetector.xml"
    tree = ET.parse(original)
    root = tree.getroot()
    before = canonical(root, original.parent, drop_fields=True)
    fields = root.findall("fields")
    if len(fields) != 1 or not fields[0].findall("field"):
        raise ValueError("Unexpected ODD field definition")
    root.remove(fields[0])
    for node in root.iter():
        if "ref" in node.attrib:
            node.set("ref", str((original.parent / node.get("ref")).resolve()))
    if canonical(root, original.parent) != before:
        raise ValueError("Zero-field wrapper changed more than field selection/references")
    ET.indent(tree)
    wrapper = work / "odd-zero.xml"
    tree.write(wrapper, encoding="utf-8", xml_declaration=True)
    import ROOT as R
    masses = {p: float(R.TDatabasePDG.Instance().GetParticle(PDG[p]).Mass()) for p in PDG}
    samples = rows()
    for row in samples:
        mass = masses[row["particle"]]
        row.update(mass_GeV=mass, kinetic_energy_GeV=math.hypot(row["energy_GeV"], mass)-mass)
    paths = set(referenced_files(baseline / "detector.xml")) | referenced_files(wrapper)
    paths |= set(baseline.rglob("*.json")) | set(baseline.rglob("*.xml"))
    paths |= {baseline / "baseline.json", PROTOCOL,
              Path(__file__).resolve(), Path(__file__).with_name("nodd_transport.py"),
              args.odd_library.resolve(), *libraries}
    for library in libraries + [args.odd_library.resolve()]:
        registration = library.with_suffix('.components')
        if registration.exists():
            paths.add(registration)
        for parent in (library.parent, library.parent.parent):
            cache = parent / 'CMakeCache.txt'
            if cache.exists():
                paths.add(cache)
    ddsim_package = Path(importlib.util.find_spec('DDSim').origin).parent
    paths |= set(ddsim_package.rglob('*.py'))
    for package in ('dd4hep', 'DDG4'):
        paths.add(Path(importlib.util.find_spec(package).origin))
    setup = Path('/Users/salzburg/cernbox/configs/acts/acts_setup.sh')
    lock = Path('/Users/salzburg/Documents/work/externals/ci-dependencies/spack.lock')
    paths |= {setup, lock}
    # Pin every maintained geometry/export input; analyses may evolve separately.
    for name in git("ls-files", "detector", "prototypes", "tools").splitlines():
        path = ROOT / name
        if path.suffix in (".py", ".json", ".xml", ".cpp", ".hpp", ".h") or path.name == "CMakeLists.txt":
            paths.add(path)
    manifest = dict(status="PROTOTYPE matched-field baseline-stage response",
                    native_report_path=str(args.native_report.resolve()),
                    native_gate_at_preparation="PENDING; nODD transport forbidden until bound native PASS" if pending else "PASS",
                    source_commit=git("rev-parse", "HEAD"), producer_sha256=sha(__file__),
                    repository_dirty=bool(git('status','--porcelain')),
                    producer_protocol_scoped_status=git('status','--porcelain','--',str(Path(__file__).relative_to(ROOT)),
                                                         str(Path(__file__).with_name('nodd_transport.py').relative_to(ROOT)),
                                                         str(PROTOCOL.relative_to(ROOT))),
                    protocol_sha256=sha(PROTOCOL), odd_revision=ODD_PIN,
                    geometries={"nodd": dict(label="LAYOUT-001", compact=str(baseline / "detector.xml"),
                                            libraries=[str(p) for p in libraries],
                                            collections=["BARRELHits", "EDGEHits"], baseline_directory=str(baseline)),
                                "odd-zero": dict(label="ODD zero-field control", compact=str(wrapper),
                                                libraries=[str(args.odd_library.resolve())],
                                                collections=["ECalBarrelCollection", "ECalEndcapCollection"])},
                    samples=samples, immutable={str(p.resolve()): sha(p) for p in sorted(paths)},
                    runtime=dict(Python=platform.python_version(), ROOT=R.gROOT.GetVersion(),
                                 Geant4=subprocess.check_output(['geant4-config','--version'],text=True).strip(),
                                 setup_sha256=sha(setup), spack_lock_sha256=sha(lock),
                                 DDSim_package_sha256={str(p):sha(p) for p in sorted(ddsim_package.rglob('*.py'))}),
                    transport=dict(physics="FTFP_BERT", range_cut_mm=.7, magnetic_field="zero",
                                   ECAL_sensitive_maximum_step_mm=5.,
                                   gun="native Geant4 gun; explicit momentumAmp command; persisted total-energy denominator",
                                   mass_GeV=masses, origin_mm=[0, 0, 0], event_seeder=False),
                    field_off_control=dict(original_root_sha256=sha(original), wrapper_sha256=sha(wrapper),
                                           canonical_except_fields_equal=True, removed_field_blocks=1))
    save(work / "manifest.json", manifest)
    print("Prepared", len(samples), "populations;", sum(s["requested_events"] for s in samples), "events")


def verify(work):
    manifest = json.loads((work / "manifest.json").read_text())
    for name, digest in manifest["immutable"].items():
        if sha(name) != digest:
            raise ValueError("Changed immutable input: " + name)
    return manifest


def audit_input(path, row, collections):
    from podio import root_io
    identities = set()
    counts = {name: 0 for name in collections}
    maximum_momentum_residual = 0.
    maximum_origin_residual = 0.
    total_energies = []
    reader = root_io.Reader(str(path))
    for frame in reader.get("events"):
        headers = frame.get("EventHeader")
        if len(headers) != 1:
            raise ValueError("Expected one EventHeader")
        identity = (headers[0].getRunNumber(), headers[0].getEventNumber())
        if identity != (row["actual_run_number"], len(identities)):
            raise ValueError("Run/event boundary differs from the frozen macro block")
        if identity in identities:
            raise ValueError("Duplicate EventHeader")
        identities.add(identity)
        primaries = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
        if len(primaries) != 1 or primaries[0].getPDG() != PDG[row["particle"]]:
            raise ValueError("Incorrect primary multiplicity/species")
        primary = primaries[0]
        p = primary.getMomentum()
        vertex = primary.getVertex()
        persisted = [p.x, p.y, p.z, vertex.x, vertex.y, vertex.z, primary.getEnergy()]
        if not all(math.isfinite(value) for value in persisted):
            raise ValueError("Nonfinite primary kinematics/origin")
        origin_residual = max(abs(vertex.x), abs(vertex.y), abs(vertex.z))
        maximum_origin_residual = max(maximum_origin_residual, origin_residual)
        expected_energy = math.hypot(row["energy_GeV"], row["mass_GeV"])
        if origin_residual > 1e-7 or abs(primary.getEnergy()-expected_energy) > 1e-7:
            raise ValueError("Persisted primary origin/total energy differs from protocol")
        momentum = math.sqrt(p.x*p.x + p.y*p.y + p.z*p.z)
        eta = math.asinh(p.z / math.hypot(p.x, p.y))
        phi = math.atan2(p.y, p.x)
        residual = abs(momentum - row["energy_GeV"])
        maximum_momentum_residual = max(maximum_momentum_residual, residual)
        if residual > 1e-7 or abs(eta-row["eta"]) > 1e-7 or abs(phi-row["phi_rad"]) > 1e-7:
            raise ValueError("Persisted primary differs from frozen momentum/direction")
        total_energies.append(float(primary.getEnergy()))
        for name in collections:
            hits = frame.get(name)
            ids = [int(hit.getCellID()) for hit in hits]
            if len(set(ids)) != len(ids):
                raise ValueError("Duplicate source cell")
            counts[name] += len(ids)
    if len(identities) != row["requested_events"]:
        raise ValueError("Incomplete raw population")
    if max(total_energies)-min(total_energies) > 1e-7:
        raise ValueError("Population is not monoenergetic")
    return dict(events=len(identities), cells_by_collection=counts,
                maximum_momentum_residual_GeV=maximum_momentum_residual,
                maximum_origin_residual_mm=maximum_origin_residual,
                generated_total_energy_GeV=math.fsum(total_energies)/len(total_energies),
                generated_total_energy_range_GeV=[min(total_energies), max(total_energies)])


def run(args):
    work = args.work.resolve()
    manifest = verify(work)
    if args.geometry == "nodd":
        bind_native(work, manifest)
    from DDSim.Helper.Random import Random
    if Random().enableEventSeed is not False:
        raise ValueError("Unexpected EventSeeder default")
    selected = [r for r in manifest["samples"] if r["geometry"] == args.geometry
                and ((r["kind"] == "muons") == (args.population == "muons"))]
    group = work / "raw" / (args.geometry + "-" + args.population)
    if group.exists():
        raise ValueError("Transport group exists; retain it and choose a fresh work path")
    group.mkdir(parents=True)
    (group / "rng").mkdir()
    macro = group / "commands.mac"
    lines = ["/gun/position 0 0 0 mm"]
    for index, row in enumerate(selected):
        row["path"] = str(group / (row["id"] + ".root"))
        row["actual_run_number"] = index
        row["rng_audit_path"] = str(group / "rng" / (row["id"] + ".json"))
        theta = 2*math.atan(math.exp(-row["eta"]))
        direction = [math.sin(theta)*math.cos(row["phi_rad"]),
                     math.sin(theta)*math.sin(row["phi_rad"]), math.cos(theta)]
        lines.extend(["/ddg4/EDM4hepOutput/Output " + row["path"],
                      "/gun/particle " + row["particle"],
                      f"/gun/momentumAmp {row['energy_GeV']:.17g} GeV",
                      "/gun/direction " + " ".join(format(v, ".17g") for v in direction),
                      "/random/setSeeds " + " ".join(map(str, row["seed_pair"])),
                      "/i118/saveRandomState " + row["rng_audit_path"],
                      f"/run/beamOn {row['requested_events']}"])
    macro.write_text("\n".join(lines) + "\n")
    geom = manifest["geometries"][args.geometry]
    steering = group / "steering.py"
    shutil.copyfile(Path(__file__).with_name("nodd_transport.py"), steering)
    command = [sys.executable, shutil.which("ddsim"), "--compactFile", geom["compact"],
               "--steeringFile", str(steering),
               "--runType", "run", "--enableG4Gun", "--macroFile", str(macro),
               "--numberOfThreads", "1", "--random.seed", "12099999", "--physics.list", "FTFP_BERT",
               "--physics.rangecut", "0.7", "--part.userParticleHandler", "",
               "--outputConfig.forceEDM4HEP", "--outputFile", str(group / "unused.root")]
    if args.population == "muons":
        command.append("--enableDetailedShowerMode")
    environment = os.environ.copy()
    directories = list(dict.fromkeys(str(Path(p).parent) for p in geom["libraries"]))
    for name in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        environment[name] = os.pathsep.join(directories) + os.pathsep + environment.get(name, "")
    environment["I118_TRANSPORT_AUDIT"] = str(group / "native-transport-audit.json")
    shutil.copyfile(__file__, group / "producer.py")
    log = group / "transport.log"
    started = time.monotonic()
    with log.open("w") as stream:
        result = subprocess.run(command, env=environment, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    receipt = dict(exit_code=result.returncode, command=command, elapsed_seconds=time.monotonic()-started,
                   producer_sha256=sha(group / "producer.py"), protocol_sha256=manifest["protocol_sha256"],
                   steering_sha256=sha(steering),
                   manifest_sha256=sha(work / "manifest.json"), macro_sha256=sha(macro), log_sha256=sha(log),
                   detailed_showers=args.population == "muons", samples=[])
    save(group / "execution.json", receipt)
    if result.returncode:
        raise RuntimeError("Transport failed; retained " + str(log))
    if any(message in log.read_text(errors="replace") for message in ("COMMAND NOT FOUND", "Batch is interrupted", "Command aborted")):
        raise RuntimeError("Geant4 macro aborted despite a normal process exit")
    audit_path = group / "native-transport-audit.json"
    audit = json.loads(audit_path.read_text())
    if audit["maximum_abs_magnetic_field_tesla"] != 0 or audit["matched_ECAL_sensitive_step_mm"] != 5.:
        raise RuntimeError("Actual native field/step policy differs from the protocol")
    receipt["native_transport_audit_sha256"] = sha(audit_path)
    if "EventSeeder added" in log.read_text(errors="replace"):
        raise RuntimeError("Unexpected EventSeeder during transport")
    for row in selected:
        rng_path = Path(row["rng_audit_path"])
        rng = json.loads(rng_path.read_text())
        if rng["effective_seed"] != row["seed"]:
            raise RuntimeError("Actual native RNG seed differs from its frozen block seed")
        row["rng_audit_sha256"] = sha(rng_path)
        row["rng_state_sha256"] = sha(str(rng_path) + ".state")
        row["actual_random_engine"] = rng["engine"]
        row.update(sha256=sha(row["path"]), exit_code=0,
                   bytes=Path(row["path"]).stat().st_size,
                   truth=audit_input(row["path"], row, geom["collections"]))
        receipt["samples"].append(row)
        save(group / "execution.json", receipt)
        print(args.geometry, row["id"], row["truth"]["events"], "verified events", flush=True)
    receipt["all_inputs_verified"] = True
    if len({r["rng_state_sha256"] for r in selected}) != len(selected):
        raise RuntimeError("Native macro blocks reused an initial RNG state")
    save(group / "execution.json", receipt)


def index(args):
    work = args.work.resolve()
    manifest = verify(work)
    bind_native(work, manifest)
    indexed = []
    receipts = []
    for geometry in ("nodd", "odd-zero"):
        for population in ("showers", "muons"):
            group = work / "raw" / (geometry + "-" + population)
            receipt = json.loads((group / "execution.json").read_text())
            if receipt["exit_code"] or not receipt.get("all_inputs_verified"):
                raise ValueError("Transport group is failed/incomplete")
            for name, key in (("commands.mac", "macro_sha256"), ("transport.log", "log_sha256"), ("producer.py", "producer_sha256"),
                              ("steering.py", "steering_sha256"),
                              ("native-transport-audit.json", "native_transport_audit_sha256")):
                if sha(group / name) != receipt[key]:
                    raise ValueError("Transport execution artifact changed")
            receipts.append(dict(path=str(group / "execution.json"), sha256=sha(group / "execution.json")))
            for row in receipt["samples"]:
                if sha(row["path"]) != row["sha256"]:
                    raise ValueError("Raw source changed")
                if (sha(row['rng_audit_path']) != row['rng_audit_sha256']
                        or sha(row['rng_audit_path']+'.state') != row['rng_state_sha256']):
                    raise ValueError("Executed RNG audit/state changed")
                indexed.append(row)
    expected = {(r["geometry"], r["id"]): r for r in manifest["samples"]}
    if len(indexed) != len(expected) or len({(r["geometry"], r["id"]) for r in indexed}) != len(indexed):
        raise ValueError("Population inventory changed")
    for row in indexed:
        if any(row[k] != v for k, v in expected[(row["geometry"], row["id"])].items()):
            raise ValueError("Executed population differs from protocol")
    save(work / "samples.json", dict(manifest_sha256=sha(work / "manifest.json"), receipts=receipts, samples=indexed))
    geom = manifest["geometries"]["nodd"]
    save(work / "reference-input.json", dict(geometry_label="LAYOUT-001", compact=dict(path=geom["compact"], sha256=sha(geom["compact"])),
         libraries=[dict(path=p, sha256=sha(p)) for p in geom["libraries"]],
         artifacts=[dict(path=str(work / "manifest.json"), sha256=sha(work / "manifest.json")),
                   dict(path=str(work / "native-pass-binding.json"), sha256=sha(work / "native-pass-binding.json")),
                   dict(path=manifest["native_report_path"], sha256=sha(manifest["native_report_path"])),
                   dict(path=str(work / "samples.json"), sha256=sha(work / "samples.json")), *receipts],
         samples=[dict(id=r["id"], path=r["path"], sha256=r["sha256"], events=r["requested_events"],
                       particle=r["particle"], energy_GeV=r["energy_GeV"], eta=r["eta"], exit_code=r["exit_code"])
                  for r in indexed if r["geometry"] == "nodd"]))
    print("Indexed", len(indexed), "populations;", sum(r["requested_events"] for r in indexed), "events")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["prepare", "run", "index"])
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--nodd-directory", type=Path)
    parser.add_argument("--native-report", type=Path)
    parser.add_argument("--allow-pending-native", action="store_true",
                        help="Freeze inputs and run only independent ODD controls while nODD audit is pending")
    parser.add_argument("--library", type=Path, action="append")
    parser.add_argument("--odd-source", type=Path)
    parser.add_argument("--odd-library", type=Path)
    parser.add_argument("--geometry", choices=["nodd", "odd-zero"])
    parser.add_argument("--population", choices=["showers", "muons"])
    args = parser.parse_args()
    {"prepare": prepare, "run": run, "index": index}[args.stage](args)


if __name__ == "__main__":
    main()
