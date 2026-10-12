"""Mounting proposal controls; test perturbations never alter retained geometry."""
import copy
import json
import math
from pathlib import Path
import unittest

from mounting import check_mounts, make_mounts
from outward import load_layout


class MountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads(Path(__file__).with_name('inputs.json').read_text())
        cls.settings=json.loads(Path(__file__).with_name('mounting.json').read_text())
        cls.layout=load_layout(cls.config)
        cls.mounts=make_mounts(cls.layout,cls.config,cls.settings)
        cls.result=check_mounts(cls.layout,cls.config,cls.settings,cls.mounts)

    def test_inventory_contact_and_unchanged_baseline(self):
        original=copy.deepcopy(self.layout)
        assembly,boxes,rings,feet,layers=make_mounts(self.layout,self.config,self.settings)
        self.assertEqual(original,self.layout)
        self.assertEqual(len(rings),4*6)
        self.assertEqual(len(feet),(12+22+18+30)*6)
        self.assertEqual(sum(r['role']=='end mounting' for r in rings),8)
        for f in feet:
            spine=next(b for b in boxes if b['module_id']==f['module_id'] and b['kind']=='spine')
            back=sum(spine['center_mm'][i]*spine['n'][i] for i in range(2))+spine['half_w_mm']
            self.assertAlmostEqual(back,f['back_normal_mm'])
            self.assertLess(f['back_normal_mm'],f['ring_inner_mm'])
        self.assertEqual(self.result['maximum_station_pitch_mm'],220.)
        self.assertEqual(self.result['end_ring_to_service_axial_gap_mm'],5.)

    def test_nominal_fit_and_service_intersection_control(self):
        self.assertFalse(any(self.result['nominal_conflicts'].values()))
        changed=copy.deepcopy(self.mounts)
        # Test-only ring at the superseded +560 mm station occupies the service bay.
        ring=next(r for r in changed[2] if r['layer_id']=='A-pixel-B4' and r['z_mm']==546.)
        ring.update(z_mm=560.,z_min_mm=556.,z_max_mm=564.)
        result=check_mounts(self.layout,self.config,self.settings,changed)
        self.assertTrue(result['nominal_conflicts']['ring_routes'])
        self.assertLess(result['end_ring_to_service_axial_gap_mm'],0.)

    def test_old_end_positions_and_oversize_feet_rejected(self):
        old=dict(self.settings,bearing_z_mm=self.config['bearing_z_mm'],section_z_mm=112.,axial_locator_z_mm=-560.)
        with self.assertRaisesRegex(ValueError,'past the continuous stave'):
            make_mounts(self.layout,self.config,old)
        with self.assertRaisesRegex(ValueError,'narrow spine'):
            make_mounts(self.layout,self.config,dict(self.settings,foot_tangential_width_mm=11.))

    def test_curved_foot_mass_against_numerical_integration(self):
        # Independent trapezoidal integral; 1000 steps is a test quadrature choice.
        for lid in ['A-pixel-B1','A-pixel-B4']:
            f=next(f for f in self.mounts[3] if f['layer_id']==lid)
            a=f['half_u_mm']; r=f['ring_inner_mm']; steps=1000; du=2*a/steps
            heights=[math.sqrt(r*r-(-a+i*du)**2)-f['back_normal_mm'] for i in range(steps+1)]
            volume=(sum(heights)-.5*(heights[0]+heights[-1]))*du*2*f['half_v_mm']
            self.assertAlmostEqual(volume*self.config['density_g_cm3']['CFRP']/1000,f['mass_g'],places=7)


if __name__=='__main__':unittest.main()
