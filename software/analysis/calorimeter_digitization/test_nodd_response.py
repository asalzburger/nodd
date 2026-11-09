"""Scientific controls: descriptor identity and shared-reference covariance."""
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from nodd_response import decode, descriptors, ratio, shower_summary


class ResponseControls(unittest.TestCase):
    def test_zero_denominator_remains_undefined(self):
        result = ratio(np.array([0., 2.]), np.array([0., 4.]))
        self.assertTrue(np.isnan(result[0]))
        self.assertEqual(result[1], .5)

    def test_actual_descriptor_offsets_and_signed_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'detector.xml'
            path.write_text('<lccdd><readouts><readout name="A"><id>system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6</id></readout><readout name="B"><id>system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,y:-16</id></readout></readouts></lccdd>')
            fields = descriptors(path, ['A', 'B'])
            cid = 9 | (2 << 8) | (47 << 14) | (63 << 30)
            self.assertEqual(decode(cid, fields['A'], 'layer'), 47)
            self.assertEqual(decode(cid, fields['A'], 'side'), 2)
            self.assertEqual(decode(cid, fields['A'], 'x'), -1)
            self.assertEqual(decode(48 << 16, fields['B'], 'layer'), 48)

    def test_shared_calibration_keeps_geometry_ratio_and_covariance(self):
        runs = []
        events = {}
        def add(key, kind, geometry, eta, triples):
            runs.append(dict(fixture=key, kind=kind, geometry=geometry,
                             sample=dict(eta=eta, particle='e-', energy_GeV=20, id=key,
                                         sha256=key, truth=dict(generated_total_energy_GeV=20.)),
                             receipt=dict(output_sha256=key)))
            events[key] = [dict(raw_GeV=a, modes={'off':dict(energy_GeV=b), 'on':dict(energy_GeV=c)})
                           for a,b,c in triples]
        for eta in (0,1,2,-2):
            add('cal'+str(eta), 'calibration', 'odd-zero', eta, [(9,9,9),(11,11,11)])
        add('nodd', 'showers', 'nodd', 0, [(5.,4.95,4.9)]*4)
        add('odd', 'showers', 'odd-zero', 0, [(10.,9.9,9.8)]*4)
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(work=Path(directory))
            with patch('nodd_response.read_events', side_effect=lambda row:events[row['fixture']]), patch('nodd_response.longitudinal', return_value={'scope':'synthetic unit control'}):
                result = shower_summary(runs, {'geometries':{'nodd':{},'odd-zero':{}}}, args)
        comparison = result['geometry_comparisons'][0]
        for stage in ('raw','off','on'):
            self.assertAlmostEqual(comparison['stages'][stage]['mean_ratio_nodd_over_ODD'], .5)
            self.assertLess(comparison['stages'][stage]['mean_ratio_bootstrap']['SE'], 1e-14)
        cov = np.asarray(result['response_bootstrap_covariance'])
        self.assertGreater(cov[0,3], 0.)
        self.assertAlmostEqual(cov[0,3]**2/(cov[0,0]*cov[3,3]), 1., places=12)
        self.assertEqual(result['populations'][0]['n'], 4)
        self.assertEqual(result['populations'][0]['stages']['raw']['visible_fraction_histogram']['entries'], 4)


if __name__ == '__main__':
    unittest.main()
