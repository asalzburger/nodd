#!/usr/bin/env python3
"""Check saved Gen3 propagation outputs, without inferring acceptance."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys


def check(directory, tracks):
    import uproot

    directory = Path(directory)
    report = json.loads((directory / "surfaces.json").read_text())
    lookup = {s["geometry_id"]: s["ids"]["system"] for s in report["sensors"]}
    systems = Counter()
    errors = []
    with uproot.open(directory / "summary.root") as file:
        tree = file["propagation_summary"]
        summary = tree.arrays(
            ["nSensitives", "nPortals", "nMaterials", "pathLength"], library="np"
        )
        if tree.num_entries != tracks:
            errors.append("Incomplete track summaries")
        for sensitive, portal, material, path in zip(
            *(
                summary[k]
                for k in ("nSensitives", "nPortals", "nMaterials", "pathLength")
            )
        ):
            if (
                min(sensitive, portal, material) <= 0
                or not math.isfinite(path)
                or path <= 0
            ):
                errors.append("Track has invalid crossings or path")
    with uproot.open(directory / "steps.root") as file:
        tree = file["propagation_steps"]
        arrays = tree.arrays(
            [
                "volume_id",
                "boundary_id",
                "layer_id",
                "approach_id",
                "sensitive_id",
                "extra_id",
            ],
            library="ak",
        )
        if tree.num_entries != tracks:
            errors.append("Incomplete saved steps")
        for rows in zip(*(arrays[k] for k in arrays.fields)):
            for v, b, l, a, s, x in zip(*rows):
                if s:
                    # The public ACTS GeometryIdentifier masks: volume8,
                    # boundary8, layer12, approach8, sensitive20, extra8.
                    identifier = (
                        (int(v) << 56)
                        | (int(b) << 48)
                        | (int(l) << 36)
                        | (int(a) << 28)
                        | (int(s) << 8)
                        | int(x)
                    )
                    if identifier not in lookup:
                        errors.append("Navigated sensitive lacks a native source")
                    else:
                        systems[lookup[identifier]] += 1
    if set(systems) != set(range(1, 8)):
        errors.append("Sparse probe did not cross all seven systems")
    return dict(
        status="PASS" if not errors else "FAIL",
        errors=errors,
        seed=42,
        tracks=tracks,
        systems_crossed=dict(sorted(systems.items())),
        minimum_sensitive_crossings=int(min(summary["nSensitives"])),
        maximum_sensitive_crossings=int(max(summary["nSensitives"])),
        minimum_portal_crossings=int(min(summary["nPortals"])),
        minimum_material_crossings=int(min(summary["nMaterials"])),
        minimum_path_mm=float(min(summary["pathLength"])),
        maximum_path_mm=float(max(summary["pathLength"])),
        hashes={
            name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in ("surfaces.json", "steps.root", "summary.root")
        },
        mode="Gen3 Navigator + StraightLineStepper; energy loss/scattering disabled",
        limitations=[
            "128 seeded probes test software navigation; no acceptance, magnetic-field or reconstruction qualification."
        ],
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", type=Path, required=True)
    p.add_argument("--tracks", type=int, default=128)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.tracks <= 0:
        p.error("tracks must be positive")
    result = check(args.directory, args.tracks)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    sys.exit(bool(result["errors"]))
