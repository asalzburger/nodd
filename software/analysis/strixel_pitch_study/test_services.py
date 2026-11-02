"""Physical accounting controls for the DES042 conditional service model."""
import json
from pathlib import Path
import unittest

from services import evaluate, harness_count, network_loss


class ServicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=evaluate(json.loads(Path(__file__).with_name('services.json').read_text()))

    def test_fixed_load_does_not_remove_services(self):
        baseline=self.report['baseline']
        for case in self.report['cases']:
            if case['channel_dependent_fraction']==0 or case['pitch_v_mm']==.5:
                self.assertAlmostEqual(case['saved_heat_kW'],0)
                self.assertAlmostEqual(case['saved_power_envelope_L'],0)
                self.assertEqual(sum(case['power_harnesses'].values()),baseline['power_harnesses_both_ends'])

    def test_regions_and_fixed_fibres_conserve_volume(self):
        baseline=self.report['baseline']
        for case in self.report['cases']:
            self.assertEqual(case['fibre_harnesses'],1584)
            self.assertEqual(case['fibre_envelope_L'],baseline['fibre_envelope_L'])
            self.assertAlmostEqual(sum(case['saved_power_envelope_by_region_L'].values()),case['saved_power_envelope_L'])
            self.assertAlmostEqual(case['cable_envelope_L']+case['saved_power_envelope_L'],baseline['cable_envelope_L'])
            self.assertAlmostEqual(sum(case['one_end_sector_service_area_mm2']),case['one_end_service_area_mm2'])

    def test_integral_channel_grid_and_discrete_cable_plateau(self):
        cases=[x for x in self.report['cases'] if x['power_normalization']=='CMS_PS_comparator'
               and x['channel_dependent_fraction']==1]
        self.assertEqual([sum(c['channels'].values()) for c in cases],
                         [1521745920,760872960,507248640,380436480])
        self.assertEqual([sum(c['power_harnesses'].values()) for c in cases],[1584,864,720,720])
        self.assertAlmostEqual(cases[2]['saved_power_envelope_L'],cases[3]['saved_power_envelope_L'])

    def test_network_rounding_and_fixed_board_load(self):
        self.assertEqual(harness_count(12,8,0,8,12),1)
        self.assertEqual(harness_count(12,8,5,8,12),2)
        self.assertEqual(harness_count(30,8/3,5,8,12),1)

    def test_losses_scale_quadratically_without_hv_current(self):
        taps=[100,200]
        unit=network_loss(taps,300,1,.0175,2.4)
        self.assertAlmostEqual(unit,.2*.0175/2.4*5)
        self.assertAlmostEqual(network_loss(taps,300,2,.0175,2.4),4*unit)
        fixed=[(c['fixed_HV_leakage_kW'],c['fixed_boards_kW']) for c in self.report['cases']]
        self.assertEqual(set(fixed),{(24.768,3.6)})


if __name__=='__main__':unittest.main()
