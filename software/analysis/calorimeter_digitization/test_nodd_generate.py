"""Frozen population identity and input-integrity controls for nODD transport."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from nodd_generate import ROOT, bind_native, canonical, referenced_files, rows, sha, validate_native, verify


class FrozenTransportControls(unittest.TestCase):
    def native_fixture(self, base):
        (base / 'detector.xml').write_text('<lccdd/>')
        (base / 'materials.xml').write_text('<materials/>')
        library = base / 'factory.dylib'; library.write_bytes(b'native-fixture')
        systems = {f'root{i}':i for i in range(10)}
        record = dict(layout='LAYOUT-001', compact_sha256=sha(base/'detector.xml'),
                      materials_sha256=sha(base/'materials.xml'),
                      components=[dict(system_mapping=[dict(name=k,integrated_system_id=v) for k,v in systems.items()])])
        (base/'baseline.json').write_text(json.dumps(record))
        native = dict(status='PASS', overlap_count=0, baseline_manifest_sha256=sha(base/'baseline.json'),
                      compact_sha256=record['compact_sha256'], materials_sha256=record['materials_sha256'],
                      native_systems=systems, overlap_tolerance_mm=1e-5,
                      native_auditor_sha256=sha(ROOT/'tools/calorimeter_baselines/native.py'),
                      libraries={library.name:sha(library)})
        report = base/'native.json'; report.write_text(json.dumps(native))
        return library, report

    def test_stale_geometry_cannot_inherit_native_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory).resolve()
            library, report=self.native_fixture(base)
            validate_native(base,report,[library])
            (base/'detector.xml').write_text('<lccdd><changed-volume/></lccdd>')
            with self.assertRaisesRegex(ValueError,'geometry/material'):
                validate_native(base,report,[library])

    def test_pending_report_never_authorizes_nodd_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory).resolve()
            library, report=self.native_fixture(base)
            report.unlink()
            manifest=dict(native_report_path=str(report),geometries={'nodd':dict(baseline_directory=str(base),libraries=[str(library)])})
            with self.assertRaises(FileNotFoundError):
                bind_native(base,manifest)
            self.assertFalse((base/'native-pass-binding.json').exists())

    def test_complete_matrix_and_separate_reference_denominators(self):
        samples = rows()
        self.assertEqual(len(samples), 48)
        self.assertEqual(sum(r["requested_events"] for r in samples), 9500)
        nodd = [r for r in samples if r["geometry"] == "nodd"]
        odd = [r for r in samples if r["geometry"] == "odd-zero"]
        self.assertEqual((len(nodd), sum(r["requested_events"] for r in nodd)), (22, 4550))
        self.assertEqual(sum(r["requested_events"] for r in odd if r["kind"] == "calibration"), 400)
        self.assertFalse(any(r["kind"] == "calibration" for r in nodd))

    def test_disjoint_seed_pairs_and_population_ids(self):
        samples = rows()
        self.assertEqual(len({(r["geometry"], r["id"]) for r in samples}), len(samples))
        seeds = [s for r in samples for s in r["seed_pair"]]
        self.assertEqual(len(set(seeds)), len(seeds))
        self.assertTrue(all(s > 0 for s in seeds))

    def test_negative_endcap_is_bounded_control(self):
        negative = [r for r in rows() if r["eta"] == -2]
        self.assertEqual(len(negative), 5)
        self.assertEqual(sorted(r["seed"] for r in negative), [120018, 121018, 122002, 123002, 124003])
        self.assertEqual({r["energy_GeV"] for r in negative if r["kind"] == "showers"}, {20})
        self.assertFalse(any(r["particle"] == "gamma" for r in negative))

    def test_canonical_field_exception_does_not_hide_geometry_change(self):
        original = ET.fromstring('<lccdd><include ref="a.xml"/><detector id="8"/><fields><field strength="3"/></fields></lccdd>')
        zero = ET.fromstring('<lccdd><include ref="/tmp/a.xml"/><detector id="8"/></lccdd>')
        self.assertEqual(canonical(original, Path('/tmp'), True), canonical(zero, Path('/tmp')))
        zero.find('detector').set('id', '9')
        self.assertNotEqual(canonical(original, Path('/tmp'), True), canonical(zero, Path('/tmp')))

    def test_recursive_source_closure_and_changed_input_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            a = base / 'a.xml'
            b = base / 'b.xml'
            a.write_text('<lccdd><include ref="b.xml"/></lccdd>')
            b.write_text('<lccdd/>')
            self.assertEqual(referenced_files(a), {a, b})
            (base / 'manifest.json').write_text(json.dumps({'immutable': {str(b): sha(b)}}))
            verify(base)
            b.write_text('<lccdd changed="yes"/>')
            with self.assertRaisesRegex(ValueError, 'Changed immutable input'):
                verify(base)


if __name__ == '__main__':
    unittest.main()
