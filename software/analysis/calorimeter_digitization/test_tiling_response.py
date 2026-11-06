"""Synthetic software regressions; no detector construction or transport.

Run with a Python environment providing NumPy, for example:
  software/env/run.sh python3 software/analysis/calorimeter_digitization/test_tiling_response.py
"""
from contextlib import ExitStack, redirect_stdout
import io
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import tiling_response as response


class ResponseAccounting(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='nodd-response-software-')
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.factory = self.work / 'factory'
        self.factory.mkdir()
        (self.factory / 'library').write_text('synthetic factory')
        self.args = SimpleNamespace(work=self.work, factory=self.factory, geometry='tiled',
                                    calibration_only=False, skip_calibration=False,
                                    output=self.work / 'analysis.json')
        self.manifest = dict(groups={}, compacts=dict(tiled='t', continuous='c'),
                             protocol_sha256='p', factory=dict(path=response.relative(self.factory / 'library')),
                             points=[dict(id='C', direction=[0, 0, 1])])
        for geometry in ('tiled', 'continuous'):
            response.save(self.work / (geometry + '-native.json'),
                          dict(status='PASS', normal_cleanup_completed=True,
                               compact_sha256=self.manifest['compacts'][geometry]))
        self.stack = self.enterContext(ExitStack())
        self.stack.enter_context(redirect_stdout(io.StringIO()))
        self.stack.enter_context(patch.object(response, 'verify', return_value=self.manifest))

    @staticmethod
    def row(name, n=2, kind='response'):
        return dict(id=name, file=name + '.root', geometry='tiled', point_id='C', energy_GeV=20,
                    n=n, kind=kind, seed=123, seed_pair=[123, 456])

    def controller_fixtures(self, final_contents=None):
        """Emulate output-file closure, including a change after checkpoint."""
        class Reader:
            def __init__(self, path):
                self.path = Path(path)

            def get(self, key):
                return [None] * int(self.path.read_text())

        class Process:
            returncode = 0

            def __init__(self, command, env, cwd, stdout, stderr):
                self.outputs = []
                self.polls = 0
                macro = Path(command[command.index('--macroFile') + 1]).read_text()
                for line in macro.splitlines():
                    if line.startswith('/ddg4/EDM4hepOutput/Output '):
                        output = Path(line.split(' ', 1)[1])
                    if line.startswith('/run/beamOn '):
                        n = int(line.split()[-1])
                        output.write_text(str(n))
                        stdout.write(f'Finished run {len(self.outputs)} after {n} events\n')
                        self.outputs.append(output)
                stdout.write('Reused HepRandom engine instance MixMaxRng\n')
                stdout.flush()

            def poll(self):
                self.polls += 1
                if final_contents is not None and self.polls == 1:
                    return None  # observe a complete checkpoint first
                if final_contents is not None:
                    for output in self.outputs:
                        output.write_text(final_contents)
                return 0

        random_module = ModuleType('DDSim.Helper.Random')
        random_module.__file__ = str(self.factory / 'library')
        random_module.Random = type('Random', (), dict(__module__=random_module.__name__, enableEventSeed=False))
        podio = ModuleType('podio')
        podio.root_io = SimpleNamespace(Reader=Reader)
        self.stack.enter_context(patch.dict('sys.modules', {'DDSim.Helper.Random': random_module, 'podio': podio}))
        self.stack.enter_context(patch.object(response.subprocess, 'Popen', Process))
        self.stack.enter_context(patch.object(response.time, 'sleep'))

    def test_resume_preserves_evidence_and_rejects_tampering(self):
        self.controller_fixtures()
        first, second = self.row('first'), self.row('second')
        self.manifest['groups']['tiled'] = [first]
        response.run(self.args)
        record = response.execution_record(self.args, self.manifest, first)
        self.assertTrue(record['final_output_verified'])
        self.assertEqual(record['verified_event_count'], 2)
        evidence = {kind: (response.ROOT / record[kind + '_file'], record[kind + '_sha256'])
                    for kind in ('macro', 'producer', 'log')}
        self.assertFalse((self.work / first['file']).exists())
        self.manifest['groups']['tiled'].append(second)
        response.run(self.args)
        self.assertEqual(len(list((self.work / 'attempts').iterdir())), 2)
        self.assertTrue(all(response.sha(path) == digest for path, digest in evidence.values()))
        for kind, (path, _) in evidence.items():
            with self.subTest(kind=kind):
                original = path.read_bytes()
                path.write_bytes(original + b'changed')
                with self.assertRaisesRegex(ValueError, kind):
                    response.execution_record(self.args, self.manifest, first)
                path.write_bytes(original)
        raw = self.work / record['sample']['file']
        raw.write_text('corrupted')
        with self.assertRaises(ValueError):
            response.execution_record(self.args, self.manifest, first)

    def test_final_output_hash_is_rechecked_after_checkpoint(self):
        self.controller_fixtures(final_contents='2\n')
        row = self.row('closure')
        self.manifest['groups']['tiled'] = [row]
        response.run(self.args)
        record = response.execution_record(self.args, self.manifest, row)
        self.assertTrue(record['final_output_verified'])
        self.assertEqual(record['verified_event_count'], 2)
        self.assertNotEqual(record['checkpoint_output_sha256'], record['output_sha256'])

    def test_final_incomplete_event_count_is_rejected(self):
        self.controller_fixtures(final_contents='1')
        self.manifest['groups']['tiled'] = [self.row('incomplete')]
        with self.assertRaisesRegex(RuntimeError, 'Incomplete finished run'):
            response.run(self.args)

    def analysis_fixtures(self):
        rows = [self.row('cal', 100, 'calibration'), self.row('zero', 200), self.row('sparse', 200)]
        self.manifest.update(groups=dict(tiled=rows),
                             analysis=dict(bootstrap_seed=11893000, bootstrap_replicates=2000, histogram_bins=1000),
                             materials_sha256='mat')
        version = self.work / 'dd4hep'
        version.mkdir()
        (version / 'DD4hepConfigVersion.cmake').write_text('set(PACKAGE_VERSION "software-fixture")')
        (self.factory / 'CMakeCache.txt').write_text('DD4hep_DIR:PATH=' + str(version))
        (self.factory / 'libnODDCalorimeterPrototype.components').write_text('synthetic')
        names = ('manifest.json', 'tiled.xml', 'continuous.xml', 'materials.xml', 'expected.json',
                 'sensitive-diagnostic.xml', 'sensitive-diagnostic.edm4hep.root', 'sensitive-diagnostic.log',
                 'pilot-tiled.edm4hep.root', 'pilot-tiled.log')
        for name in names:
            (self.work / name).write_text('synthetic')
        defaults = dict(software_fixture=True)
        self.stack.enter_context(patch.object(response, 'sensitive_defaults', return_value=defaults))
        response.save(self.work / 'pilot-checks.json', dict(synthetic=True))
        response.save(self.work / 'sensitive-diagnostic.json',
                      dict(status='PASS', materials_sha256='mat', defaults=defaults, birks_constant_mm_per_MeV=0,
                           producer_file=response.relative(self.factory / 'library'),
                           producer_sha256=response.sha(self.factory / 'library'),
                           compact_sha256=response.sha(self.work / 'sensitive-diagnostic.xml')))
        log = self.work / 'log'
        log.write_text("Setting up SD for EDGE with Geant4ScintillatorCalorimeterAction\n"
                       "Adding default filter 'edep0' to sensitive detector for 'EDGE'\n"
                       "GlobalRangeCut RangeCut0.700000mm\n")
        for row in rows:
            (self.work / row['file']).write_text('synthetic')
            response.save(self.work / (row['id'] + '.execution.json'),
                          dict(sample=row, log_file=response.relative(log), macro_file=response.relative(log),
                               producer_file=response.relative(log)))
        arrays = dict(cal=np.ones(100), zero=np.zeros(200), sparse=np.r_[1., np.zeros(199)])

        def read(args, manifest, row):
            values = arrays[row['id']]
            layers = np.zeros((len(values), 48))
            layers[:, 0] = values
            return values, layers, {}, {}

        self.stack.enter_context(patch.object(response, 'read_sample', read))
        self.stack.enter_context(patch.dict('sys.modules', {'ROOT': SimpleNamespace(gROOT=SimpleNamespace(GetVersion=lambda: 'software-fixture'))}))
        self.stack.enter_context(patch.object(response.shutil, 'which', return_value=str(self.factory / 'library')))
        self.stack.enter_context(patch.object(response.subprocess, 'check_output', return_value='software-fixture'))
        self.stack.enter_context(patch.dict(response.os.environ, {'DD4hep_DIR': str(version)}))
        return arrays

    def test_zero_sparse_widths_and_histogram_denominators(self):
        self.analysis_fixtures()
        # Fresh reproduction may prepare a different factory than the CLI
        # default. Analysis must retain the manifest's actual registration.
        self.args.factory = self.work / 'unrelated-cli-default'
        response.analyze(self.args)
        result = json.loads(self.args.output.read_text())
        zero, sparse = result['samples']
        self.assertIsNone(zero['relative_width'])
        self.assertEqual(zero['bootstrap']['undefined_width_replicates'], 2000)
        self.assertIsNone(zero['bootstrap']['relative_width_standard_error'])
        self.assertEqual(zero['quantiles_GeV']['q50'], 0)
        self.assertGreater(sparse['bootstrap']['undefined_width_replicates'], 0)
        self.assertLess(sparse['bootstrap']['undefined_width_replicates'], 2000)
        self.assertIsNone(sparse['bootstrap']['relative_width_percentile95'])
        for sample in result['samples']:
            histogram = sample['histogram']
            self.assertEqual(sum(histogram['counts']) + histogram['underflow'] + histogram['overflow'], 200)

    def test_shared_reference_covariance_and_positive_calibration_gate(self):
        arrays = self.analysis_fixtures()
        # With constant response energies at the cut, its reference fluctuation
        # must move both tail fractions together in the same bootstrap replicate.
        arrays.update(cal=np.linspace(.9, 1.1, 100), zero=np.full(200, .8), sparse=np.full(200, .8))
        response.analyze(self.args)
        joint = json.loads(self.args.output.read_text())['joint_tail_bootstrap']
        covariance = np.asarray(joint['covariance'])
        self.assertEqual(joint['sample_ids'], ['zero', 'sparse'])
        self.assertEqual(covariance.shape, (2, 2))
        self.assertTrue(np.allclose(covariance, covariance.T))
        self.assertGreater(covariance[0, 1], .1)
        self.assertTrue(np.allclose(covariance, covariance[0, 0]))
        arrays['cal'] = np.zeros(100)
        with self.assertRaisesRegex(ValueError, 'Calibration'):
            response.analyze(self.args)


if __name__ == '__main__':
    unittest.main()
