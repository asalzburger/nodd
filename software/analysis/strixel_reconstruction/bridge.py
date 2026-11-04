#!/usr/bin/env python3
"""Bridge the fresh 0.5 mm cross-check to retained DES041 event subsets."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
POPULATIONS = (("fatras", "muon"), ("fatras", "electron"), ("geant4", "muon"),
               ("geant4", "electron"), ("geant4", "pion"))
PTS = (1, 5, 10, 100)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(reference, fresh):
    """Join by event ID; compare every original retained observable exactly."""
    ids = np.asarray(reference["event"])
    new_ids = np.asarray(fresh["event"])
    if len(set(ids.tolist())) != len(ids) or len(set(new_ids.tolist())) != len(new_ids):
        raise ValueError("Repeated bridge event identity")
    lookup = {int(event): i for i, event in enumerate(ids)}
    if any(int(event) not in lookup for event in new_ids):
        raise ValueError("Fresh bridge event missing from frozen reference")
    indices = np.asarray([lookup[int(event)] for event in new_ids])
    results = {}
    for key in reference:
        if key not in fresh:
            raise ValueError("Frozen retained observable missing in fresh arrays: " + key)
        a, b = np.asarray(reference[key])[indices], np.asarray(fresh[key])
        if a.shape != b.shape:
            raise ValueError("Bridge shape mismatch: " + key)
        equal = (a == b)
        if a.dtype.kind == "f" and b.dtype.kind == "f":
            equal |= np.isnan(a) & np.isnan(b)
        differences = np.asarray(~equal).reshape(len(new_ids), -1).any(axis=1)
        finite = np.isfinite(a) & np.isfinite(b)
        maximum = float(np.max(np.abs(a[finite].astype(float) - b[finite].astype(float)))) if np.any(finite) else None
        results[key] = {"identical": bool(np.all(equal)), "different_events": int(differences.sum()),
                        "maximum_absolute_finite_difference": maximum}
    return {"events_compared": len(new_ids), "all_original_observables_identical": all(x["identical"] for x in results.values()),
            "observables": results}


def bridge(data):
    data = Path(data)
    inventory_path = data / "native-reports.json.gz"
    inventory = json.loads(gzip.decompress(inventory_path.read_bytes()))
    native = {item["case"]: item for item in inventory["reports"]}
    cases = {}
    for simulation, particle in POPULATIONS:
        for pt in PTS:
            case = f"{simulation}-{particle}-pt{pt}-pitch0.5"
            current = data / "cases" / case / "events.npz"
            directory = (ROOT / "docs/validation/tracker-reconstruction/validation/selected" / f"pt{pt}"
                         if (simulation, particle) == ("fatras", "muon") else
                         ROOT / "docs/validation/tracker-reconstruction-species" / simulation / particle / f"pt{pt}")
            old = directory / "events.npz"
            old_summary = directory / "summary.json.gz"
            metadata = json.loads(gzip.decompress(old_summary.read_bytes()))
            with np.load(old, allow_pickle=False) as a, np.load(current, allow_pickle=False) as b:
                result = compare({k: a[k] for k in a.files}, {k: b[k] for k in b.files})
            report = native[case]["report"]
            if metadata["seed"] != report["seed"] or metadata["profile"] != report["profile"]:
                raise ValueError("Reference bridge seed/profile differs: " + case)
            result.update(reference_events=metadata["events"], reference_native_source_revision=metadata["native_source_revision"],
                          reference_summary_sha256=digest(old_summary), reference_events_sha256=digest(old),
                          fresh_events_sha256=digest(current), fresh_native_source_revision=report["source_revision"],
                          seed=report["seed"], profile=report["profile"],
                          old_ambiguity_budget_provably_nonlimiting=report["event_audit"]["old_1000_budget_provably_nonlimiting"]
                          if (simulation, particle) == ("fatras", "muon") else None)
            cases[case] = result
    return {"schema_version": 1, "status": "PASS" if all(x["all_original_observables_identical"] for x in cases.values()) else "DIFFERENCES",
            "scope": "20 fresh 0.5 mm samples joined to the same event IDs in retained 5000-event references; exact original observable and NaN-mask comparison",
            "limitation": "The retained reference has no complete original native-hit payload. This bridge compares all original portable observables; transport pairing across fresh pitches is checked separately.",
            "source_sha256": digest(__file__), "native_inventory_sha256": digest(inventory_path), "cases": cases}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    result = bridge(args.data)
    if args.verify:
        if json.loads(args.output.read_text()) != result:
            raise ValueError("Stored bridge evidence differs from exact replay")
    else:
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(result["status"], len(result["cases"]), "0.5 mm bridge cases")
    if result["status"] != "PASS":
        p.exit(1, "Bridge differences require assessment; no exact reproduction claim\n")


if __name__ == "__main__":
    main()
