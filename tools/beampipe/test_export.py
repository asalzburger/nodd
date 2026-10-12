import copy
import json
from pathlib import Path
import tempfile
import unittest
from export import export, ROOT

class BeamPipeExport(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "detector/config/beampipe.json").read_text())

    def test_shell_is_not_solid_cylinder(self):
        import math
        with tempfile.TemporaryDirectory() as directory:
            expected = export(self.config, directory)
            self.assertAlmostEqual(expected["wall_volume_mm3"], math.pi * (27.8**2 - 27**2) * 8000)
            self.assertEqual(expected["sensitive_count"], 0)

    def test_invalid_dimensions_and_world(self):
        for key, value in (("wall_mm", 0), ("inner_radius_mm", -1), ("half_length_mm", float("nan")), ("world_half_size_mm", [20, 100, 4100]), ("system_id", 1)):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                config = copy.deepcopy(self.config)
                config[key] = value
                with self.assertRaises(ValueError):
                    export(config, directory)

if __name__ == "__main__":
    unittest.main()
