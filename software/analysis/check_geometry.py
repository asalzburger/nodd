#!/usr/bin/env python3
"""Compare native source identities/frames/bounds with converted ACTS surfaces."""

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pixel_audit", ROOT / "tools/pixel_barrel_dd4hep/validate.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def compare(report, expected):
    source = [e for e in expected["entities"] if e["role"] == "sensitive"]
    result = audit.compare_sensors(report["sensors"], source)
    errors = list(result["errors"])
    geoids = [s["geometry_id"] for s in report["sensors"]]
    if len(set(geoids)) != len(geoids) or 0 in geoids:
        errors.append("ACTS geometry identifiers duplicate or zero")
    if report["generation"] != 3:
        errors.append("Geometry is not Gen3")
    if {s["ids"]["system"] for s in report["sensors"]} != set(range(1, 8)):
        errors.append("Missing tracker subsystem")
    if not report["volumes"] or not all(v["portals"] > 0 for v in report["volumes"]):
        errors.append("Missing Gen3 volume portals")
    portals = report.get("beampipe_portals", [])
    pipe = expected["beam"]["config"]
    if len(portals) != 1:
        errors.append("Expected one cylindrical beryllium pipe portal")
    else:
        p = portals[0]
        for name, value in dict(
            radius_mm=pipe["inner_radius_mm"] + pipe["wall_mm"] / 2,
            half_length_mm=pipe["half_length_mm"],
            thickness_mm=pipe["wall_mm"],
            elemental_Z=4,
        ).items():
            if not math.isclose(p[name], value, abs_tol=1e-6, rel_tol=1e-8):
                errors.append("BeamPipe " + name + " mismatch")
        if not math.isfinite(p["radiation_length_mm"]) or p["radiation_length_mm"] <= 0:
            errors.append("Invalid beryllium radiation length")
    return dict(
        status="PASS" if not errors else "FAIL",
        errors=errors,
        sensitive_comparison=result,
        unique_geometry_ids=len(set(geoids)),
        volumes=len(report["volumes"]),
        beampipe_portals=portals,
        portals_by_volume=report["volumes"],
        systems={
            str(i): sum(s["ids"]["system"] == i for s in report["sensors"])
            for i in range(1, 8)
        },
        limitations=[
            "Comparison verifies source conservation and connected-volume construction; actual propagation checked separately.",
            "Try-all navigation prioritizes correctness, not reconstruction performance; passive material mapping remains incomplete.",
        ],
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for key in ("report", "expected", "output"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    result = compare(
        json.loads(a.report.read_text()), json.loads(a.expected.read_text())
    )
    result["hashes"] = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in dict(
            report=a.report, expected=a.expected, checker=Path(__file__)
        ).items()
    }
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "errors",
                    "unique_geometry_ids",
                    "volumes",
                    "systems",
                )
            }
        )
    )
    sys.exit(bool(result["errors"]))
