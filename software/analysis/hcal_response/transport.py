"""Standalone HCAL pion raw-deposit PROTOTYPE generation, transport and readback."""
import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import resource
import shutil
import signal
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
COLLECTIONS = {"HCALBarrelHits": 13, "HCALEndcapHits": 14}
MASS_GEV = 0.13957039
ENERGY_GEV = 50.0
LEGACY_DESCRIPTOR = "system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1"
ID_DESCRIPTOR = LEGACY_DESCRIPTOR + ",unit:8"
PARENT_MASK = ((1 << 32)-1) | (255 << 42)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def verify_hashes(directory, hashes):
    for name, digest in hashes.items():
        if Path(name).name != name or sha(Path(directory) / name) != digest:
            raise ValueError("Changed or unsafe artifact: " + name)


def decode_cell(cell):
    if not isinstance(cell, int) or cell < 0 or cell >> 50:
        raise ValueError("Noncanonical HCAL cell ID")
    fields = dict(unit=(cell >> 42) & 255, system=cell & 255, side=(cell >> 8) & 3, sector=(cell >> 10) & 15,
        layer=(cell >> 14) & 63, carrier=(cell >> 20) & 4095,
        module=(cell >> 32) & 3, sensor=(cell >> 34) & 63,
        x=-((cell >> 40) & 1), y=-((cell >> 41) & 1))
    if fields["system"] not in (13, 14) or fields["side"] not in (0, 1, 2) or fields["layer"] >= 60:
        raise ValueError("HCAL system/side/layer outside design")
    if fields["module"] > 1 or fields["sensor"] >= 36 or fields["x"] or fields["y"]:
        raise ValueError("HCAL tile address outside design")
    if fields["system"] == 13 and fields["side"] != 0:
        raise ValueError("HCAL barrel side is not zero")
    if fields["system"] == 14 and fields["side"] not in (1, 2):
        raise ValueError("HCAL endcap side is not signed")
    return fields


def sensitive_count(expected):
    count = expected["raw_sensitive_volumes"] if "raw_sensitive_volumes" in expected else expected["sensitive_tiles"]
    if isinstance(count, dict):
        count = count.get("total", sum(count.values()))
    count = int(count)
    if count <= 0:
        raise ValueError("Expected nonzero sensitive tile population")
    return count


def geometry_units(expected):
    """Normalize modern unit families and the retained unit0 readback format."""
    if "units" in expected:
        return {int(key):value for key,value in expected["units"].items()}
    return {0:dict(channel_map=expected["unit_tile_map"])}


def compile_unit_centers(expected):
    units=geometry_units(expected);result={}
    if 0 not in units:raise ValueError("Original common unit0 is missing")
    for uid,unit in units.items():
        if not 0<=uid<=255 or not 1<=len(unit["channel_map"])<=72:raise ValueError("Physical unit capacity")
        for row in unit["channel_map"]:
            module,sensor=row["module"],row["sensor"];center=row["tile_center_mm"];size=row.get("tile_size_mm")
            key=(uid,module,sensor)
            if type(module)is not int or type(sensor)is not int or not 0<=module<2 or not 0<=sensor<36 or key in result or len(center)!=3 or not all(math.isfinite(x) for x in center):
                raise ValueError("Invalid or duplicate physical channel")
            if "units" in expected and (size is None or len(size)!=3 or not all(math.isfinite(x) and x>0 for x in size)):
                raise ValueError("Explicit positive tile dimensions required")
            result[key]=center
    return result


def checked_direction(eta, phi):
    if eta is None or phi is None or not math.isfinite(eta) or not math.isfinite(phi):
        raise ValueError("Fixed eta and phi must both be finite")
    if not -3 <= eta <= 3 or not -math.pi <= phi < math.pi:
        raise ValueError("Fixed direction outside the declared phase space")
    return float(eta),float(phi)


def prepare(args):
    geometry = args.geometry.resolve()
    expected = load(geometry / "expected.json")
    if "export_sha256" in expected:
        verify_hashes(geometry, expected["export_sha256"])
    if "units" in expected:compile_unit_centers(expected)
    if expected["id_descriptor"] not in (ID_DESCRIPTOR,LEGACY_DESCRIPTOR):
        raise ValueError("Unexpected HCAL ID descriptor")
    tree = ET.parse(geometry / "detector.xml")
    roots = tree.findall("detectors/detector")
    if tree.find("fields") is not None or len(roots) != 2 or {int(d.get("id")) for d in roots} != {13, 14}:
        raise ValueError("Expected exactly HCAL-only roots, no field")
    if {d.get("name") for d in roots} != {"HCALBarrel", "HCALEndcaps"}:
        raise ValueError("Unexpected HCAL detector names")
    if {d.get("readout") for d in roots} != set(COLLECTIONS):
        raise ValueError("Unexpected HCAL readout names")
    if args.events <= 0:
        raise ValueError("Positive event population required")
    role=getattr(args,"sample_role","angular")
    eta=getattr(args,"fixed_eta",None);phi=getattr(args,"fixed_phi",None)
    fixed=eta is not None or phi is not None
    primary_sample=getattr(args,"primary_sample",None)
    direction_receipt=getattr(args,"direction_receipt",None)
    if fixed:
        eta,phi=checked_direction(eta,phi)
        if primary_sample is not None or role not in ("calibration","validation") or direction_receipt is None:
            raise ValueError("Fixed sample requires its own calibration/validation role and frozen direction receipt")
        if args.events!={"calibration":2000,"validation":10000}[role]:
            raise ValueError("Fixed cohort population differs from the prospective protocol")
        direction=load(direction_receipt)
        winner=direction.get("winner",direction.get("direction",{}))
        if abs(float(winner["eta"])-eta)>1e-12 or abs(float(winner["phi_rad"])-phi)>1e-12:
            raise ValueError("Fixed input differs from the frozen geometry-selected winner")
    elif role!="angular" or direction_receipt is not None:
        raise ValueError("Angular sample must not carry a fixed-cohort role/direction")
    old=None
    if primary_sample is not None:
        primary_sample=Path(primary_sample).resolve();old=load(primary_sample/"sample.json")
        verify_hashes(primary_sample,old["hashes"])
        if old["events"]!=args.events or old.get("pdg")!=-211 or old.get("energy_GeV")!=50.:
            raise ValueError("Retained angular primary cohort differs")
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    names = ["detector.xml", "materials.xml", "expected.json", "placements.csv"]
    for name in names:
        shutil.copyfile(geometry / name, out / name)
    if fixed:
        shutil.copyfile(direction_receipt,out/"direction.json");names.append("direction.json")
    momentum = math.sqrt(ENERGY_GEV**2 - MASS_GEV**2)
    if old is not None:
        for name in ("particles.HEPEvt","truth-input.jsonl"):
            shutil.copyfile(primary_sample/name,out/name)
    else:
        rng = random.Random(args.input_seed)
        with (out / "particles.HEPEvt").open("w") as events, (out / "truth-input.jsonl").open("w") as truth:
            for i in range(args.events):
                event_eta,event_phi=(eta,phi) if fixed else (rng.uniform(-3.,3.),rng.uniform(-math.pi,math.pi))
                p = [momentum*math.cos(event_phi)/math.cosh(event_eta),momentum*math.sin(event_phi)/math.cosh(event_eta),momentum*math.tanh(event_eta)]
                events.write("1\n1 -211 0 0 " + " ".join(f"{x:.17g}" for x in p+[MASS_GEV]) + "\n")
                truth.write(json.dumps(dict(event=i,energy_GeV=ENERGY_GEV,eta=event_eta,phi=event_phi,momentum_GeV=p),separators=(",", ":"))+"\n")
    truth_rows=[json.loads(line) for line in (out/"truth-input.jsonl").read_text().splitlines()]
    if len(truth_rows)!=args.events or [r["event"] for r in truth_rows]!=list(range(args.events)):
        raise ValueError("Noncontiguous or incomplete input truth")
    for row in truth_rows:
        checked_direction(row["eta"],row["phi"])
        if not math.isfinite(row["energy_GeV"]) or abs(row["energy_GeV"]-50)>1e-12:
            raise ValueError("Primary cohort does not have fixed total energy50GeV")
    names += ["particles.HEPEvt", "truth-input.jsonl"]
    manifest = dict(status="DRAFT / PROTOTYPE",events=args.events,input_seed=None if fixed else old["input_seed"] if old is not None else args.input_seed,
        sample_id=getattr(args,"sample_id",None) or out.name,sample_role=role,
        expected_transport_seed={"angular":202650001,"calibration":202650102,"validation":202650103}[role],
        pdg=-211,mass_GeV=MASS_GEV,energy_GeV=ENERGY_GEV,
        distributions=dict(total_energy_GeV=50.,eta=eta if fixed else [-3,3],phi_rad=phi if fixed else [-math.pi,math.pi],independent_uniform_angles=not fixed),
        fixed_direction=dict(eta=eta,phi_rad=phi,direction_receipt_sha256=sha(out/"direction.json")) if fixed else None,
        reused_primary_sample_sha256=sha(primary_sample/"sample.json") if old is not None else None,
        geometry_scope="HCAL barrel/endcaps only; no ECAL, tracker, beam pipe, solenoid/field or FCAL",
        collections=COLLECTIONS,expected_raw_sensitive_ids=sensitive_count(expected),
        source_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        source_state=subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).splitlines(),
        geometry_manifest=expected,hashes={name:sha(out/name) for name in names},producer_sha256=sha(__file__))
    save(out/"sample.json",manifest)
    print(f"Prepared {args.events} pi- primaries; role={role}; Etotal=50GeV; {manifest['expected_raw_sensitive_ids']:,} raw sensitive volumes")


def run(args):
    sample = args.sample.resolve(); manifest = load(sample / "sample.json")
    verify_hashes(sample, manifest["hashes"])
    if manifest.get("expected_transport_seed",args.seed)!=args.seed:
        raise ValueError("Transport seed differs from the declared independent cohort")
    if args.skip < 0 or args.events <= 0 or args.threads <= 0 or args.events < args.threads:
        raise ValueError("Invalid run population/workers")
    if args.skip + args.events > manifest["events"]:
        raise ValueError("Requested events exceed input population")
    if not math.isfinite(args.max_step_mm) or args.max_step_mm < 0:
        raise ValueError("Invalid explicit maximum step")
    if not math.isfinite(args.reserve_gib) or args.reserve_gib < 0:
        raise ValueError("Invalid disk reserve")
    reserve = args.reserve_gib * 1024**3
    if shutil.disk_usage(sample).free < reserve:
        raise ValueError("Insufficient disk reserve")
    libs = [args.geometry_library.resolve(), args.audit_library.resolve()]
    library_hashes = {str(p): sha(p) for p in libs}
    executable = shutil.which("ddsim")
    if not executable:
        raise ValueError("DDSim unavailable")
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False); (out / "audit").mkdir()
    env = os.environ.copy()
    env.update(NODD_HCAL_AUDIT=str(out / "audit"), NODD_HCAL_MAX_STEP_MM=format(args.max_step_mm, ".17g"),
        NODD_HCAL_EXPECTED_GEOMETRY=str(sample/"expected.json"),
        NODD_HCAL_GEOMETRY_LIBRARY=str(libs[0]), NODD_HCAL_AUDIT_LIBRARY=str(libs[1]), NODD_HCAL_EXPECTED_RAW_IDS=str(manifest["expected_raw_sensitive_ids"]))
    for name in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[name] = os.pathsep.join([*(str(p.parent) for p in libs), env.get(name, "")])
    steering = Path(__file__).with_name("steering.py")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_state = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    producer_hashes = {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__), steering,
        Path(__file__).with_name("Audit.cpp"), Path(__file__).with_name("CMakeLists.txt")]}
    command = [sys.executable, "-u", executable, "--compactFile", str(sample / "detector.xml"),
        "--steeringFile", str(steering), "--runType", "batch", "--inputFiles", str(sample / "particles.HEPEvt"),
        "--numberOfEvents", str(args.events), "--skipNEvents", str(args.skip), "--numberOfThreads", str(args.threads),
        "--random.seed", str(args.seed), "--random.enableEventSeed", "--physics.list", "FTFP_BERT",
        "--physics.rangecut", "0.7", "--part.userParticleHandler", "", "--outputConfig.forceEDM4HEP",
        "--outputFile", str(out / "events.root")]
    start = time.monotonic(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = datetime.now(timezone.utc).isoformat(); free = shutil.disk_usage(out).free
    common = dict(command=command, started_at=started, events=args.events, skip=args.skip, seed=args.seed,
        threads=args.threads, max_step_mm=args.max_step_mm, reserve_bytes=reserve,
        library_sha256=library_hashes, source_revision=revision, source_state=source_state,
        producer_sha256=producer_hashes)
    save(out / "started.json", dict(common, free_bytes=free))
    disk_abort = False; last_status = start
    with (out / "transport.log").open("w") as log:
        with subprocess.Popen(command, env=env, cwd=out, stdout=log, stderr=subprocess.STDOUT) as child:
            while child.poll() is None:
                if shutil.disk_usage(out).free < reserve:
                    disk_abort = True; child.send_signal(signal.SIGINT)
                if time.monotonic() - last_status >= 30:
                    last_status = time.monotonic()
                    size = (out / "events.root").stat().st_size if (out / "events.root").exists() else 0
                    print(f"HCAL DDSim {args.threads} workers: {last_status-start:.1f}s; ROOT {size/1e6:.1f} MB; free {shutil.disk_usage(out).free/1024**3:.1f} GiB", flush=True)
                time.sleep(1)
            code = child.returncode
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(common, ended_at=datetime.now(timezone.utc).isoformat(), exit_code=code,
        disk_abort=disk_abort, wall_seconds=time.monotonic()-start,
        cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        peak_rss_bytes=after.ru_maxrss*(1 if sys.platform == "darwin" else 1024),
        output_bytes=(out / "events.root").stat().st_size if (out / "events.root").exists() else 0,
        free_bytes_after=shutil.disk_usage(out).free, sample_sha256=sha(sample / "sample.json"),
        steering_sha256=sha(steering), runner_sha256=sha(__file__), ddsim_sha256=sha(executable),
        log_sha256=sha(out / "transport.log"),
        producers_unchanged=all(sha(ROOT/p)==digest for p,digest in producer_hashes.items()),
        libraries_unchanged=all(sha(p)==digest for p,digest in library_hashes.items()),
        maps_audit_sha256=sha(out / "audit/maps-initialized.json") if (out / "audit/maps-initialized.json").exists() else None,
        converted_solids_sha256=sha(out / "audit/converted-solids.json") if (out / "audit/converted-solids.json").exists() else None)
    save(out / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2), flush=True)
    if code or disk_abort or not receipt["producers_unchanged"] or not receipt["libraries_unchanged"]:
        raise RuntimeError("HCAL transport failed; all diagnostics retained")


def audit(args):
    import edm4hep
    import ROOT as PyROOT
    from podio import root_io
    directory = args.run.resolve(); sample = args.sample.resolve()
    receipt = load(directory / "receipt.json"); manifest = load(sample / "sample.json")
    verify_hashes(sample, manifest["hashes"])
    if receipt["exit_code"] or receipt["disk_abort"] or receipt["sample_sha256"] != sha(sample / "sample.json"):
        raise ValueError("Incomplete or changed HCAL transport")
    if receipt["log_sha256"] != sha(directory / "transport.log"):
        raise ValueError("Changed transport log")
    if not receipt["producers_unchanged"] or not receipt["libraries_unchanged"]:
        raise ValueError("Transport producer/library changed")
    log = (directory / "transport.log").read_text()
    if not re.search(r"\bFTFP_BERT\b", log) or not re.search(r"with seed\s+" + str(receipt["seed"]) + r"\b", log):
        raise ValueError("Observed physics/seed missing")
    maps_path = directory / "audit/maps-initialized.json"; maps = load(maps_path)
    if maps["status"] != "PASS" or maps["thread_id"] >= 0 or maps["raw_sensitive_ids"] != manifest["expected_raw_sensitive_ids"] or maps["native_contexts_checked"] != manifest["expected_raw_sensitive_ids"] or receipt["maps_audit_sha256"] != sha(maps_path):
        raise ValueError("Incomplete/changed serial map initialization")
    converted_path = directory / "audit/converted-solids.json"
    converted = load(converted_path)
    expected_active={name for u in geometry_units(manifest["geometry_manifest"]).values() for name in (u.get("active_volume_names",{}).values() if isinstance(u.get("active_volume_names",{}),dict) else u.get("active_volume_names",[]))}
    if converted["status"] != "PASS" or (expected_active and {v["volume"] for v in converted["solids"]}!=expected_active) or any(r["mismatches"] or r["probes"] < 10000 for r in converted["solids"]) or receipt.get("converted_solids_sha256") != sha(converted_path):
        raise ValueError("Converted sensitive solid membership gate failed/changed")
    workers = [load(p) for p in sorted((directory / "audit").glob("worker-*.json"))]
    tids = {w["thread_id"] for w in workers}
    required_tids = set(range(receipt["threads"])) if receipt["threads"] > 1 else {-1}
    if tids != required_tids or len(workers) != receipt["threads"] or sum(w["events"] for w in workers) != receipt["events"]:
        raise ValueError("Incomplete worker population/event count")
    for w in workers:
        if w["status"] != "complete" or w["maximum_abs_magnetic_field_tesla"] != 0 or set(w["sensitive_hcal"]) != {"HCALBarrel", "HCALEndcaps"}:
            raise ValueError("Incomplete HCAL worker audit")
        if not any(r["mm"] == [.7]*4 for r in w["region_cuts"]):
            raise ValueError("Worker range cuts differ")
        for info in w["sensitive_hcal"].values():
            for volume in info["volumes"]:
                if volume["Birks_mm_per_MeV"] != 0 or (receipt["max_step_mm"] > 0 and volume["max_step_mm"] > receipt["max_step_mm"]):
                    raise ValueError("Unexpected worker sensitive response/step")
    observed = {}
    observer_paths = sorted((directory / "audit").glob("events-*.jsonl"))
    for path in observer_paths:
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if record["event"] in observed:
                raise ValueError("Duplicate observed event")
            observed[record["event"]] = record
    required_ids = set(range(receipt["skip"], receipt["skip"]+receipt["events"]))
    if set(observed) != required_ids:
        raise ValueError("Incomplete observer event set")
    with (sample / "placements.csv").open(newline="") as source:
        allowed_parents = {}
        for row in csv.DictReader(source):
            values = {key: int(row[key]) for key in ("system", "side", "sector", "layer", "carrier")}
            parent = values["system"] | values["side"] << 8 | values["sector"] << 10 | values["layer"] << 14 | values["carrier"] << 20 | int(row.get("unit",0)) << 42
            if parent in allowed_parents:
                raise ValueError("Duplicate geometry carrier parent")
            allowed_parents[parent] = ([float(row[k]) for k in ("x_mm", "y_mm", "z_mm")],
                [[float(row[f"a{i}{j}"]) for j in range(3)] for i in range(3)])
    if len(allowed_parents) != manifest["expected_raw_sensitive_ids"]:
        raise ValueError("Placement-table/raw-volume population differs")
    unit_centers = compile_unit_centers(manifest["geometry_manifest"])
    maximum_position_error_mm = 0.
    truth = [json.loads(line) for line in (sample / "truth-input.jsonl").read_text().splitlines()]
    output = directory / "event-summary.jsonl"
    if output.exists():
        raise ValueError("Refusing event-summary overwrite")
    counts = dict.fromkeys(COLLECTIONS, 0); seen = set(); maximum_errors = dict(momentum_GeV=0., energy_GeV=0., eta=0., phi=0.)
    max_closure = dict(step_native_GeV=0., native_saved_GeV=0., saved_layer_GeV=0.)
    with output.open("w") as stream:
        for frame in root_io.Reader(str(directory / "events.root")).get("events"):
            header, = frame.get("EventHeader"); event = int(header.getEventNumber())
            if int(header.getRunNumber()) != 0 or event not in required_ids or event in seen:
                raise ValueError("Unexpected/repeated event identity")
            seen.add(event)
            primary, = [p for p in frame.get("MCParticles") if p.getGeneratorStatus() == 1]
            if primary.getPDG() != -211 or (primary.getVertex().x, primary.getVertex().y, primary.getVertex().z) != (0., 0., 0.):
                raise ValueError("Expected one origin pi- primary")
            p = primary.getMomentum(); momentum = [float(p.x), float(p.y), float(p.z)]
            energy = float(primary.getEnergy()); eta = math.asinh(p.z/math.hypot(p.x,p.y)); phi = math.atan2(p.y,p.x)
            ref = truth[event]
            errors = dict(momentum_GeV=max(abs(a-b) for a,b in zip(momentum,ref["momentum_GeV"])),
                energy_GeV=abs(energy-ref["energy_GeV"]), eta=abs(eta-ref["eta"]),
                phi=abs((phi-ref["phi"]+math.pi)%(2*math.pi)-math.pi))
            if any(errors[k] > (1e-7 if k.endswith("GeV") else 1e-9) for k in errors):
                raise ValueError("Saved primary differs from generated input")
            for k, error in errors.items(): maximum_errors[k] = max(maximum_errors[k], error)
            energies = {}; hitcounts = {}; profile = [0.]*60; cell_records = []
            observation = observed[event]
            for index, (name, system) in enumerate(COLLECTIONS.items()):
                ids = set(); deposits = []
                for hit in frame.get(name):
                    cell = int(hit.getCellID()); deposit = float(hit.getEnergy())
                    fields = decode_cell(cell)
                    if (fields["unit"],fields["module"],fields["sensor"]) not in unit_centers:
                        raise ValueError("Saved cell is absent from its physical unit channel map")
                    if cell & PARENT_MASK not in allowed_parents or cell in ids or fields["system"] != system or not math.isfinite(deposit) or deposit <= 0:
                        raise ValueError("Invalid saved HCAL hit")
                    position = hit.getPosition()
                    if not all(math.isfinite(x) for x in (position.x,position.y,position.z)):
                        raise ValueError("Nonfinite saved HCAL hit position")
                    origin, basis = allowed_parents[cell & PARENT_MASK]
                    local = unit_centers[(fields["unit"],fields["module"],fields["sensor"])]
                    expected_position = [origin[j] + sum(local[i]*basis[i][j] for i in range(3)) for j in range(3)]
                    position_error = max(abs(a-b) for a,b in zip((position.x,position.y,position.z),expected_position))
                    if position_error > .001:
                        raise ValueError("Saved global cell position differs from original physical tile center")
                    maximum_position_error_mm = max(maximum_position_error_mm,position_error)
                    cell_records.append((cell, deposit, float(position.x), float(position.y), float(position.z)))
                    ids.add(cell); deposits.append(deposit); profile[fields["layer"]] += deposit
                energies[name] = math.fsum(deposits); hitcounts[name] = len(ids); counts[name] += len(ids)
                if len(ids) != observation["native_hit_counts"][index] or abs(energies[name]-observation["native_hit_energies_GeV"][index]) > 1e-7+2e-6*energies[name]:
                    raise ValueError("Native/saved HCAL collection closure failed")
            signal = math.fsum(energies.values())
            closures = dict(step_native_GeV=abs(observation["step_energy_GeV"]-observation["native_hit_energy_GeV"]),
                native_saved_GeV=abs(signal-observation["native_hit_energy_GeV"]),
                saved_layer_GeV=max(abs(a-b) for a,b in zip(profile,observation["layer_energies_GeV"])))
            if any(delta > 1e-7+2e-6*signal for delta in closures.values()):
                raise ValueError("Event energy/profile closure failed")
            for key, delta in closures.items(): max_closure[key] = max(max_closure[key], delta)
            stream.write(json.dumps(dict(event=event, energy_GeV=energy, eta=eta, phi=phi,
                signal_GeV=signal, response=signal/energy, energies_GeV=energies, counts=hitcounts,
                cells_sha256=hashlib.sha256(b"".join(struct.pack("<Qdddd", *row) for row in sorted(cell_records))).hexdigest(),
                layer_energies_GeV=profile, terminal_six_fraction=math.fsum(profile[-6:])/signal if signal else 0.,
                observer={key: observation[key] for key in ("step_energy_GeV", "native_hit_energy_GeV",
                    "world_escape_kinetic_GeV", "first_primary_inelastic_position_mm")}), separators=(",", ":")) + "\n")
    if seen != required_ids:
        raise ValueError("Incomplete saved event set")
    file = PyROOT.TFile.Open(str(directory / "events.root"), "READ")
    if not file or file.IsZombie() or file.Get("events").GetEntries() != len(seen):
        raise ValueError("ROOT event count mismatch")
    compression = dict(algorithm=int(file.GetCompressionAlgorithm()), level=int(file.GetCompressionLevel())); file.Close()
    proof = dict(status="PASS", events=len(seen), event_ids=dict(min=min(seen),max=max(seen)),
        identity_order="Primary IDs checked; output ordering unrestricted", cells_by_collection=counts,
        maximum_input_errors=maximum_errors, maximum_energy_closure_GeV=max_closure,
        maximum_saved_position_error_mm=maximum_position_error_mm, position_tolerance_mm=.001,
        position_check="Every saved hit versus original physical tile center transformed by exported carrier world pose; tolerance covers persisted float32 rounding",
        compression=compression, root_sha256=sha(directory / "events.root"),
        event_summary_sha256=sha(output), receipt_sha256=sha(directory / "receipt.json"),
        audit_sha256=sha(__file__), transport_runner_sha256=receipt["runner_sha256"],
        auditor_matches_launch_source=sha(__file__)==receipt["runner_sha256"],
        sample=manifest, workers=workers, maps_audit=maps, converted_solids_audit=converted,
        worker_audit_sha256={p.name: sha(p) for p in sorted((directory / "audit").glob("worker-*.json"))},
        observer_sha256={p.name: sha(p) for p in observer_paths},
        leakage_scope="World-boundary escaped kinetic energy; not total-energy balance or local HCAL-boundary leakage")
    save(directory / "readback.json", proof)
    print(json.dumps({k:v for k,v in proof.items() if k not in ("workers","sample")}, indent=2))


def compare(args):
    """Compare exact persisted per-event cell IDs, energies and positions."""
    samples = []
    for directory in (args.first,args.second):
        proof = load(directory / "readback.json")
        if proof["status"] != "PASS" or proof["event_summary_sha256"] != sha(directory / "event-summary.jsonl"):
            raise ValueError("Comparison requires an unchanged audited event ledger")
        samples.append({r["event"]: r for r in [json.loads(l) for l in (directory / "event-summary.jsonl").read_text().splitlines()]})
    if set(samples[0]) != set(samples[1]): raise ValueError("Comparison event sets differ")
    changed = [event for event in samples[0] if samples[0][event]["cells_sha256"] != samples[1][event]["cells_sha256"]]
    result = dict(status="PASS" if not changed else "FAIL", events=len(samples[0]),
        mismatched_events=changed,scope="Exact saved cellID, deposit and global position bits, by primary ID",
        source_readback_sha256=[sha(d/"readback.json") for d in (args.first,args.second)])
    if args.output: save(args.output,result)
    print(json.dumps(result,indent=2))
    if changed: raise ValueError("Serial/MT saved cells differ")


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="stage", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--geometry",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    p.add_argument("--events",type=int,default=10000); p.add_argument("--input-seed",type=int,default=20261120)
    p.add_argument("--fixed-eta",type=float);p.add_argument("--fixed-phi",type=float)
    p.add_argument("--primary-sample",type=Path);p.add_argument("--direction-receipt",type=Path)
    p.add_argument("--sample-role",choices=("angular","calibration","validation"),default="angular");p.add_argument("--sample-id")
    p = sub.add_parser("run")
    for name in ("sample","output","geometry-library","audit-library"): p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--events",type=int,default=10000); p.add_argument("--skip",type=int,default=0); p.add_argument("--threads",type=int,default=12)
    p.add_argument("--seed",type=int,default=202650001); p.add_argument("--reserve-gib",type=float,default=30.); p.add_argument("--max-step-mm",type=float,default=5.)
    p = sub.add_parser("audit"); p.add_argument("--sample",type=Path,required=True); p.add_argument("--run",type=Path,required=True)
    p = sub.add_parser("compare"); p.add_argument("--first",type=Path,required=True); p.add_argument("--second",type=Path,required=True); p.add_argument("--output",type=Path)
    args = parser.parse_args(); globals()[args.stage](args)

if __name__ == "__main__": main()
