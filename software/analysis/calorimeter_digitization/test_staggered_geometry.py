"""Physical packing controls for the isolated board-staggering test."""
import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from staggered_geometry import (HARDWARE, ENDCAP_ID_BLOCK, PHASES, area, barrel_layout,
    edge_layout, half_board, material_board, pack, panel_rows, part_volume,
    prepare, tangent_boards, validate_modules, encode_geometry)
from barrel_export import hardware as barrel_hardware
from untiled_geometry import number, polygon, location


class StaggeredPacking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.barrel, base = barrel_layout()
        hardware, _ = barrel_hardware(cls.barrel, base)
        cls.board = ET.Element("board", name="square")
        for part in hardware["board_parts"]:
            node = ET.SubElement(cls.board, "piece", name=part["name"], role=part["role"], material=part["material"])
            encode_geometry(node, part)
        cls.half = half_board(cls.board)
        cls.edge, layouts, _ = edge_layout()
        cls.ecal = json.loads((HARDWARE / "cassettes.json").read_text())["ecal"]
        cls.base_phase = layouts["edges"]["phase_mm"]
        cls.base_modules = layouts["edges"]["modules"]
        cls.families = [pack(cls.edge["config"], cls.ecal, cls.edge["outer_polygon_mm"], cls.base_phase + radial,
                            True, tangent_phase_mm=tangent, inner_partial_row=bool(radial)) for tangent, radial in PHASES]

    def test_default_packer_preserves_pinned_physical_modules(self):
        # Golden physical snapshot from source 3af5538; excludes provenance and
        # callbacks. Includes every original electrode and actual ASIC position.
        keys = ("index", "grid", "center_mm", "board", "sensor", "active", "full", "pads", "asics")
        data = [{key: m[key] for key in keys} for m in self.base_modules]
        digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "1e6c7d7317e5f16b6726352dc6fb3401b1dfe6bbac8479241f794698e724b535")

    def test_tangent_family_preserves_span_gaps_and_capacity(self):
        for count in (6, 7, 8):
            old = tangent_boards(count, False)
            new = tangent_boards(count, True)
            self.assertEqual(len(old), count)
            self.assertEqual(len(new), count + 1)
            bounds = [(u - (47 if family == "square" else 23), u + (47 if family == "square" else 23)) for u, family, _ in new]
            self.assertEqual(bounds[0][0], old[0][0] - 47)
            self.assertEqual(bounds[-1][1], old[-1][0] + 47)
            self.assertTrue(all(abs(right[0] - left[1] - 2) < 1e-10 for left, right in zip(bounds, bounds[1:])))
            self.assertEqual(sum(4 if family == "square" else 2 for _, family, _ in new), 4 * count)
            self.assertEqual(sum(256 if family == "square" else 128 for _, family, _ in new), 256 * count)

    def test_narrow_board_is_real_hardware_with_two_asic_stacks(self):
        parts = self.half.findall("piece")
        self.assertEqual(len(parts), 16)
        for role, width, height in (("sensitive", 40, 88), ("sensor_edge", 42, 90), ("pcb", 46, 94)):
            for part in (p for p in parts if p.get("role") == role):
                vertices = polygon(part)
                self.assertEqual(max(p[0] for p in vertices) - min(p[0] for p in vertices), width)
                self.assertEqual(max(p[1] for p in vertices) - min(p[1] for p in vertices), height)
        for role in ("bond", "readout", "thermal_pad", "thermal_post"):
            items = [p for p in parts if p.get("role") == role]
            self.assertEqual(len(items), 2)
            self.assertEqual({location(p)[:2] for p in items}, {(0., -22.), (0., 22.)})

    def test_narrow_material_and_guard_changes_are_explicit(self):
        full = self.board.findall("piece")
        narrow = self.half.findall("piece")
        volume = lambda parts, role: sum(part_volume(p) for p in parts if p.get("role") == role)
        self.assertEqual(2 * volume(narrow, "sensitive") - volume(full, "sensitive"), -704 * .5)
        self.assertEqual(2 * volume(narrow, "sensor_edge") - volume(full, "sensor_edge"), 164 * .5)
        for role in ("bond", "readout", "thermal_pad", "thermal_post"):
            self.assertAlmostEqual(2 * volume(narrow, role), volume(full, role))

    def test_axial_phases_preserve_rows_and_physical_clearances(self):
        for layer in self.barrel["layers"]:
            axial = PHASES[layer["index"] % 4][1]
            for panel in layer["panels"]:
                rows, actual, frame_gap, bay_gap = panel_rows(panel, axial)
                self.assertEqual(len(rows), panel["board_rows"])
                self.assertGreaterEqual(frame_gap, 0)
                self.assertGreaterEqual(bay_gap, 2)
                self.assertEqual(actual, (24 if panel["kind"] == "short" else 48) if axial else 0)
                self.assertTrue(all(abs((new - old) + panel["bay_sign"] * actual) < 1e-10
                                    for new, old in zip(rows, panel["row_centers_mm"])))

    def test_edge_families_have_physical_electronics_and_disjoint_id_blocks(self):
        identifiers = set()
        for phase, layout in enumerate(self.families):
            modules = copy.deepcopy(layout["modules"])
            self.assertLess(max(m["index"] for m in modules), ENDCAP_ID_BLOCK)
            for module in modules:
                module["index"] += phase * ENDCAP_ID_BLOCK
                self.assertNotIn(module["index"], identifiers)
                identifiers.add(module["index"])
            validate_modules(modules, channels_limit=32768)
            self.assertLess(max(identifiers), 1024)

    def test_radial_half_phase_keeps_only_feasible_inner_profiles(self):
        innermost = [m for m in self.families[2]["modules"] if m["grid"][0] == -1]
        self.assertTrue(innermost)
        self.assertTrue(all(not m["full"] for m in innermost))
        for module in innermost:
            self.assertGreaterEqual(min(x + module["center_mm"][0] for x, _ in module["board"]), 130 - 1e-8)
        # The doubly shifted family's two narrow inner fragments fail the
        # original physical minimum area/width; they must not be fabricated or
        # retained by weakening those constraints merely to fill the aperture.
        self.assertFalse([m for m in self.families[3]["modules"] if m["grid"][0] == -1])
        self.assertGreater(self.families[3]["rejected"]["small_or_narrow_profile"], 0)
        for family in self.families:
            for module in family["modules"]:
                self.assertGreaterEqual(area(module["sensor"]), self.edge["config"]["minimum_sensor_area_mm2"] - 1e-8)

    def test_tangent_phase_rejects_unwrapped_or_nonfinite_values(self):
        for value in (-1., 96., math.nan):
            with self.assertRaises(ValueError):
                pack(self.edge["config"], self.ecal, self.edge["outer_polygon_mm"], self.base_phase, True,
                     False, tangent_phase_mm=value)

    def test_unsupported_source_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "detector.xml").write_text("<unsupported/>")
            output = root / "output"
            with self.assertRaisesRegex(ValueError, "Unsupported original tiled input hash"):
                prepare(root, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
