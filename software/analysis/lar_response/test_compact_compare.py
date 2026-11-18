"""Small independent checks of paired raw-width inference and input contracts."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import compact_compare as c


class PairedControls(unittest.TestCase):
    def contract(self):
        return dict(reference_compact_sha256='a'*64, candidate_compact_sha256='b'*64,
                    input_sha256='c'*64, truth_sha256='d'*64, transition_union_abs_eta=[1.2, 1.6])

    def loaded(self):
        values = np.array([[15., .1, -2., .1, .1/15], [30., 1.25, -.5, .2, .2/30],
                           [50., -1.4, .5, .3, .3/50], [75., 2.5, 2., .4, .4/75]])
        result = {}
        for i, name in enumerate(c.MODELS):
            contract = self.contract()
            sample = dict(input_sha256=contract['input_sha256'], truth_sha256=contract['truth_sha256'],
                          source_primary_manifest_sha256='e'*64,
                          hashes={'detector.xml':contract[name+'_compact_sha256'],
                                  'particles.HEPEvt':contract['input_sha256'], 'truth-input.jsonl':contract['truth_sha256']})
            result[name] = ([{'event':n} for n in range(4)], values.copy(), {'input':sample})
        return result

    def test_manual_width_and_zeros(self):
        # [0, 1, 2] has mean=1 and unbiased sample SD=1; zero stays in denominator.
        row = c.moments([0., 1., 2.])
        self.assertEqual(row['events'], 3); self.assertEqual(row['zero_events'], 1)
        self.assertEqual(row['sample_sd'], 1); self.assertEqual(row['fractional_width'], 1)
        self.assertEqual(row['below_half_mean_events'], 1)
        zero = c.moments([0., 0., 0.])
        self.assertEqual(zero['mean_response'], 0); self.assertEqual(zero['sample_sd'], 0)
        self.assertIsNone(zero['fractional_width']); self.assertEqual(zero['zero_events'], 3)
        self.assertIsNone(c.moments([])['mean_response'])
        self.assertIsNone(c.moments([1.])['sample_sd'])

    def test_wrong_label_or_primary_is_rejected(self):
        loaded, contract = self.loaded(), self.contract()
        c.validate_pair(loaded, contract, expected_events=4)
        wrong = copy.deepcopy(loaded); wrong['candidate'][2]['input']['hashes']['detector.xml'] = 'a'*64
        with self.assertRaisesRegex(ValueError, 'geometry'): c.validate_pair(wrong, contract, expected_events=4)
        wrong = copy.deepcopy(loaded); wrong['candidate'][1][2, 1] += .01
        with self.assertRaisesRegex(ValueError, 'illumination'): c.validate_pair(wrong, contract, expected_events=4)
        wrong = copy.deepcopy(loaded); wrong['candidate'][0][3]['event'] = 2
        with self.assertRaisesRegex(ValueError, 'event IDs'): c.validate_pair(wrong, contract, expected_events=4)
        wrong = copy.deepcopy(loaded); wrong['candidate'][2]['input']['source_primary_manifest_sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'source primary'): c.validate_pair(wrong, contract, expected_events=4)

    def test_shared_bootstrap_preserves_scale_invariance(self):
        loaded = self.loaded()
        loaded['candidate'][1][:, 3:] *= 2
        result = c.summarize(loaded, self.contract(), bootstrap=64, seed=123)
        contrast = result['candidate_minus_reference']['global'][0]
        self.assertAlmostEqual(contrast['difference'], 0, places=14)
        self.assertTrue(np.allclose(contrast['ci95'], [0, 0], atol=1e-14))
        # All four primary IDs remain; projection denominators are common.
        self.assertEqual(sum(r['events'] for r in result['models']['candidate']['projections']['abs_eta']['bins']), 4)
        self.assertEqual(result['models']['candidate']['projections']['transition_union']['bins'][1]['events'], 2)
        json.dumps(result, allow_nan=False)

    def test_zero_bins_keep_undefined_bootstrap_and_null_covariance(self):
        loaded = self.loaded()
        loaded['candidate'][1][:, 3:] = 0
        result = c.summarize(loaded, self.contract(), bootstrap=16, seed=2)
        row = result['models']['candidate']['global']
        self.assertEqual(row['events'], 4); self.assertEqual(row['zero_events'], 4)
        self.assertIsNone(row['fractional_width'])
        self.assertEqual(row['fractional_width_bootstrap'], {'ci95':None, 'undefined':16})
        self.assertIsNone(result['candidate_minus_reference']['global'][0]['difference'])
        order = result['width_covariance']['order']; i = order.index('candidate:global:0')
        self.assertTrue(all(x is None for x in result['width_covariance']['matrix'][i]))
        json.dumps(result, allow_nan=False)

    def test_migration_from_geometry_not_signal(self):
        contract = self.contract()
        contract['geometry_transition'] = {
            'reference':dict(barrel_full_eta=1.2, barrel_any_eta=1.3, endcap_any_eta=1.4, endcap_full_eta=1.5),
            'candidate':dict(barrel_full_eta=1.35, barrel_any_eta=1.55, endcap_any_eta=1.4, endcap_full_eta=1.5)}
        out = c.geometry_migration(np.array([.5, 1.25, 1.35, 1.45, 2.]), contract)
        matrix = np.array(out['counts'])
        self.assertEqual(matrix.sum(), 5)
        self.assertEqual(matrix[0, 0], 1); self.assertEqual(matrix[2, 0], 1)
        self.assertEqual(matrix[3, 0], 1); self.assertEqual(matrix[2, 2], 1)
        self.assertEqual(matrix[1, 1], 1)

    def test_histogram_denominator_and_overflow(self):
        raw, norm = c.histogram(np.array([0., .1, .2, .8]), .1)
        for hist in (raw, norm):
            self.assertEqual(sum(hist['counts'])+hist['underflow']+hist['overflow'], 4)
            self.assertEqual(hist['events'], 4)
        self.assertIsNone(c.histogram(np.zeros(3), 0)[1])

    def test_serial_maps_bind_frozen_count_and_receipt(self):
        # Five is a small fixture count, independent of any detector inventory.
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory); (run / 'audit').mkdir()
            maps = dict(status='PASS', thread_id=-1, raw_sensitive_ids=5, native_contexts_checked=5)
            path = run / 'audit/maps-initialized.json'; path.write_text(json.dumps(maps))
            digest = c.common.sha(path)
            (run / 'receipt.json').write_text(json.dumps(dict(maps_audit_sha256=digest)))
            (run / 'readback.json').write_text(json.dumps(dict(maps_audit_sha256=digest, maps_audit=maps)))
            self.assertEqual(c.validate_maps(run, 'candidate', {'candidate_raw_sensitive_ids':5})['raw_sensitive_ids'], 5)
            with self.assertRaisesRegex(ValueError, 'map initialization'):
                c.validate_maps(run, 'candidate', {'candidate_raw_sensitive_ids':6})
            maps['native_contexts_checked'] = 4; path.write_text(json.dumps(maps))
            with self.assertRaisesRegex(ValueError, 'map initialization'):
                c.validate_maps(run, 'candidate', {'candidate_raw_sensitive_ids':5})


if __name__ == '__main__':
    unittest.main()
