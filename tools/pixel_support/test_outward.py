"""Controls for orientation, exact section selection and clearance screening."""
import copy
import json
import math
from pathlib import Path
import unittest

from outward import envelopes, gap, load_layout, section, stave_span, _obb_overlap


class OutwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path(__file__).with_name('inputs.json').read_text())
        cls.settings = json.loads(Path(__file__).with_name('outward.json').read_text())
        cls.layout = load_layout(cls.config)
        cls.assembly = section(cls.layout, cls.config, cls.settings)

    def test_outward_mount_preserves_sensitive_positions(self):
        original = copy.deepcopy(self.layout)
        bodies, sensors, parts, tubes = section(self.layout, self.config, self.settings)
        self.assertEqual(self.layout, original)
        self.assertEqual(len(bodies), 12+22+18+30)
        self.assertEqual(len(tubes), 2*len(bodies))
        self.assertEqual(len(sensors), 12+22+2*(18+30))
        for p in parts:
            b = next(b for b in bodies if b['module_id'] == p['module_id'])
            displacement = sum((p['center_mm'][i]-b['center_mm'][i])*b['n'][i] for i in range(3))
            self.assertGreaterEqual(displacement-p['half_w_mm']+1e-10, b['half_w_mm'])
        for tube in tubes:
            core = next(p for p in parts if p['module_id'] == tube['module_id'] and p['kind'] == 'core')
            for axis, half in [('u', 'half_u_mm'), ('n', 'half_w_mm')]:
                offset = abs(sum((tube['center_mm'][i]-core['center_mm'][i])*core[axis][i] for i in range(2)))
                self.assertLess(offset+tube['outer_radius_mm'], core[half])

    def test_section_gaps_and_nonuniform_columns_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'exactly one module'):
            section(self.layout, self.config, dict(self.settings, section_z_mm=0.))
        changed = copy.deepcopy(self.layout)
        body = next(b for b in changed['bodies'] if b['subsystem'] == 'pixel' and b['region'] == 'barrel')
        body['center_mm'][0] += .1  # Test-only perturbation along one stave.
        with self.assertRaisesRegex(ValueError, 'z-uniform'):
            section(changed, self.config, self.settings)
        with self.assertRaisesRegex(ValueError, 'Baseline changed'):
            load_layout(dict(self.config, baseline_sha256='0'*64))

    def test_outward_full_width_spine_collision_control(self):
        bodies = self.assembly[0]
        narrow = envelopes(bodies, self.config)
        self.assertFalse(any(_obb_overlap(p, b) for p in narrow for b in bodies
                             if p['module_id'] != b['module_id']))
        cfg = copy.deepcopy(self.config)
        cfg['families']['single']['spine_mm'] = 23.
        cfg['families']['quad']['spine_mm'] = 43.2
        broad = envelopes(bodies, cfg)
        self.assertTrue(any(_obb_overlap(p, b) for p in broad for b in bodies
                            if p['module_id'] != b['module_id']))

    def test_passive_span_rejects_module_overhang(self):
        # Test-only two bodies occupying [-5, 5]; passive endpoints are independent.
        bodies=[dict(center_mm=[0,0,z],half_v_mm=1,layer_id='test') for z in [-4,4]]
        self.assertEqual(stave_span(bodies,{}),(-5,5))
        self.assertEqual(stave_span(bodies,{'passive_stave_z_mm':{'test':[-6,7]}}),(-6,7))
        for span in [[-4,7],[-6,4],[float('nan'),7],[7,-6]]:
            with self.assertRaisesRegex(ValueError,'contain every occupied'):
                stave_span(bodies,{'passive_stave_z_mm':{'test':span}})

    def test_gap_against_rotated_analytic_boxes(self):
        # Test-only two-mm squares: gaps are one mm and sqrt(2) mm.
        a = dict(center_mm=[0., 0., 0.], u=[1., 0., 0.], v=[0., 0., 1.],
                 n=[0., 1., 0.], half_u_mm=1., half_v_mm=1., half_w_mm=1.)
        for angle in [0., .713]:
            def rotated(box):
                box = copy.deepcopy(box)
                for k in ['center_mm', 'u', 'n']:
                    x, y, z = box[k]
                    box[k] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle)+y*math.cos(angle), z]
                return box
            for centre, expected in [([3., 0., 0.], 1.), ([3., 3., 0.], math.sqrt(2)), ([1., 0., 0.], 0.)]:
                b = dict(a, center_mm=centre)
                self.assertAlmostEqual(gap(rotated(a), rotated(b), 1e-7), expected)


if __name__ == '__main__':
    unittest.main()
