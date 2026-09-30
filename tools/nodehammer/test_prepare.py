"""Small non-detector fixtures exercise unit, rotation and opacity safeguards."""

import json
from pathlib import Path
import struct
import tempfile
import unittest

import prepare


class DisplayChecks(unittest.TestCase):
    def test_column_major_parent_rotation(self):
        # Test values only: +90 degrees around z, then translate along local x.
        nodes = {1: {"locRot": [0, 1, 0, -1, 0, 0, 0, 0, 1], "locTrl": [3, 0, 0]},
                 2: {"parentId": 1, "locTrl": [2, 0, 0]}}
        rotation, centre = prepare.transforms(nodes)[2]
        self.assertEqual(centre, [3, 2, 0])
        self.assertEqual(prepare.mv(rotation, [1, 0, 0]), [0, 1, 0])

    def glb_fixture(self):
        # Deliberately different test lengths make axis and unit mistakes visible.
        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2, 3, 4, 1]
        glb_matrix = matrix.copy()
        glb_matrix[12:15] = [0.02, 0.03, 0.04]
        render = {"nodes": [{"name": "test_box", "semanticNodeId": 7, "localTransform": matrix}]}
        semantic = {"nodes": [{"id": 7, "logVolId": 1}], "logVols": [{"id": 1, "shapeId": 1}],
                    "shapes": [{"id": 1, "type": "box", "dx": 1, "dy": 2, "dz": 3}]}
        palette = {"test_material": {"rgb": [0.2, 0.4, 0.6], "alpha": 0.5}}
        gltf = {"nodes": [{"name": "test_box", "matrix": glb_matrix, "mesh": 0}],
                "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
                "accessors": [{"min": [-0.01, -0.02, -0.03], "max": [0.01, 0.02, 0.03]}],
                "materials": [{"name": "test_material", "alphaMode": "BLEND",
                               "pbrMetallicRoughness": {"baseColorFactor": [0.2, 0.4, 0.6, 0.5]}}]}
        return gltf, render, palette, semantic

    def check_glb(self, fixture):
        gltf, *arguments = fixture
        payload = json.dumps(gltf).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.glb"
            path.write_bytes(struct.pack("<IIIII", 0x46546C67, 2, len(payload) + 20,
                                         len(payload), 0x4E4F534A) + payload)
            return prepare.audit_glb(path, *arguments)

    def test_valid_unit_and_opacity_conversion(self):
        self.assertEqual(self.check_glb(self.glb_fixture())["box_dimensions_checked"], 1)

    def test_missing_translation_conversion_fails(self):
        fixture = self.glb_fixture()
        fixture[0]["nodes"][0]["matrix"][12] = 2
        with self.assertRaisesRegex(ValueError, "transform/length unit"):
            self.check_glb(fixture)

    def test_wrong_mesh_scale_fails(self):
        fixture = self.glb_fixture()
        fixture[0]["accessors"][0]["max"][2] = 0.3
        with self.assertRaisesRegex(ValueError, "box size"):
            self.check_glb(fixture)

    def test_opaque_export_of_translucent_material_fails(self):
        fixture = self.glb_fixture()
        del fixture[0]["materials"][0]["alphaMode"]
        with self.assertRaisesRegex(ValueError, "BLEND"):
            self.check_glb(fixture)

    def test_new_unknown_material_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, "unclassified display material"):
            prepare.config_text({}, [{"name": "new_unclassified_material"}])


if __name__ == "__main__":
    unittest.main()
