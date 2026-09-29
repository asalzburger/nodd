"""Meaningful geometry-contract tests for the unsigned finite-module prototype."""
import copy
import hashlib
import json
from collections import defaultdict
import math
import unittest

from tools.module_layout.geometry import (
    _obb_overlap, body_overlap_diagnostics, cross, dot, generate_layout,
    load_models, norm, summarize, LEGACY_VARIANTS, REVIEW_VARIANTS, REVIEW_MODELS_PATH,
    LAYOUTS_PATH,
)


def fixture(subsystem="pixel", kind="cylinder"):
    layer = dict(id="test-layer",station_group="test-station",subsystem=subsystem,kind=kind)
    if kind == "cylinder":
        layer.update(r_m=.100,z_min_m=-.02,z_max_m=.02)
    elif kind == "disc":
        layer.update(r_min_m=.100,r_max_m=.200,z_m=.500)
    return dict(id="test-only",layers=[layer])


LEGACY_OUTPUT_SHA256 = {'cobe/flat': '8d651e76d531083aac717d9ef64b66b8bdc74ea62d12560714b38e4508e54392', 'cobe/staggered': '2f111da7b00b85d1f026c9ad47d9e846b16b6f546a570eb666c961111c9fc27a', 'cobe/tilted': '110be76b9edcedb695a0c353a9134b99671981e94dfcc53432865cbaf4a5a82e', 'cobe/hybrid': '65b551c3d8061e4c44d907b3cafdb50b55a59b184561910d74928708f0b29ba7', 'cobe/hybrid_clearance': 'ac70abc230d41d8d7e92a430de38b0f651c4470ebf27421689d885453963b55c', 'cobe/staggered_clearance': 'e6b52b0bae55f24aaa4bc0c2bca76e0654a2d95acf3081ad04542d7347b302d2', 'pint/flat': '02a498f7082ce503e608744ea3511d4a8efb5d34e30956441178b844a3f2ea7c', 'pint/staggered': 'b22d77924b272f9cf2a57b3e036d41f100f152459425d1dcbbd089af2cb01ae9', 'pint/tilted': 'ffbc2e12a07a91f09f5d25c88cc4f9a9e9d33895fe5104d13542868222da64b2', 'pint/hybrid': 'cff4dec3ddf4bcc890ce9c3d4b44db96c4e265cb854506cfe6f1013cda2de796', 'pint/hybrid_clearance': '039cbda6be1f6b611bf2d30233be0b8a63bcc8bc3cd9e7f08c9b2e5f8a24214f', 'pint/staggered_clearance': '3fe7b1e59cff87a984585e3251358ab0f300f98a2a2c3ba72ed115dbb1cc930d'}


class FiniteGeometryTest(unittest.TestCase):
    def test_legacy_output_bytes_preserved(self):
        # Captured before the reviewer-directed implementation. These hashes cover
        # every patch/body/metadata field, including all previously rejected controls.
        for candidate in ("cobe", "pint"):
            for variant in LEGACY_VARIANTS:
                with self.subTest(candidate=candidate,variant=variant):
                    value = json.dumps(generate_layout(candidate,variant),sort_keys=True,separators=(",", ":"))
                    self.assertEqual(hashlib.sha256(value.encode()).hexdigest(),LEGACY_OUTPUT_SHA256[candidate+"/"+variant])

    def test_review_layouts_clear_boxes_and_keep_nominal_cobe_layers(self):
        expected = next(c["layers"] for c in json.loads(LAYOUTS_PATH.read_text())["candidates"] if c["id"]=="cobe")
        for variant in REVIEW_VARIANTS:
            with self.subTest(variant=variant):
                layout = generate_layout("cobe",variant)
                self.assertEqual(layout["layers"],expected)
                self.assertEqual(body_overlap_diagnostics(layout)["overlapping_body_pairs"],0)
                self.assertEqual(layout["metadata"]["host_diagnostics"]["host_overflow_modules"],0)

    def test_review_no_z_staves_keep_phi_radius_tilt_and_body_clearance(self):
        layout = generate_layout("cobe","review_default")
        grouped = defaultdict(list)
        for body in layout["bodies"]:
            if body["region"] == "barrel" and body["subsystem"] in ("pixel", "long_strip"):
                grouped[body["layer_id"],body["col"]].append(body)
        self.assertTrue(grouped)
        for bodies in grouped.values():
            reference = bodies[0]
            ordered = sorted(bodies,key=lambda b:b["center_mm"][2])
            for body in bodies:
                self.assertEqual(body["center_mm"][:2],reference["center_mm"][:2])
                self.assertEqual(body["u"],reference["u"])
                self.assertEqual(body["n"],reference["n"])
                self.assertEqual(body["radial_offset_mm"],reference["radial_offset_mm"])
            for a,b in zip(ordered,ordered[1:]):
                self.assertGreaterEqual(b["center_mm"][2]-a["center_mm"][2],a["half_v_mm"]+b["half_v_mm"]+.2-1e-9)
        for name,p in layout["metadata"]["review_placement"]["layers"].items():
            if p.get("z_stagger") is False:
                self.assertEqual(p["z_row_policy"],"fit_endpoints")
                for actual,nominal in zip(p["unrotated_active_z_extent_mm"],p["nominal_z_extent_mm"]):
                    self.assertAlmostEqual(actual,nominal)

    def test_review_tilt_uses_common_phi_radius_instead_of_added_phi_shells(self):
        layout = generate_layout("cobe","review_short_tilt")
        grouped = defaultdict(list)
        for body in layout["bodies"]:
            if body["region"] == "barrel" and body["subsystem"] in ("short_strip", "long_strip"):
                grouped[body["layer_id"],body["row"]].append(body)
        for bodies in grouped.values():
            radii = [math.hypot(*b["center_mm"][:2]) for b in bodies]
            self.assertAlmostEqual(min(radii),max(radii))
            for body in bodies:
                radial = [body["center_mm"][0]/radii[0],body["center_mm"][1]/radii[0],0.]
                self.assertAlmostEqual(dot(body["n"],radial),math.cos(math.radians(12.)))
                self.assertEqual(body["phi_method"],"tilted")
                if body["subsystem"] == "long_strip":
                    self.assertEqual(body["radial_offset_mm"],0.)

    def test_review_options_change_only_the_requested_subsystem(self):
        layouts = {v:generate_layout("cobe",v) for v in REVIEW_VARIANTS}
        def placements(layout, subsystem):
            # Counts can change preceding IDs; compare the physical placements.
            keys=("layer_id","center_mm","u","v","n","half_u_mm","half_v_mm","face")
            return [{key:m[key] for key in keys} for m in layout["modules"] if m["subsystem"]==subsystem]
        base = layouts["review_default"]
        self.assertEqual(placements(base,"short_strip"),placements(layouts["review_pixel_z"],"short_strip"))
        self.assertEqual(placements(base,"pixel"),placements(layouts["review_short_tilt"],"pixel"))
        for variant,layout in layouts.items():
            self.assertEqual(placements(base,"long_strip"),placements(layout,"long_strip"))
        self.assertEqual(placements(layouts["review_pixel_z"],"pixel"),placements(layouts["review_pixel_z_short_tilt"],"pixel"))
        self.assertEqual(placements(layouts["review_short_tilt"],"short_strip"),placements(layouts["review_pixel_z_short_tilt"],"short_strip"))

    def test_review_endcaps_preserve_previous_cleared_tiling(self):
        old,new=generate_layout("cobe","hybrid_clearance"),generate_layout("cobe","review_default")
        keys=("layer_id","center_mm","u","v","n","half_u_mm","half_v_mm","face","level")
        def ends(layout):
            return [{k:m[k] for k in keys} for m in layout["modules"] if m["region"]=="endcap"]
        self.assertEqual(ends(old),ends(new))

    def test_review_rejects_inclined_and_inconsistent_controls(self):
        with self.assertRaisesRegex(ValueError,"cobe"):
            generate_layout("pint","review_default")
        models=load_models(REVIEW_MODELS_PATH)
        models["review_placement"]["barrel"]["pixel"]["tilt_degrees"]=12.
        with self.assertRaisesRegex(ValueError,"tangential"):
            generate_layout("cobe","review_default",models=models)

    def test_rejected_fixed_pitch_control_exposes_barrel_endcap_collision(self):
        models=load_models(REVIEW_MODELS_PATH)
        models["review_placement"]["barrel"]["long_strip"]["z_row_policy"]="fixed_body_pitch_cover"
        layout=generate_layout("cobe","review_default",models=models)
        diagnostic=body_overlap_diagnostics(layout)
        self.assertGreater(diagnostic["cross_layer_pairs"],0)
        self.assertEqual(set(diagnostic["by_subsystem_pair"]),{"long_strip/long_strip"})
        self.assertEqual(layout["metadata"]["host_diagnostics"]["host_overflow_modules"],0)

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
