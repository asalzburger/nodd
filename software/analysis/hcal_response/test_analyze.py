"""Independent statistics/invalid-input checks for the published observable."""
import math
import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import analyze
import statistics
import unittest

from analyze import categories, moments


class RawResponseContracts(unittest.TestCase):
    def test_nonfinite_directions_fail(self):
        for eta,phi in ((math.nan,0.),(0.,math.nan),(math.inf,0.),(0.,-math.inf)):
            with self.subTest(eta=eta,phi=phi), self.assertRaises(ValueError):
                categories([dict(eta=eta,phi=phi)])

    def test_out_of_range_azimuth_fails(self):
        for phi in (-math.pi-1e-6,math.pi,math.pi+1e-6):
            with self.subTest(phi=phi), self.assertRaises(ValueError):
                categories([dict(eta=0.,phi=phi)])
        self.assertEqual(len(categories([dict(eta=0.,phi=-math.pi)])["phi"]),1)

    def test_zero_response_events_remain_and_width_is_undefined(self):
        result = moments([0.,0.,0.])
        self.assertEqual((result["events"],result["zero_events"]),(3,3))
        self.assertEqual(result["mean_response"],0.)
        self.assertEqual(result["sample_sd"],0.)
        self.assertIsNone(result["fractional_width"])

    def test_sample_width_matches_independent_statistics(self):
        data = [0.,.013,.025,.018,.021,.032]
        result = moments(data)
        self.assertAlmostEqual(result["sample_sd"],statistics.stdev(data),places=15)
        self.assertAlmostEqual(result["fractional_width"],statistics.stdev(data)/statistics.mean(data),places=15)
        self.assertEqual(result["zero_events"],1)

    def test_sampling_scale_invariance_and_true_energy_denominators(self):
        signal=np.array([.2,.4,.8,1.]);energy=np.full(4,50.)
        first=analyze.fixed_statistics(signal,energy,.02);second=analyze.fixed_statistics(signal,energy,.01)
        self.assertAlmostEqual(first['raw_sd'],statistics.stdev(signal),places=14)
        self.assertAlmostEqual(first['fractional_sd'],statistics.stdev(signal)/50,places=14)
        self.assertAlmostEqual(first['residual_sd'],statistics.stdev(signal)/(.02*50),places=14)
        for values in(first,second):
            self.assertAlmostEqual(values['raw_cv'],values['corrected_cv'],places=14)
            self.assertAlmostEqual(values['raw_cv'],values['fractional_cv'],places=14)
        self.assertAlmostEqual(second['residual_sd'],2*first['residual_sd'],places=14)
        self.assertNotEqual(first['residual_mean'],0.)

    def test_matched_bootstrap_identity_and_mismatched_direction_rejection(self):
        # Explicit synthetic validation fixture, never a detector parameter.
        rows=[dict(event=i,energy_GeV=50.,eta=-3+6*(i+.5)/10000,phi=-math.pi+2*math.pi*((i*37)%10000+.5)/10000,signal_GeV=.4+.01*(i%11),response=(.4+.01*(i%11))/50) for i in range(10000)]
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp);receipt=dict(exit_code=0,source_revision='TEST',seed=202650001);analyze.save(run/'receipt.json',receipt)
            (run/'event-summary.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            analyze.save(run/'readback.json',dict(status='PASS',events=10000,event_summary_sha256=analyze.sha(run/'event-summary.jsonl'),receipt_sha256=analyze.sha(run/'receipt.json'),sample=dict(sample_role='angular')))
            result=analyze.paired_angular_comparison(rows,run,12,13001000)
            for bins in result['width_differences'].values():
                for b in bins:self.assertEqual(b['edge_minus_baseline'],0.);self.assertEqual(b['ci95'],[0.,0.])
            changed=[dict(r) for r in rows];changed[0]['eta']+=.01
            with self.assertRaises(ValueError):analyze.paired_angular_comparison(changed,run,12,13001000)

    def test_held_out_calibration_does_not_force_validation_bias_to_zero(self):
        def fixture(run,n,role,seed,signals):
            run.mkdir();direction=dict(eta=.12,phi_rad=.03125,direction_receipt_sha256='TEST-direction')
            sample=dict(sample_role=role,sample_id='TEST-'+role,fixed_direction=direction,hashes={k:'TEST-same-'+k for k in ('detector.xml','materials.xml','expected.json')})
            receipt=dict(exit_code=0,seed=seed,source_revision='TEST',producer_sha256={});analyze.save(run/'receipt.json',receipt)
            rows=[]
            for i in range(n):
                signal=signals[i%2];rows.append(dict(event=i,energy_GeV=50.,eta=.12,phi=.03125,signal_GeV=signal,response=signal/50,layer_energies_GeV=[signal]+[0.]*59,terminal_six_fraction=0.,observer=dict(world_escape_kinetic_GeV=0.)))
            (run/'event-summary.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));analyze.save(run/'readback.json',dict(status='PASS',events=n,event_summary_sha256=analyze.sha(run/'event-summary.jsonl'),receipt_sha256=analyze.sha(run/'receipt.json'),sample=sample))
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);cal=base/'cal';val=base/'val';fixture(cal,2000,'calibration',202650102,(.8,1.2));fixture(val,10000,'validation',202650103,(.9,1.3))
            frozen=base/'frozen.json';analyze.calibrate(argparse.Namespace(run=cal,output=frozen,bootstrap=20))
            with patch.object(analyze,'fixed_plot'):
                analyze.fixed_analyze(argparse.Namespace(run=val,calibration_run=cal,calibration=frozen,output=base/'result',bootstrap=20))
            result=json.loads((base/'result/summary.json').read_text());self.assertAlmostEqual(result['statistics']['fs'],.02,places=14);self.assertAlmostEqual(result['statistics']['residual_mean'],.1,places=13)
            self.assertAlmostEqual(result['statistics']['raw_cv'],result['statistics']['corrected_cv'],places=14)
            for h in result['histograms'].values():self.assertEqual(sum(h['counts']),10000)
            self.assertEqual(result['bootstrap']['calibration_seed'],13001002);self.assertEqual(result['bootstrap']['validation_seed'],13001001)


if __name__ == '__main__': unittest.main()
