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
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(output["status"], target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    analyze(parser.parse_args().directory)
