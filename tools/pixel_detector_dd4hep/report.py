#!/usr/bin/env python3
"""Retain compact, native-construction and portable-display validation evidence."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build", type=Path, default=ROOT / "build/dd4hep")
    p.add_argument(
        "--display", type=Path, default=ROOT / "build/nodehammer/pixel-detector"
    )
    p.add_argument("--output", type=Path, default=ROOT / "docs/validation/DES-015")
    a = p.parse_args()
    out = a.output
    out.mkdir(parents=True, exist_ok=True)
    native = read(a.build / "detector/pixel-detector-validation.json")
    expected = read(a.build / "detector/pixel-detector/expected.json")
    display = read(a.display / "report.json")
    workflow = read(a.build / "pixel-workflow.json")
    if native["status"] != "PASS" or workflow["status"] != "PASS":
        raise ValueError("Cannot publish passing evidence from failed workflow")
    barrel = read(a.build / "detector/pixel-detector/barrel/expected.json")
    names = {e["name"] for e in barrel["entities"]}
    masses = defaultdict(float)
    roles = defaultdict(float)
    for e in expected["entities"]:
        if "mass_g" not in e:
            continue
        group = (
            "barrel"
            if e["name"] in names
            else "endcap_negative" if e["center_mm"][2] < 0 else "endcap_positive"
        )
        masses[group] += e["mass_g"]
        roles[e["role"]] += e["mass_g"]
    localroles = {
        "disc_support",
        "disc_mount",
        "pickup",
        "disc_foot",
        "cooling_tube",
        "coolant",
        "local_services",
    }
    local = sum(
        e.get("mass_g", 0)
        for e in expected["entities"]
        if e["role"] in localroles and 607 < e["center_mm"][2] < 630
    )
    carrier = (roles["carrier"] + roles["rail"]) / 2
    account = expected["service_accounting"]["endcap"]
    reference = account["local_disc_reference"]
    summary = dict(
        status="PASS — construction/display/initialization only; engineering limits remain",
        source_revision=native["commit"],
        baseline=expected["provenance"]["combined_config"],
        counts=native["counts"],
        mass_g=dict(masses),
        total_mass_g=native["mass_g"],
        mass_by_role_g=dict(roles),
        local_disc_passive_g=local,
        pr36_local_disc_passive_g=reference["disc_passive_mass_g"],
        carrier_per_end_g=carrier,
        pr36_additive_carrier_per_end_g=reference["shared_support_per_end_g"],
        flange_necks={
            k: account[k]["flange_necks"] for k in ("transport_N", "transport_P")
        },
        versions=dict(
            DD4hep=native["dd4hep_version"],
            ROOT=native["root_version"],
            nodehammer=display["nodehammer_version"],
        ),
        limitations=[
            "Thermal stress and conservative/stress trunk screens remain failed from PR36.",
            "Rear flange reference packing also fails; effective material cells are not manufactured routes.",
            "Geant4 initialization only, no events, no field definition and no hit/physics validation.",
            "No ACTS conversion/re-evaluation of shifted endcap coverage in this implementation.",
            "Core inserts, radial pipes, coupling hardware and flex routes are inventory-normalized approximations.",
        ],
    )
    write(out / "summary.json", summary)
    for src, name in [
        (a.build / "detector/pixel-detector-validation.json", "native.json"),
        (a.display / "report.json", "nodehammer.json"),
        (a.build / "pixel-workflow.json", "workflow.json"),
        (a.build / "detector/pixel-detector/manifest.json", "manifest.json"),
        (
            a.build / "detector/pixel-detector/service-accounting.json",
            "service-accounting.json",
        ),
    ]:
        shutil.copyfile(src, out / name)
    write(
        out / "artifacts.json",
        {
            q.name: hashlib.sha256(q.read_bytes()).hexdigest()
            for q in sorted(out.glob("*.json"))
            if q.name != "artifacts.json"
        },
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
