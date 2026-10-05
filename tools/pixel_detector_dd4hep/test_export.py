"""Source comparisons and material conservation, independent of DD4hep."""

import copy
import gzip
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("combined_export", HERE / "export.py")
combined = importlib.util.module_from_spec(spec)
spec.loader.exec_module(combined)
ROOT = combined.ROOT


class CombinedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.cfg = combined.read(ROOT / "detector/config/pixel-detector.json")
        cls.result = combined.export(cls.cfg, cls.out)
        cls.source = json.loads(
            gzip.decompress(
                (
                    ROOT
                    / "docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz"
                ).read_bytes()
            )
        )
        cls.ec, _, _ = combined.load_inputs()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_barrel_entities_and_materials_unchanged(self):
        before = json.loads((self.out / "barrel/expected.json").read_text())
        names = {e["name"] for e in before["entities"]}
        self.assertEqual(
            before["entities"],
            [e for e in self.result["entities"] if e["name"] in names],
        )
        for name, mat in before["materials"].items():
            self.assertEqual(mat, self.result["materials"][name])

    def test_counts_and_source_sensitive_centres(self):
        self.assertEqual(self.result["counts"]["module"], 5066)
        self.assertEqual(self.result["counts"]["sensitive"], 14858)
        source = {
            p["id"]: p
            for p in self.source["modules"]
            if p["subsystem"] == "pixel" and p["region"] == "endcap"
        }
        bodies = {
            b["module_id"]: b
            for b in self.source["bodies"]
            if b["subsystem"] == "pixel" and b["region"] == "endcap"
        }
        discs = {d["layer"]: d for d in combined.disc_records(self.source, self.ec)}
        seen = set()
        for e in self.result["entities"]:
            if e["role"] != "sensitive" or e["ids"]["system"] == 1:
                continue
            p = source[e["ids"]["sensor"]]
            b = bodies[p["module_id"]]
            d = discs[b["layer_id"]]
            side = d["side"]
            face = 1 if b["row"] % 2 else -1
            levels = 3 if b["row"] == 0 else 2
            # Independent direct DES014 equation, not proposal() output.
            z = d["proposed_z_mm"] + side * face * (4.1 + (b["col"] % levels) * 1.65)
            for a, v in zip(e["center_mm"], [*p["center_mm"][:2], z]):
                self.assertAlmostEqual(a, v, places=8)
            self.assertEqual(e["normal"], [0, 0, -side * face])
            self.assertEqual(e["size_mm"][:2], [2 * p["half_u_mm"], 2 * p["half_v_mm"]])
            key = tuple(e["ids"].values())
            self.assertNotIn(key, seen)
            seen.add(key)
        self.assertEqual(len(seen), 8064)

    def test_local_disc_constituent_volume_conservation(self):
        # Expand effective recipes by physical volume and compare PR36's disjoint
        # inventory, excluding module stack and explicit genuine packing air.
        def expand(mat, v, out):
            recipe = self.result["materials"][mat]
            if "volume_fractions" in recipe:
                for k, f in recipe["volume_fractions"].items():
                    expand(k, v * f, out)
            else:
                out[mat] = out.get(mat, 0) + v

        observed = {}
        roles = {
            "disc_support",
            "disc_mount",
            "pickup",
            "disc_foot",
            "cooling_tube",
            "coolant",
            "local_services",
        }
        for e in self.result["entities"]:
            if e["role"] in roles and 607 < e["center_mm"][2] < 630:
                expand(e["material"], e["volume_mm3"], observed)
        reference = {}
        for c in combined.read(ROOT / self.cfg["screening"])["materials_mechanics"][
            "components"
        ]:
            if c["scope"] == "disc":
                mat = combined.MATERIAL_MAP[c["material"]]
                reference[mat] = reference.get(mat, 0) + c["volume_mm3"]
        for mat, v in reference.items():
            self.assertAlmostEqual(observed[mat], v, places=6, msg=mat)
        self.assertGreaterEqual(observed["Air"], 0)

    def test_malformed_cable_fraction_and_stale_pin_fail(self):
        for change in ("cable", "pin"):
            cfg = copy.deepcopy(self.cfg)
            if change == "cable":
                cfg["cable_volume_fractions"]["Copper"] = float("nan")
            else:
                cfg["input_sha256"][cfg["screening"]] = "0" * 64
            with self.assertRaises(ValueError):
                combined.export(cfg, self.out / "bad")

    def test_proper_endcap_frames_and_id_ranges(self):
        import xml.etree.ElementTree as ET

        tree = ET.parse(self.out / "pixel-detector.xml")
        for d in tree.findall("detectors/detector"):
            if d.get("name") == "PixelBarrel":
                continue
            for disc in d.findall("disc"):
                self.assertIn(int(disc.get("id")), range(1, 10))
                for m in disc.findall("module"):
                    ux, uy, vx, vy, nz = [
                        float(m.get(k)) for k in ("ux", "uy", "vx", "vy", "nz")
                    ]
                    self.assertAlmostEqual((ux * vy - uy * vx) * nz, 1.0)
                    self.assertLess(int(m.get("col")), 32)
                    self.assertLess(int(m.get("id")), 65536)


if __name__ == "__main__":
    unittest.main()
