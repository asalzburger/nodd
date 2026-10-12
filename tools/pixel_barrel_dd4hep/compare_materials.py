#!/usr/bin/env python3
"""Compare low/nominal/high copper DD4hep reports without moving geometry."""

import argparse
import hashlib
import json
from pathlib import Path


def compare(paths):
    reports = [json.loads(path.read_text()) for path in paths]
    low, nominal, high = reports
    for report in reports:
        if report["status"] != "PASS":
            raise ValueError("Every input must be a successful geometry validation")
        for key in ("compact_sha256", "counts", "packed_identifiers"):
            if report[key] != nominal[key]:
                raise ValueError("Geometry or identifiers differ: " + key)
        if len(report["navigation"]) != len(nominal["navigation"]):
            raise ValueError("Navigation samples differ")
        for actual, reference in zip(report["navigation"], nominal["navigation"]):
            for key in (
                "origin_mm",
                "direction",
                "sensitive_crossings",
                "hits_by_layer",
                "material_path_mm",
            ):
                if actual[key] != reference[key]:
                    raise ValueError("Navigation geometry differs: " + key)
        for name, material in report["materials"].items():
            if (
                not name.startswith(("CableMix_", "end_"))
                and material != nominal["materials"][name]
            ):
                raise ValueError("Non-cable material changed: " + name)
    if not low["mass_g"] < nominal["mass_g"] < high["mass_g"]:
        raise ValueError("Total mass does not increase with configured copper")
    for rays in zip(*(report["navigation"] for report in reports)):
        if not rays[0]["x_over_x0"] <= rays[1]["x_over_x0"] <= rays[2]["x_over_x0"]:
            raise ValueError("Radiation-length scan is not monotonic with copper")
    return {
        "status": "PASS",
        "geometry_and_navigation_unchanged": True,
        "non_cable_materials_unchanged": True,
        "copper_response_monotonic": True,
        "runs": [
            dict(
                label=label,
                report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                mass_g=report["mass_g"],
                mean_x_over_x0=sum(r["x_over_x0"] for r in report["navigation"])
                / len(report["navigation"]),
                maximum_x_over_x0=max(r["x_over_x0"] for r in report["navigation"]),
            )
            for label, path, report in zip(("low", "nominal", "high"), paths, reports)
        ],
        "sampling_note": "Unweighted 75-ray navigation sample; not an angular average or hermeticity measure.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--low", type=Path, required=True)
    parser.add_argument("--nominal", type=Path, required=True)
    parser.add_argument("--high", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare([args.low, args.nominal, args.high])
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        "PASS: geometry/IDs/navigation unchanged; only cable-containing materials vary"
    )


if __name__ == "__main__":
    main()
