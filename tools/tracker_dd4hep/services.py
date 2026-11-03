"""Conserve service payload in shared corridors, with one physical tray."""

from collections import defaultdict
import copy
import math
import xml.etree.ElementTree as ET


def number(piece, key):
    return float(piece.get(key).removesuffix("*mm").removesuffix("*rad"))


def reconcile(doc, matdoc, entities, recipes):
    by_name = {e["name"]: e for e in entities}
    removed = set()
    groups = defaultdict(list)
    actions = []
    for detector in doc.findall("./detectors/detector"):
        for piece in list(detector.findall("piece")):
            name = piece.get("name")
            if name.startswith("long_barrel_trunk_"):
                detector.remove(piece)
                removed.add(name)
                continue
            if not name.startswith(("short_barrel_trunk_", "short_endcap_trunk_")):
                continue
            e = by_name[name]
            key = tuple(
                round(number(piece, k), 12) for k in ("rmin", "rmax", "start", "angle")
            )
            groups[key].append((piece, e))
            removed.add(name)
            detector.remove(piece)
    actions.append(
        dict(
            action="replace long-barrel standalone trunk with DES023 cumulative barrel+endcap trunk",
            removed_names=sorted(n for n in removed if n.startswith("long_barrel")),
        )
    )
    owner = next(
        d
        for d in doc.findall("./detectors/detector")
        if d.get("name") == "ShortStripBarrel"
    )
    new_entities = []
    payload_before = defaultdict(float)
    payload_after = defaultdict(float)
    for group_index, (key, members) in enumerate(sorted(groups.items())):
        ri, ro, start, angle = key
        intervals = [
            (
                number(p, "w") - number(p, "length") / 2,
                number(p, "w") + number(p, "length") / 2,
                p,
                e,
            )
            for p, e in members
        ]
        breaks = sorted(set(round(z, 9) for a, b, p, e in intervals for z in (a, b)))
        for p, e in members:
            if e["role"] == "service_cell":
                for m, v in e["constituent_volumes_mm3"].items():
                    payload_before[m] += v
        for j, (a, b) in enumerate(zip(breaks, breaks[1:])):
            overlaps = [(p, e) for lo, hi, p, e in intervals if lo < (a + b) / 2 < hi]
            if not overlaps:
                continue
            capacity = angle / 2 * (ro * ro - ri * ri) * (b - a)
            payload = defaultdict(float)
            is_cell = all(e["role"] == "service_cell" for p, e in overlaps)
            if is_cell:
                for p, e in overlaps:
                    scale = (b - a) / number(p, "length")
                    for m, v in e["constituent_volumes_mm3"].items():
                        payload[m] += v * scale
                for m, v in payload.items():
                    payload_after[m] += v
                if sum(payload.values()) > capacity * (1 + 1e-10):
                    raise ValueError(
                        "Shared short-strip payload exceeds physical corridor"
                    )
                filled = dict(payload)
                filled["Air"] = filled.get("Air", 0) + max(
                    0, capacity - sum(payload.values())
                )
                masses = {
                    m: v * recipes[m]["density_g_cm3"]
                    for m, v in filled.items()
                    if v > 0
                }
                density = sum(masses.values()) / capacity
                material = f"SharedShortTrunk_{group_index}_{j}"
                node = ET.SubElement(matdoc, "material", name=material)
                ET.SubElement(node, "D", value=f"{density:.17g}", unit="g/cm3")
                fractions = {m: v / sum(masses.values()) for m, v in masses.items()}
                for m, f in fractions.items():
                    ET.SubElement(node, "fraction", n=f"{f:.17g}", ref=m)
                recipes[material] = dict(
                    density_g_cm3=density, composition=fractions, basis="mass_fraction"
                )
                role = "service_cell"
            else:
                # Co-located standalone tray skins become one common carrier.
                materials = {e["material"] for p, e in overlaps}
                if len(materials) != 1:
                    raise ValueError("Shared tray materials disagree")
                material = materials.pop()
                density = recipes[material]["density_g_cm3"]
                role = "tray"
            name = f"SharedShortTrunk_{group_index}_{j}"
            piece = copy.deepcopy(overlaps[0][0])
            piece.set("name", name)
            piece.set("material", material)
            piece.set("w", f"{(a+b)/2:.17g}*mm")
            piece.set("length", f"{b-a:.17g}*mm")
            owner.append(piece)
            new_entities.append(
                dict(
                    name=name,
                    role=role,
                    component="shared_short_services",
                    material=material,
                    center_mm=[0, 0, (a + b) / 2],
                    volume_mm3=capacity,
                    mass_g=capacity * density / 1000,
                    constituent_volumes_mm3=dict(payload),
                )
            )
    for m, v in payload_before.items():
        if not math.isclose(v, payload_after[m], rel_tol=1e-10, abs_tol=1e-5):
            raise ValueError("Service constituent not conserved: " + m)
    actions.append(
        dict(
            action="partition shared short-strip trunks; sum payload and retain one tray",
            removed_names=sorted(n for n in removed if n.startswith("short_")),
            new_placements=len(new_entities),
            payload_before_mm3=dict(payload_before),
            payload_after_mm3=dict(payload_after),
            air="Preserve cable-void air and count unused corridor air once.",
        )
    )
    entities = [e for e in entities if e["name"] not in removed] + new_entities
    return entities, actions
