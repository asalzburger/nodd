import json
import math
from pathlib import Path
import tempfile
import unittest

from central_sample import MASS, primaries


class FixedPrimaryTests(unittest.TestCase):
    def test_hepevt_and_ledger_have_single_electron_and_exact_total_energy(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            phi = math.radians(.7)
            primaries(out, 4, 50., .1, phi)
            lines = (out / 'particles.HEPEvt').read_text().splitlines()
            self.assertEqual(len(lines), 8)
            rows = [json.loads(line) for line in (out / 'truth-input.jsonl').read_text().splitlines()]
            self.assertEqual([row['event'] for row in rows], list(range(4)))
            for i, row in enumerate(rows):
                self.assertEqual(lines[2*i], '1')
                self.assertEqual(lines[2*i+1].split()[:4], ['1', '11', '0', '0'])
                px, py, pz = map(float, lines[2*i+1].split()[4:7])
                self.assertAlmostEqual(math.sqrt(px*px+py*py+pz*pz+MASS*MASS), 50., places=12)
                self.assertAlmostEqual(math.asinh(pz/math.hypot(px, py)), .1, places=14)
                self.assertAlmostEqual(math.atan2(py, px), phi, places=14)
                self.assertEqual(row['momentum_GeV'], [px, py, pz])


if __name__ == '__main__':
    unittest.main()
