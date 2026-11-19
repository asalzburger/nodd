"""Independent algebra and population/uncertainty controls; no ROOT imports."""
from copy import deepcopy
import math
import json
from pathlib import Path
import statistics
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from central_analyze import (COUNTS, ENERGY, ETA, GEOMETRY, METRICS, MODELS,
                             PHI, SEEDS, bootstrap, histogram, scalar_metrics,
                             summarize, validate_population, load_population)


def fixture(name='lar', population='calibration'):
    n = COUNTS[population]; seed = SEEDS[name][population]
    values = np.tile([ENERGY, ETA, PHI, 1., 1. / ENERGY], (n, 1))
    receipt = {'events': n, 'skip': 0, 'threads': 12, 'seed': seed,
               'command': ['--physics.list', 'FTFP_BERT', '--physics.rangecut', '.7', '--random.enableEventSeed']}
    # Match the exact spelling DDSim records in executed commands.
    receipt['command'][3] = '0.7'
    point = {'energy_GeV': ENERGY, 'eta': ETA, 'phi_rad': PHI,
             'population': population, 'transport_seed': seed, 'events': n}
    roles = {'LArBarrel': {'volumes': [{'max_step_mm': 5., 'Birks_mm_per_MeV': 0}]},
             'LArEndcaps': {'volumes': [{'max_step_mm': 5., 'Birks_mm_per_MeV': 0}]}}
    if name == 'siw':
        roles = {key: {'max_step_mm': 5., 'Birks_mm_per_MeV': 0} for key in ('BARREL', 'EDGE')}
    workers = [{'thread_id': i, 'events': n // 12 + (i < n % 12), 'status': 'complete',
                'maximum_abs_magnetic_field_tesla': 0, 'rng_engine': 'MixMaxRng',
                'begin_run_rng_seed': seed, 'region_cuts': [{'mm': [.7] * 4}],
                'sensitive_lar' if name == 'lar' else 'sensitive_si': deepcopy(roles)} for i in range(12)]
    proof = {'events': n, 'sample': {'events': n, 'validation_point': point, 'hashes': GEOMETRY[name].copy()},
             'cells_by_collection': {k: 1 for k in (('LArBarrelHits', 'LArEndcapHits') if name == 'lar' else ('BARRELHits', 'EDGEHits'))},
             'workers': workers}
    return values, receipt, proof


class CentralResponse(unittest.TestCase):
    def test_independent_calibration_does_not_recenter_heldout_or_change_cv(self):
        cal = np.array([1., 2., 3.])
        ev = np.array([0., 1., 2., 3., 9.])
        result = scalar_metrics(cal, ev)
        expected_f = statistics.mean(cal) / 50
        corrected = [x / (50 * expected_f) for x in ev]
        self.assertAlmostEqual(result['effective_response_fraction'], expected_f)
        self.assertAlmostEqual(result['raw_fraction_sd'], statistics.stdev(ev) / 50)
        self.assertAlmostEqual(result['corrected_fraction_mean'], statistics.mean(corrected))
        self.assertNotAlmostEqual(result['corrected_fraction_mean'], 1.)
        self.assertAlmostEqual(result['corrected_fraction_sd'], statistics.stdev(corrected))
        self.assertAlmostEqual(result['raw_energy_cv'], statistics.stdev(corrected) / statistics.mean(corrected))
        self.assertEqual(result['raw_energy_cv'], result['corrected_fraction_cv'])

    def test_calibration_uncertainty_is_common_scale_not_event_noise(self):
        cal = {name: np.array([1., 1.5, 2., 2.5, 3.]) for name in MODELS}
        ev = {name: np.full(30, 2.) for name in MODELS}
        draws = bootstrap(cal, ev, replicates=200, seed=10)
        for name in MODELS:
            # No variation exists within evaluation events. Refitting a common
            # f can move their common mean but must never create shower width.
            self.assertTrue(np.all(draws[name][:, METRICS.index('corrected_fraction_sd')] == 0))
            self.assertGreater(draws[name][:, METRICS.index('corrected_fraction_mean')].std(), .01)
        # Even identical detector inputs have independent bootstrap streams.
        self.assertFalse(np.array_equal(draws['lar'], draws['siw']))

    def test_full_summary_keeps_zeros_tails_covariance_and_scale_invariance(self):
        cal = {'lar': np.array([5., 6., 7., 8., 9.]), 'siw': np.array([.5, .6, .7, .8, .9])}
        ev = {'lar': np.array([0., 6., 7., 7.5, 8., 9.]), 'siw': np.array([0., .6, .7, .75, .8, .9])}
        result = summarize(cal, ev, {}, replicates=100, seed=23)
        for name in MODELS:
            model = result['models'][name]
            for distribution in model['distributions'].values():
                self.assertEqual(distribution['moments']['zero_events'], 1)
                hist = distribution['histogram']
                self.assertEqual(sum(hist['counts']) + hist['underflow'] + hist['overflow'], len(ev[name]))
            ci = model['metric_ci95']['effective_response_fraction']
            self.assertGreater(ci[1], ci[0])
            np.testing.assert_allclose(model['metric_ci95']['raw_energy_cv'], model['metric_ci95']['corrected_fraction_cv'], rtol=0, atol=0)
        matrix = np.array(result['metric_covariance']['matrix'])
        self.assertEqual(matrix.shape, (2 * len(METRICS), 2 * len(METRICS)))
        self.assertTrue(np.isfinite(matrix).all())
        np.testing.assert_allclose(matrix, matrix.T, rtol=0, atol=1e-14)
        self.assertGreater(np.linalg.eigvalsh(matrix).min(), -1e-12)
        self.assertEqual(result['models']['lar']['corrected_overlay_histogram']['edges'],
                         result['models']['siw']['corrected_overlay_histogram']['edges'])

    def test_histogram_flows_are_not_lost_or_renormalized_away(self):
        result = histogram(np.array([0., 1., 2., 3., 4.]), edges=np.array([1., 2., 3.]))
        self.assertEqual(result['counts'], [1, 2])
        self.assertEqual((result['underflow'], result['overflow'], result['events']), (1, 1, 5))

    def test_protocol_rejects_geometry_direction_population_and_rng_relabeling(self):
        for name in MODELS:
            for population in ('calibration', 'evaluation'):
                values, receipt, proof = fixture(name, population)
                self.assertEqual(validate_population(name, population, values, receipt, proof)['events'], COUNTS[population])
                altered = values.copy(); altered[0, 2] = 0
                with self.assertRaisesRegex(ValueError, 'direction'):
                    validate_population(name, population, altered, receipt, proof)
                wrong = deepcopy(proof); wrong['sample']['hashes']['detector.xml'] = 'wrong'
                with self.assertRaisesRegex(ValueError, 'geometry'):
                    validate_population(name, population, values, receipt, wrong)
                wrong = deepcopy(receipt); wrong['seed'] += 1
                with self.assertRaisesRegex(ValueError, 'stream'):
                    validate_population(name, population, values, wrong, proof)
                wrong = deepcopy(proof); wrong['sample']['validation_point']['population'] = 'wrong'
                with self.assertRaisesRegex(ValueError, 'validation point'):
                    validate_population(name, population, values, receipt, wrong)
                with self.assertRaisesRegex(ValueError, 'population'):
                    validate_population(name, population, values[:-1], receipt, proof)

    def test_invalid_inputs_fail_without_clipping(self):
        for cal, ev in (([0., 0.], [1., 2.]), ([1., 2.], [0., 0.]),
                        ([1., 2.], [-1., 3.]), ([1., math.nan], [1., 2.])):
            with self.assertRaises(ValueError):
                scalar_metrics(np.array(cal), np.array(ev))

    def test_bound_study_protocol_cannot_be_silently_replaced(self):
        values, receipt, proof = fixture()
        proof['sample']['study_protocol_sha256'] = 'frozen-study'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'readback.json').write_text(json.dumps(proof))
            (root / 'receipt.json').write_text(json.dumps(receipt))
            with patch('central_analyze.common.load_run', return_value=([], values, {})):
                data, evidence = load_population(root, 'lar', 'calibration', 'frozen-study')
                self.assertEqual(len(data), 2000)
                self.assertEqual(evidence['study_protocol_sha256'], 'frozen-study')
                with self.assertRaisesRegex(ValueError, 'study protocol'):
                    load_population(root, 'lar', 'calibration', 'other-study')

    def test_cli_bootstrap_cannot_disagree_with_frozen_protocol(self):
        from central_analyze import analyze
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol = root / 'protocol.json'
            protocol.write_text(json.dumps({'statistics': {'bootstrap_replicates': 1000, 'bootstrap_seed': 5019001}}))
            for replicas, seed in ((1001, 5019001), (1000, 5019002)):
                with self.assertRaisesRegex(ValueError, 'Bootstrap settings'):
                    analyze(root, root / 'output', replicas, seed, protocol)


if __name__ == '__main__':
    unittest.main()
