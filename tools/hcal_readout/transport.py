"""Check saved standalone DES036 muon hits; no response qualification."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance(directory, expected, native):
    """Bind saved runs to the checked fixture and the actual executed argv.

    Execution metadata is recorded by the runner, not an independent measurement
    of firmware/physics configuration. Saved MC primaries are checked separately.
    """
    if native["status"] != "PASS" or native["execution"]["expected_sha256"] != sha(directory / "expected.json"):
        raise ValueError("transport fixture must match the passing native inventory")
    for name in ("readout.xml", "materials.xml"):
        if expected["export_sha256"][name] != sha(directory / name):
            raise ValueError("changed compact/material export")
        root = ET.parse(directory / name).getroot()
        if any(e.tag.rsplit("}", 1)[-1] == "field" or
               (e.tag.rsplit("}", 1)[-1] == "fields" and len(e)) for e in root.iter()):
            raise ValueError("smoke contract requires no field definition")
    records = json.loads((directory / "smoke-commands.json").read_text())
    if len(records) != 2 or {r["module"] for r in records} != {0, 1}:
        raise ValueError("missing or duplicate simulation jobs")
    for record in records:
        module = record["module"]
        if record["schema_version"] != 1 or record["exit_code"] != 0 or not record.get("finished_at"):
            raise ValueError("incomplete or failed simulation job")
        required = {"expected", "compact", "materials", "library", "ddsim", "runner", "python_executable"}
        if set(record["inputs"]) != required:
            raise ValueError("incomplete simulation input identities")
        for name, item in record["inputs"].items():
            if sha(item["path"]) != item["sha256"]:
                raise ValueError("changed simulation input " + name)
        identities = record["inputs"]
        for name, filename in (("expected", "expected.json"), ("compact", "readout.xml"), ("materials", "materials.xml")):
            if Path(identities[name]["path"]).resolve() != (directory / filename).resolve():
                raise ValueError("simulation used another fixture " + name)
        if (identities["library"]["sha256"] != native["execution"]["library_sha256"] or
                identities["compact"]["sha256"] != native["execution"]["compact_sha256"]):
            raise ValueError("simulation/native input mismatch")
        if Path(record["factory_search_prefix"]).resolve() != Path(identities["library"]["path"]).parent.resolve():
            raise ValueError("simulation factory search mismatch")
        tile = next(p for p in expected["parts"] if p["role"] == "sensitive" and p["module"] == module and p["sensor"] == 0)
        x, y, _ = tile["center_mm"]
        settings = {"events": 1, "particle": "mu-", "gun_energy_argument": "10*GeV",
                    "position_mm": [x, y, -50], "direction": [0, 0, 1], "seed": 42,
                    "physics_list": "FTFP_BERT",
                    "field_definition": "absent from compact; no field CLI override"}
        if record["settings"] != settings:
            raise ValueError("simulation settings outside smoke contract")
        stem = directory / ("module" + str(module) + "-smoke")
        argv = record["command"]
        wanted = [identities["python_executable"]["path"], identities["ddsim"]["path"], "--compactFile", str(directory.resolve() / "readout.xml"),
                  "--runType", "batch", "--numberOfEvents", "1", "--enableGun",
                  "--gun.particle", "mu-", "--gun.energy", "10*GeV",
                  f"--gun.position={x} {y} -50", "--gun.direction", "0 0 1",
                  "--random.seed", "42", "--physics.list", "FTFP_BERT",
                  "--part.userParticleHandler", "", "--outputFile", str(stem.resolve().with_suffix(".root"))]
        if argv != wanted:
            raise ValueError("executed command differs from recorded smoke settings")
        for name, suffix in (("root", ".root"), ("log", ".log")):
            item = record["outputs"][name]
            if Path(item["path"]).resolve() != stem.with_suffix(suffix).resolve() or sha(item["path"]) != item["sha256"]:
                raise ValueError("changed or substituted saved output " + name)
    return records


def positive_finite_hit(energy, position):
    return math.isfinite(energy) and energy > 0 and all(math.isfinite(v) for v in position)


def check(directory, output):
    import ROOT

    ROOT.gROOT.SetBatch(True)
    expected = json.loads((directory / "expected.json").read_text())
    native = json.loads((directory / "native.json").read_text())
    records = provenance(directory, expected, native)
    allowed = {(p["module"], p["sensor"]) for p in expected["parts"] if p["role"] == "sensitive"}
    errors, events = [], []
    for module in (0, 1):
        stem = directory / ("module" + str(module) + "-smoke")
        log = stem.with_suffix(".log").read_text()
        file = ROOT.TFile.Open(str(stem.with_suffix(".root")))
        if not file or file.IsZombie():
            raise ValueError("missing saved ROOT output")
        tree = file.Get("events")
        if not tree or tree.GetEntries() != 1 or "Finished run 0 after 1 events" not in log:
            raise ValueError("incomplete saved event")
        tree.GetEntry(0)
        primaries = []
        for particle in tree.MCParticles:
            if int(particle.generatorStatus) != 1:
                continue
            momentum = [float(particle.momentum.x), float(particle.momentum.y), float(particle.momentum.z)]
            if int(particle.PDG) != 13 or any(not math.isfinite(v) for v in momentum) or any(
                    abs(a - b) > 1e-8 for a, b in zip(momentum, (0, 0, 10))):
                errors.append("saved primary differs from mu- beam momentum contract")
            primaries.append({"PDG": int(particle.PDG), "momentum_GeV": momentum, "mass_GeV": float(particle.mass)})
        if len(primaries) != 1:
            errors.append("expected one saved primary")
        hits = []
        for hit in getattr(tree, "HCALReadoutHits"):
            cid = int(hit.cellID)
            board = (cid >> 32) & 3
            sensor = (cid >> 34) & 63
            if (cid & 255) != 9 or (cid >> 8) & ((1 << 24) - 1):
                errors.append("wrong system or carrier parent ID")
            if (board, sensor) not in allowed or (cid >> 40) & 3:
                errors.append("invalid module/tile/cell address")
            energy = float(hit.energy)
            position = [float(hit.position.x), float(hit.position.y), float(hit.position.z)]
            if not positive_finite_hit(energy, position):
                errors.append("nonpositive/nonfinite saved energy or nonfinite position")
            hits.append({"cell_id": cid, "module": board, "sensor": sensor,
                         "energy_GeV": energy, "position_mm": position})
        if not any(hit["module"] == module for hit in hits):
            errors.append("no positive-energy hit in selected board " + str(module))
        version = re.search(r"Geant4 version Name:\s*(.+)", log)
        record = next(r for r in records if r["module"] == module)
        aliases = {item["path"]: "{" + name + "}" for name, item in (record["inputs"] | record["outputs"]).items()}
        events.append({"target_module": module, "events": int(tree.GetEntries()), "saved_hits": hits,
                       "saved_primaries": primaries, "recorded_settings": record["settings"],
                       "recorded_execution": record["execution"],
                       "executed_argv_with_path_aliases": [aliases.get(arg, arg) for arg in record["command"]],
                       "recorded_python": record["python"], "exit_code": record["exit_code"],
                       "started_at": record["started_at"], "finished_at": record["finished_at"],
                       "input_sha256": {name: item["sha256"] for name, item in record["inputs"].items()},
                       "Geant4": version.group(1).strip() if version else None,
                       "root_sha256": sha(stem.with_suffix(".root")), "log_sha256": sha(stem.with_suffix(".log"))})
        file.Close()
    result = {"status": "FAIL" if errors else "PASS", "errors": errors,
              "scope": "Two standalone mu- geometry/finite-positive-energy/identifier smoke events, gun argument 10*GeV and saved primary momentum 10GeV/c. Execution settings are bound to runner metadata and actual input/output hashes; MC primary is independently inspected. No optical, front-end, timing, shower or hadron-collider performance claim.",
              "metadata_sha256": sha(directory / "smoke-commands.json"),
              "expected_sha256": sha(directory / "expected.json"),
              "native_sha256": sha(directory / "native.json"), "checker_sha256": sha(__file__),
              "native_execution": native["execution"], "events": events}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], len(events), "saved events;", sum(len(e["saved_hits"]) for e in events), "hits")
    return 1 if errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(check(args.directory, args.output))
