"""Display-only fixtures; no ROOT dependency or detector dimensions."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import export_root


class DisplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.palette = Path(self.temp.name) / "display.json"
        self.palette.write_text(json.dumps({"styles": {"Silicon": {
            "root_color": 860, "rgb": [1, 0, 0], "alpha": 0.5}}}))
        self.volume = Mock()
        self.volume.GetName.return_value = "test_sensor"
        self.volume.IsAssembly.return_value = False
        self.volume.GetNdaughters.return_value = 0
        self.volume.GetMaterial.return_value.GetName.return_value = "Silicon"
        self.volume.GetLineColor.return_value = 860
        self.volume.GetFillColor.return_value = 860
        self.volume.GetTransparency.return_value = 50
        self.world = Mock()
        self.world.GetName.return_value = "test_world"
        self.world.IsAssembly.return_value = True
        self.world.GetNdaughters.return_value = 1
        self.world.GetNode.return_value.GetVolume.return_value = self.volume
        self.manager = Mock()
        self.manager.GetTopVolume.return_value = self.world
        self.ROOT = Mock()
        colour = self.ROOT.gROOT.GetColor.return_value
        colour.GetRed.return_value = 0
        colour.GetGreen.return_value = 0.2
        colour.GetBlue.return_value = 1

    def snapshot(self):
        with patch.object(export_root, "PALETTE", self.palette):
            return export_root.snapshot(self.manager, self.ROOT)

    def test_distinct_rgb_allowed_and_actual_root_rgb_retained(self):
        self.assertEqual(self.snapshot()["test_sensor"]["rgb"], [0, 0.2, 1])

    def test_wrong_root_index_still_rejected(self):
        self.volume.GetLineColor.return_value = 800
        with self.assertRaisesRegex(ValueError, "colour index"):
            self.snapshot()

    def test_undefined_root_colour_still_rejected(self):
        self.ROOT.gROOT.GetColor.return_value = None
        with self.assertRaisesRegex(ValueError, "undefined"):
            self.snapshot()

    def test_effective_transparency_can_differ_from_config_alpha(self):
        self.volume.GetTransparency.return_value = 25
        self.assertEqual(self.snapshot()["test_sensor"]["transparency"], 25)


if __name__ == "__main__":
    unittest.main()
