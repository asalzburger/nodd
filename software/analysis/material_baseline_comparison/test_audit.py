"""The explicit native audit cannot be applied to different geometry/recordings."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1]/'material_profiles/categorize.py'
spec = importlib.util.spec_from_file_location('category_launcher', path)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class AuditIdentityTests(unittest.TestCase):
    def test_audit_is_bound_to_inputs_and_supported_passive_volume(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            files = [p/name for name in ('tracks.root', 'tracker.xml', 'materials.xml', 'factory.dylib', 'lookups.json')]
            for f in files:
                f.write_text(f.name)
            recording, compact, materials, factory, lookups = files
            audit = {'recording_sha256': launcher.sha(recording), 'compact_sha256': launcher.sha(compact),
                'materials_sha256': launcher.sha(materials), 'factories': [{'sha256': launcher.sha(factory)}],
                'lookups_sha256': launcher.sha(lookups), 'rows': 1,
                'certified_steps': [{'track': 5, 'step': 3, 'category': 4,
                    'volume': 'pickup', 'path': '/ShortStripEndcap/pickup'}]}
            report = p/'provenance.json'; report.write_text(json.dumps(audit))
            labels = launcher.audit_labels(report, recording, compact, [factory], p)
            self.assertEqual(Path(labels).read_text(), '5 3 pickup\n')
            factory.write_text('changed geometry')
            with self.assertRaisesRegex(ValueError, 'identities'):
                launcher.audit_labels(report, recording, compact, [factory], p)
            factory.write_text(factory.name)
            audit['certified_steps'][0]['category'] = 5
            report.write_text(json.dumps(audit))
            with self.assertRaisesRegex(ValueError, 'passive-endcap'):
                launcher.audit_labels(report, recording, compact, [factory], p)


if __name__ == '__main__':
    unittest.main()
