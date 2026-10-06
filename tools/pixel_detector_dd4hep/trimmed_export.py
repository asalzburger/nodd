"""Deterministic DES019 adapter of frozen DES017/018 evidence to DD4hep."""

from collections import Counter, defaultdict
import copy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from export import export as barrel_export, mm, read, sha, write_xml
from materials import Materials
from model import ROOT
from endcap_parts import Parts, volume
from endcap_services import carrier
from trimmed_modules import module_xml, patches
from trimmed_services import transport

TAU = 2 * math.pi


def placed(template, datum, removed, radial):
    frozen = {m["module_id"]: m for m in template["modules"]}
    anchor = (datum**2 - radial["luminous_half_z_mm"] ** 2) / datum
    result = []
    for raw in template["raw_modules"]:
        if raw["row"] in removed:
            continue
        old = frozen[raw["module_id"]]
        dz = old["local_z_mm"]
        result.append(
            dict(
                raw,
                local_z_mm=dz,
                level=old["level"],
                mount_face=old["mount_face"],
                center_mm=[
                    raw["center_mm"][0] * (1 + dz / anchor),
                    raw["center_mm"][1] * (1 + dz / anchor),
                    datum + dz,
                ],
            )
        )
    return result


def support(
    parts,
    dx,
    mats,
    cfg,
    own,
    radial,
    modules,
    disc,
    datum,
    side,
    name,
    fractions,
    local_bounds,
):
    p = cfg["plate"]
    m = cfg["mounting"]
    c = own["cooling"]
    f = cfg["flex"]
    r0, R = p["r_min_mm"], p["r_max_mm"]
    skin = p["skin_mm"]
    core = p["core_mm"]
    ann = math.pi * (R**2 - r0**2)
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
    cooling = disc["after"]["cooling"]
    chips = disc["after"]["chips"]
    outer = c["tube_OD_mm"] / 2
    inner = outer - c["tube_wall_mm"]
    arcL = TAU * sum(t["radius_mm"] for t in cooling["tracks"])
    radialL = sum(t["radial_legs_mm"] for t in cooling["circuits"])
    bendL = sum(t["bends_allowance_mm"] for t in cooling["circuits"])
    tiA = math.pi * (outer**2 - inner**2)
    co2A = math.pi * inner**2
    stemA = math.prod(own["stem_mm"])
    insertV = chips * stemA * (core / 2 + c["routing_planes_mm"][1])
    glueV = faceA * p["glue_equivalent_mm"]
    corecap = faceA * core - math.pi * outer**2 * arcL
    corevol = dict(
        Graphite=insertV, Epoxy=glueV, Titanium=tiA * radialL, CO2=co2A * radialL
    )
    corevol["Foam"] = corecap - sum(corevol.values())
    coremat = mats.effective("EC_Foam_" + name, corevol, corecap)
    # One occupied window per chip, on its mounted face; full structural envelope retained.
    skinV = 2 * faceA * skin
    windowV = chips * stemA * skin
    skinmat = mats.effective(
        "EC_CFRP_" + name, dict(CFRP=skinV - windowV, Graphite=windowV), skinV
    )
    activeA = math.prod(radial["active_mm"])
    cradleV = activeA * own["pickup_mm"]["cradle"]
    cradle = (
        mats.effective(
            "EC_CFRP_cradle",
            dict(
                CFRP=(activeA - stemA) * own["pickup_mm"]["cradle"],
                Graphite=stemA * own["pickup_mm"]["cradle"],
            ),
            cradleV,
        )
        if "EC_CFRP_cradle" not in mats.recipes
        else "EC_CFRP_cradle"
    )
    rings = {m["row"] for m in modules}
    ringr = [
        sum(math.hypot(*m["center_mm"][:2]) for m in modules if m["row"] == row)
        / sum(m["row"] == row for m in modules)
        for row in rings
    ]
    flexV = 2 * TAU * sum(ringr) * f["bus_width_mm"] * f["bus_envelope_mm"]
    flexV += 2 * f["radial_fans"] * (R - r0) * f["bus_width_mm"] * f["bus_envelope_mm"]
    flexV += sum(
        (R - math.hypot(*m["center_mm"][:2]) + f["tail_extra_length_mm"])
        * f["tail_width_mm"]
        * f["tail_envelope_mm"]
        for m in modules
    )
    hwV = (
        (
            m["hardware_allowance_g_per_disc"]
            + len(modules) * m["module_clip_allowance_g"]
        )
        * 1000
        / mats.recipes["Titanium"]["density_g_cm3"]
    )
    localvol = dict(Titanium=tiA * bendL + hwV, CO2=co2A * bendL)
    for mat, frac in fractions.items():
        localvol[mat] = flexV * frac
    lo, hi = local_bounds
    localmat = mats.effective("EC_Service_local_" + name, localvol, ann * (hi - lo))
    for label, t, w, mat in [
        ("core", core, 0, coremat),
        ("skin_front", skin, -(core + skin) / 2, skinmat),
        ("skin_back", skin, (core + skin) / 2, skinmat),
    ]:
        plate = parts.add(
            dx,
            name + "_" + label,
            "sector",
            mat,
            "disc_support",
            center=(0, 0, side * w),
            datum=side * datum,
            rmin=r0,
            rmax=R,
            dz=t,
            angle=TAU,
        )
        if label == "core":
            for i, track in enumerate(cooling["tracks"]):
                tube = parts.add(
                    plate,
                    f"{name}_evaporator{i}",
                    "torus",
                    "Titanium",
                    "cooling_tube",
                    center=(0, 0, side * c["routing_planes_mm"][1]),
                    radius=track["radius_mm"],
                    rmin=0,
                    rmax=outer,
                )
                parts.add(
                    tube,
                    f"{name}_coolant{i}",
                    "torus",
                    "CO2",
                    "coolant",
                    radius=track["radius_mm"],
                    rmin=0,
                    rmax=inner,
                )
        for k, angle in enumerate(m["angles_deg"]):
            phi = math.radians(angle)
            radius = (m["tab_start_r_mm"] + m["tab_end_r_mm"]) / 2
            parts.add(
                dx,
                f"{name}_tongue{k}_{label}",
                "tongue",
                mat,
                "disc_mount",
                center=(radius * math.cos(phi), radius * math.sin(phi), side * w),
                rotation=(0, 0, phi),
                datum=side * datum,
                start=m["tab_start_r_mm"],
                end=m["tab_end_r_mm"],
                width=m["tab_width_mm"],
                radius=R,
                dz=t,
            )
    for module in modules:
        phi = math.atan2(module["u"][1], module["u"][0])
        face = module["mount_face"]
        h = module["level"] * own["level_spacing_mm"]
        for patch, a, b in patches(module, radial):
            x, y = [
                module["center_mm"][i] + a * module["u"][i] + b * module["v"][i]
                for i in range(2)
            ]
            prefix = f'{name}_m{module["module_id"]}_p{patch}'
            w = face * ((core + 2 * skin) / 2 + h)
            for label, mat in [
                ("cradle", cradle),
                ("graphite", "Graphite"),
                ("insulator", "Polyimide"),
                ("TIM", "Epoxy"),
                ("bond", "Epoxy"),
            ]:
                t = own["pickup_mm"][label]
                parts.add(
                    dx,
                    prefix + "_pickup_" + label,
                    "box",
                    mat,
                    "pickup",
                    center=(x, y, side * (w + face * t / 2)),
                    rotation=(0, 0, phi),
                    datum=side * datum,
                    dx=radial["active_mm"][0],
                    dy=radial["active_mm"][1],
                    dz=t,
                )
                w += face * t
            if h:
                shift = (
                    own["stem_offsets_mm"]["single_radial"]
                    if module["family"] == "single"
                    else -math.copysign(
                        own["stem_offsets_mm"]["quad_toward_center_v"], b
                    )
                )
                sx, sy = [q + shift * module["v"][i] for i, q in enumerate([x, y])]
                parts.add(
                    dx,
                    prefix + "_stem",
                    "box",
                    "Graphite",
                    "disc_foot",
                    center=(sx, sy, side * face * ((core + 2 * skin) / 2 + h / 2)),
                    rotation=(0, 0, phi),
                    datum=side * datum,
                    dx=own["stem_mm"][0],
                    dy=own["stem_mm"][1],
                    dz=h,
                )
    parts.add(
        dx,
        name + "_local_services",
        "sector",
        localmat,
        "local_services",
        center=(0, 0, side * (lo + hi) / 2),
        datum=side * datum,
        rmin=r0,
        rmax=R,
        dz=hi - lo,
        angle=TAU,
    )
    return dict(
        datum_mm=datum,
        modules=len(modules),
        chips=chips,
        cooling=cooling,
        core_constituents_mm3=corevol,
        skin_constituents_mm3=dict(CFRP=skinV - windowV, Graphite=windowV),
        core_capacity_mm3=corecap,
        local_constituents_mm3=localvol,
        flex_inventory_mm3=flexV,
        note="DES019 disjoint allocation; not an exact reproduction of DES017 approximate budget or manufacturing CAD.",
    )


def export(config, output):
    for p, h in config["input_sha256"].items():
        if sha(ROOT / p) != h:
            raise ValueError("Changed preliminary baseline pin: " + p)
    fractions = config["cable_volume_fractions"]
    if (
        set(fractions) != {"Copper", "Polyimide", "Air"}
        or any(not math.isfinite(v) or v < 0 for v in fractions.values())
        or not math.isclose(sum(fractions.values()), 1, abs_tol=1e-12)
    ):
        raise ValueError(
            "Cable volume fractions must be finite, nonnegative and sum to one"
        )
    if config["local_service_w_mm"] != [8, 10]:
        raise ValueError("Unexpected local service bounds")
    cfg = read(ROOT / config["endcap_inputs"])
    own = read(ROOT / config["support_variant_inputs"])
    radial = read(ROOT / config["radial_inputs"])
    template = read(ROOT / config["layout"])
    schedule = read(ROOT / config["apertures"])["variants"]["four-single-two-quad"]
    die = read(ROOT / "tools/module_layout/review_models.json")["pixel"]
    bc = read(ROOT / config["barrel_config"])
    bc["cable_volume_fractions"] = fractions
    output.mkdir(parents=True, exist_ok=True)
    expected = barrel_export(bc, output / "barrel")
    compact = ET.parse(output / "barrel/pixel-barrel.xml").getroot()
    for axis, size in zip("xyz", config["world_half_size_mm"]):
        compact.find(f"define/constant[@name='world_{axis}']").set("value", mm(size))
    for name, value in [
        ("tracker_region_rmax", config["transport"]["rear_r_mm"][1]),
        ("tracker_region_zmax", config["transport"]["rear_turn_abs_z_mm"][1]),
    ]:
        ET.SubElement(compact.find("define"), "constant", name=name, value=mm(value))
    mats = Materials(bc, read(ROOT / cfg["inherited_materials"]))
    mats.root = ET.parse(output / "barrel/materials.xml").getroot()
    mats.recipes = expected["materials"]
    entities = expected["entities"]
    parts = Parts(entities)
    ro = ET.SubElement(compact.find("readouts"), "readout", name="PixelEndcapHits")
    ro.append(copy.deepcopy(compact.find("readouts/readout/segmentation")))
    descriptor = "system:5,layer:4,stave:6,module:10,sensor:10,x:-9,y:-9"
    ET.SubElement(ro, "id").text = descriptor
    accounting = dict(
        discs=[], inherited_scenario_screens=schedule["accumulated_services"]
    )
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
        for di, d in enumerate(schedule["positive_discs"], 1):
            datum = d["datum_mm"]
            name = f"disc{sideName}{di}"
            dx = ET.SubElement(det, "disc", id=str(di), name=name, z=mm(side * datum))
            entities.append(
                dict(name=name, role="disc", center_mm=[0, 0, side * datum])
            )
            modules = placed(template, datum, d["removed_rows"], radial)
            for m in modules:
                module_xml(
                    dx, m, radial, bc["module"], entities, side, system, di, datum, die
                )
            account = support(
                parts,
                dx,
                mats,
                cfg,
                own,
                radial,
                modules,
                d,
                datum,
                side,
                name,
                fractions,
                config["local_service_w_mm"],
            )
            account.update(side=side, disc=di, removed_rows=d["removed_rows"])
            accounting["discs"].append(account)
        carrier(
            parts,
            det,
            cfg,
            side,
            sideName,
            [
                dict(proposed_z_mm=side * d["datum_mm"])
                for d in schedule["positive_discs"]
            ],
        )
        accounting["transport_" + sideName] = transport(
            parts,
            det,
            mats,
            cfg,
            config,
            schedule,
            bc,
            side,
            sideName,
            schedule["positive_discs"],
            template["rings"],
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
        status=config["status"],
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
        for p in sorted(Path(__file__).parent.glob("*.py"))
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
