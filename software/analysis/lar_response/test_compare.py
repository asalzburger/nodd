import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from compare import binned_moments, index, load_run, moments, sha, validate_contract


class ComparisonControls(unittest.TestCase):
    def test_production_contract_rejects_detector_policy_and_raw_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'audit').mkdir()
            receipt = dict(events=10000, skip=0, threads=12, seed=133812341,
                           command=['--physics.list', 'FTFP_BERT', '--physics.rangecut', '0.7', '--random.enableEventSeed'])
            workers = [dict(thread_id=i, events=834 if i<4 else 833, status='complete',
                maximum_abs_magnetic_field_tesla=0, rng_engine='MixMaxRng', begin_run_rng_seed=133812341,
                region_cuts=[dict(mm=[.7]*4)], processes={p:['StepLimiter'] for p in ['e-','e+']},
                sensitive_si={s:dict(max_step_mm=5, Birks_mm_per_MeV=0) for s in ['BARREL','EDGE']}) for i in range(12)]
            (root/'events.root').write_bytes(b'ROOT test fixture')
            proof = dict(cells_by_collection={'BARRELHits':1,'EDGEHits':1}, workers=workers, root_sha256=sha(root/'events.root'))
            def save():
                (root/'receipt.json').write_text(json.dumps(receipt))
                (root/'readback.json').write_text(json.dumps(proof))
                for w in workers:(root/'audit'/f'worker-{w["thread_id"]}.json').write_text(json.dumps(w))
            save(); self.assertEqual(validate_contract(root,'siw_original')['status'],'PASS')
            with self.assertRaisesRegex(ValueError,'detector'):validate_contract(root,'lar')
            receipt['threads']=1;save()
            with self.assertRaisesRegex(ValueError,'production'):validate_contract(root,'siw_original')
            receipt['threads']=12;workers[0]['region_cuts'][0]['mm'][0]=1;save()
            with self.assertRaisesRegex(ValueError,'cuts'):validate_contract(root,'siw_original')
            workers[0]['region_cuts'][0]['mm'][0]=.7;save()
            (root/'events.root').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'ROOT'):validate_contract(root,'siw_original')
            (root/'events.root').write_bytes(b'ROOT test fixture')
            receipt['max_step_mm']=5
            proof['cells_by_collection']={'LArBarrelHits':1,'LArEndcapHits':1}
            for w in workers:
                del w['sensitive_si']
                w['sensitive_lar']={s:dict(volumes=[dict(max_step_mm=5,Birks_mm_per_MeV=0,density_g_cm3=1.396)]) for s in ['LArBarrel','LArEndcaps']}
            save();self.assertEqual(validate_contract(root,'lar')['status'],'PASS')
            receipt['max_step_mm']=0;save()
            with self.assertRaisesRegex(ValueError,'step policy'):validate_contract(root,'lar')
            receipt['max_step_mm']=5
            workers[0]['sensitive_lar']['LArBarrel']['volumes'][0]['density_g_cm3']=1.4;save()
            with self.assertRaisesRegex(ValueError,'density'):validate_contract(root,'lar')

    def test_bootstrap_multiplicity_matches_explicit_repeated_sample(self):
        values = np.array([0., .01, .3, 2., .6])
        categories = np.array([0, 0, 0, 1, 1])
        weights = np.array([2, 1, 4, 3, 2])
        means, widths = binned_moments(values, categories, weights, 2)
        for i in range(2):
            explicit = np.repeat(values[categories == i], weights[categories == i])
            self.assertAlmostEqual(means[i], explicit.mean())
            self.assertAlmostEqual(widths[i], explicit.std(ddof=1) / explicit.mean())

    def test_scaling_retains_width_zeros_and_own_mean_tail(self):
        values = np.array([0., 1., 2., 2., 5.])
        a, b = moments(values), moments(values * .01)
        for key in ("fractional_width", "below_half_mean_fraction", "zero_events"):
            self.assertAlmostEqual(a[key], b[key])
        self.assertEqual(a["events"], 5)

    def test_bin_boundaries_and_outside_rejection(self):
        np.testing.assert_equal(index(np.array([0., 1., 2.]), np.array([0., 1., 2.])), [0, 1, 1])
        with self.assertRaises(ValueError): index(np.array([3.]), np.array([0., 1., 2.]))

    def test_ledger_tampering_and_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = {"exit_code": 0, "disk_abort": False, "events": 2, "skip": 0}
            (root / "receipt.json").write_text(json.dumps(receipt))
            rows = [dict(event=i, energy_GeV=20., eta=0., phi=0., signal_GeV=.2, response=.01) for i in (0, 1)]
            def save():
                (root / "event-summary.jsonl").write_text("\n".join(map(json.dumps, rows)))
                proof = {"status": "PASS", "receipt_sha256": sha(root / "receipt.json"), "event_summary_sha256": sha(root / "event-summary.jsonl"), "root_sha256": "fixture"}
                (root / "readback.json").write_text(json.dumps(proof))
            save(); self.assertEqual(len(load_run(root)[0]), 2)
            rows[1]["event"] = 0; save()
            with self.assertRaisesRegex(ValueError, "duplicate"): load_run(root)
            rows[1]["event"] = 1; save()
            (root / "event-summary.jsonl").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "Changed"): load_run(root)


if __name__ == "__main__": unittest.main()
