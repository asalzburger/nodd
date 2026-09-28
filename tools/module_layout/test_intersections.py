"""Synthetic numerical controls, never production detector parameters."""

import math
import unittest

import numpy as np

from intersections import (KAPPA_MM, SurfaceIndex, evaluate, ideal_layer_hits,
                           positions, track_sensor_hits, traversal_limit)


def track(**overrides):
    return dict(dict(origin_mm=[0., 0., 0.], eta=0., phi=0., charge=1,
                     pt_GeV=1., field_T=0.), **overrides)


def patch(name="fixture", center=(100., 0., 0.), u=(0., 1., 0.), v=(0., 0., 1.),
          hu=10., hv=10., **extra):
    return dict(id=name, sensor_id=name, module_id=name, center_mm=list(center),
                u=list(u), v=list(v), half_u_mm=hu, half_v_mm=hv,
                layer_id="fixture-layer", station_id="fixture-layer", subsystem="pixel",
                region="barrel", face=0, **extra)


class ExactControls(unittest.TestCase):
    def test_straight_finite_bounds_and_forward_only(self):
        layout = {"modules": [patch(), patch("behind", (-100., 0., 0.)),
                               patch("miss", (100., 30., 0.))]}
        self.assertEqual(track_sensor_hits(layout, [track()]), [["fixture"]])
        self.assertEqual(track_sensor_hits(layout, [track(phi=math.atan(.1))]), [["fixture"]])
        self.assertEqual(track_sensor_hits(layout, [track(phi=math.atan(.10001))]), [[]])

    def test_shifted_origin_and_longitudinal_motion(self):
        ray = track(origin_mm=[1., .5, -150.], eta=math.asinh(1.))
        layout = {"modules": [patch(center=(100., .5, -51.), hu=.01, hv=.01)]}
        self.assertEqual(track_sensor_hits(layout, [ray]), [["fixture"]])
        np.testing.assert_allclose(positions(ray, 99.), [100., .5, -51.], atol=1e-12)

    def test_zero_field_limit(self):
        ray = track(eta=.6, phi=1.2)
        bent = dict(ray, field_T=1e-12)
        np.testing.assert_allclose(positions(ray, [0., 100., 900.]),
                                   positions(bent, [0., 100., 900.]), atol=1e-9)

    def test_charge_sign_lorentz_convention(self):
        positive = track(field_T=3.)
        negative = dict(positive, charge=-1)
        a, b = positions(positive, 500.), positions(negative, 500.)
        self.assertLess(a[1], 0.)
        self.assertGreater(b[1], 0.)
        self.assertAlmostEqual(a[0], b[0])
        self.assertAlmostEqual(a[1], -b[1])
        layout = {"modules": [patch("positive", a, hu=.01, hv=.01),
                               patch("negative", b, hu=.01, hv=.01)]}
        self.assertEqual(track_sensor_hits(layout, [positive, negative]), [["positive"], ["negative"]])

    def test_tilted_general_plane_root_and_residual(self):
        ray = track(field_T=3., phi=.31, eta=1.2, origin_mm=[1., .7, 113.])
        expected = 340.
        center = positions(ray, expected)
        u = np.array([.3, .8, -.2]); u /= np.linalg.norm(u)
        v = np.cross(u, [.1, -.2, .9]); v /= np.linalg.norm(v)
        layout = {"modules": [patch(center=center, u=u, v=v, hu=.1, hv=.1)]}
        actual = SurfaceIndex(layout).hits(ray)
        self.assertEqual(len(actual), 1)
        self.assertAlmostEqual(actual[0][1], expected, places=6)
        self.assertLess(abs(np.dot(positions(ray, actual[0][1])-center, np.cross(u,v))), 1e-6)

    def test_two_roots_even_when_endpoint_residual_same_sign(self):
        # Circle radius 100 mm; x=50 mm is crossed twice before the half-turn.
        ray = track(field_T=1., pt_GeV=100*KAPPA_MM)
        second_s = 100.*5*math.pi/6
        center = positions(ray, second_s)
        layout = {"modules": [patch(center=center, hu=.01, hv=1.)]}
        hits = SurfaceIndex(layout).hits(ray)
        self.assertEqual(len(hits), 1)
        self.assertAlmostEqual(hits[0][1], second_s, places=6)

    def test_tangent_plane_isolated_contact(self):
        ray = track(field_T=1., pt_GeV=100*KAPPA_MM)
        center = positions(ray, 50*math.pi)
        layout = {"modules": [patch(center=center, hu=.01, hv=1.)]}
        hits = SurfaceIndex(layout).hits(ray)
        self.assertEqual(len(hits), 1)
        self.assertAlmostEqual(hits[0][1], 50*math.pi, places=5)

    def test_voxel_broadphase_matches_exhaustive_curved_tilted(self):
        rng = np.random.default_rng(105)
        modules = []
        rays = [track(field_T=3., charge=charge, eta=eta, phi=.7,
                      origin_mm=[1., 1., 150.]) for charge in (-1, 1) for eta in (0., 1., 3.)]
        for i, ray in enumerate(rays):
            for j, s in enumerate(np.linspace(5., traversal_limit(ray)*.999, 9)):
                u = rng.normal(size=3); u /= np.linalg.norm(u)
                v = np.cross(u, rng.normal(size=3)); v /= np.linalg.norm(v)
                modules.append(patch(f"p{i}-{j}", positions(ray, s), u, v, hu=.05, hv=.05))
        index = SurfaceIndex({"modules": modules}, voxel_mm=47., segment_mm=150.)
        for ray in rays:
            self.assertEqual([i for i,s in index.hits(ray)],
                             [i for i,s in index.hits(ray, all_surfaces=True)])

    def test_host_exit_and_curling_limit(self):
        self.assertAlmostEqual(traversal_limit(track()), 1140.)
        self.assertAlmostEqual(traversal_limit(track(eta=math.asinh(10.))), 315.)
        curved = track(field_T=3.)
        limit = traversal_limit(curved)
        self.assertAlmostEqual(np.linalg.norm(positions(curved, limit)[:2]), 1140., places=7)
        self.assertAlmostEqual(traversal_limit(track(field_T=1.,pt_GeV=100*KAPPA_MM)), 100*math.pi)

    def test_ideal_cylinder_disks_displaced_helix(self):
        ray = track(field_T=3., eta=.7, origin_mm=[1., .5, -150.])
        point = positions(ray, 500.)
        layers = [dict(id="c",subsystem="pixel",kind="cylinder",r_m=np.linalg.norm(point[:2])/1000,
                       z_min_m=point[2]/1000-.0001,z_max_m=point[2]/1000+.0001),
                  dict(id="d",subsystem="pixel",kind="disc",z_m=point[2]/1000,
                       r_min_m=np.linalg.norm(point[:2])/1000-.0001,
                       r_max_m=np.linalg.norm(point[:2])/1000+.0001)]
        self.assertEqual(ideal_layer_hits(layers, ray), ["c", "d"])

    def test_inclined_ideal_hit_and_unsupported_orientation_rejected(self):
        normal = math.sqrt(.5)
        layer = dict(id="inclined",subsystem="pixel",kind="inclined_ring",
                     normal_r=normal,normal_z=normal,r0_m=.1,z0_m=.1,
                     r1_m=.08,z1_m=.12,r2_m=.12,z2_m=.08)
        self.assertEqual(ideal_layer_hits([layer],track(eta=math.asinh(1.))), ["inclined"])
        reverse = dict(layer,normal_z=-normal,z1_m=.08,z2_m=.12)
        with self.assertRaisesRegex(ValueError,"orientation"):
            ideal_layer_hits([reverse],track(eta=math.asinh(1.)))
        with self.assertRaisesRegex(ValueError,"endpoints"):
            ideal_layer_hits([dict(layer,r1_m=.07)],track(eta=math.asinh(1.)))

    def test_physical_sensor_dedup_and_same_module_stereo_pair(self):
        modules = [dict(patch("a",center=(100.,0.,0.)),sensor_id="shared"),
                   dict(patch("b",center=(100.,0.,0.)),sensor_id="shared")]
        for module_id, y in (("complete",0.), ("incomplete",30.)):
            for face in (0,1):
                modules.append(dict(patch(f"{module_id}-{face}",center=(200.+face, y*face,0.)),
                                    subsystem="long_strip", layer_id="long",station_id="long",
                                    module_id=module_id,face=face))
        report = evaluate({"modules":modules}, [track()])
        self.assertEqual(report["per_track"]["sensor_hits"], [4])
        self.assertEqual(report["per_track"]["complete_long_strip_pairs"], [1])
        self.assertEqual(report["per_track"]["orphan_long_strip_faces"], [1])
        self.assertEqual(report["per_track"]["per_subdetector"]["pixel"]["orphan_long_strip_faces"], [0])
        self.assertEqual(report["per_track"]["stations"], [2])

    def test_stereo_parallax_loses_pair(self):
        ray = track(eta=math.asinh(1.))
        modules = [dict(patch("front",center=(100.,0.,100.),hv=.5),
                        subsystem="long_strip",module_id="pair",face=0),
                   dict(patch("back",center=(103.,0.,100.),hv=.5),
                        subsystem="long_strip",module_id="pair",face=1)]
        report = evaluate({"modules":modules}, [ray])
        self.assertEqual(report["per_track"]["sensor_hits"], [1])
        self.assertEqual(report["per_track"]["complete_long_strip_pairs"], [0])
        self.assertEqual(report["per_track"]["orphan_long_strip_faces"], [1])
        self.assertEqual(report["per_track"]["stations"], [0])

    def test_faces_from_different_pairs_do_not_form_a_station(self):
        modules = [dict(patch("left",center=(100.,0.,0.)),subsystem="long_strip",module_id="left",face=0),
                   dict(patch("right",center=(101.,0.,0.)),subsystem="long_strip",module_id="right",face=1)]
        report = evaluate({"modules":modules}, [track()])
        self.assertEqual(report["per_track"]["sensor_hits"], [2])
        self.assertEqual(report["per_track"]["complete_long_strip_pairs"], [0])
        self.assertEqual(report["per_track"]["orphan_long_strip_faces"], [2])
        self.assertEqual(report["per_track"]["stations"], [0])

    def test_extra_hit_cannot_hide_different_ideal_station_hole(self):
        layers = [dict(id=lid,subsystem="pixel",kind="cylinder",r_m=radius,
                       z_min_m=-.1,z_max_m=.1) for lid,radius in (("miss",.1),("hit",.2))]
        modules = [dict(patch("one",center=(200.,0.,0.)),layer_id="hit",station_id="hit"),
                   dict(patch("extra",center=(300.,0.,0.)),layer_id="extra",station_id="extra")]
        report = evaluate({"modules":modules,"layers":layers}, [track()])
        self.assertEqual(report["per_track"]["stations"], [2])
        self.assertEqual(report["per_track"]["ideal_stations"], [2])
        self.assertEqual(report["per_track"]["missing_stations"], [1])
        self.assertEqual(report["per_track"]["extra_stations"], [1])


if __name__ == "__main__":
    unittest.main()
