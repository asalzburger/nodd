import copy
import importlib.util
import json
import math
from pathlib import Path
import unittest

import numpy as np

SPEC=importlib.util.spec_from_file_location('eta_study',Path(__file__).with_name('study.py'))
study=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


class EtaApertureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.own,cls.support,cls.cfg,cls.limits=study.inputs()

    def test_zero_field_limit_and_vertex_box(self):
        cfg=copy.deepcopy(self.own);cfg['max_abs_field_T']=0.
        self.assertAlmostEqual(study.inner_bound(3070.,cfg),(3070.-150.)/math.sinh(4.)-math.sqrt(2))
        self.assertEqual(study.inner_bound(-3070.,cfg),study.inner_bound(3070.,cfg))

    def test_continuous_bound_against_helix_positions(self):
        for eta in np.linspace(2.,4.,9):
          for field in [0.,2.,3.,4.]:
           for pt in [1.,2.,100.]:
            for charge in [-1.,0.,1.]:
             for phi in np.linspace(-math.pi,math.pi,7):
                t=dict(eta=float(eta),phi=float(phi),field_T=field,pt_GeV=pt,charge=charge,origin_mm=[1.,-1.,150.])
                for z in self.cfg['positive_disc_datums_mm']:
                    arc=(z-150.)/math.sinh(eta)
                    self.assertGreaterEqual(math.hypot(*study.intersections.positions(t,arc)[:2])+1e-10,study.inner_bound(z,self.own))

    def test_half_turn_domain_is_enforced(self):
        bad=copy.deepcopy(self.own);bad['pt_min_GeV']=0.001
        with self.assertRaisesRegex(ValueError,'half-turn'):
            study.inner_bound(3070.,bad)

    def test_active_rectangle_maximum_requires_corners(self):
        patch=dict(center_mm=[40.,0.,3000.],u=[0.,1.,0.],v=[1.,0.,0.],half_u_mm=10.,half_v_mm=9.6)
        self.assertAlmostEqual(max(math.hypot(*c[:2]) for c in study.corners(patch)),math.hypot(49.6,10.))

    def test_removal_preserves_first_retained_ring_witness(self):
        for name in study.VARIANTS:
            full,rings=study.placed(name,3070.,self.cfg)
            removed=study.prefix(study.ring_screens(full,rings,self.cfg,self.own))
            kept=[m for m in full if m['row'] not in removed]
            row=next(r['row'] for r in rings if r['row'] not in removed)
            t=study.first_retained_witness(full,row,self.cfg,self.own)
            retained=dict(modules=study.baseline.radial.active_patches(kept,self.cfg))
            hits=study.intersections.track_sensor_hits(retained,[t],return_patch_hits=True,host_radius_mm=234.)[0]
            self.assertIn(t['target_patch_id'],hits)
            unsafe=dict(modules=[p for p in retained['modules'] if p['row']!=row])
            lost=study.intersections.track_sensor_hits(unsafe,[t],return_patch_hits=True,host_radius_mm=234.)[0]
            self.assertNotIn(t['target_patch_id'],lost)
            self.assertTrue(all(m in full for m in kept))

    def test_fields_and_transverse_vertices_make_bound_stricter(self):
        self.assertLess(study.inner_bound(3070.,self.own),study.inner_bound(3070.,self.own,'straight-on-axis'))
        self.assertLess(study.inner_bound(3070.,self.own,'all-pt-half-turn'),study.inner_bound(3070.,self.own))

    def test_baseline_input_pins(self):
        self.assertEqual(self.own['pt_min_GeV'],1.)
        self.assertEqual(self.own['eta_max'],4.)
        self.assertEqual(self.limits['plate_outer_mm'],188.5)

    def test_retained_artifacts_and_matched_native_evidence(self):
        directory=study.ROOT/'docs/validation/DES-018'
        manifest=json.loads((directory/'artifacts.json').read_text())
        for name,wanted in manifest['artifact_sha256'].items():
            self.assertEqual(study.digest(directory/name),wanted,name)
        for name,wanted in manifest['producer_sha256'].items():
            self.assertEqual(study.digest(study.ROOT/name),wanted,name)
        screening=json.loads((directory/'screening.json').read_text())
        native=json.loads((directory/'acts.json').read_text())
        for name in study.VARIANTS:
            result=screening['variants'][name]
            self.assertEqual(result['removed_chips_all_18'],424)
            self.assertTrue(result['matched_coverage']['all_in_scope_patch_hits_preserved'])
            self.assertEqual(native['variants'][name]['changed_in_scope_hit_sets'],[])
            self.assertTrue(all(v['passed'] for v in native['variants'][name]['audits'].values()))
            self.assertTrue(all(v['passed'] for v in native['variants'][name]['exhaustive'].values()))

    def test_heterogeneous_reference_service_savings(self):
        screening=json.loads((study.ROOT/'docs/validation/DES-018/screening.json').read_text())
        original=json.loads((study.ROOT/'docs/validation/DES-017/screening.json').read_text())
        # First8 discs lose7 complete chip rows: cable savings212+220+346,
        # with2 circuits/ring and both4mm pipe legs. Disc9 is the bypass control.
        removed_demand=778.+7*2*2*math.pi*2**2
        for name in study.VARIANTS:
            before=next(s for s in original['variants'][name]['services']['scenarios'] if s['scenario']=='reference')['end_trunks'][0]['after_disc_8_demand_mm2']
            after=next(s for s in screening['variants'][name]['accumulated_services']['scenarios'] if s['scenario']=='reference')['sides'][0]['first_eight_disc_demand_mm2']
            self.assertAlmostEqual(before-after,removed_demand)


if __name__=='__main__':
    unittest.main()
