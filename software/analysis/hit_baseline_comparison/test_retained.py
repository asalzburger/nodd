"""Offline consistency of delivered binwise hit evidence and both plot options."""
import json
from pathlib import Path
import unittest

import numpy as np

from reduce import sha
from plot import COLORS

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'docs/validation/baseline-hit-comparison'


class RetainedHitEvidence(unittest.TestCase):
    def test_profiles_and_covariance_close(self):
        data=json.loads((DATA/'profiles.json').read_text())
        self.assertEqual(len(data['edges']),81)
        for name,case in data['baselines'].items():
            self.assertEqual(sum(case['counts']),100000)
            q=case['quantities'];cov=np.array(case['component_covariance_of_mean'])
            np.testing.assert_allclose(sum(np.array(q[c]['mean']) for c in COLORS),q['total']['mean'],atol=1e-13)
            np.testing.assert_allclose(cov.sum(axis=(1,2)),q['total']['variance'],atol=1e-13)
            for i,c in enumerate(COLORS):
                np.testing.assert_allclose(cov[:,i,i],q[c]['variance'],atol=1e-13)
            self.assertAlmostEqual(case['global_mean']['total']*100000,case['native_checks']['distinct_hits'])
            self.assertEqual(case['native_checks']['dd_sensitive_placements'],45646 if name=='old' else 46682)
            self.assertEqual(case['native_checks']['g4_sensitive_placements'],case['native_checks']['dd_sensitive_placements'])
        np.testing.assert_array_equal(data['baselines']['old']['counts'],data['baselines']['current']['counts'])
        for stat in ('mean','variance'):
            np.testing.assert_array_equal(data['baselines']['old']['quantities']['long_strip'][stat],
                                          data['baselines']['current']['quantities']['long_strip'][stat])

    def test_rendering_and_controls_match(self):
        report=json.loads((DATA/'figures/plot-report.json').read_text())
        self.assertEqual(report['colors'],COLORS)
        for color in COLORS.values():self.assertIn(color,(ROOT/'README.md').read_text().lower())
        for f in report['files']:self.assertEqual(sha(DATA/'figures'/f['name']),f['sha256'])
        self.assertEqual(sha(DATA/'profiles.json'),report['data_sha256'])
        self.assertEqual(sha(Path(__file__).with_name('plot.py')),report['plotter_sha256'])
        for name in ('old','current'):
            control=json.loads((DATA/f'{name}-box-control.json').read_text())
            self.assertEqual(control['rays'],256)
            self.assertEqual(control['finite_box_mismatches'],[])
        control=json.loads((DATA/'observer-noninterference.json').read_text())
        self.assertEqual(control['rays'],300)
        self.assertEqual(len(control['branches']),32)
        self.assertTrue(all(control['branches'].values()))


if __name__=='__main__':unittest.main()
