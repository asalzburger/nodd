"""Inspect the retained transverse DDSim smoke output (requires uproot).

This verifies saved hits, not detector acceptance or magnetic-field transport.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import uproot


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root, log, native):
    text = log.read_text()
    geometry = json.loads(native.read_text())
    with uproot.open(root) as data:
        events = data["events"]
        fields = ["cellID", "eDep", "pathLength", "position.x", "position.y", "position.z"]
        hits = {
            name: events["ShortStripBarrelHits/ShortStripBarrelHits." + name]
            .array(library="np")[0].tolist()
            for name in fields
        }
        event_count = events.num_entries
    layers = sorted({(cell >> 5) & 7 for cell in hits["cellID"]})
    errors = []
    if event_count != 1:
        errors.append("Expected one saved event")
    if layers != [0, 1, 2, 3]:
        errors.append("Saved hits do not exercise every barrel layer")
    if not all((cell & 31) == 3 for cell in hits["cellID"]):
        errors.append("Unexpected detector system ID")
    if not hits["eDep"] or not all(value > 0 for value in hits["eDep"]):
        errors.append("Expected positive deposited energy in every saved hit")
    if not all(0.19 < value < 0.21 for value in hits["pathLength"]):
        errors.append("Transverse hit path differs from the 0.2 mm sensor fixture")
    if "Finished run 0 after 1 events" not in text:
        errors.append("Missing completed DDSim event evidence")
    if not re.search(r"7952\s+sensitive path entries", text):
        errors.append("Unexpected sensitive-path inventory")
    if "direction:( 1.000  0.000  0.000)" not in text:
        errors.append("This checker expects the transverse gun fixture")
    version = re.search(r"Geant4 version Name:\s*(.+)", text)
    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "scope": "One transverse 10 GeV mu- DDSim event; saved EDM4hep hits inspected",
        "execution": geometry["execution"],
        "input_provenance": geometry["input_provenance"],
        "geant4_version_log": version.group(1).strip() if version else None,
        "physics_list": "FTFP_BERT",
        "random_seed": 42,
        "field_T": 0,
        "events": event_count,
        "sensitive_paths": 7952,
        "saved_hits": len(hits["cellID"]),
        "layers": layers,
        "hit_data": hits,
        "hashes": {
            "root": sha(root), "runtime_log": sha(log),
            "native_report": sha(native), "checker": sha(Path(__file__)),
        },
        "limitations": [
            "No field is defined in this compact; curved coverage is a separate vacuum analytical sample.",
            "One seeded event verifies transport and saved sensitive hits, not physics performance, occupancy or radiation tolerance.",
            "The earlier axial geantino event initialized successfully but did not exercise the barrel.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.root, args.log, args.native)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ["status", "errors", "events", "saved_hits", "layers"]}))
    raise SystemExit(1 if result["errors"] else 0)
