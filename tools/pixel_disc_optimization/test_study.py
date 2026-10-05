"""Independent area, containment, finite-z and physical-envelope controls."""
import copy
import json
from pathlib import Path
import unittest
from shapely.geometry import box
import study


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg=json.loads(Path(study.__file__).with_name('inputs.json').read_text())

    def test_overlap_counts_repeated_silicon_not_union_or_guard_as_active(self):
        cfg=dict(self.cfg,annulus_mm=[.1,10.])
        r=study.metrics([box(0,0,2,2),box(1,0,3,2)],cfg)
        self.assertAlmostEqual(r['summed_mm2'],8)
        self.assertAlmostEqual(r['union_mm2'],6)
        self.assertAlmostEqual(r['overlap_over_union_percent'],100/3)
        self.assertAlmostEqual(r['overlap_over_installed_percent'],25)
        same=study.metrics([box(0,0,2,2)]*3,cfg)
        self.assertAlmostEqual(same['overlap_over_union_percent'],200)

    def test_circle_superset_rejects_a_thin_outer_gap(self):
        cfg=dict(self.cfg,annulus_mm=[1.,10.])
        self.assertGreater(study.metrics([box(-9.999,-10,9.999,10)],cfg)['uncovered_annulus_superset_mm2'],0)
        self.assertEqual(study.metrics([box(-11,-11,11,11)],cfg)['uncovered_annulus_superset_mm2'],0)

    def test_continuous_vertex_certificate_and_deliberate_hole(self):
        cfg=dict(self.cfg,annulus_mm=[1.,5.],active_mm=[20.,20.],luminous_half_z_mm=2.,certificate_max_depth=4)
        module=dict(center_mm=[0.,0.,12.],u=[1.,0.,0.],v=[0.,1.,0.])
        self.assertTrue(study.coverage_certificate([module],cfg,10.)['passed'])
        self.assertFalse(study.coverage_certificate([dict(module,center_mm=[20.,0.,12.])],cfg,10.)['passed'])

    def test_body_periphery_can_collide_when_active_matrices_clear(self):
        cfg=dict(self.cfg,body_mm=[20.4,21.4])
        a=dict(center_mm=[0.,0.,10.],u=[1.,0.,0.],v=[0.,1.,0.],level=0,local_z_mm=4.1)
        b=dict(a,center_mm=[0.,20.,10.])
        self.assertGreater(study.body_polygon(a,cfg).intersection(study.body_polygon(b,cfg)).area,0)
        self.assertEqual(study.rectangle(a['center_mm'],a['u'],a['v'],10,9.6).intersection(study.rectangle(b['center_mm'],b['u'],b['v'],10,9.6)).area,0)
        self.assertTrue(study.body_screen([a,b],cfg)['overlaps_or_insufficient_gap'])
        b['center_mm'][2]=11.2
        self.assertFalse(study.body_screen([a,b],cfg)['overlaps_or_insufficient_gap'])

    def test_selected_layout_clears_bodies_and_certifies_first_disc(self):
        cfg=self.cfg;raw=study.candidates(cfg,.45);placed=study.stagger(raw,cfg,cfg['disc_datum_mm'])
        body=study.body_screen(placed,cfg)
        self.assertFalse(body['overlaps_or_insufficient_gap'])
        self.assertGreaterEqual(body['minimum_beam_radius_mm'],cfg['beam_clearance_radius_mm'])
        self.assertTrue(study.coverage_certificate(placed,cfg,cfg['disc_datum_mm'])['passed'])
        r=study.metrics(study.project(placed,cfg,cfg['disc_datum_mm'],guard=cfg['sensor_guard_mm']),cfg)
        self.assertLessEqual(r['overlap_over_union_percent'],10)
        self.assertLessEqual(r['annular_overlap_over_union_percent'],10)
        # The inherited larger guard is a physical design control, not acceptance.
        control=study.metrics(study.project(placed,cfg,cfg['disc_datum_mm'],guard=.5),cfg)
        self.assertGreater(control['overlap_over_union_percent'],10)

    def test_far_disc_has_same_module_indices_and_passes_limits(self):
        raw=study.candidates(self.cfg,.45);near=study.stagger(raw,self.cfg,615.2);far=study.stagger(raw,self.cfg,3070.)
        self.assertEqual([m['id'] for m in near],[m['id'] for m in far])
        self.assertFalse(study.body_screen(far,self.cfg)['overlaps_or_insufficient_gap'])
        r=study.metrics(study.project(far,self.cfg,3070.,guard=self.cfg['sensor_guard_mm']),self.cfg)
        self.assertLessEqual(r['annular_overlap_over_union_percent'],10)
        self.assertTrue(study.coverage_certificate(far,self.cfg,3070.)['passed'])

if __name__=='__main__':unittest.main()
