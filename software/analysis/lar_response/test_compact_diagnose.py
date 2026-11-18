"""Scientific guard checks for saved-model distribution diagnosis."""
import copy
import unittest

import numpy as np
import compact_calibrate as calibration
import compact_diagnose as diagnosis


class DiagnosisGuards(unittest.TestCase):
    def test_saved_predictions_use_excluded_fold_and_reject_training_overlap(self):
        ids = np.arange(10)
        folds = calibration.make_folds(ids)
        scope = dict(compact_sha256='a'*64, materials_sha256='b'*64)
        values = np.tile([10., .5, 0., 5., .5], (10, 1))
        models = []
        for fold in range(5):
            models.append(dict(excluded_fold=fold, scope=scope,
                               algorithm=calibration.ALGORITHM,
                               eta_edges=calibration.ETA_EDGES.tolist(),
                               gains=[float(fold+1)]*60,
                               training_primary_ids_sha256=calibration.ids_hash(ids[folds != fold]),
                               heldout_primary_ids_sha256=calibration.ids_hash(ids[folds == fold])))
        np.testing.assert_allclose(diagnosis.saved_predictions(values, ids, models, scope), .5/(folds+1))
        leaked = copy.deepcopy(models)
        leaked[0]['training_primary_ids_sha256'] = calibration.ids_hash(ids)
        with self.assertRaisesRegex(ValueError, 'whole validation fold'):
            diagnosis.saved_predictions(values, ids, leaked, scope)

    def test_histogram_retains_underflow_overflow_and_closed_last_edge(self):
        h = diagnosis.hist(np.array([-1., 0., 1., 3., 4.]), np.array([0., 1., 2., 3.]))
        self.assertEqual(h['counts'], [1, 1, 1])
        self.assertEqual((h['events'], h['underflow'], h['overflow']), (5, 1, 1))
        self.assertEqual(sum(h['counts'])+h['underflow']+h['overflow'], h['events'])


if __name__ == '__main__':
    unittest.main()
