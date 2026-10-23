#!/usr/bin/env python3
"""Account for every generated probe and reconstruct native sensitive crossings."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def complete_order(events, tracks, expected, label):
    """One probe per event prevents survivor renumbering from hiding failures."""
    keys = [(int(event), int(track)) for event, track in zip(events, tracks)]
    counts = Counter(keys)
    wanted = {(event, 0) for event in range(expected)}
    missing = sorted(wanted - counts.keys())
    extra = sorted(counts.keys() - wanted)
    duplicated = sorted(key for key, count in counts.items() if count != 1)
    if missing or extra or duplicated or len(keys) != expected:
        raise ValueError(f"{label}: incomplete probe identities: missing={missing[:12]}, "
                         f"extra={extra[:12]}, duplicated={duplicated[:12]}")
    return sorted(range(expected), key=lambda i: keys[i])


def geometry_id(volume, boundary, layer, approach, sensitive, extra):
    # Preserve all 64 bits; a float conversion would lose native identity bits.
    return ((int(volume) << 56) | (int(boundary) << 48) | (int(layer) << 36)
            | (int(approach) << 28) | (int(sensitive) << 8) | int(extra))


def count_systems(steps, source_system):
    counts = [0] * 7
    identifiers = []
    names = ("volume_id", "boundary_id", "layer_id", "approach_id", "sensitive_id", "extra_id")
    for fields in zip(*(steps[name] for name in names)):
        if int(fields[4]) == 0:
            continue
        identifier = geometry_id(*fields)
        if identifier not in source_system:
            raise ValueError(f"sensitive geometry identifier absent from DD4hep source: {identifier}")
        system = source_system[identifier]
        if system not in range(1, 8):
            raise ValueError(f"unexpected native tracker system {system}")
        counts[system - 1] += 1
        identifiers.append(identifier)
    return counts, len(identifiers) - len(set(identifiers))


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def extract(directory):
    import awkward as ak
    import numpy as np
    import uproot
    report_path = directory / "run.json"
    report = json.loads(report_path.read_text())
    config = report["configuration"]
    expected = config["tracks"]
    try:
        with uproot.open(directory / "particles.root") as root:
            particles = root["particles"].arrays(library="ak")
        with uproot.open(directory / "summary.root") as root:
            summary = root["propagation_summary"].arrays(library="ak")
        with uproot.open(directory / "steps.root") as root:
            steps = root["propagation_steps"].arrays(library="ak")
        orders = [complete_order(summary.event_nr, summary.track_nr, expected, "summary"),
                  complete_order(steps.event_nr, steps.track_nr, expected, "steps")]
        generated_order = complete_order(particles.event_id, [0] * len(particles), expected, "generated")
        source = json.loads((directory / "surfaces.json").read_text())["sensors"]
        source_system = {s["geometry_id"]: s["ids"]["system"] for s in source}
        if len(source_system) != len(source):
            raise ValueError("duplicate sensitive identifiers in the DD4hep conversion")
        rows, generated, repeated = [], [], []
        max_r = max_z = 0.
        for event, (gi, si, ti) in enumerate(zip(generated_order, *orders)):
            p, s, t = particles[gi], summary[si], steps[ti]
            if len(p.px) != 1:
                raise ValueError(f"event {event}: expected exactly one generated particle")
            truth = {name: float(p[name][0]) for name in ("px", "py", "pz", "q", "eta", "phi", "vx", "vy", "vz")}
            if not np.isfinite(list(truth.values())).all():
                raise ValueError(f"event {event}: nonfinite generated kinematics")
            pt = float(np.hypot(truth["px"], truth["py"]))
            eta = float(np.arcsinh(truth["pz"] / pt))
            phi = float(np.arctan2(truth["py"], truth["px"]))
            if not np.isclose(pt, config["pt_GeV"], rtol=1e-6, atol=0):
                raise ValueError(f"event {event}: generated pT differs from requested pT")
            if truth["q"] not in (-1, 1) or abs(int(p.particle_type[0])) != 13:
                raise ValueError(f"event {event}: expected a charged muon")
            if any(truth[name] != 0 for name in ("vx", "vy", "vz")):
                raise ValueError(f"event {event}: nonzero origin vertex")
            if not config["eta_range"][0] <= eta <= config["eta_range"][1]:
                raise ValueError(f"event {event}: generated eta outside requested interval")
            for record in (s, t):
                for name, value in (("pt", pt), ("eta", eta), ("phi", phi)):
                    if not np.isclose(float(record[name]), value, rtol=1e-6, atol=1e-6):
                        raise ValueError(f"event {event}: generated and propagated {name} disagree")
                if np.sign(float(record.qOverP)) != truth["q"]:
                    raise ValueError(f"event {event}: propagated charge differs from generated charge")
            split, repeats = count_systems(ak.to_list(t), source_system)
            if sum(split) != int(s.nSensitives):
                raise ValueError(f"event {event}: native summary and source-matched step counts disagree")
            if repeats:
                repeated.append({"event_nr": event, "repeat_crossings": repeats})
            if len(t.g_r):
                max_r = max(max_r, float(ak.max(t.g_r)))
                max_z = max(max_z, float(ak.max(abs(t.g_z))))
            row = {"event_nr": event, "track_nr": 0, "eta": eta, "phi": phi,
                   "pt_GeV": pt, "charge": int(truth["q"]), "nSensitives": sum(split)}
            row.update({f"nSensitives_system{i}": split[i - 1] for i in range(1, 8)})
            row["pathLength_mm"] = float(s.pathLength)
            rows.append(row)
            generated.append({"event_nr": event, **truth, "pt_GeV": pt})
        field = report["field_report"]["configuration"]
        margin = config["maximum_step_mm"]
        if max_r + margin >= field["r_max_mm"] or max_z + margin >= field["z_max_mm"]:
            raise ValueError("recorded trajectory plus one full integration step exceeds field-map support")
        write_csv(directory / "counts.csv", rows)
        write_csv(directory / "generated.csv", generated)
        accounting = {
            "generated": len(particles), "summary": len(summary), "steps": len(steps),
            "matched_unique_probes": len(rows), "missing_probes": 0, "duplicated_probe_ids": 0,
            "summary_step_source_count_mismatches": 0,
            "zero_sensitive_probes": sum(row["nSensitives"] == 0 for row in rows),
            "repeated_sensitive_crossings": repeated,
            "max_recorded_r_mm": max_r, "max_recorded_abs_z_mm": max_z,
            "field_support_margin_mm": margin,
            "charge_counts": dict(Counter(str(row["charge"]) for row in rows)),
            "max_attempted_steps": int(ak.max(summary.nAttemptedSteps)),
            "max_rejected_steps": int(ak.max(summary.nRejectedSteps)),
            "max_reverse_steps": int(ak.max(summary.nReverseSteps)),
            "max_path_length_mm": max(row["pathLength_mm"] for row in rows),
        }
        report.update(status="PASS", accounting=accounting,
                      accounting_script_sha256=sha256(__file__),
                      artifact_sha256={name: sha256(directory / name) for name in
                                       ("particles.root", "summary.root", "steps.root", "surfaces.json", "counts.csv", "generated.csv")})
    except Exception as error:
        report.update(status="FAIL", accounting_error=str(error))
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        raise
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: all {expected} generated probes, source-matched sensitive counts, pT and map support")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    extract(parser.parse_args().directory)
