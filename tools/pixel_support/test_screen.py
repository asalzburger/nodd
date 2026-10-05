import copy
import json
import unittest
from pathlib import Path
from screen import beam, run

class ScreeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg=json.loads(Path(__file__).with_name('inputs.json').read_text())
        cls.result=run(cls.cfg)

    def test_actual_chip_inventory_energy_conservation(self):
        # Independently count two inner sets of 47 singles and outer sets of 24 quads.
        self.assertEqual(self.result['totals']['modules'], (12+22)*47+(18+30)*24)
        chips=(12+22)*47+4*(18+30)*24
        self.assertAlmostEqual(self.result['totals']['nominal_power_W'],chips*2.688)
        for r in self.result['layers']:
            absorbed=(r['exit_quality_stress_imbalanced']-.1)*r['flow_per_circuit_g_s']*313.18
            self.assertAlmostEqual(absorbed,r['stave_stress_W']*2/3)
            self.assertLess(r['exit_quality_stress_imbalanced'],.45)
            self.assertLess(r['circuit_stress_imbalanced_W'],300)

    def test_changed_geometry_refuses_stale_evidence(self):
        cfg=copy.deepcopy(self.cfg);cfg['baseline_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Baseline changed'):run(cfg)

    def test_full_width_beams_detect_staggering_collision(self):
        cfg=copy.deepcopy(self.cfg)
        cfg['families']['single']['spine_mm']=23
        cfg['families']['quad']['spine_mm']=43.2
        result=run(cfg)
        self.assertTrue(result['cross_section_screen']['support_body_conflicts'])
        self.assertFalse(self.result['cross_section_screen']['support_body_conflicts'])
        self.assertFalse(self.result['cross_section_screen']['support_support_conflicts'])

    def test_span_scaling_is_dimensionally_consistent(self):
        a=beam([(10,1,0)],100,.1,250,9.80665)
        b=beam([(10,1,0)],100,.1,500,9.80665)
        self.assertAlmostEqual(b['sag_um']/a['sag_um'],16)
        self.assertAlmostEqual(b['first_bending_Hz']/a['first_bending_Hz'],.25)

if __name__=='__main__':unittest.main()
