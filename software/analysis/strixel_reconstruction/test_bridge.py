import unittest
import numpy as np
from bridge import compare


class BridgeTest(unittest.TestCase):
    def test_identity_join_keeps_nan_masks(self):
        old = {'event': np.array([2, 0, 1]), 'v': np.array([[1., np.nan], [2., 3.], [4., 5.]])}
        new = {'event': np.array([0, 2]), 'v': np.array([[2., 3.], [1., np.nan]])}
        self.assertTrue(compare(old, new)['all_original_observables_identical'])
        new['v'][1, 0] = 1.1
        self.assertEqual(compare(old, new)['observables']['v']['different_events'], 1)

    def test_duplicate_or_missing_events_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            compare({'event': np.array([0, 0])}, {'event': np.array([0])})
        with self.assertRaisesRegex(ValueError, 'missing'):
            compare({'event': np.array([0])}, {'event': np.array([1])})


if __name__ == '__main__':
    unittest.main()
