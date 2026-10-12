"""Explicit provisional material recipes; DD4hep XML fractions are by mass."""

import math
import json
from pathlib import Path
import xml.etree.ElementTree as ET

# A complete pinned natural-element table avoids ROOT's sparse-Z mixture trap.
# It contains no detector materials; recipes below remain explicit/configurable.
ELEMENTS = json.loads(
    (Path(__file__).resolve().parents[2] / "detector/config/elements.json").read_text()
)["elements"]


class Materials:
    def __init__(self, config, support):
        self.root = ET.Element("materials")
        self.recipes = {}
        self.cache = {}
        for item in ELEMENTS:
            name, z, a = item["name"], item["Z"], item["A"]
            node = ET.SubElement(
                self.root, "element", name=name, formula=name, Z=str(z)
            )
            ET.SubElement(node, "atom", type="A", value=str(a), unit="g/mol")
        self.add("Air", 0.0012, {"N": 0.754, "O": 0.234, "Ar": 0.012})
        self.add("Vacuum", 1e-12, {"H": 1.0})
        self.add("Silicon", 2.329, {"Si": 1.0})
        self.add("Copper", 8.96, {"Cu": 1.0})
        self.add("Titanium", support["density_g_cm3"]["titanium"], {"Ti": 1.0})
        self.add("Graphite", support["density_g_cm3"]["graphite"], {"C": 1.0})
        self.add(
            "Polyimide",
            support["density_g_cm3"]["insulation"],
            {"C": 22, "H": 10, "N": 2, "O": 5},
            atoms=True,
        )
        self.add(
            "Epoxy",
            support["density_g_cm3"]["glue"],
            {"C": 15, "H": 44, "O": 7},
            atoms=True,
        )
        self.add("CO2", config["coolant_density_g_cm3"], {"C": 1, "O": 2}, atoms=True)
        f = config["cfrp_carbon_mass_fraction"]
        if not 0 < f < 1:
            raise ValueError("CFRP carbon mass fraction must be in (0,1)")
        self.add("CFRP", support["density_g_cm3"]["CFRP"], {"C": f, "Epoxy": 1 - f})
        self.add("Foam", support["density_g_cm3"]["foam"], {"C": f, "Epoxy": 1 - f})
        self.effective(
            "PatternedCopper", {"Copper": config["module"]["flex_copper_coverage"]}, 1.0
        )

    def add(self, name, density, fractions, atoms=False):
        if not math.isfinite(density) or density <= 0:
            raise ValueError("Positive finite material density required")
        if not atoms and not math.isclose(sum(fractions.values()), 1, abs_tol=1e-12):
            raise ValueError("Mass fractions must sum to one")
        if any(v <= 0 for v in fractions.values()):
            raise ValueError("Positive constituents required")
        x = ET.SubElement(self.root, "material", name=name)
        ET.SubElement(x, "D", value=format(density, ".17g"), unit="g/cm3")
        for ref, value in sorted(fractions.items()):
            ET.SubElement(
                x,
                "composite" if atoms else "fraction",
                n=format(value, ".17g"),
                ref=ref,
            )
        self.recipes[name] = dict(
            density_g_cm3=density,
            composition=fractions,
            basis="atom_count" if atoms else "mass_fraction",
        )
        return name

    def effective(self, name, volumes, capacity):
        """Normalize constituent volumes, adding only genuine remaining air."""
        if capacity <= 0 or any(
            not math.isfinite(v) or v < 0 for v in volumes.values()
        ):
            raise ValueError("Invalid effective material inventory")
        if sum(volumes.values()) > capacity * (1 + 1e-12):
            raise ValueError("Constituent inventory exceeds cell capacity")
        filled = dict(volumes)
        filled["Air"] = filled.get("Air", 0.0) + max(
            0.0, capacity - sum(volumes.values())
        )
        mass = {
            k: v * self.recipes[k]["density_g_cm3"] for k, v in filled.items() if v > 0
        }
        density = sum(mass.values()) / capacity
        self.add(name, density, {k: v / sum(mass.values()) for k, v in mass.items()})
        self.recipes[name]["volume_fractions"] = {
            k: v / capacity for k, v in filled.items()
        }
        return name

    def cable(self, volumes, capacity, fractions):
        total = sum(volumes.values())
        composition = {k: total * f for k, f in fractions.items()}
        # Cache identical recipes (longitudinal reference packing is constant).
        key = tuple(
            (k, round(v / capacity, 13)) for k, v in sorted(composition.items())
        )
        if key not in self.cache:
            self.cache[key] = self.effective(
                "CableMix_" + str(len(self.cache)), composition, capacity
            )
        return self.cache[key]

    def core(self, name, foam_capacity, glue_volume):
        # Glue fills intrinsic pores of low-density foam. Retain foam mass and
        # add the inherited extra glue inventory without enlarging the core.
        masses = {
            "Foam": foam_capacity * self.recipes["Foam"]["density_g_cm3"],
            "Epoxy": glue_volume * self.recipes["Epoxy"]["density_g_cm3"],
        }
        self.add(
            name,
            sum(masses.values()) / foam_capacity,
            {k: v / sum(masses.values()) for k, v in masses.items()},
        )
        self.recipes[name][
            "note"
        ] = "Glue replaces foam pore space; retain original foam mass plus explicit internal-glue mass."
        return name
