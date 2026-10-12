"""Long-detector unit conversion regression, with a deliberately synthetic GLB."""

import json
from pathlib import Path
import struct
import tempfile
import unittest
from prepare import rescale_glb_translations


class RescaleTests(unittest.TestCase):
    def fixture(self, path, wrong=False):
        matrix = [
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            -215.2643585205078,
            1.0,
        ]
        ref = dict(name="test_long_placement", localTransform=matrix)
        actual = matrix.copy()
        f32 = lambda v: struct.unpack("<f", struct.pack("<f", v))[0]
        actual[14] = matrix[14] if wrong else f32(f32(matrix[14]) * f32(0.01))
        payload = json.dumps(
            dict(nodes=[dict(name=ref["name"], matrix=actual)])
        ).encode()
        payload += b" " * ((-len(payload)) % 4)
        tail = struct.pack("<II", 4, 0x004E4942) + b"TEST"
        path.write_bytes(
            struct.pack(
                "<IIIII",
                0x46546C67,
                2,
                20 + len(payload) + len(tail),
                len(payload),
                0x4E4F534A,
            )
            + payload
            + tail
        )
        return {"nodes": [ref]}, tail

    def test_exact_rescaling_preserves_mesh_bytes_and_tolerance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "test.glb"
            ref, tail = self.fixture(p)
            report = rescale_glb_translations(p, ref)
            self.assertGreater(report["maximum_rounding_correction_m"], 1e-7)
            data = p.read_bytes()
            size = struct.unpack_from("<I", data, 12)[0]
            self.assertEqual(data[20 + size :], tail)
            result = json.loads(data[20 : 20 + size])
            self.assertEqual(
                result["nodes"][0]["matrix"][14],
                ref["nodes"][0]["localTransform"][14] * 0.01,
            )
            self.assertEqual(
                rescale_glb_translations(p, ref)["translations_corrected"], 0
            )

    def test_wrong_units_fail_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "test.glb"
            ref, _ = self.fixture(p, wrong=True)
            before = p.read_bytes()
            with self.assertRaises(ValueError):
                rescale_glb_translations(p, ref)
            self.assertEqual(before, p.read_bytes())
