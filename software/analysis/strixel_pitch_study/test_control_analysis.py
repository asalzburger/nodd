import unittest

from control_analysis import MODEL, validate_control


class GaussianControlGateTest(unittest.TestCase):
    def inventory(self):
        return {'reports': [{'report': dict(pt_GeV=100., pitch_mm=p, requested_events=5000,
                                            outcome='completed', response_model=MODEL)}
                            for p in (.5, 1., 1.5, 2.)]}

    def test_incomplete_or_duplicate_matrix_is_rejected(self):
        value = self.inventory()
        value['reports'].pop()
        with self.assertRaisesRegex(ValueError, 'exactly four pitches'):
            validate_control(value)
        value = self.inventory()
        value['reports'][1] = value['reports'][0]
        with self.assertRaisesRegex(ValueError, 'exactly four pitches'):
            validate_control(value)

    def test_digital_response_cannot_be_relabelled_as_control(self):
        value = self.inventory()
        value['reports'][0]['report']['response_model'] = 'geometric'
        with self.assertRaisesRegex(ValueError, 'response label'):
            validate_control(value)

    def test_control_requires_complete_count_and_source_fingerprints(self):
        value = self.inventory()
        value['reports'][0]['report']['requested_events'] = 4999
        with self.assertRaisesRegex(ValueError, '5000-event'):
            validate_control(value)
        value = self.inventory()
        with self.assertRaisesRegex(ValueError, 'source fingerprints'):
            validate_control(value)


if __name__ == '__main__':
    unittest.main()
