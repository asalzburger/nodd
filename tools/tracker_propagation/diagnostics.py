#!/usr/bin/env python3
"""Retain per-probe numerical differences and finite-sampling diagnostics."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def table(path):
    import numpy as np
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    return {name: np.array([float(row[name]) for row in rows]) for name in rows[0]}


def summarize(values):
    import numpy as np
    n = len(values)
    return {"entries": n, "mean": float(np.mean(values)) if n else None,
            "standard_error": float(np.std(values) / np.sqrt(n)) if n else None}


def edge_diagnostics(nominal_path, refined_path, changed):
    """Locate changed native crossings and diagnose finite sensor-edge flips."""
    import numpy as np
    import uproot
    sensors = {s["geometry_id"]: s for s in json.loads((nominal_path / "surfaces.json").read_text())["sensors"]}
    names = ("volume_id", "boundary_id", "layer_id", "approach_id", "sensitive_id", "extra_id")
    def crossings(record):
        result = {}
        positions = np.column_stack([np.asarray(record[k]) for k in ("g_x", "g_y", "g_z")])
        for i, fields in enumerate(zip(*(record[k] for k in names))):
            v, b, l, a, s, e = map(int, fields)
            if s:
                result[(v << 56) | (b << 48) | (l << 36) | (a << 28) | (s << 8) | e] = positions[i]
        return result, positions
    def local_edge(sensor, positions):
        center, normal = np.array(sensor["center_mm"]), np.array(sensor["normal"])
        distance = (positions - center) @ normal
        indices = np.flatnonzero(distance[:-1] * distance[1:] <= 0)
        if not len(indices):
            return None
        i = int(indices[0])
        fraction = distance[i] / (distance[i] - distance[i + 1])
        position = positions[i] + fraction * (positions[i + 1] - positions[i])
        local = np.array([sensor["u"], sensor["v"]]) @ (position - center)
        return {"local_uv_mm": local.tolist(),
                "approximate_edge_clearance_mm": float(min(np.array(sensor["size_mm"][:2]) / 2 - abs(local))),
                "interpolation_segment_mm": float(np.linalg.norm(positions[i + 1] - positions[i]))}
    with uproot.open(nominal_path / "steps.root") as a, uproot.open(refined_path / "steps.root") as b:
        nominal = a["propagation_steps"].arrays(library="ak")
        refined = b["propagation_steps"].arrays(library="ak")
    for item in changed:
        i = item["event_nr"]
        left, xyz_left = crossings(nominal[i])
        right, xyz_right = crossings(refined[i])
        common = left.keys() & right.keys()
        item["maximum_common_crossing_shift_mm"] = max(float(np.linalg.norm(left[k] - right[k])) for k in common)
        item["changed_sensors"] = [{"geometry_id": gid, "source_path": sensors[gid]["source_path"],
                                     "system": sensors[gid]["ids"]["system"],
                                     "nominal_crossed": gid in left, "refined_crossed": gid in right,
                                     "nominal_edge_diagnostic": local_edge(sensors[gid], xyz_left),
                                     "refined_edge_diagnostic": local_edge(sensors[gid], xyz_right)}
                                    for gid in sorted(left.keys() ^ right.keys())]


def analyze(directory):
    import numpy as np
    config = json.loads((directory / "study.json").read_text())
    output = {"status": "PASS", "interpretation": "Diagnostics of crossing counts, not tracking performance. Numerical comparisons retain every changed event. Charge, eta and phi splits are descriptive; no exact detector symmetry is assumed.",
              "paired": {}, "sampling": {}, "input_sha256": {}}
    def read(case):
        report = json.loads((case / "run.json").read_text())
        source = case / "counts.csv"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if report["status"] != "PASS" or digest != report["artifact_sha256"]["counts.csv"]:
            raise ValueError(f"unvalidated or changed counts: {case}")
        output["input_sha256"][str(case.relative_to(directory))] = digest
        return table(source)
    for pt in config["pt_GeV"]:
        nominal = read(directory / f"pt_{pt:g}GeV")
        for name in ("half-step", "fine-map"):
            control = read(directory / "controls" / name / f"pt_{pt:g}GeV")
            n = len(control["eta"])
            for key in ("event_nr", "track_nr", "eta", "phi", "charge"):
                np.testing.assert_allclose(nominal[key][:n], control[key], rtol=0, atol=1e-6)
            changed = []
            for i in range(n):
                delta = [int(control[f"nSensitives_system{s}"][i] - nominal[f"nSensitives_system{s}"][i]) for s in range(1, 8)]
                if any(delta):
                    changed.append({"event_nr": i, "eta": float(control["eta"][i]),
                                    "phi": float(control["phi"][i]), "charge": int(control["charge"][i]),
                                    "delta_system1_to_7": delta})
            output["paired"][f"{pt:g}GeV/{name}"] = {"probes": n, "changed_probes": changed}
            if changed:
                output["status"] = "DIFFERENCES_REQUIRE_REVIEW"
                edge_diagnostics(directory / f"pt_{pt:g}GeV",
                                 directory / "controls" / name / f"pt_{pt:g}GeV", changed)
        independent = read(directory / "controls/independent-seed" / f"pt_{pt:g}GeV")
        groups = {}
        for name, systems in (("full_tracker", range(1, 8)), ("pixel", (1, 2, 3)),
                              ("short_strip", (4, 5)), ("long_strip", (6, 7))):
            values = sum(nominal[f"nSensitives_system{s}"] for s in systems)
            other = sum(independent[f"nSensitives_system{s}"] for s in systems)
            groups[name] = {
                "nominal": summarize(values), "independent_seed": summarize(other),
                "charge": {str(q): summarize(values[nominal["charge"] == q]) for q in (-1, 1)},
                "eta_sign": {label: summarize(values[mask]) for label, mask in
                             (("negative", nominal["eta"] < 0), ("positive", nominal["eta"] >= 0))},
                "phi_octants": [summarize(values[(nominal["phi"] >= low) & (nominal["phi"] < high)])
                                 for low, high in zip(np.linspace(-np.pi, np.pi, 9)[:-1], np.linspace(-np.pi, np.pi, 9)[1:])],
            }
        output["sampling"][str(pt)] = groups
    target = directory / "controls/diagnostics.json"
    output["edge_diagnostic_method"] = "Source-local u/v intersection estimated by linear interpolation between adjacent saved steps. Signed clearance is positive inside. This is a diagnostic of an edge flip, not an exact propagated miss distance or a convergence bound."
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(output["status"], target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    analyze(parser.parse_args().directory)
