"""Narrow controls; native/persisted-data checks opt in with NODD_HIGHSTAT_NATIVE=1."""
import argparse
import copy
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

import highstat_sample as sample
import highstat_readback as readback
from angular_sample import ROOT, save, sha


class PipelineControls(unittest.TestCase):
    def test_seed_and_primary_repeatability_and_independence(self):
        pairs = [sample.seed_pair(i, 14410000, 144812341) for i in range(12)]
        self.assertEqual(len(set(sum((list(p) for p in pairs), []))), 24)
        first = list(sample.primary_records(100, pairs[0][0], 0))
        second = list(sample.primary_records(100, pairs[1][0], 100))
        self.assertEqual(first, list(sample.primary_records(100, pairs[0][0], 0)))
        self.assertFalse({tuple(r['momentum_GeV']) for r in first} & {tuple(r['momentum_GeV']) for r in second})
        for record in first + second:
            self.assertTrue(10 <= record['energy_GeV'] <= 80 and -3 <= record['eta'] <= 3 and -math.pi <= record['phi'] <= math.pi)
            self.assertAlmostEqual(math.sqrt(sum(p*p for p in record['momentum_GeV']) + sample.ELECTRON_MASS_GEV**2), record['energy_GeV'], places=12)
        self.assertEqual([r['campaign_event'] for r in second], list(range(100, 200)))

    def test_source_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p/'sample.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'retained frozen'):
                sample.verify_source(p)

    def fixture(self, p):
        source = p/'source'; source.mkdir()
        for filename in ('detector.xml','materials.xml'):
            (source/filename).write_text('explicit unit-test fixture '+filename)
        (source/'truth-input.jsonl').write_text(json.dumps(dict(momentum_GeV=[1,2,3]))+'\n')
        hashes = {name:sha(source/name) for name in ('detector.xml','materials.xml')}
        prior = dict(events=1,input_seed=13310000,source_revision='unit-test-source',hashes=hashes)
        args = argparse.Namespace(source=source,output=p/'campaign',training_events=24,validation_events=12,
            batch_events=12,primary_seed=14410000,transport_seed=144812341,bytes_per_event=1270000.,reserve_gib=30.)
        return source, hashes, prior, args

    def test_batch_manifests_bind_ids_seeds_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); source, hashes, prior, args=self.fixture(p)
            with mock.patch.object(sample,'verify_source',return_value=prior), mock.patch.object(sample,'FROZEN_HASHES',hashes), mock.patch.object(sample.shutil,'disk_usage',return_value=argparse.Namespace(free=10**12)):
                sample.prepare(args)
                campaign=json.loads((args.output/'campaign.json').read_text())
                self.assertEqual([x['split'] for x in campaign['batches']],['train','train','validation'])
                all_ids=[]
                for entry in campaign['batches']:
                    _, loaded, folder=sample.load_batch(args.output,entry['batch'])
                    rows=[json.loads(line) for line in (folder/'truth-input.jsonl').read_text().splitlines()]
                    all_ids += [r['campaign_event'] for r in rows]
                    self.assertEqual([r['event'] for r in rows],list(range(12)))
                    self.assertEqual(sha(folder/'particles.HEPEvt'),entry['input_sha256'])
                    self.assertEqual(len((folder/'particles.HEPEvt').read_text().splitlines()),24)
                    manifest=json.loads((folder/'sample.json').read_text())
                    self.assertEqual(manifest['source_revision'],campaign['source_revision'])
                    self.assertFalse(manifest['campaign']['original_source_events_reused'])
                self.assertEqual(all_ids,list(range(36)))
                with self.assertRaises(FileExistsError): sample.prepare(args)
                target=args.output/campaign['batches'][0]['input']/'truth-input.jsonl'
                target.write_text(target.read_text()+'\n')
                with self.assertRaisesRegex(ValueError,'primary records'): sample.load_batch(args.output,'train-000')

    def test_disk_and_seed_guard_fail_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); _,hashes,prior,args=self.fixture(p)
            with mock.patch.object(sample,'verify_source',return_value=prior), mock.patch.object(sample.shutil,'disk_usage',return_value=argparse.Namespace(free=1)):
                with self.assertRaisesRegex(ValueError,'disk budget'): sample.prepare(args)
            self.assertFalse(args.output.exists())
            args.primary_seed=13310000
            with mock.patch.object(sample,'verify_source',return_value=prior), mock.patch.object(sample.shutil,'disk_usage',return_value=argparse.Namespace(free=10**12)):
                with self.assertRaisesRegex(ValueError,'seeds must be fresh'): sample.prepare(args)
            self.assertFalse(args.output.exists())
            args.primary_seed=args.transport_seed
            with mock.patch.object(sample,'verify_source',return_value=prior), mock.patch.object(sample.shutil,'disk_usage',return_value=argparse.Namespace(free=10**12)):
                with self.assertRaisesRegex(ValueError,'seeds must be fresh'): sample.prepare(args)
            self.assertFalse(args.output.exists())
            args.primary_seed=14410000;args.reserve_gib=float('nan')
            with mock.patch.object(sample,'verify_source',return_value=prior):
                with self.assertRaisesRegex(ValueError,'disk guard'): sample.prepare(args)
            self.assertFalse(args.output.exists())

    def test_worker_checks_preserve_response_and_completeness(self):
        base=dict(status='complete',thread_id=0,events=12,maximum_abs_magnetic_field_tesla=0,
            begin_run_rng_seed=12345,rng_engine='MixMaxRng',
            region_cuts=[dict(mm=[.7]*4)],sensitive_si={name:dict(max_step_mm=5,Birks_mm_per_MeV=0) for name in ('BARREL','EDGE')})
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'audit').mkdir(); path=p/'audit/worker-0.json'; save(path,base)
            self.assertEqual(len(readback.validate_workers(p,dict(threads=1,events=12,seed=12345))),1)
            for key,value in [('status','incomplete'),('events',11),('maximum_abs_magnetic_field_tesla',.1),('region_cuts',[]),('begin_run_rng_seed',999),('rng_engine','Ranlux64Engine')]:
                bad=copy.deepcopy(base);bad[key]=value;save(path,bad)
                with self.assertRaises(ValueError):readback.validate_workers(p,dict(threads=1,events=12,seed=12345))
            without_engine=copy.deepcopy(base);del without_engine['rng_engine'];save(path,without_engine)
            self.assertEqual(len(readback.validate_workers(p,dict(threads=1,events=12,seed=12345))),1)
            without_seed=copy.deepcopy(base);del without_seed['begin_run_rng_seed'];save(path,without_seed)
            with self.assertRaisesRegex(ValueError,'seed differs'):readback.validate_workers(p,dict(threads=1,events=12,seed=12345))
            bad=copy.deepcopy(base);bad['sensitive_si']['BARREL']['Birks_mm_per_MeV']=1;save(path,bad)
            with self.assertRaises(ValueError):readback.validate_workers(p,dict(threads=1,events=12,seed=12345))

    def test_run_batch_checks_actual_steering_before_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            def artifact_hash(path):
                path=Path(path)
                if path.name=='angular_transport.py':return 'changed-steering'
                if path.name=='geometry.so':return sample.GEOMETRY_LIBRARY_SHA256
                if path.name=='audit.so':return sample.AUDIT_LIBRARY_SHA256
                return sample.RUNNER_SHA256
            args=argparse.Namespace(campaign=p,batch='train-000',geometry_library=p/'geometry.so',audit_library=p/'audit.so')
            with mock.patch.object(sample,'load_batch',return_value=({}, {}, p/'input')), mock.patch.object(sample,'sha',side_effect=artifact_hash), mock.patch.object(sample.original,'run') as transport:
                with self.assertRaisesRegex(ValueError,'angular_transport.py'):sample.run_batch(args)
                transport.assert_not_called()

    def test_readback_checks_steering_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);run=p/'run';folder=p/'input';run.mkdir();folder.mkdir()
            save(folder/'sample.json',{})
            receipt=dict(exit_code=0,disk_abort=False,sample_sha256=sha(folder/'sample.json'),
                geometry_library_sha256=sample.GEOMETRY_LIBRARY_SHA256,audit_library_sha256=sample.AUDIT_LIBRARY_SHA256,
                runner_sha256=sample.RUNNER_SHA256,steering_sha256='changed-steering')
            save(run/'receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'different steering'):readback.validate_inputs(run,folder)
            del receipt['steering_sha256'];save(run/'receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'different steering'):readback.validate_inputs(run,folder)

    def test_primary_reference_mismatch_rejected(self):
        ref=next(sample.primary_records(1,14410000,0))
        values=[*ref['momentum_GeV'],ref['energy_GeV']]
        energy,eta,phi,errors=readback.verify_primary(values,ref)
        self.assertLess(max(errors.values()),1e-12)
        values[0]+=.001
        with self.assertRaisesRegex(ValueError,'differs'):readback.verify_primary(values,ref)

    def test_zero_signal_and_truth_free_reconstruction(self):
        class Probe:
            def probe(self,eta,phi,fraction):return [.7,.8,.9,.1]
        empty=np.zeros(59)
        out=readback.reconstructed(empty,empty,Probe())
        self.assertFalse(out['valid']);self.assertTrue(np.array_equal(out['feature'],np.zeros(10)))
        cells=np.zeros(59);cells[0]=1;cells[1:4]=[2000,20,1000]
        centre=cells[1:4]; moment=np.outer(centre,centre)
        cells[4:10]=[moment[0,0],moment[1,1],moment[2,2],moment[0,1],moment[0,2],moment[1,2]]
        cells[10]=1;cells[58]=1
        out=readback.reconstructed(cells,empty,Probe())
        self.assertTrue(out['valid']);self.assertEqual(out['feature'][1:5].tolist(),[.7,.8,.9,.1])
        self.assertAlmostEqual(out['feature'][6],1.);self.assertEqual(out['region'],0)


@unittest.skipUnless(os.getenv('NODD_HIGHSTAT_NATIVE')=='1','requires verified ACTS Spack ROOT/EDM4hep runtime')
class NativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import ROOT as R
        import edm4hep
        cls.R=R;readback.declare_native(R)

    def hits(self, entries):
        hits=self.R.edm4hep.SimCalorimeterHitCollection()
        for cell,energy,pos in entries:
            h=hits.create();h.setCellID(cell);h.setEnergy(energy);h.setPosition(self.R.edm4hep.Vector3f(*pos))
        return hits

    def test_native_accumulation_matches_original_and_fsum(self):
        entries=[(8+(layer<<14)+(i<<30),.01/(i+1),(1000+i,-20+i,100+layer)) for i,layer in enumerate((0,2,47))]
        hits=self.hits(entries)
        fast=np.asarray(list(self.R.nodd_highstat.cells(hits,8)))
        old=np.asarray(list(self.R.nodd_staggering.cells(hits)))
        np.testing.assert_allclose(fast,old,rtol=1e-15,atol=1e-15)
        self.assertAlmostEqual(fast[0],math.fsum(float(h.getEnergy()) for h in hits),places=15)
        self.assertEqual(fast[58],3)

    def test_native_rejects_duplicate_system_layer_energy_position(self):
        good=(8,1.,(1000,0,0))
        cases=[[good,good],[(9,1.,(1000,0,0))],[(8+(48<<14),1.,(1000,0,0))],
               [(8,0.,(1000,0,0))],[(8,float('nan'),(1000,0,0))],[(8,1.,(float('inf'),0,0))]]
        for entries in cases:
            with self.subTest(entries=entries):
                with self.assertRaises(Exception):self.R.nodd_highstat.cells(self.hits(entries),8)

    def test_native_primary_requires_one_origin_electron(self):
        particles=self.R.edm4hep.MCParticleCollection()
        p=particles.create();p.setGeneratorStatus(1);p.setPDG(11)
        p.setMomentum(self.R.edm4hep.Vector3d(10,1,1));p.setMass(sample.ELECTRON_MASS_GEV)
        p.setVertex(self.R.edm4hep.Vector3d(0,0,0))
        self.assertEqual(len(self.R.nodd_highstat.primary(particles)),4)
        p.setPDG(22)
        with self.assertRaises(Exception):self.R.nodd_highstat.primary(particles)
        p.setPDG(11);p.setVertex(self.R.edm4hep.Vector3d(1,0,0))
        with self.assertRaises(Exception):self.R.nodd_highstat.primary(particles)
        p.setVertex(self.R.edm4hep.Vector3d(0,0,0));p2=particles.create();p2.setGeneratorStatus(1);p2.setPDG(11)
        with self.assertRaises(Exception):self.R.nodd_highstat.primary(particles)

    def test_persisted_pilot_audit_and_old_features_equivalence(self):
        run=ROOT/'build/ecal-staggering/pilot12';folder=ROOT/'build/ecal-staggering/input-dev'
        if not run.exists():self.skipTest('retained local pilot unavailable')
        from podio import root_io
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'analysis'
            readback.extract(argparse.Namespace(run=run,sample=folder,output=output))
            old=json.loads((run/'readback.json').read_text());new=json.loads((output/'readback.json').read_text())
            self.assertEqual(new['events'],old['events']);self.assertEqual(new['cells_by_collection'],old['cells_by_collection'])
            self.assertEqual(new['event_ids'],old['event_ids']);self.assertEqual(new['maximum_input_errors'],old['maximum_input_errors'])
            self.assertEqual(new['root_sha256'],old['root_sha256']);self.assertEqual(new['worker_events'],old['worker_events'])
            old_rows={r['event']:r for r in map(json.loads,(run/'event-summary.jsonl').read_text().splitlines())}
            new_rows={r['event']:r for r in map(json.loads,(output/'event-summary.jsonl').read_text().splitlines())}
            self.assertEqual(set(old_rows),set(new_rows))
            for event in old_rows:
                self.assertEqual(new_rows[event]['counts'],old_rows[event]['counts'])
                self.assertAlmostEqual(new_rows[event]['signal_GeV'],old_rows[event]['signal_GeV'],places=15)
            arrays=np.load(output/'features/features.npz')
            geometry,native=readback.build_masks(self.R,folder)
            for frame in root_io.Reader(str(run/'events.root')).get('events'):
                header,=frame.get('EventHeader');event=header.getEventNumber()
                b=np.asarray(list(self.R.nodd_staggering.cells(frame.get('BARRELHits'))))
                d=np.asarray(list(self.R.nodd_staggering.cells(frame.get('EDGEHits'))))
                original=readback.reconstructed(b,d,native)
                np.testing.assert_allclose(arrays['features'][event],original['feature'],rtol=1e-10,atol=1e-10)
                np.testing.assert_allclose(arrays['layer_signal'][event],(b+d)[10:58],rtol=1e-14,atol=1e-14)
                self.assertEqual(arrays['valid_axis'][event],original['valid'])
            self.assertEqual(set(arrays.files),{'features','signal','response','energy','eta','phi','region','valid_axis','reconstructed_eta','reconstructed_phi','layer_signal','event'})


if __name__=='__main__':unittest.main()
