"""Failure controls for the gate between native geometry and transport."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.muon_dd4hep import run_validation as runner


class ValidationGateTests(unittest.TestCase):
    def invoke(self, geometry_status='PASS', geometry_rc=0, observed_events=1000):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ('compact.xml', 'expected.json', 'factory.dylib'):
                (folder / name).write_text('test fixture')
            commands = []

            def execute(command, log, records, env):
                commands.append(command)
                if command[1] == '-B':
                    output = Path(command[command.index('--output') + 1])
                    output.write_text(json.dumps({'status': geometry_status, 'overlaps': [] if geometry_status == 'PASS' else ['fixture overlap']}))
                    return geometry_rc
                return 0

            with patch.dict('sys.modules', {'dd4hep': SimpleNamespace(mm=0.1), 'ROOT': SimpleNamespace(gROOT=SimpleNamespace(GetVersion=lambda: 'fixture'))}), \
                    patch.object(runner.shutil, 'which', return_value='/bin/true'), \
                    patch.object(runner, 'execute', side_effect=execute), \
                    patch.object(runner, 'event_count', return_value={'events': observed_events}), \
                    patch.object(runner, 'digest', return_value='fixture-sha'):
                rc = runner.main(['--compact', str(folder/'compact.xml'), '--expected', str(folder/'expected.json'),
                                  '--library', str(folder/'factory.dylib'), '--output-dir', str(folder/'out')])
            return rc, json.loads((folder/'out/run.json').read_text()), commands

    def test_stock_success_does_not_override_native_overlap_failure(self):
        rc, report, commands = self.invoke(geometry_status='FAIL', geometry_rc=1)
        self.assertEqual(rc, 1)
        self.assertEqual(len(commands), 2)
        self.assertIn('gate failed', report['errors'][0])
        self.assertNotIn('--enableGun', str(commands))

    def test_zero_exit_without_native_pass_still_blocks_transport(self):
        rc, report, commands = self.invoke(geometry_status='FAIL', geometry_rc=0)
        self.assertEqual(rc, 1)
        self.assertEqual(len(commands), 2)

    def test_successful_process_with_wrong_event_count_fails(self):
        rc, report, commands = self.invoke(observed_events=999)
        self.assertEqual(rc, 1)
        self.assertEqual(len(commands), 3)
        self.assertIn('event count differs', report['errors'][0])
        # mm conversion is essential: stock checkOverlaps passes a raw ROOT value.
        self.assertAlmostEqual(report['stock_tolerance_native'], 1e-6)
        self.assertIn('20*GeV', commands[-1])
        self.assertIn('92393', commands[-1])


if __name__ == '__main__':
    unittest.main()
