"""Offline integrity of the delivered binwise evidence and native material model."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'docs/validation/baseline-material-comparison'


class RetainedEvidenceTests(unittest.TestCase):
    def test_map_keys_bins_and_zero_slabs_match_native_report(self):
        raw = gzip.decompress((DATA/'material_map.json.gz').read_bytes())
        report = json.loads((DATA/'current-mapping-report.json').read_text())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), report['material_map']['sha256'])
        material = json.loads(raw)
        selection = json.loads((DATA/'selection.json').read_text())
        expected = {s['material_key']: s for s in selection['surfaces']}
        actual = {s['key']: s for s in material['KeyedSurfaces']}
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(actual), 67)
        bins = empty = 0
        for key, surface in actual.items():
            grid = surface['material']['data']
            shape = expected[key]['bins'].get('z', expected[key]['bins'].get('r'))
            # ACTS serializes the second coordinate as rows and phi as columns.
            self.assertEqual([b['bins'] for b in surface['material']['binUtility']['binningdata']],
                             [expected[key]['bins']['phi'], shape])
            self.assertEqual(len(grid), shape)
            self.assertTrue(all(len(row) == expected[key]['bins']['phi'] for row in grid))
            for row in grid:
                for slab in row:
                    self.assertGreaterEqual(slab['thickness'], 0)
                    bins += 1
                    empty += slab['thickness'] == 0
        self.assertEqual((bins, empty), (8650, 2003))

    def test_ratio_and_zero_inclusive_components_recompute(self):
        data = json.loads((DATA/'comparison.json').read_text())
        for baseline in data['baselines'].values():
            for q in ('X0', 'L0'):
                geant = baseline['geant4']['quantities'][q]
                components = [v['mean'] for k, v in geant.items() if k != 'total']
                np.testing.assert_allclose(np.sum(components, axis=0), geant['total']['mean'], rtol=2e-13, atol=2e-14)
                acts = baseline['acts']['quantities'][q]
                np.testing.assert_allclose(baseline['ratio'][q]['mean'], np.array(acts['mean'])/geant['total']['mean'])
                self.assertTrue(all(baseline['ratio'][q]['valid']))
        current = data['baselines']['current']['classification']
        self.assertEqual((current['density_mismatches'], current['unassigned_steps']), (0, 0))
        self.assertEqual((current['tgeo_density_disagreements'], current['geant4_audited_rescues']), (149,149))

    def test_rendered_artifacts_and_sources_have_recorded_hashes(self):
        report = json.loads((DATA/'figures/plot-report.json').read_text())
        for f in report['files']:
            self.assertEqual(hashlib.sha256((DATA/'figures'/f['name']).read_bytes()).hexdigest(), f['sha256'])
        self.assertEqual(hashlib.sha256((DATA/'comparison.json').read_bytes()).hexdigest(), report['comparison_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/'software/analysis/material_baseline_comparison/plot.py').read_bytes()).hexdigest(), report['plotter_sha256'])
        self.assertEqual((report['passive_alpha'], report['sensitive_alpha']), (.5,1))


if __name__ == '__main__':
    unittest.main()
