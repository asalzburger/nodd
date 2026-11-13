"""Matched-primary LAr ECAL raw-deposit PROTOTYPE transport and full readback.

Large ROOT/event ledgers stay local. This does not implement LAr digitization.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
COLLECTIONS = {"LArBarrelHits": 10, "LArEndcapHits": 11}
DETECTORS = {"LArBarrel", "LArEndcaps"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def load(path):
    return json.loads(Path(path).read_text())


def verify_hashes(directory, hashes):
    for name, digest in hashes.items():
        if Path(name).name != name or sha(Path(directory) / name) != digest:
            raise ValueError("Changed or unsafe artifact: " + name)


def ecal_only(tree):
    """Retain the full placed LAr models and services, remove tracker roots only."""
    tree = deepcopy(tree)
    root = tree.getroot()
    if root.find("fields") is not None:
        raise ValueError("Unexpected field configuration")
    detectors = root.find("detectors")
    if detectors is None:
        raise ValueError("Missing detector section")
    retained = []
    for node in list(detectors):
        system = int(node.get("id"))
        if system in COLLECTIONS.values():
            retained.append(node)
        elif 0 <= system <= 7:
            detectors.remove(node)
        else:
            raise ValueError("Unexpected detector root")
    if {int(d.get("id")) for d in retained} != {10, 11} or len(retained) != 2:
        raise ValueError("Need exactly the complete LAr barrel and endcaps")
    if {d.get("name") for d in retained} != DETECTORS:
        raise ValueError("Unexpected LAr detector names")
    names = {d.get("readout") for d in retained}
    if names != set(COLLECTIONS):
        raise ValueError("Unexpected LAr readout names")
    readouts = root.find("readouts")
    for node in list(readouts):
        if node.get("name") not in names:
            readouts.remove(node)
    if len(readouts) != 2:
        raise ValueError("Need exactly two LAr readouts")
    includes = root.findall("includes/gdmlFile")
    if len(includes) != 1 or includes[0].get("ref") != "materials.xml":
        raise ValueError("Unexpected material include")
    return tree


def cell_inventory(root):
    """Read canonical membership from the actual compact segmentation tables."""
    result = {}
    for ro in root.findall("readouts/readout"):
        name = ro.get("name")
        seg = ro.find("segmentation")
        descriptor = ro.findtext("id")
        if name not in COLLECTIONS or not descriptor or seg is None:
            raise ValueError("Missing LAr segmentation")
        item = dict(system=COLLECTIONS[name], descriptor=descriptor)
        if name == "LArBarrelHits":
            values = list(map(float, seg.get("reference_table_mm").split()))
            if len(values) % 5:
                raise ValueError("Bad barrel reference table")
            keys = [[int(values[i]), int(values[i+1])] for i in range(0, len(values), 5)]
            if len({tuple(k) for k in keys}) != len(keys):
                raise ValueError("Duplicate barrel references")
            item.update(planes=int(seg.get("planes")), phi_merge=int(seg.get("phi_merge")), keys=keys)
        else:
            values = list(map(float, seg.get("reference_table_mm").split()))
            wheels = list(map(float, seg.get("wheel_table_mm").split()))
            if len(values) % 6 or len(wheels) != 12:
                raise ValueError("Bad turbine reference/wheel table")
            keys = [[int(values[i]), int(values[i+1]), int(values[i+2])] for i in range(0, len(values), 6)]
            if len({tuple(k) for k in keys}) != len(keys):
                raise ValueError("Duplicate turbine references")
            item.update(wheel_planes=[int(wheels[i+2]) for i in range(0, 12, 4)], keys=keys)
        result[name] = item
    if set(result) != set(COLLECTIONS):
        raise ValueError("Missing readout inventory")
    return result


def decode(cell, descriptor):
    if not isinstance(cell, int) or cell < 0:
        raise ValueError("Invalid cell ID")
    fields = {}; offset = 0
    for field in descriptor.split(","):
        key, count = field.split(":"); count = int(count); bits = abs(count)
        value = (cell >> offset) & ((1 << bits) - 1)
        if count < 0 and value >= (1 << (bits - 1)):
            value -= 1 << bits
        fields[key] = value; offset += bits
    if cell >> offset:
        raise ValueError("Unused/high cell-ID bits")
    return fields


def compile_inventory(inventory):
    return {name: dict(item, key_set={tuple(k) for k in item["keys"]})
            for name, item in inventory.items()}


def validate_cell(cell, name, inventory):
    item = inventory[name]; f = decode(cell, item["descriptor"])
    if f["system"] != item["system"] or f["gap"] != 0:
        raise ValueError("Wrong system or noncanonical gap")
    if name == "LArBarrelHits":
        if (not 0 <= f["plane"] < item["planes"] or
                f["plane"] % item["phi_merge"] or
                (f["layer"], f["theta"]) not in item["key_set"]):
            raise ValueError("Ghost/noncanonical barrel cell")
    else:
        w = f["wheel"]
        if (f["side"] not in (1, 2) or not 0 <= w < 3 or
                not 0 <= f["plane"] < item["wheel_planes"][w] or
                (w, f["rho"], f["z"]) not in item["key_set"]):
            raise ValueError("Ghost/noncanonical turbine cell")
    return f


def prepare(args):
    baseline = args.baseline.resolve(); primary = args.primary_sample.resolve()
    previous = load(primary / "sample.json")
    verify_hashes(primary, {"particles.HEPEvt": previous["input_sha256"],
                            "truth-input.jsonl": previous["truth_sha256"]})
    report = load(baseline / "baseline.json")
    if report["layout"] != "LAYOUT-002":
        raise ValueError("Expected LAr baseline")
    verify_hashes(baseline, {"detector.xml": report["compact_sha256"],
                             "materials.xml": report["materials_sha256"]})
    source_tree = ET.parse(baseline / "detector.xml")
    tree = ecal_only(source_tree)
    # Extraction may remove unrelated roots/readouts only, never alter LAr nodes.
    for source in source_tree.findall("detectors/detector"):
        if int(source.get("id")) in (10, 11):
            dest = next(d for d in tree.findall("detectors/detector") if d.get("id") == source.get("id"))
            if ET.tostring(source) != ET.tostring(dest):
                raise ValueError("LAr physical placement changed in extraction")
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    ET.indent(tree)
    tree.write(out / "detector.xml", encoding="utf-8", xml_declaration=True)
    for name, directory in (("materials.xml", baseline), ("particles.HEPEvt", primary),
                            ("truth-input.jsonl", primary)):
        shutil.copyfile(directory / name, out / name)
    rows = [json.loads(line) for line in (out / "truth-input.jsonl").read_text().splitlines()]
    if len(rows) != previous["events"] or [r["event"] for r in rows] != list(range(len(rows))):
        raise ValueError("Noncontiguous/incomplete primary ledger")
    manifest = dict(status="PROTOTYPE", events=len(rows),
        source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        geometry_scope="Complete LAr barrel/endcaps and local services; ECAL-only B=0; no tracker, solenoid, HCAL or FCAL",
        geometry_extraction="Remove detector roots0-7 and unused readouts only; LAr physical nodes byte-equivalent before serialization",
        distributions=previous["distributions"], input_seed=previous["input_seed"],
        electron_mass_GeV=previous["electron_mass_GeV"],
        source_baseline_sha256=sha(baseline / "baseline.json"),
        source_compact_sha256=sha(baseline / "detector.xml"),
        source_primary_manifest_sha256=sha(primary / "sample.json"),
        source_primary_revision=previous["source_revision"],
        input_sha256=sha(out / "particles.HEPEvt"), truth_sha256=sha(out / "truth-input.jsonl"),
        hashes={name: sha(out / name) for name in ("detector.xml", "materials.xml", "particles.HEPEvt", "truth-input.jsonl")},
        collections=COLLECTIONS, inventory=cell_inventory(tree.getroot()),
        producer_sha256=sha(__file__), source_baseline=report)
    save(out / "sample.json", manifest)
    print(f"Prepared {len(rows)} matched-primary events; two full LAr roots; {out}")


def run(args):
    sample = args.sample.resolve(); manifest = load(sample / "sample.json")
    verify_hashes(sample, manifest["hashes"])
    if args.skip < 0 or args.events <= 0 or args.threads <= 0 or args.events < args.threads:
        raise ValueError("Invalid run population/workers")
    if args.skip + args.events > manifest["events"]:
        raise ValueError("Requested events exceed the matched input population")
    if not math.isfinite(args.max_step_mm) or args.max_step_mm < 0:
        raise ValueError("Invalid explicit maximum step")
    if args.reserve_gib < 0 or not math.isfinite(args.reserve_gib):
        raise ValueError("Invalid disk reserve")
    reserve = args.reserve_gib * 1024**3
    if shutil.disk_usage(sample).free < reserve:
        raise ValueError("Insufficient disk reserve")
    libs = [p.resolve() for p in args.geometry_library]
    if len(libs) != 2 or len(set(libs)) != 2:
        raise ValueError("Two distinct LAr geometry libraries required")
    auditlib = args.audit_library.resolve()
    library_hashes = {str(p): sha(p) for p in [*libs, auditlib]}
    executable = shutil.which("ddsim")
    if not executable:
        raise ValueError("DDSim is unavailable")
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False); (out / "audit").mkdir()
    env = os.environ.copy(); env["NODD_LAR_AUDIT"] = str(out / "audit")
    env["NODD_LAR_MAX_STEP_MM"] = format(args.max_step_mm, ".17g")
    env["NODD_LAR_AUDIT_LIBRARY"] = str(auditlib)
    for name in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[name] = os.pathsep.join([*(str(p.parent) for p in [*libs, auditlib]), env.get(name, "")])
    steering = Path(__file__).with_name("steering.py")
    source_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_state = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    producer_paths = [Path(__file__).with_name(name) for name in
                      ("transport.py", "Audit.cpp", "steering.py", "CMakeLists.txt")]
    producer_hashes = {str(p.relative_to(ROOT)): sha(p) for p in producer_paths}
    command = [sys.executable, "-u", executable, "--compactFile", str(sample / "detector.xml"),
        "--steeringFile", str(steering), "--runType", "batch", "--inputFiles", str(sample / "particles.HEPEvt"),
        "--numberOfEvents", str(args.events), "--skipNEvents", str(args.skip), "--numberOfThreads", str(args.threads),
        "--random.seed", str(args.seed), "--random.enableEventSeed", "--physics.list", "FTFP_BERT",
        "--physics.rangecut", "0.7", "--part.userParticleHandler", "", "--outputConfig.forceEDM4HEP",
        "--outputFile", str(out / "events.root")]
    start = time.monotonic(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = datetime.now(timezone.utc).isoformat(); free = shutil.disk_usage(out).free
    save(out / "started.json", dict(command=command, started_at=started, events=args.events,
        skip=args.skip, seed=args.seed, threads=args.threads, max_step_mm=args.max_step_mm,
        reserve_bytes=reserve, free_bytes=free, library_sha256=library_hashes,
        source_revision=source_revision, source_state=source_state, producer_sha256=producer_hashes))
    disk_abort = False; last_status = start
    with (out / "transport.log").open("w") as log:
        with subprocess.Popen(command, env=env, cwd=out, stdout=log, stderr=subprocess.STDOUT) as child:
            while child.poll() is None:
                if shutil.disk_usage(out).free < reserve:
                    disk_abort = True; child.send_signal(signal.SIGINT)
                if time.monotonic() - last_status >= 30:
                    last_status = time.monotonic()
                    size = (out / "events.root").stat().st_size if (out / "events.root").exists() else 0
                    print(f"LAr DDSim {args.threads} workers: {last_status-start:.1f}s; ROOT {size/1e6:.1f} MB; free {shutil.disk_usage(out).free/1024**3:.1f} GiB", flush=True)
                time.sleep(1)
            code = child.returncode
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(command=command, started_at=started, ended_at=datetime.now(timezone.utc).isoformat(),
        exit_code=code, disk_abort=disk_abort, events=args.events, skip=args.skip, threads=args.threads,
        seed=args.seed, max_step_mm=args.max_step_mm, wall_seconds=time.monotonic()-start,
        cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        peak_rss_bytes=after.ru_maxrss*(1 if sys.platform == "darwin" else 1024),
        output_bytes=(out / "events.root").stat().st_size if (out / "events.root").exists() else 0,
        free_bytes_after=shutil.disk_usage(out).free, sample_sha256=sha(sample / "sample.json"),
        steering_sha256=sha(steering), runner_sha256=sha(__file__), library_sha256=library_hashes,
        ddsim_sha256=sha(executable), log_sha256=sha(out / "transport.log"),
        source_revision=source_revision, source_state=source_state, producer_sha256=producer_hashes,
        producers_unchanged=all(sha(ROOT/p)==digest for p,digest in producer_hashes.items()),
        libraries_unchanged=all(sha(p)==digest for p,digest in library_hashes.items()),
        maps_audit_sha256=sha(out / "audit/maps-initialized.json") if (out / "audit/maps-initialized.json").exists() else None)
    save(out / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2), flush=True)
    if code or disk_abort or not receipt["producers_unchanged"] or not receipt["libraries_unchanged"]:
        raise RuntimeError("LAr transport failed; all diagnostics retained")


def check_workers(workers, receipt):
    tids = {w["thread_id"] for w in workers}
    required = set(range(receipt["threads"])) if receipt["threads"] > 1 else {0}
    # Geant4 serial mode commonly uses -2; accept it only for a one-thread run.
    if receipt["threads"] == 1 and tids == {-2}:
        required = {-2}
    if tids != required or len(workers) != receipt["threads"]:
        raise ValueError("Incomplete worker audit set")
    if sum(w["events"] for w in workers) != receipt["events"]:
        raise ValueError("Worker event totals differ")
    for w in workers:
        if (w["status"] != "complete" or not w.get("maps_initialized_serially") or w["maximum_abs_magnetic_field_tesla"] != 0 or
                set(w["sensitive_lar"]) != DETECTORS or
                w["requested_max_step_mm"] != receipt["max_step_mm"]):
            raise ValueError("Worker physical audit differs")
        if not any(r["mm"] == [.7]*4 for r in w["region_cuts"]):
            raise ValueError("Missing declared production cuts")
        for role in w["sensitive_lar"].values():
            if role["logical_volumes"] != len(role["volumes"]) or role["logical_volumes"] <= 0:
                raise ValueError("Invalid sensitive volume inventory")
            for volume in role["volumes"]:
                if abs(volume["density_g_cm3"]-1.396) > 1e-8 or volume["Birks_mm_per_MeV"] != 0:
                    raise ValueError("Unexpected LAr proxy material response")
                step = volume["max_step_mm"]; native = volume["native_max_step_mm"]
                cap = receipt["max_step_mm"]
                if cap > 0 and (step is None or step <= 0 or step > cap):
                    raise ValueError("Numerical step cap not active")
                if cap == 0 and (step != native or volume["numeric_cap_applied"]):
                    raise ValueError("Native step policy was modified")
    return {str(w["thread_id"]): w["events"] for w in workers}


def audit(args):
    import edm4hep  # noqa: F401; registers EDM dictionaries
    import ROOT as PyROOT
    from podio import root_io
    sample = args.sample.resolve(); run_dir = args.run.resolve()
    manifest = load(sample / "sample.json"); receipt = load(run_dir / "receipt.json")
    verify_hashes(sample, manifest["hashes"])
    if (receipt["exit_code"] != 0 or receipt["disk_abort"] or
            receipt["sample_sha256"] != sha(sample / "sample.json")):
        raise ValueError("Incomplete or changed LAr transport")
    if receipt["log_sha256"] != sha(run_dir / "transport.log"):
        raise ValueError("Transport log changed")
    log = (run_dir / "transport.log").read_text()
    if not re.search(r"\bFTFP_BERT\b", log) or not re.search(r"with seed\s+" + str(receipt["seed"]) + r"\b", log):
        raise ValueError("Observed physics/seed missing")
    maps_path = run_dir / "audit/maps-initialized.json"
    maps = load(maps_path)
    if (maps["status"] != "PASS" or maps["thread_id"] >= 0 or
            maps["raw_sensitive_ids"] != 43648 or maps["native_contexts_checked"] != 43648 or
            receipt.get("maps_audit_sha256") != sha(maps_path)):
        raise ValueError("Incomplete or changed serial map initialization")
    if not receipt.get("producers_unchanged") or not receipt.get("libraries_unchanged"):
        raise ValueError("Run producer/library bytes changed during transport")
    workers = [load(p) for p in sorted((run_dir / "audit").glob("worker-*.json"))]
    worker_events = check_workers(workers, receipt)
    expected = [json.loads(line) for line in (sample / "truth-input.jsonl").read_text().splitlines()]
    required_ids = set(range(receipt["skip"], receipt["skip"]+receipt["events"]))
    inventory = compile_inventory(manifest["inventory"])
    output = run_dir / "event-summary.jsonl"
    if output.exists():
        raise ValueError("Refusing event-summary overwrite")
    maximum_errors = dict(momentum_GeV=0., energy_GeV=0., eta=0., phi=0.)
    counts = dict.fromkeys(COLLECTIONS, 0); seen = set(); occupancy = set()
    with output.open("w") as stream:
        for frame in root_io.Reader(str(run_dir / "events.root")).get("events"):
            header, = frame.get("EventHeader"); event = int(header.getEventNumber())
            if int(header.getRunNumber()) != 0 or event not in required_ids or event in seen:
                raise ValueError("Unexpected/repeated event identity")
            seen.add(event)
            primaries = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
            if len(primaries) != 1 or primaries[0].getPDG() != 11:
                raise ValueError("Not one saved primary electron")
            primary = primaries[0]; v = primary.getVertex()
            if (v.x, v.y, v.z) != (0, 0, 0):
                raise ValueError("Primary is not at origin")
            p = primary.getMomentum(); momentum = [float(p.x), float(p.y), float(p.z)]
            energy = float(primary.getEnergy()); eta = math.asinh(p.z/math.hypot(p.x, p.y)); phi = math.atan2(p.y, p.x)
            ref = expected[event]
            errors = dict(momentum_GeV=max(abs(a-b) for a, b in zip(momentum, ref["momentum_GeV"])),
                energy_GeV=abs(energy-ref["energy_GeV"]), eta=abs(eta-ref["eta"]),
                phi=abs((phi-ref["phi"]+math.pi)%(2*math.pi)-math.pi))
            if any(errors[k] > (1e-7 if k.endswith("GeV") else 1e-9) for k in errors):
                raise ValueError("Saved primary differs from matched input")
            for key, error in errors.items():
                maximum_errors[key] = max(maximum_errors[key], error)
            energies = {}; hits_per_collection = {}; region_energies = {}
            for name in COLLECTIONS:
                ids = set(); deposits = []; regions = {}
                for hit in frame.get(name):
                    cell = int(hit.getCellID()); deposited = float(hit.getEnergy())
                    if cell in ids or not math.isfinite(deposited) or deposited <= 0:
                        raise ValueError("Duplicate/nonpositive/nonfinite LAr hit")
                    fields = validate_cell(cell, name, inventory)
                    position = hit.getPosition()
                    if not all(math.isfinite(x) for x in (position.x, position.y, position.z)):
                        raise ValueError("Nonfinite saved hit position")
                    ids.add(cell); deposits.append(deposited); occupancy.add(cell)
                    region = str(fields["layer"]) if name == "LArBarrelHits" else f"{fields['side']}:{fields['wheel']}"
                    regions.setdefault(region, []).append(deposited)
                energies[name] = math.fsum(deposits); hits_per_collection[name] = len(ids)
                region_energies[name] = {key: math.fsum(values) for key, values in regions.items()}
                counts[name] += len(ids)
            signal = math.fsum(energies.values())
            stream.write(json.dumps(dict(event=event, energy_GeV=energy, eta=eta, phi=phi,
                signal_GeV=signal, response=signal/energy, energies_GeV=energies,
                counts=hits_per_collection, region_energies_GeV=region_energies), separators=(",", ":")) + "\n")
    if seen != required_ids:
        raise ValueError("Incomplete saved event set")
    file = PyROOT.TFile.Open(str(run_dir / "events.root"), "READ")
    if not file or file.IsZombie() or file.Get("events").GetEntries() != len(seen):
        raise ValueError("ROOT event count mismatch")
    compression = dict(algorithm=int(file.GetCompressionAlgorithm()), level=int(file.GetCompressionLevel())); file.Close()
    proof = dict(status="PASS", events=len(seen), event_ids=dict(min=min(seen), max=max(seen)),
        identity_order="Saved event IDs checked; output ordering unrestricted", cells_by_collection=counts,
        unique_occupied_cells=len(occupancy), maximum_input_errors=maximum_errors,
        compression=compression, root_sha256=sha(run_dir / "events.root"),
        event_summary_sha256=sha(output), receipt_sha256=sha(run_dir / "receipt.json"),
        audit_sha256=sha(__file__), sample=manifest, worker_events=worker_events, workers=workers,
        maps_audit=maps, maps_audit_sha256=sha(maps_path),
        worker_audit_sha256={p.name: sha(p) for p in sorted((run_dir / "audit").glob("worker-*.json"))})
    save(run_dir / "readback.json", proof)
    print(json.dumps({k: v for k, v in proof.items() if k not in ("workers", "sample")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="stage", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--baseline", type=Path, required=True); p.add_argument("--primary-sample", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("run")
    for name in ("sample", "output", "audit-library"):
        p.add_argument("--"+name, type=Path, required=True)
    p.add_argument("--geometry-library", type=Path, action="append", required=True)
    p.add_argument("--events", type=int, default=10000); p.add_argument("--skip", type=int, default=0)
    p.add_argument("--threads", type=int, default=12); p.add_argument("--seed", type=int, default=133812341)
    p.add_argument("--reserve-gib", type=float, default=30)
    p.add_argument("--max-step-mm", type=float, default=5., help="Explicit common numeric cap; 0 preserves native limits")
    p = sub.add_parser("audit")
    p.add_argument("--sample", type=Path, required=True); p.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(); globals()[args.stage](args)


if __name__ == "__main__":
    main()
