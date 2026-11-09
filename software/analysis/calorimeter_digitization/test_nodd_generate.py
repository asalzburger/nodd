"""Frozen population identity and input-integrity controls for nODD transport."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from nodd_generate import canonical, referenced_files, rows, sha, verify


class FrozenTransportControls(unittest.TestCase):
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
