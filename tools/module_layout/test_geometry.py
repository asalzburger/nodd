"""Meaningful geometry-contract tests for the unsigned finite-module prototype."""
import copy
import math
import unittest

from tools.module_layout.geometry import (
    _obb_overlap, body_overlap_diagnostics, cross, dot, generate_layout,
    load_models, norm, summarize,
)


def fixture(subsystem="pixel", kind="cylinder"):
    layer = dict(id="test-layer",station_group="test-station",subsystem=subsystem,kind=kind)
    if kind == "cylinder":
        layer.update(r_m=.100,z_min_m=-.02,z_max_m=.02)
    elif kind == "disc":
        layer.update(r_min_m=.100,r_max_m=.200,z_m=.500)
    return dict(id="test-only",layers=[layer])


class FiniteGeometryTest(unittest.TestCase):
    def test_pixel_islands_sensor_area_dedup_and_seam(self):
        layout = generate_layout(fixture(),"flat","quad")
        patches = [p for p in layout["modules"] if p["module_id"] == 1]
        self.assertEqual(len(patches),4)
        self.assertEqual(len({p["sensor_id"] for p in patches}),1)
        self.assertAlmostEqual(sum(p["active_area_mm2"] for p in patches),1536.)
        a,b = patches[0],patches[1]
        delta = [x-y for x,y in zip(b["center_mm"],a["center_mm"])]
        self.assertAlmostEqual(abs(dot(delta,a["v"])),19.4)
        summary = summarize(layout)["total"]
        self.assertEqual(summary["sensors"],summary["modules"])
        self.assertEqual(summary["patches"],4*summary["sensors"])
        self.assertAlmostEqual(summary["sensor_area_m2"],summary["sensors"]*41.2*39.6*1e-6)

    def test_longstrip_is_two_rotated_separated_sensors_one_module(self):
        layout = generate_layout(fixture("long_strip"),"flat")
        a,b = layout["modules"][:2]
        self.assertEqual(a["module_id"],b["module_id"])
        self.assertNotEqual(a["sensor_id"],b["sensor_id"])
        self.assertAlmostEqual(dot(a["u"],b["u"]),math.cos(.04))
        self.assertAlmostEqual(norm([x-y for x,y in zip(a["center_mm"],b["center_mm"])]),5.)
        self.assertAlmostEqual(a["sensor_area_mm2"],97.*97.)

    def test_configuration_updates_active_shapes_and_rejects_other_shapes(self):
        model = load_models()
        model["short_strip"]["active_v_mm"] = 48.
        layout = generate_layout(fixture("short_strip"),"flat",models=model)
        self.assertEqual(layout["modules"][0]["half_v_mm"],24.)
        model["short_strip"]["shape"] = "trapezoid"
        with self.assertRaisesRegex(ValueError,"rectangle"):
            generate_layout(fixture("short_strip"),"flat",models=model)

    def test_all_frames_orthonormal_unique_and_deterministic(self):
        a = generate_layout(fixture("long_strip","disc"),"tilted")
        b = generate_layout(fixture("long_strip","disc"),"tilted")
        self.assertEqual(a,b)
        self.assertEqual(len({p["id"] for p in a["modules"]}),len(a["modules"]))
        for p in a["modules"]:
            self.assertAlmostEqual(dot(p["u"],p["v"]),0.)
            self.assertAlmostEqual(norm(p["u"]),1.)
            self.assertAlmostEqual(norm(p["v"]),1.)
            self.assertAlmostEqual(dot(cross(p["u"],p["v"]),p["n"]),1.)

    def test_pint_normals_and_full_modules_overhang_retained(self):
        layout = generate_layout("pint","tilted")
        layers = {l["id"]:l for l in layout["layers"]}
        records = [p for p in layout["modules"] if p["region"] == "inclined"]
        self.assertTrue(records)
        for p in records:
            layer = layers[p["layer_id"]]
            self.assertAlmostEqual(p["n"][2],layer["normal_z"])
            self.assertAlmostEqual(math.hypot(*p["n"][:2]),layer["normal_r"])
            self.assertEqual(p["half_v_mm"],48.)
            self.assertEqual(p["station_id"],layer["station_group"])
        self.assertGreater(layout["metadata"]["host_diagnostics"]["inclined_overhang_modules"],0)

    def test_overlap_is_3d_with_cross_layer_and_touching_not_interior(self):
        a = dict(module_id=1,layer_id="one",level=0,subsystem="pixel",center_mm=[0.,0.,0.],
                 u=[1.,0.,0.],v=[0.,1.,0.],n=[0.,0.,1.],half_u_mm=2.,half_v_mm=2.,half_w_mm=.5)
        b = copy.deepcopy(a)
        b.update(module_id=2,layer_id="two",center_mm=[0.,0.,1.])
        self.assertFalse(_obb_overlap(a,b))
        b["center_mm"][2]=.9
        self.assertTrue(_obb_overlap(a,b))
        d = body_overlap_diagnostics(dict(bodies=[a,b]))
        self.assertEqual(d["overlapping_body_pairs"],1)
        self.assertEqual(d["cross_layer_pairs"],1)
        self.assertEqual(d["same_layer_same_level_pairs"],0)

    def test_clearance_variants_clear_all_trial_boxes_and_host(self):
        for candidate in ("cobe", "pint"):
            for variant in ("hybrid_clearance", "staggered_clearance"):
                with self.subTest(candidate=candidate,variant=variant):
                    layout = generate_layout(candidate,variant)
                    self.assertEqual(body_overlap_diagnostics(layout)["overlapping_body_pairs"],0)
                    self.assertEqual(layout["metadata"]["host_diagnostics"]["host_overflow_modules"],0)

    def test_nonphysical_sensor_inputs_rejected(self):
        models = load_models()
        models["pixel"]["guard_mm"] = -.1
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            generate_layout(fixture(),"flat",models=models)
        models = load_models()
        models["long_strip"]["separation_mm"] = .1
        with self.assertRaisesRegex(ValueError,"separation"):
            generate_layout(fixture(),"flat",models=models)

    def test_host_overflow_not_silently_cropped(self):
        custom = fixture("long_strip","disc")
        custom["layers"][0].update(r_min_m=1.100,r_max_m=1.140,z_m=3.149)
        layout = generate_layout(custom,"staggered")
        self.assertGreater(layout["metadata"]["host_diagnostics"]["host_overflow_modules"],0)
        self.assertEqual(layout["modules"][0]["half_u_mm"],48.)


if __name__ == "__main__":
    unittest.main()
