"""Check saved standalone DES036 muon hits; no response qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(directory, output):
    import ROOT

    ROOT.gROOT.SetBatch(True)
    expected = json.loads((directory / "expected.json").read_text())
    native = json.loads((directory / "native.json").read_text())
    if native["status"] != "PASS" or native["execution"]["expected_sha256"] != sha(directory / "expected.json"):
        raise ValueError("transport fixture must match the passing native inventory")
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
        hits = []
        for hit in getattr(tree, "HCALReadoutHits"):
            cid = int(hit.cellID)
            board = (cid >> 32) & 3
            sensor = (cid >> 34) & 63
            if (cid & 255) != 9 or (cid >> 8) & ((1 << 24) - 1):
                errors.append("wrong system or carrier parent ID")
            if (board, sensor) not in allowed or (cid >> 40) & 3:
                errors.append("invalid module/tile/cell address")
            if float(hit.energy) <= 0:
                errors.append("nonpositive saved energy")
            hits.append({"cell_id": cid, "module": board, "sensor": sensor,
                         "energy_GeV": float(hit.energy),
                         "position_mm": [float(hit.position.x), float(hit.position.y), float(hit.position.z)]})
        if not any(hit["module"] == module for hit in hits):
            errors.append("no positive-energy hit in selected board " + str(module))
        version = re.search(r"Geant4 version Name:\s*(.+)", log)
        events.append({"target_module": module, "events": int(tree.GetEntries()), "saved_hits": hits,
                       "Geant4": version.group(1).strip() if version else None,
                       "root_sha256": sha(stem.with_suffix(".root")), "log_sha256": sha(stem.with_suffix(".log"))})
        file.Close()
    result = {"status": "FAIL" if errors else "PASS", "errors": errors,
              "scope": "Two seeded10GeV mu- standalone geometry/positive-energy/identifier smoke events; no optical, front-end, timing, shower or hadron-collider performance claim.",
              "seed": 42, "physics_list": "FTFP_BERT", "field_T": 0,
              "expected_sha256": sha(directory / "expected.json"),
              "native_sha256": sha(directory / "native.json"), "checker_sha256": sha(__file__),
              "execution": native["execution"], "events": events}
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
