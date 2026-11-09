"""Scientific controls: descriptor identity and shared-reference covariance."""
import tempfile
import json
import copy
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

import numpy as np

from nodd_response import (bind_configuration, decode, descriptors, longitudinal, ratio,
                           shower_summary, verify_runs, global_index, expected_configuration,
                           muon_bindings, reuse_muons, sha)
from nodd_generate import rows


class ResponseControls(unittest.TestCase):
    def test_muon_subset_preserves_full_population_seeds(self):
        manifest = dict(samples=rows(), geometries={g:dict(collections=[g]) for g in ('nodd','odd-zero')})
        selected = [s for s in manifest['samples'] if s['kind']=='muons']
        self.assertEqual(len(selected),6)
        self.assertEqual([global_index(manifest,s) for s in selected],list(range(38,44)))
        self.assertEqual([expected_configuration(global_index(manifest,s),s,manifest)['seed'] for s in selected],
                         [129300,129400,129500,129600,129700,129800])

    def test_closed_muon_reuse_rejects_changed_output_or_final_inputs(self):
        runs=[dict(kind='muons',sample=dict(id='synthetic-A'),receipt=dict(identity='frozen'))]
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory); args=SimpleNamespace(work=work,muon_summary=work/'muon-summary.json')
            samples=work/'synthetic-samples.json';samples.write_text('{}')
            snapshot=work/'runs-muons.json';snapshot.write_text(json.dumps(runs))
            provenance={k:'frozen' for k in ('analysis_sha256','protocol_sha256','analysis_notes_sha256',
                'plugin_registration_audit_sha256','transport_manifest_sha256','muon_source_sha256')}
            current=dict(settings=dict(threshold=.6),pedestal=dict(SD=.13),provenance=provenance)
            cached=copy.deepcopy(current);cached['muons']=dict(scope='synthetic aggregate')
            cached['provenance'].update(muon_bindings=muon_bindings(runs),native_runs_sha256=sha(snapshot),samples_sha256=sha(samples))
            args.muon_summary.write_text(json.dumps(cached))
            completion=Path(str(args.muon_summary)+'.completion.json')
            completion.write_text(json.dumps(dict(output_sha256=sha(args.muon_summary),samples_path=str(samples),provenance=cached['provenance'])))
            self.assertEqual(reuse_muons(args,runs,copy.deepcopy(current)),cached['muons'])
            changed=copy.deepcopy(runs);changed[0]['sample']['id']='synthetic-B'
            with self.assertRaisesRegex(ValueError,'final verified inputs/source'):
                reuse_muons(args,changed,copy.deepcopy(current))
            args.muon_summary.write_text(json.dumps(dict(cached,muons=dict(scope='altered'))))
            with self.assertRaisesRegex(ValueError,'output changed'):
                reuse_muons(args,runs,copy.deepcopy(current))

    def test_outer_population_labels_cannot_override_bound_sample(self):
        sample = dict(geometry='nodd', kind='showers')
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(work=Path(directory))
            for key, changed in (('geometry', 'odd-zero'), ('kind', 'calibration')):
                with self.subTest(key=key):
                    row = dict(sample=sample, **sample)
                    row[key] = changed
                    (args.work/'runs.json').write_text(json.dumps([row]))
                    with patch('nodd_response.ordered_samples', return_value=({}, [sample])):
                        with self.assertRaisesRegex(ValueError, 'labels differ'):
                            verify_runs(args)

    def test_configuration_and_raw_identity_are_bound(self):
        expected={'seed':125500,'collections':['BARRELHits','EDGEHits']}
        receipt={'identity':{'configuration':expected,'input_sha256':'raw-A'}}
        bind_configuration(receipt,dict(expected),expected,'raw-A')
        with self.assertRaisesRegex(ValueError,'configuration/input'):
            bind_configuration(receipt,dict(expected,seed=125600),expected,'raw-A')
        with self.assertRaisesRegex(ValueError,'configuration/input'):
            bind_configuration(receipt,dict(expected),expected,'raw-B')

    def test_fully_empty_longitudinal_population_retains_events(self):
        events=[dict(raw_GeV=0.,modes={mode:dict(energy_GeV=0.,cells={'A':[],'B':[]}) for mode in ('off','on')}) for _ in range(4)]
        frame=SimpleNamespace(get=lambda name:[])
        podio=SimpleNamespace(root_io=SimpleNamespace(Reader=lambda path:SimpleNamespace(get=lambda name:[frame]*4)))
        with patch.dict(sys.modules,{'podio':podio}),patch('nodd_response.descriptors',return_value={'A':{},'B':{}}):
            result=longitudinal({'sample':{'path':'synthetic-empty'}},events,{'compact':'unused','collections':['A','B']})
        self.assertEqual(result['events'],4)
        self.assertEqual(result['axes'],[])
        self.assertEqual(result['stages']['raw']['mean'],[])

    def test_zero_denominator_remains_undefined(self):
        result = ratio(np.array([0., 2.]), np.array([0., 4.]))
        self.assertTrue(np.isnan(result[0]))
        self.assertEqual(result[1], .5)

    def test_actual_descriptor_offsets_and_signed_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'detector.xml'
            path.write_text('<lccdd><readouts><readout name="A"><id>system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6</id></readout><readout name="B"><id>system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,y:-16</id></readout></readouts></lccdd>')
            fields = descriptors(path, ['A', 'B'])
            cid = 9 | (2 << 8) | (47 << 14) | (63 << 30)
            self.assertEqual(decode(cid, fields['A'], 'layer'), 47)
            self.assertEqual(decode(cid, fields['A'], 'side'), 2)
            self.assertEqual(decode(cid, fields['A'], 'x'), -1)
            self.assertEqual(decode(48 << 16, fields['B'], 'layer'), 48)

    def test_shared_calibration_keeps_geometry_ratio_and_covariance(self):
        runs = []
        events = {}
        def add(key, kind, geometry, eta, triples):
            runs.append(dict(fixture=key, kind=kind, geometry=geometry,
                             sample=dict(eta=eta, particle='e-', energy_GeV=20, id=key,
                                         sha256=key, truth=dict(generated_total_energy_GeV=20.)),
                             receipt=dict(output_sha256=key)))
            events[key] = [dict(raw_GeV=a, modes={'off':dict(energy_GeV=b), 'on':dict(energy_GeV=c)})
                           for a,b,c in triples]
        for eta in (0,1,2,-2):
            add('cal'+str(eta), 'calibration', 'odd-zero', eta, [(9,9,9),(11,11,11)])
        add('nodd', 'showers', 'nodd', 0, [(5.,4.95,4.9)]*4)
        add('odd', 'showers', 'odd-zero', 0, [(10.,9.9,9.8)]*4)
        with tempfile.TemporaryDirectory() as directory:
            args = SimpleNamespace(work=Path(directory))
            with patch('nodd_response.read_events', side_effect=lambda row:events[row['fixture']]), patch('nodd_response.longitudinal', return_value={'scope':'synthetic unit control'}):
                result = shower_summary(runs, {'geometries':{'nodd':{},'odd-zero':{}}}, args)
        comparison = result['geometry_comparisons'][0]
        for stage in ('raw','off','on'):
            self.assertAlmostEqual(comparison['stages'][stage]['mean_ratio_nodd_over_ODD'], .5)
            self.assertLess(comparison['stages'][stage]['mean_ratio_bootstrap']['SE'], 1e-14)
        cov = np.asarray(result['response_bootstrap_covariance'])
        self.assertGreater(cov[0,3], 0.)
        self.assertAlmostEqual(cov[0,3]**2/(cov[0,0]*cov[3,3]), 1., places=12)
        self.assertEqual(result['populations'][0]['n'], 4)
        self.assertEqual(result['populations'][0]['stages']['raw']['visible_fraction_histogram']['entries'], 4)


if __name__ == '__main__':
    unittest.main()
