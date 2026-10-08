"""Explicit candidate pixel passive-aperture amendment; never moves a sensor."""

import copy
import math
import xml.etree.ElementTree as ET


def enlarge_pixel_aperture(doc, materials, entities, recipes, radius):
    if not math.isfinite(radius) or radius <= 27:
        raise ValueError("Candidate pixel passive aperture must exceed27mm")
    by_name = {e["name"]: e for e in entities}
    actions = []
    cache = {}
    for detector in doc.findall("./detectors/detector"):
        if not detector.get("name").startswith("PixelEndcap"):
            continue
        for part in detector.iter("part"):
            if part.get("shape") != "sector" or part.get("rmin") is None:
                continue
            old = float(part.get("rmin").removesuffix("*mm"))
            if old != 27:
                continue
            outer = float(part.get("rmax").removesuffix("*mm"))
            if radius >= outer:
                raise ValueError("Aperture consumes a passive part")
            if any(
                float(part.get(k, "0*mm").removesuffix("*mm")) != 0 for k in ("x", "y")
            ):
                raise ValueError(
                    "Non-coaxial passive sector needs a separate amendment"
                )
            removed = (
                float(part.get("angle").removesuffix("*rad"))
                / 2
                * (radius**2 - old**2)
                * float(part.get("dz").removesuffix("*mm"))
            )
            e = by_name[part.get("name")]
            capacity = e["volume_mm3"] - removed
            if capacity <= 0:
                raise ValueError("No positive passive volume remains")
            oldmat = e["material"]
            recipe = recipes[oldmat]
            oldmass = e["mass_g"]
            filler = None
            if "volume_fractions" in recipe:
                fractions = {
                    k if k == "Air" else "pixel_" + k: v
                    for k, v in recipe["volume_fractions"].items()
                }
                filler = next(
                    (
                        k
                        for k in ("pixel_Foam", "pixel_CFRP", "Air")
                        if fractions.get(k, 0) > 0
                    ),
                    "Air",
                )
                constituents = {k: v * e["volume_mm3"] for k, v in fractions.items()}
                if constituents.get(filler, 0) < removed:
                    raise ValueError(
                        "Removed aperture exceeds foam/unused-air inventory: "
                        + e["name"]
                        + " "
                        + str(fractions)
                    )
                constituents[filler] -= removed
                masses = {
                    k: v * recipes[k]["density_g_cm3"]
                    for k, v in constituents.items()
                    if v > 0
                }
                total = sum(masses.values())
                density = total / capacity
                key = (oldmat, round(removed / e["volume_mm3"], 14))
                if key not in cache:
                    name = "Aperture_" + oldmat + "_" + str(len(cache))
                    node = ET.SubElement(materials, "material", name=name)
                    ET.SubElement(node, "D", value=f"{density:.17g}", unit="g/cm3")
                    for k, v in masses.items():
                        ET.SubElement(node, "fraction", n=f"{v/total:.17g}", ref=k)
                    recipes[name] = dict(
                        density_g_cm3=density,
                        composition={k: v / total for k, v in masses.items()},
                        basis="mass_fraction",
                    )
                    cache[key] = name
                newmat = cache[key]
                part.set("material", newmat)
                e["material"] = newmat
            else:
                density = recipe["density_g_cm3"]
            e["volume_mm3"] = capacity
            e["mass_g"] = capacity * density / 1000
            part.set("rmin", f"{radius:.17g}*mm")
            actions.append(
                dict(
                    name=e["name"],
                    old_aperture_mm=old,
                    new_aperture_mm=radius,
                    removed_volume_mm3=removed,
                    removed_mass_g=oldmass - e["mass_g"],
                    preserved_payload=(
                        "All non-filler constituents unchanged"
                        if filler
                        else "Pure support shortened"
                    ),
                    filler=filler,
                )
            )
    if not actions:
        raise ValueError("No pixel passive apertures found")
    return actions
