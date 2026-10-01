#!/usr/bin/env python3
"""Export a pinned pixel barrel working baseline to a standalone DD4hep compact."""

from collections import Counter, defaultdict
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools/pixel_support"))
from mounting import make_mounts
from outward import load_layout, stave_span
from materials import Materials
from module_geometry import describe, stave_frame


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mm(value):
    return format(value, ".17g") + "*mm"


def rad(value):
    return format(value, ".17g") + "*rad"


def read(path):
    return json.loads(path.read_text())


def write_xml(path, root):
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def export(config, output):
    for name, value in config["input_sha256"].items():
        if sha(ROOT / name) != value:
            raise ValueError("Pinned baseline input changed: " + name)
    fractions = config["cable_volume_fractions"]
    if (
        set(fractions) != {"Copper", "Polyimide", "Air"}
        or any(not math.isfinite(v) or v < 0 for v in fractions.values())
        or not math.isclose(sum(fractions.values()), 1, abs_tol=1e-12)
    ):
        raise ValueError(
            "Cable volume fractions must be finite, nonnegative and sum to one"
        )
    if type(config["system_id"]) is not int or not 0 <= config["system_id"] < 2**5:
        raise ValueError("system_id must fit its unsigned 5-bit field")
    module = config["module"]
    if (
        any(not math.isfinite(v) or v <= 0 for v in module.values())
        or module["flex_copper_coverage"] > 1
    ):
        raise ValueError("Invalid module dimensions or copper coverage")
    support = read(ROOT / config.get("support_config", "tools/pixel_support/inputs.json"))
    mounts = read(ROOT / "tools/pixel_support/mounting.json")
    layout = load_layout(support)
    models = read(ROOT / "tools/module_layout/review_models.json")["pixel"]
    route = read_gzip(
        ROOT / config.get("routing", "docs/validation/DES-002/outward-A-services/routing.json.gz")
    )
    service_summary = read(
        ROOT / config.get("service_summary", "docs/validation/DES-002/outward-A-services/screening.json")
    )
    assembly, boxes, rings, feet, layers = make_mounts(layout, support, mounts)
    materials = Materials(config, support)
    compact = ET.Element("lccdd")
    ET.SubElement(
        compact,
        "info",
        name="nODDPixelBarrel",
        title=f"PR{config['baseline_pr']} pixel barrel prototype",
        author="nODD",
        version="0.1",
        status="prototype",
    )
    includes = ET.SubElement(compact, "includes")
    ET.SubElement(includes, "gdmlFile", ref="materials.xml")
    define = ET.SubElement(compact, "define")
    for axis, value in zip("xyz", config["world_half_size_mm"]):
        ET.SubElement(define, "constant", name="world_" + axis, value=mm(value))
    display = ET.SubElement(compact, "display")
    palette = read(ROOT / "detector/config/display.json")["styles"]
    for name, style in palette.items():
        ET.SubElement(
            define,
            "constant",
            name="nodd_colour_" + name,
            value=str(style["root_color"]),
        )
        ET.SubElement(
            display,
            "vis",
            name=name,
            r=str(style["rgb"][0]),
            g=str(style["rgb"][1]),
            b=str(style["rgb"][2]),
            alpha=str(style["alpha"]),
            showDaughters="true",
            visible="true",
        )
    readouts = ET.SubElement(compact, "readouts")
    ro = ET.SubElement(readouts, "readout", name="PixelBarrelHits")
    ET.SubElement(
        ro,
        "segmentation",
        type="CartesianGridXY",
        grid_size_x=mm(module["pixel_pitch_mm"]),
        grid_size_y=mm(module["pixel_pitch_mm"]),
        offset_x=mm(module["pixel_pitch_mm"] / 2),
        offset_y=mm(module["pixel_pitch_mm"] / 2),
    )
    descriptor = "system:5,layer:3,stave:6,module:16,sensor:16,x:-9,y:-9"
    ET.SubElement(ro, "id").text = descriptor
    detectors = ET.SubElement(compact, "detectors")
    detector = ET.SubElement(
        detectors,
        "detector",
        id=str(config["system_id"]),
        name="PixelBarrel",
        type="nODDPixelBarrel",
        readout="PixelBarrelHits",
    )
    ET.SubElement(detector, "sensitive", type="tracker")
    entities = []
    material_targets = defaultdict(lambda: dict(volume_mm3=0.0, mass_g=0.0))

    def entity(name, role, center, volume=None, material=None, **extra):
        e = dict(name=name, role=role, center_mm=list(center), **extra)
        if volume is not None:
            e.update(
                volume_mm3=volume,
                material=material,
                mass_g=volume * materials.recipes[material]["density_g_cm3"] / 1000,
            )
            material_targets[material]["volume_mm3"] += volume
            material_targets[material]["mass_g"] += e["mass_g"]
        entities.append(e)

    def world(b, u, v, w):
        return [
            b["center_mm"][j] + u * b["u"][j] + v * b["v"][j] + w * b["n"][j]
            for j in range(3)
        ]

    pixel_bodies = [
        b
        for b in layout["bodies"]
        if b["subsystem"] == "pixel" and b["region"] == "barrel"
    ]
    patches = defaultdict(list)
    for p in layout["modules"]:
        if p["subsystem"] == "pixel" and p["region"] == "barrel":
            patches[p["module_id"]].append(p)
    # Fixed readout fields must also represent every pixel, not only VolumeIDs.
    limits = {"module_id": 2**16, "id": 2**16}
    for b in pixel_bodies:
        if not 0 <= b["module_id"] < limits["module_id"] or not 0 <= b["col"] < 2**6:
            raise ValueError(
                "Module or stave identifier exceeds readout field capacity"
            )
        for patch in patches[b["module_id"]]:
            if not 0 <= patch["id"] < limits["id"]:
                raise ValueError("Sensor identifier exceeds readout field capacity")
            # CartesianGridXY rounds position/pitch to the nearest bin centre.
            if (
                max(patch["half_u_mm"], patch["half_v_mm"]) / module["pixel_pitch_mm"]
                >= 255.5
            ):
                raise ValueError(
                    "Pixel pitch overflows signed 9-bit x/y readout fields"
                )
            for half_size in (patch["half_u_mm"], patch["half_v_mm"]):
                half_pixels = half_size / module["pixel_pitch_mm"]
                if not math.isclose(half_pixels, round(half_pixels), abs_tol=1e-9):
                    raise ValueError(
                        "Active patch requires an even integral pixel grid"
                    )
    if len(layers) >= 2**3:
        raise ValueError("Layer identifiers exceed the unsigned 3-bit field")
    stack = support["stack_mm"]
    for index, layer in enumerate(layers, 1):
        lid = layer["layer"]
        lname = "layer" + str(index)
        lx = ET.SubElement(detector, "layer", id=str(index), name=lname)
        entity(lname, "layer", [0, 0, 0])
        bs = [b for b in pixel_bodies if b["layer_id"] == lid]
        for col in sorted(set(b["col"] for b in bs)):
            column = sorted([b for b in bs if b["col"] == col], key=lambda b: b["row"])
            b = column[0]
            phi, radius, offset_u = stave_frame(b)
            zlo, zhi = stave_span(column, support)
            length = zhi - zlo
            zy = (zhi + zlo) / 2
            sn = f"{lname}_stave{col}"
            sx = ET.SubElement(
                lx,
                "stave",
                id=str(col),
                name=sn,
                phi=rad(phi),
                radius=mm(radius),
                offset_u=mm(offset_u),
                length=mm(length),
            )
            origin = dict(b, center_mm=[b["center_mm"][0], b["center_mm"][1], 0.0])
            entity(sn, "stave", origin["center_mm"])
            width = 2 * b["half_u_mm"]
            fam = support["families"][b["family"]]
            depth = b["half_w_mm"]
            materials_by_layer = {
                "interface": "Epoxy",
                "insulation": "Polyimide",
                "graphite": "Graphite",
                "top_skin": "CFRP",
                "bottom_skin": "CFRP",
            }
            for kind in [
                "interface",
                "insulation",
                "graphite",
                "top_skin",
                "core",
                "bottom_skin",
            ]:
                thickness = stack[kind]
                w = depth + thickness / 2
                wid = fam["spine_mm"] if kind in ["core", "bottom_skin"] else width
                attr = dict(
                    name=kind,
                    width=mm(wid),
                    thickness=mm(thickness),
                    w=mm(w),
                    center_y=mm(zy),
                    vis="Foam" if kind == "core" else materials_by_layer[kind],
                )
                capacity = wid * length * thickness
                if kind == "core":
                    outer = fam["tube_OD_mm"] / 2
                    inner = outer - fam["tube_wall_mm"]
                    holes = 2 * math.pi * outer**2 * length
                    mat = materials.core(
                        sn + "_Core",
                        capacity - holes,
                        width * stack["internal_glue_equivalent"] * length,
                    )
                    attr.update(
                        material=mat,
                        tube_outer=mm(outer),
                        tube_inner=mm(inner),
                        tube_offset=mm(fam["tube_offset_mm"]),
                        tube_material="Titanium",
                        coolant_material="CO2",
                        tube_vis="Titanium",
                        coolant_vis="CO2",
                    )
                    ET.SubElement(sx, "core", **attr)
                    entity(
                        sn + "_core",
                        "support",
                        world(origin, 0, zy, w),
                        capacity - holes,
                        mat,
                    )
                    for k, sign in enumerate([-1, 1]):
                        center = world(origin, sign * fam["tube_offset_mm"], zy, w)
                        entity(
                            sn + "_tube_" + str(k),
                            "cooling_tube",
                            center,
                            math.pi * (outer**2 - inner**2) * length,
                            "Titanium",
                        )
                        entity(
                            sn + "_coolant_" + str(k),
                            "coolant",
                            center,
                            math.pi * inner**2 * length,
                            "CO2",
                        )
                else:
                    mat = materials_by_layer[kind]
                    ET.SubElement(sx, "slab", material=mat, **attr)
                    entity(
                        sn + "_" + kind,
                        "support",
                        world(origin, 0, zy, w),
                        capacity,
                        mat,
                    )
                depth += thickness
            for b in column:
                mid = b["module_id"]
                name = f"m{mid}"
                mx = ET.SubElement(
                    sx, "module", name=name, id=str(mid), z=mm(b["center_mm"][2])
                )
                ids = dict(
                    system=config["system_id"], layer=index, stave=col, module=mid
                )
                entity(name, "module", b["center_mm"], ids=ids)
                ps = patches[mid]
                shape = describe(b, ps, models, layout)
                local = shape['local']
                uc, vc, su, sv = (shape[k] for k in ('u','v','width','length'))
                tx = ET.SubElement(
                    mx,
                    "sensor",
                    u=mm(uc),
                    v=mm(vc),
                    width=mm(su),
                    length=mm(sv),
                    thickness=mm(module["sensor_mm"]),
                    material="Silicon",
                    vis="Silicon",
                )
                active_volume = sum(
                    4 * p["half_u_mm"] * p["half_v_mm"] * module["sensor_mm"]
                    for p in ps
                )
                entity(
                    name + "_substrate",
                    "sensor_guard",
                    world(b, uc, vc, 0),
                    su * sv * module["sensor_mm"] - active_volume,
                    "Silicon",
                )
                for (u, v), p in zip(local, ps):
                    pid = p["id"]
                    ET.SubElement(
                        tx,
                        "patch",
                        id=str(pid),
                        u=mm(u - uc),
                        v=mm(v - vc),
                        width=mm(2 * p["half_u_mm"]),
                        length=mm(2 * p["half_v_mm"]),
                    )
                    entity(
                        f"{name}_sensor_{pid}",
                        "sensitive",
                        p["center_mm"],
                        4 * p["half_u_mm"] * p["half_v_mm"] * module["sensor_mm"],
                        "Silicon",
                        normal=p["n"],
                        size_mm=[
                            2 * p["half_u_mm"],
                            2 * p["half_v_mm"],
                            module["sensor_mm"],
                        ],
                        ids=dict(ids, sensor=pid),
                    )

                def passive(part, tag, u, v, w, du, dv, dw, mat, role="module_passive"):
                    if (
                        max(
                            abs(u) + du / 2 - b["half_u_mm"],
                            abs(v) + dv / 2 - b["half_v_mm"],
                            abs(w) + dw / 2 - b["half_w_mm"],
                        )
                        > 1e-9
                    ):
                        raise ValueError(
                            "Module component outside frozen body: " + name + " " + part
                        )
                    ET.SubElement(
                        mx,
                        tag,
                        name=part,
                        u=mm(u),
                        v=mm(v),
                        w=mm(w),
                        width=mm(du),
                        length=mm(dv),
                        thickness=mm(dw),
                        material=mat,
                        vis="Copper" if mat == "PatternedCopper" else mat,
                    )
                    entity(
                        name + "_" + part, role, world(b, u, v, w), du * dv * dw, mat
                    )

                # Front flex faces beam; chips and contact shims face the stave.
                w = -module["sensor_mm"] / 2
                for part, t, mat in [
                    ("flex_glue", module["epoxy_mm"], "Epoxy"),
                    (
                        "flex_cu_inner",
                        module["flex_copper_layer_mm"],
                        "PatternedCopper",
                    ),
                    ("flex_polyimide", module["flex_polyimide_mm"], "Polyimide"),
                    (
                        "flex_cu_outer",
                        module["flex_copper_layer_mm"],
                        "PatternedCopper",
                    ),
                ]:
                    passive(part, "passive", uc, vc, w - t / 2, su, sv, t, mat)
                    w -= t
                asicw = (
                    module["sensor_mm"] / 2
                    + module["bump_standoff_mm"]
                    + module["asic_mm"] / 2
                )
                for k, die in enumerate(shape['dies']):
                    dieu, diev = die['u'], die['v']
                    passive(
                        f"asic{k}",
                        "die",
                        dieu,
                        diev,
                        asicw,
                        die["width"],
                        die["length"],
                        module["asic_mm"],
                        "Silicon",
                        "asic",
                    )
                    back = asicw + module["asic_mm"] / 2
                    shim = b["half_w_mm"] - back
                    if shim <= 0:
                        raise ValueError(
                            "Module stack reaches or exceeds fixed support plane"
                        )
                    passive(
                        f"contact{k}",
                        "passive",
                        dieu,
                        diev,
                        back + shim / 2,
                        die["width"],
                        die["length"],
                        shim,
                        "Graphite",
                        "contact_shim",
                    )
        for j, r in enumerate(r for r in rings if r["layer_id"] == lid):
            name = f"{lname}_ring{j}"
            length = r["z_max_mm"] - r["z_min_mm"]
            ET.SubElement(
                lx,
                "ring",
                name=name,
                rmin=mm(r["r_min_mm"]),
                rmax=mm(r["r_max_mm"]),
                length=mm(length),
                z=mm(r["z_mm"]),
                material="CFRP",
                vis="CFRP",
            )
            entity(
                name,
                "ring",
                [0, 0, r["z_mm"]],
                math.pi * (r["r_max_mm"] ** 2 - r["r_min_mm"] ** 2) * length,
                "CFRP",
            )
        for j, f in enumerate(f for f in feet if f["layer_id"] == lid):
            name = f"{lname}_foot{j}"
            back = f["back_normal_mm"]
            outer = f["ring_inner_mm"]
            phi = math.atan2(f["n"][1], f["n"][0])
            ET.SubElement(
                lx,
                "foot",
                name=name,
                width=mm(2 * f["half_u_mm"]),
                length=mm(2 * f["half_v_mm"]),
                back_radius=mm(back),
                outer_radius=mm(outer),
                phi=rad(phi),
                z=mm(f["center_mm"][2]),
                material="CFRP",
                vis="CFRP",
            )
            volume = f["mass_g"] / support["density_g_cm3"]["CFRP"] * 1000
            entity(name, "foot", f["center_mm"], volume, "CFRP")

    cable_footprint_volume = 0.0
    for step in route["longitudinal"]:
        if step["scenario"] != "reference":
            continue
        a, b = step["abs_z_min_mm"], step["abs_z_max_mm"]
        sign = 1 if step["side"] == "positive" else -1
        length = b - a
        capacity = step["envelope_area_mm2"] * length
        volumes = {k: v * length for k, v in step["footprint_mm2"].items()}
        cable_footprint_volume += sum(volumes.values())
        mat = materials.cable(volumes, capacity, fractions)
        name = "cable_" + step["id"]
        ET.SubElement(
            detector,
            "service",
            name=name,
            rmin=mm(step["r_min_mm"]),
            rmax=mm(step["r_max_mm"]),
            length=mm(length),
            phi=rad(step["phi_center_rad"]),
            phi_width=rad(step["phi_width_rad"]),
            z=mm(sign * (a + b) / 2),
            material=mat,
            vis="Cable",
        )
        entity(name, "cable", [0, 0, sign * (a + b) / 2], capacity, mat)
    # End service cells carry exactly the source route inventory. Partitioning
    # replaces overlapping illustrative elbows; routing path lengths are retained.
    cells, accounting = service_cells(route, service_summary, config, support)
    for cell in cells:
        mat = materials.effective(
            cell["name"] + "_Material",
            cell["constituent_volumes_mm3"],
            cell["volume_mm3"],
        )
        ET.SubElement(
            detector,
            "service",
            name=cell["name"],
            rmin=mm(cell["rmin"]),
            rmax=mm(cell["rmax"]),
            length=mm(cell["length"]),
            phi=rad(cell["phi"]),
            phi_width=rad(cell["phi_width"]),
            z=mm(cell["z"]),
            material=mat,
            vis="Service",
        )
        entity(cell["name"], "service_cell", [0, 0, cell["z"]], cell["volume_mm3"], mat)
    allids = [tuple(e["ids"].values()) for e in entities if e["role"] == "sensitive"]
    if len(allids) != len(set(allids)):
        raise ValueError("Duplicate sensitive identifier tuple")
    counts = dict(Counter(e["role"] for e in entities))
    source_files = [
        "detector/config/elements.json",
        "detector/config/display.json",
        "detector/config/pixel-barrel.json",
        "tools/pixel_barrel_dd4hep/export.py",
        "tools/pixel_barrel_dd4hep/materials.py",
        "tools/pixel_barrel_dd4hep/module_geometry.py",
        "tools/pixel_support/mounting.py",
        "tools/pixel_support/outward.py",
        "detector/src/PixelBarrel.cpp",
        "detector/src/PixelComponents.cpp",
        "detector/src/PixelServices.cpp",
        "detector/include/nodd/PixelComponents.hpp",
        "detector/include/nodd/PixelDisplay.hpp",
        "detector/include/nodd/PixelServices.hpp",
    ]
    provenance = dict(
        baseline_revision=config["baseline_revision"],
        baseline_layout_sha256=support["baseline_sha256"],
        input_sha256=config["input_sha256"],
        source_sha256={p: sha(ROOT / p) for p in source_files},
        source_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        config_sha256=hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest(),
        python=sys.version,
    )
    expected = dict(
        status="PROTOTYPE",
        counts=counts,
        entities=entities,
        materials=materials.recipes,
        material_totals=dict(material_targets),
        service_accounting=accounting,
        readout="PixelBarrelHits",
        id_descriptor=descriptor,
        readout_pitch_mm=module["pixel_pitch_mm"],
        tolerances=config["tolerances"],
        provenance=provenance,
    )
    output.mkdir(parents=True, exist_ok=True)
    write_xml(output / "materials.xml", materials.root)
    write_xml(output / "pixel-barrel.xml", compact)
    (output / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (output / "service-cells.json").write_text(json.dumps(cells, indent=2) + "\n")
    artifacts = {
        p.name: sha(p)
        for p in [
            output / "materials.xml",
            output / "pixel-barrel.xml",
            output / "expected.json",
            output / "config.json",
            output / "service-cells.json",
        ]
    }
    (output / "manifest.json").write_text(
        json.dumps(dict(provenance=provenance, artifacts_sha256=artifacts), indent=2)
        + "\n"
    )
    return expected


def read_gzip(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def service_cells(route, summary, config, support):
    groups = {g["id"]: g for g in route["groups"]}
    gather = {g["group_id"]: g for g in route["gathering"]}
    wall = read(ROOT / "tools/pixel_support/services.json")["transport_wall_mm"]
    budget = read(ROOT / "tools/module_layout/services_budget_inputs.json")
    sector_count = summary["totals"]["cooling_sectors_per_end"]
    phi_width = 2 * math.pi / sector_count * summary["reference_phi_fraction"]
    z0, z1 = summary["bay_abs_z_mm"]
    boundary = budget["capacity"]["boundary_allowance_mm"]
    length = z1 - z0 - 2 * boundary
    cells = []
    totals = defaultdict(float)
    for r in route["radial"]:
        if r["scenario"] != "reference":
            continue
        gs = [
            g
            for g in groups.values()
            if g["side"] == r["side"] and g["sector"] == r["sector"]
        ]
        for index, segment in enumerate(r["segments"]):
            ri = segment["r_min_mm"]
            ro = segment["r_max_mm"]
            # Last bin extends across the complete trunk; it owns the axial turn.
            if index == len(r["segments"]) - 1:
                ro = summary["trunk_r_mm"][1] - boundary
            capacity = 0.5 * (ro * ro - ri * ri) * phi_width * length
            path_length = segment["r_max_mm"] - ri
            volumes = {k: v * path_length for k, v in segment["footprint_mm2"].items()}
            od = segment["cooling_pair_OD_mm"]
            pipe_wall = 2 * math.pi * (od**2 - (od - 2 * wall) ** 2) / 4 * path_length
            coolant = 2 * math.pi * (od - 2 * wall) ** 2 / 4 * path_length
            if index == len(r["segments"]) - 1:
                handoff_length = r["axial"]["abs_z_max_mm"] - r["axial"]["abs_z_min_mm"]
                for k, v in segment["footprint_mm2"].items():
                    volumes[k] += v * handoff_length
                pipe_wall += (
                    2 * math.pi * (od**2 - (od - 2 * wall) ** 2) / 4 * handoff_length
                )
                coolant += 2 * math.pi * (od - 2 * wall) ** 2 / 4 * handoff_length
            owners = [
                g for g in gs if math.isclose(g["inner_radius_mm"], ri, abs_tol=1e-9)
            ]
            for g in owners:
                for k, v in g["scenarios"]["reference"][
                    "terminal_footprint_mm2"
                ].items():
                    volumes[k] += v * gather[g["id"]]["cable_path_length_mm"]
                stub = gather[g["id"]]["cooling_branch_length_per_leg_mm"]
                od = budget["pixel"]["feed_outer_diameter_mm"]
                pipe_wall += 2 * math.pi * (od**2 - (od - 2 * wall) ** 2) / 4 * stub
                coolant += 2 * math.pi * (od - 2 * wall) ** 2 / 4 * stub
            constituents = {
                k: sum(volumes.values()) * f
                for k, f in config["cable_volume_fractions"].items()
            }
            constituents.update(Titanium=pipe_wall, CO2=coolant)
            # Internal cable air is retained; further unused cell volume is air.
            if sum(constituents.values()) > capacity:
                raise ValueError("Service inventory cannot fit its effective cell")
            name = f"end_{r['side']}_sector{r['sector']}_bin{index}"
            cells.append(
                dict(
                    name=name,
                    rmin=ri,
                    rmax=ro,
                    length=length,
                    z=(1 if r["side"] == "positive" else -1) * (z0 + z1) / 2,
                    phi=2 * math.pi * r["sector"] / sector_count,
                    phi_width=phi_width,
                    volume_mm3=capacity,
                    constituent_volumes_mm3=constituents,
                    source_groups=[g["id"] for g in owners],
                    source_route=r["id"],
                    cable_footprint_volume_mm3=volumes,
                )
            )
            for k, v in volumes.items():
                totals[k] += v
            totals["Ti"] += pipe_wall
            totals["CO2"] += coolant
    # Independent terminal report: longitudinal + cells must reproduce PR29.
    longitudinal = defaultdict(float)
    for s in route["longitudinal"]:
        if s["scenario"] == "reference":
            for k, a in s["footprint_mm2"].items():
                longitudinal[k] += a * (s["abs_z_max_mm"] - s["abs_z_min_mm"])
    target = summary["scenarios"]["reference"]
    for kind in ["ancillary", "links"]:
        if not math.isclose(
            totals[kind] + longitudinal[kind],
            target[kind + "_footprint_volume_mm3"],
            rel_tol=1e-12,
        ):
            raise ValueError("Cable inventory not conserved")
    for key, targetkey in [("Ti", "Ti_volume_mm3"), ("CO2", "full_liquid_volume_mm3")]:
        if not math.isclose(totals[key], target[targetkey], rel_tol=1e-12):
            raise ValueError("Pipe inventory not conserved")
    return cells, dict(
        cell_count=len(cells),
        end_inventory_mm3=dict(totals),
        longitudinal_footprint_mm3=dict(longitudinal),
        source_reference=target,
        conserved=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=ROOT / "detector/config/pixel-barrel.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = export(read(args.config), args.output)
    print(
        json.dumps(
            dict(
                counts=result["counts"], service_accounting=result["service_accounting"]
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
