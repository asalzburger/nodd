"""Conservation and geometric regression controls for the isolated DES017 model."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

SPEC=importlib.util.spec_from_file_location('variant_model',Path(__file__).with_name('study.py'))
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.own,cls.cfg,cls.limits,cls.prior=m.inputs()
        cls.raw,cls.rings=m.raw_control(cls.cfg,cls.prior)

    def test_four_inner_rings_retained_and_shared_quad_sensor(self):
        raw,rings=m.mixed(self.raw,self.rings,[123.,160.],[23,29],[0.,.5])
        self.assertEqual(raw[:102],self.raw[:102])
        self.assertEqual(len(rings),6)
        patches=m.radial.active_patches(raw,self.cfg)
        self.assertEqual(len(patches),102+4*(23+29))
        self.assertEqual(len({p['sensor_id'] for p in patches}),len(raw))
        self.assertEqual(len({p['id'] for p in patches}),len(patches))

    def test_inactive_quad_cross_is_not_filled(self):
        raw,_=m.mixed(self.raw,self.rings,[123.,160.],[23,29],[0.,.5])
        quad=raw[102]
        patches=m.radial.active_patches([quad],self.cfg)
        polygons=[m.reference.rectangle(p['center_mm'],p['u'],p['v'],p['half_u_mm'],p['half_v_mm']) for p in patches]
        self.assertAlmostEqual(sum(p.area for p in polygons),4*20*19.2)
        center=m.Point(*quad['center_mm'][:2])
        self.assertFalse(any(p.covers(center) for p in polygons))

    def test_chip_row_circuits_not_physical_ring_circuits(self):
        raw,rings=m.mixed(self.raw,self.rings,[123.,160.],[23,29],[0.,.5])
        placed=m.radial.stagger(raw,self.cfg,self.cfg['disc_datum_mm'])
        c=m.cooling(placed,rings,self.cfg,self.own)
        self.assertEqual((c['number_tracks'],c['number_circuits'],c['feed_return_legs']),(8,16,32))
        self.assertEqual(sum(x['chips'] for x in c['circuits']),len(m.radial.active_patches(raw,self.cfg)))
        self.assertAlmostEqual(sum(x['nominal_W'] for x in c['circuits']),c['nominal_W'])
        self.assertTrue(all(x['outlet_quality']<=self.own['cooling']['quality_limit'] for x in c['circuits']))

    def test_stem_collision_is_found_below_a_higher_module(self):
        raw=copy.deepcopy(self.raw[:2]);raw[1]['center_mm']=raw[0]['center_mm'].copy()
        placed=m.radial.stagger(raw,self.cfg,self.cfg['disc_datum_mm'])
        s=m.support_screen(placed,self.cfg,self.limits,self.own)
        self.assertFalse(s['passed'])
        self.assertTrue(s['stem_lower_module_collisions'])

    def test_sheet_power_conservation_and_conductivity_scaling(self):
        a=m.sheet_reference.sheet_resistance(20.,19.2,6.,8.,0.,1000.,.3,.5,2/3)
        b=m.sheet_reference.sheet_resistance(20.,19.2,6.,8.,0.,500.,.3,.5,2/3)
        self.assertAlmostEqual(a['sink_power_W'],1.,places=8)
        self.assertAlmostEqual(b['max_K_W'],2*a['max_K_W'],places=8)

    def test_pickup_stack_increases_required_z_spacing(self):
        self.assertAlmostEqual(sum(self.own['pickup_mm'].values()),.45)
        self.assertAlmostEqual(self.cfg['level_spacing_mm']-self.cfg['body_thickness_mm']-sum(self.own['pickup_mm'].values()),.2)

    def test_retained_evidence_consistency_and_failed_controls(self):
        out=m.ROOT/'docs/validation/DES-017'
        manifest=json.loads((out/'artifacts.json').read_text())
        for path,expected in manifest['artifact_hashes'].items():
            self.assertEqual(m.reference.digest(out/path),expected,path)
        for path,expected in manifest['producer_hashes'].items():
            self.assertEqual(m.reference.digest(m.ROOT/path),expected,path)
        report=json.loads((out/'screening.json').read_text())
        native=json.loads((out/'acts.json').read_text())
        self.assertEqual(native['provenance']['screening_sha256'],m.reference.digest(out/'screening.json'))
        layouts=[json.loads((out/(name+'-layout.json')).read_text()) for name in ['eight-single','four-single-two-quad']]
        self.assertEqual(layouts[0]['raw_modules'][:102],layouts[1]['raw_modules'][:102])
        for name,v in report['variants'].items():
            self.assertTrue(v['all_18_support_pass'])
            self.assertTrue(v['all_18_interface_overlap_pass'])
            self.assertFalse(v['original_annulus_hermetic'])
            self.assertEqual(v['cooling']['feed_return_legs'],32)
            self.assertTrue(all(t['radial_contact_pass'] for t in v['cooling']['tracks']))
            self.assertGreater(v['guard_0p5mm_control']['overlap_over_union_percent'],20)
            self.assertTrue(native[name]['passed'])
            self.assertEqual(native[name]['active_patches'],18*v['chips'])
        failed=json.loads((out/'failed-outward-controls.json').read_text())
        self.assertTrue(all(not v['passed'] and v['stem_lower_module_collisions'] for v in failed['controls'].values()))
        refined=json.loads((out/'thermal-refined.json').read_text())
        for v in refined.values():
            self.assertTrue(v['all_stress_minus40_pass'])
            self.assertFalse(v['all_stress_minus35_pass'])
            for c in v['fine_control']:
                self.assertAlmostEqual(c['sink_power_W'],1.,places=8)
                self.assertLess(c['worst_stress_temperature_change_K'],.01)


if __name__=='__main__':unittest.main()
