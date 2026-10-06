#!/usr/bin/env python3
"""Deterministic DES015 combined pixel compact; no production ODD mutation."""

from collections import Counter, defaultdict
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/pixel_barrel_dd4hep"))
from export import export as barrel_export, mm, rad, read, sha, write_xml
from materials import Materials

sys.path.insert(0, str(ROOT / "tools/pixel_endcap_support"))
from model import load_inputs, proposal, disc_records, dimensions

from endcap_parts import Parts, volume
from endcap_modules import module_xml
from endcap_services import carrier, transport

TAU = 2 * math.pi
MATERIAL_MAP = {
    "CFRP": "CFRP",
    "foam": "Foam",
    "graphite": "Graphite",
    "insulation": "Polyimide",
    "glue": "Epoxy",
    "titanium": "Titanium",
    "liquid_CO2": "CO2",
    "copper": "Copper",
}


def legacy_export(config, output):
    cfg, layout, inherited = load_inputs(ROOT / config["endcap_inputs"])
    for p, h in config["input_sha256"].items():
        if sha(ROOT / p) != h:
            raise ValueError("Changed preliminary baseline pin: " + p)
    bc = read(ROOT / config["barrel_config"])
    fractions = config["cable_volume_fractions"]
    if (
        set(fractions) != {"Copper", "Polyimide", "Air"}
        or any(not math.isfinite(v) or v < 0 for v in fractions.values())
        or not math.isclose(sum(fractions.values()), 1, abs_tol=1e-12)
    ):
        raise ValueError(
            "Cable volume fractions must be finite, nonnegative and sum to one"
        )
    bc["cable_volume_fractions"] = fractions
    output.mkdir(parents=True, exist_ok=True)
    expected = barrel_export(bc, output / "barrel")
    compact = ET.parse(output / "barrel/pixel-barrel.xml").getroot()
    for axis, size in zip("xyz", config["world_half_size_mm"]):
        compact.find(f"define/constant[@name='world_{axis}']").set("value", mm(size))
    # DDSim's standard MC-truth handler requires the tracker bounding constants.
    for name, value in [
        ("tracker_region_rmax", config["transport"]["rear_r_mm"][1]),
        ("tracker_region_zmax", config["transport"]["rear_turn_abs_z_mm"][1]),
    ]:
        ET.SubElement(compact.find("define"), "constant", name=name, value=mm(value))
    # Copy material table before adding endcap recipes, retaining every barrel recipe.
    mats = Materials(bc, inherited)
    mats.root = ET.parse(output / "barrel/materials.xml").getroot()
    mats.recipes = expected["materials"]
    entities = expected["entities"]
    parts = Parts(entities)
    baseline = read(ROOT / config["screening"])
    budget = baseline["materials_mechanics"]
    components = budget["components"]
    ro = ET.SubElement(compact.find("readouts"), "readout", name="PixelEndcapHits")
    barrelro = compact.find("readouts/readout")
    ro.append(copy.deepcopy(barrelro.find("segmentation")))
    descriptor = "system:5,layer:4,stave:5,module:16,sensor:16,x:-9,y:-9"
    ET.SubElement(ro, "id").text = descriptor
    p = cfg["plate"]
    m = cfg["mounting"]
    c = cfg["cooling"]
    thick, pickup, pitch = dimensions(cfg)
    r0, R = p["r_min_mm"], p["r_max_mm"]
    skin = p["skin_mm"]
    core = p["core_mm"]
    template = proposal(
        [b for b in layout["bodies"] if b["layer_id"] == "A-pixel-P1"], cfg
    )[0]
    radii = [
        sum(math.hypot(*b["center_mm"][:2]) for b in template if b["row"] == i)
        / sum(b["row"] == i for b in template)
        + cfg["foot"]["radial_offset_mm"]
        for i in range(5)
    ]
    ann = math.pi * (R * R - r0 * r0)
    tabarea = volume(
        "tongue",
        dict(
            start=m["tab_start_r_mm"],
            end=m["tab_end_r_mm"],
            width=m["tab_width_mm"],
            radius=R,
            dz=1,
        ),
    )
    faceA = ann + 3 * tabarea
    feetV = (
        sum(b["foot_height_mm"] for b in template)
        * cfg["foot"]["graphite_u_mm"]
        * cfg["foot"]["envelope_v_mm"]
    )
    windowV = (
        len(template)
        * cfg["foot"]["graphite_u_mm"]
        * cfg["foot"]["envelope_v_mm"]
        * skin
    )
    outer = c["tube_OD_mm"] / 2
    inner = outer - c["tube_wall_mm"]
    arcL = TAU * sum(radii)
    arcTi = math.pi * (outer * outer - inner * inner) * arcL
    arcCO2 = math.pi * inner * inner * arcL
    # Disjoint allocation of the published material inventory. Bend allowance is
    # outside the foam in DES014 and stays in the local effective service cell.
    bendL = 4 * len(radii) * c["radial_leg_extra_mm"]
    bendTi = math.pi * (outer * outer - inner * inner) * bendL
    bendCO2 = math.pi * inner * inner * bendL
    core_volumes = {
        "Foam": components[1]["volume_mm3"],
        "Graphite": components[2]["volume_mm3"] - feetV - windowV,
        "Epoxy": components[7]["volume_mm3"],
        "Titanium": components[8]["volume_mm3"] - arcTi - bendTi,
        "CO2": components[9]["volume_mm3"] - arcCO2 - bendCO2,
        "CFRP": components[10]["volume_mm3"],
    }
    core_capacity = faceA * core - math.pi * outer * outer * arcL
    skinmat = mats.effective(
        "EC_CFRP_faces",
        {"CFRP": components[0]["volume_mm3"], "Graphite": windowV},
        2 * faceA * skin,
    )
    coremat = mats.effective("EC_Foam_core", core_volumes, core_capacity)
    fullpickupA = sum(4 * b["half_u_mm"] * b["half_v_mm"] for b in template)
    cradle = mats.effective(
        "EC_CFRP_cradle",
        {"CFRP": components[4]["volume_mm3"]},
        fullpickupA * cfg["pickup"]["cradle_mm"],
    )
    local_v = {
        "Titanium": bendTi + components[12]["volume_mm3"],
        "CO2": bendCO2,
        "CFRP": components[11]["volume_mm3"],
    }
    flexV = components[14]["volume_mm3"] / cfg["flex"]["copper_volume_fraction"]
    for mat, f in fractions.items():
        local_v[mat] = local_v.get(mat, 0) + flexV * f
    serviceLo, serviceHi = config["local_service_w_mm"]
    localcap = ann * (serviceHi - serviceLo)
    localmat = mats.effective("EC_Service_local", local_v, localcap)
    accounting = {
        "local_disc_reference": budget,
        "effective_allocations": {
            skinmat: mats.recipes[skinmat],
            coremat: mats.recipes[coremat],
            cradle: mats.recipes[cradle],
            localmat: mats.recipes[localmat],
        },
        "notes": [
            "Effective core smears thermal inserts, edge closeouts and in-core radial legs; explicit tori displace it.",
            "Local service cell smears clips, mounting hardware, bend allowances and two-face flex inventory.",
            "Full tori preserve summed half-ring length, not hydraulic circuit connectivity.",
        ],
    }
    ps = defaultdict(list)
    for patch in layout["modules"]:
        if patch["subsystem"] == "pixel" and patch["region"] == "endcap":
            ps[patch["module_id"]].append(patch)
    models = read(ROOT / "tools/module_layout/review_models.json")["pixel"]
    discs = disc_records(layout, cfg)
    for side, system, sideName in [(-1, 2, "N"), (1, 3, "P")]:
        det = ET.SubElement(
            compact.find("detectors"),
            "detector",
            id=str(system),
            name="PixelEndcap" + sideName,
            type="nODDPixelEndcap",
            readout="PixelEndcapHits",
        )
        ET.SubElement(det, "sensitive", type="tracker")
        ds = sorted(
            [d for d in discs if d["side"] == side],
            key=lambda d: abs(d["proposed_z_mm"]),
        )
        for di, d in enumerate(ds, 1):
            name = f"disc{sideName}{di}"
            datum = d["proposed_z_mm"]
            dx = ET.SubElement(det, "disc", id=str(di), name=name, z=mm(datum))
            entities.append(dict(name=name, role="disc", center_mm=[0, 0, datum]))
            profile = [
                ("core", core, 0, coremat),
                ("skin_front", skin, -(core + skin) / 2, skinmat),
                ("skin_back", skin, (core + skin) / 2, skinmat),
            ]
            for label, t, w, mat in profile:
                plate = parts.add(
                    dx,
                    name + "_" + label,
                    "sector",
                    mat,
                    "disc_support",
                    center=(0, 0, side * w),
                    datum=datum,
                    rmin=r0,
                    rmax=R,
                    dz=t,
                    angle=TAU,
                )
                if label == "core":
                    for row, r in enumerate(radii):
                        tube = parts.add(
                            plate,
                            f"{name}_evaporator{row}",
                            "torus",
                            "Titanium",
                            "cooling_tube",
                            center=(0, 0, side * c["routing_planes_mm"][0]),
                            radius=r,
                            rmin=0,
                            rmax=outer,
                        )
                        parts.add(
                            tube,
                            f"{name}_coolant{row}",
                            "torus",
                            "CO2",
                            "coolant",
                            radius=r,
                            rmin=0,
                            rmax=inner,
                        )
                for ti, angle in enumerate(m["angles_deg"]):
                    phi = math.radians(angle)
                    radius = (m["tab_start_r_mm"] + m["tab_end_r_mm"]) / 2
                    parts.add(
                        dx,
                        f"{name}_tongue{ti}_{label}",
                        "tongue",
                        mat,
                        "disc_mount",
                        center=(
                            radius * math.cos(phi),
                            radius * math.sin(phi),
                            side * w,
                        ),
                        rotation=(0, 0, phi),
                        datum=datum,
                        start=m["tab_start_r_mm"],
                        end=m["tab_end_r_mm"],
                        width=m["tab_width_mm"],
                        radius=R,
                        dz=t,
                    )
            bodies = proposal(
                [b for b in layout["bodies"] if b["layer_id"] == d["layer"]], cfg
            )[0]
            for b in bodies:
                module_xml(
                    dx,
                    b,
                    ps[b["module_id"]],
                    models,
                    bc["module"],
                    entities,
                    system,
                    di,
                    side,
                    datum,
                )
                face = b["mount_face"]
                h = b["foot_height_mm"]
                phi = math.atan2(b["u"][1], b["u"][0])
                x, y = b["center_mm"][:2]
                basew = face * (thick / 2 + h)
                w = basew
                for label, mat in [
                    ("cradle", cradle),
                    ("graphite", "Graphite"),
                    ("insulation", "Polyimide"),
                    ("TIM", "Epoxy"),
                    ("bond", "Epoxy"),
                ]:
                    t = cfg["pickup"][label + "_mm"]
                    parts.add(
                        dx,
                        f"m{b['module_id']}_pickup_{label}",
                        "box",
                        mat,
                        "pickup",
                        center=(x, y, side * (w + face * t / 2)),
                        rotation=(0, 0, phi),
                        datum=datum,
                        dx=2 * b["half_u_mm"],
                        dy=2 * b["half_v_mm"],
                        dz=t,
                    )
                    w += face * t
                if h:
                    fx = x - cfg["foot"]["radial_offset_mm"] * b["v"][0]
                    fy = y - cfg["foot"]["radial_offset_mm"] * b["v"][1]
                    parts.add(
                        dx,
                        f"m{b['module_id']}_raised_foot",
                        "box",
                        "Graphite",
                        "disc_foot",
                        center=(fx, fy, side * face * (thick / 2 + h / 2)),
                        rotation=(0, 0, phi),
                        datum=datum,
                        dx=cfg["foot"]["graphite_u_mm"],
                        dy=cfg["foot"]["envelope_v_mm"],
                        dz=h,
                    )
            parts.add(
                dx,
                name + "_local_services",
                "sector",
                localmat,
                "local_services",
                center=(0, 0, side * (serviceLo + serviceHi) / 2),
                datum=datum,
                rmin=r0,
                rmax=R,
                dz=serviceHi - serviceLo,
                angle=TAU,
            )
        carrier(parts, det, cfg, side, sideName, ds)
        accounting["transport_" + sideName] = transport(
            parts, det, mats, cfg, config, baseline, bc, side, sideName, ds
        )
    targets = defaultdict(lambda: dict(volume_mm3=0.0, mass_g=0.0))
    for e in entities:
        if "material" not in e:
            continue
        e["mass_g"] = (
            e["volume_mm3"] * mats.recipes[e["material"]]["density_g_cm3"] / 1000
        )
        for k in targets[e["material"]]:
            targets[e["material"]][k] += e[k]
    expected.update(
        status="PROTOTYPE; human-selected preliminary baseline DES015",
        counts=dict(Counter(e["role"] for e in entities)),
        materials=mats.recipes,
        material_totals=dict(targets),
        detector_names=["PixelBarrel", "PixelEndcapN", "PixelEndcapP"],
        readouts_by_system={
            "1": "PixelBarrelHits",
            "2": "PixelEndcapHits",
            "3": "PixelEndcapHits",
        },
        endcap_id_descriptor=descriptor,
        service_accounting=dict(expected["service_accounting"], endcap=accounting),
    )
    expected["provenance"]["combined_config"] = config
    expected["provenance"]["combined_source_sha256"] = {
        str(p.relative_to(ROOT)): sha(p)
        for p in sorted((ROOT / "tools/pixel_detector_dd4hep").glob("*.py"))
    }
    expected["provenance"]["endcap_factory_sha256"] = {
        str(p.relative_to(ROOT)): sha(p)
        for p in sorted((ROOT / "detector/src").glob("PixelEndcap*.cpp"))
    }
    write_xml(output / "materials.xml", mats.root)
    write_xml(output / "pixel-detector.xml", compact)
    for name, data in [
        ("expected", expected),
        ("config", config),
        ("service-accounting", accounting),
    ]:
        (output / (name + ".json")).write_text(json.dumps(data, indent=2) + "\n")
    (output / "manifest.json").write_text(
        json.dumps(
            dict(
                provenance=expected["provenance"],
                artifacts_sha256={
                    p.name: sha(p)
                    for p in output.iterdir()
                    if p.is_file() and p.name != "manifest.json"
                },
            ),
            indent=2,
        )
        + "\n"
    )
    return expected


def export(config, output):
    if config.get("endcap_variant") == "DES018-trimmed-mixed":
        from trimmed_export import export as trimmed_export

        return trimmed_export(config, output)
    return legacy_export(config, output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--config",
        type=Path,
        default=ROOT / "detector/config/pixel-detector-trimmed.json",
    )
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = export(read(a.config), a.output)
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
