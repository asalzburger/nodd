"""Independent frozen-evidence regression and negative controls for DES019."""

import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("trimmed_combined", HERE / "export.py")
combined = importlib.util.module_from_spec(spec)
spec.loader.exec_module(combined)
ROOT = combined.ROOT


class TrimmedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.cfg = combined.read(ROOT / "detector/config/pixel-detector-trimmed.json")
        cls.result = combined.export(cls.cfg, cls.out)
        cls.template = combined.read(ROOT / cls.cfg["layout"])
        cls.schedule = combined.read(ROOT / cls.cfg["apertures"])["variants"][
            "four-single-two-quad"
        ]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_counts_survivors_and_lossless_source_ids(self):
        self.assertEqual(self.result["counts"]["module"], 5362)
        self.assertEqual(self.result["counts"]["sensitive"], 11806)
        frozen = {p["id"]: p for p in self.template["active_patches"]}
        keys = set()
        seen = set()
        for e in self.result["entities"]:
            if e["role"] != "sensitive" or e["ids"]["system"] == 1:
                continue
            ids = e["ids"]
            disc = self.schedule["positive_discs"][ids["layer"] - 1]
            p = frozen[e["template_patch_id"]]
            self.assertNotIn(p["row"], disc["removed_rows"])
            side = -1 if ids["system"] == 2 else 1
            # Independent transformation from frozen placed first-disc patch (no producer calls).
            original = next(
                m for m in self.template["modules"] if m["module_id"] == p["module_id"]
            )
            raw = next(
                m
                for m in self.template["raw_modules"]
                if m["module_id"] == p["module_id"]
            )
            z = disc["datum_mm"]
            dz = original["local_z_mm"]
            anchor = (z * z - 150 * 150) / z
            xy = [
                raw["center_mm"][j] * (1 + dz / anchor)
                + (p["center_mm"][j] - original["center_mm"][j])
                for j in range(2)
            ]
            self.assertLess(math.dist(e["center_mm"], [*xy, side * (z + dz)]), 1e-7)
            self.assertEqual(
                e["source_patch_id"],
                p["id"] + ((0 if side < 0 else 9) + ids["layer"] - 1) * 10000,
            )
            self.assertEqual(ids["module"], p["module_id"] - 200000)
            self.assertEqual(ids["sensor"], p["id"] - 300000)
            sign = side * original["mount_face"]
            self.assertEqual(e["u"], [sign * x for x in p["u"]])
            self.assertEqual(e["v"], p["v"])
            self.assertAlmostEqual(
                (e["u"][0] * e["v"][1] - e["u"][1] * e["v"][0]) * e["normal"][2], 1
            )
            key = tuple(sorted(ids.items()))
            self.assertNotIn(key, keys)
            keys.add(key)
            self.assertNotIn(e["source_patch_id"], seen)
            seen.add(e["source_patch_id"])
        self.assertEqual(len(seen), 5012)

    def test_barrel_identity_and_heterogeneous_cooling_transport(self):
        before = combined.read(self.out / "barrel/expected.json")
        names = {e["name"] for e in before["entities"]}
        self.assertEqual(
            before["entities"],
            [e for e in self.result["entities"] if e["name"] in names],
        )
        a = self.result["service_accounting"]["endcap"]
        self.assertEqual(sum(d["cooling"]["number_circuits"] for d in a["discs"]), 248)
        for label in ("N", "P"):
            t = a["transport_" + label]
            neck = t["flange_necks"][-1]
            ref = next(
                s
                for s in self.schedule["accumulated_services"]["scenarios"]
                if s["scenario"] == "reference"
            )
            side = next(
                s
                for s in ref["sides"]
                if s["side"] == ("positive" if label == "P" else "negative")
            )
            self.assertAlmostEqual(
                neck["utilization"], side["inherited_neck_utilization"]
            )
            self.assertEqual(neck["status"], "FAIL")
            for local, d in zip(t["disc_footprints"], self.schedule["positive_discs"]):
                ref = next(
                    s for s in d["after"]["services"] if s["scenario"] == "reference"
                )
                self.assertAlmostEqual(
                    sum(local.values()), ref["cables_mm2"] + ref["pipes_mm2"]
                )

    def test_stale_pin_and_invalid_composition_rejected(self):
        for kind in ("pin", "composition"):
            cfg = copy.deepcopy(self.cfg)
            if kind == "pin":
                cfg["input_sha256"][cfg["layout"]] = "0" * 64
            else:
                cfg["cable_volume_fractions"]["Copper"] = float("nan")
            with self.assertRaises(ValueError):
                combined.export(cfg, self.out / "bad")

    def test_cooling_material_conserved_once_per_disc(self):
        materials = self.result["materials"]

        def expand(mat, volume, out):
            if "volume_fractions" in materials[mat]:
                for child, fraction in materials[mat]["volume_fractions"].items():
                    expand(child, volume * fraction, out)
            else:
                out[mat] = out.get(mat, 0) + volume

        support = combined.read(ROOT / self.cfg["support_variant_inputs"])
        mounting = combined.read(ROOT / self.cfg["endcap_inputs"])["mounting"]
        c = support["cooling"]
        outer = c["tube_OD_mm"] / 2
        inner = outer - c["tube_wall_mm"]
        roles = {
            "disc_support",
            "disc_mount",
            "pickup",
            "disc_foot",
            "cooling_tube",
            "coolant",
            "local_services",
        }
        for d in self.schedule["positive_discs"]:
            observed = {}
            for e in self.result["entities"]:
                if e["role"] in roles and abs(e["center_mm"][2] - d["datum_mm"]) < 11:
                    expand(e["material"], e["volume_mm3"], observed)
            length = d["after"]["cooling"]["estimated_tube_length_mm"]
            hardware = (
                mounting["hardware_allowance_g_per_disc"]
                + d["after"]["modules"] * mounting["module_clip_allowance_g"]
            )
            titanium = length * math.pi * (outer**2 - inner**2)
            titanium += hardware * 1000 / materials["Titanium"]["density_g_cm3"]
            self.assertAlmostEqual(observed["Titanium"], titanium, places=7)
            self.assertAlmostEqual(
                observed["CO2"], length * math.pi * inner**2, places=7
            )


if __name__ == "__main__":
    unittest.main()
