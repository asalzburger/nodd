"""Frozen-artifact compatibility and truth-free calibration application controls."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import highstat_inference as inference


class FrozenInferenceTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.record = inference.load_record()
        self.features = np.zeros((4, 10))  # Synthetic software fixture, not detector events.
        self.signal = np.array([0., .2, .3, .4])
        self.region = np.array([0, 0, 1, 1])
        self.axis = np.array([True, False, True, False])
        self.compatibility = dict(geometry_sha256=self.manifest['geometry']['detector_xml_sha256'],
                                  feature_semantics=self.record['feature_semantics'])

    def infer(self, **kwargs):
        return inference.calibrate(self.features, self.signal, self.region, self.axis,
                                   **dict(self.compatibility, **kwargs))

    def write_features(self, folder, duplicate_ids=False):
        folder.mkdir()
        np.savez(folder / 'features.npz', features=self.features, signal=self.signal,
                 region=self.region, valid_axis=self.axis,
                 event=np.array([4, 5, 5 if duplicate_ids else 6, 7]))
        receipt = dict(self.record['feature_semantics'], status='PASS', events=4,
                       compact_sha256=self.compatibility['geometry_sha256'],
                       feature_sha256=inference.sha(folder / 'features.npz'))
        (folder / 'receipt.json').write_text(json.dumps(receipt))

    def test_zero_fallback_units_and_gain_bounds_without_fit(self):
        with patch('highstat_model.fit', side_effect=AssertionError('Must not refit')):
            for kind in ('original', 'spline'):
                result = self.infer(kind=kind)
                self.assertEqual(result['energy'][0], 0.)
                model = self.record['models'][kind]
                np.testing.assert_allclose(result['energy'][~self.axis],
                    self.signal[~self.axis] / model['fallback_response'] * model['closure'], rtol=1e-15)
                np.testing.assert_array_equal(result['zero_signal'], [True, False, False, False])
                np.testing.assert_array_equal(result['fallback'], ~self.axis)
                self.assertTrue(np.all((result['gain'] >= .5) & (result['gain'] <= 3)))

    def test_geometry_and_reordered_features_rejected(self):
        with self.assertRaisesRegex(ValueError, 'geometry mismatch'):
            inference.calibrate(self.features, self.signal, self.region, self.axis,
                geometry_sha256='0' * 64, feature_semantics=self.record['feature_semantics'])
        semantics = copy.deepcopy(self.record['feature_semantics'])
        semantics['feature_names'].reverse()
        with self.assertRaisesRegex(ValueError, 'semantics mismatch'):
            inference.calibrate(self.features, self.signal, self.region, self.axis,
                geometry_sha256=self.compatibility['geometry_sha256'], feature_semantics=semantics)

    def test_changed_coefficients_and_core_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ('models.json', 'manifest.json'):
                shutil.copy(inference.ARTIFACT / name, folder / name)
            with (folder / 'models.json').open('a') as stream:
                stream.write(' ')
            with self.assertRaisesRegex(ValueError, 'coefficient file changed'):
                self.infer(artifact=folder)
            model = copy.deepcopy(self.record)
            model['core_sha256'] = '0' * 64
            (folder / 'models.json').write_text(json.dumps(model))
            manifest = copy.deepcopy(self.manifest)
            manifest['coefficients_sha256'] = inference.sha(folder / 'models.json')
            (folder / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'inference source changed'):
                self.infer(artifact=folder)

    def test_invalid_numeric_shapes_regions_and_axis_flags_rejected(self):
        bad = [(self.features[:, :9], self.signal, self.region, self.axis),
               (self.features, [-1., .2, .3, .4], self.region, self.axis),
               (self.features, [np.nan, .2, .3, .4], self.region, self.axis),
               (self.features, self.signal, [0, 0, 2, 1], self.axis),
               (self.features, self.signal, self.region, self.axis.astype(int))]
        for args in bad:
            with self.subTest(args=str(args)[:40]), self.assertRaises(ValueError):
                inference.calibrate(*args, **self.compatibility)

    def test_file_application_needs_no_truth_and_preserves_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_features(folder / 'input')
            proof = inference.apply_file(folder / 'input', folder / 'output')
            self.assertEqual(proof['model_id'], 'nodd-ecal-staggered-spline-v1')
            self.assertFalse(proof['truth_inputs_used'])
            self.assertFalse(proof['coefficients_refitted'])
            self.assertEqual(proof['output_sha256'], inference.sha(folder / 'output/calibrated.npz'))
            with np.load(folder / 'output/calibrated.npz', allow_pickle=False) as result:
                np.testing.assert_array_equal(result['event'], [4, 5, 6, 7])
                np.testing.assert_array_equal(result['energy'], self.infer()['energy'])
            with self.assertRaises(FileExistsError):
                inference.apply_file(folder / 'input', folder / 'output')

    def test_changed_feature_bytes_and_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_features(folder / 'duplicate', duplicate_ids=True)
            with self.assertRaisesRegex(ValueError, 'event identities'):
                inference.apply_file(folder / 'duplicate', folder / 'output')
            self.assertFalse((folder / 'output').exists())
            with (folder / 'duplicate/features.npz').open('ab') as stream:
                stream.write(b'changed')
            with self.assertRaisesRegex(ValueError, 'Changed or failed'):
                inference.apply_file(folder / 'duplicate', folder / 'output')

    def test_incompatible_receipt_rejected_before_arrays_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_features(folder / 'input')
            path = folder / 'input/receipt.json'
            receipt = json.loads(path.read_text())
            receipt['producer_sha256'] = '0' * 64
            path.write_text(json.dumps(receipt))
            with patch('highstat_inference.np.load', side_effect=AssertionError('No array read')):
                with self.assertRaisesRegex(ValueError, 'geometry/semantics mismatch'):
                    inference.apply_file(folder / 'input', folder / 'output')


if __name__ == '__main__':
    unittest.main()
