"""Contracts that catch wrong HCAL persisted addresses and primary inputs."""
import argparse
import json
import math
from pathlib import Path
import tempfile
import unittest

from transport import decode_cell, ID_DESCRIPTOR, MASS_GEV, prepare, sensitive_count


def encode(**overrides):
    values = dict(system=13, side=0, sector=15, layer=59, carrier=4095, module=1, sensor=35)
    values.update(overrides)
    return sum(values[key] << offset for key, offset in
        (("system",0),("side",8),("sector",10),("layer",14),("carrier",20),("module",32),("sensor",34)))


class Contracts(unittest.TestCase):
    def test_cell_boundaries_and_reserved_fields(self):
        fields = decode_cell(encode())
        self.assertEqual([fields[k] for k in ("system","sector","layer","carrier","module","sensor")], [13,15,59,4095,1,35])
        self.assertEqual(decode_cell(encode(system=14, side=2))["side"], 2)
        for cell in (encode(layer=60), encode(module=2), encode(sensor=36), encode(side=1),
                     encode(system=14,side=0), encode() | 1 << 40, encode() | 1 << 42):
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                decode_cell(cell)

    def test_compounded_geometry_uses_context_count_not_channel_count(self):
        self.assertEqual(sensitive_count(dict(raw_sensitive_volumes=2,sensitive_tiles=144)),2)

    def test_fixed_total_energy_and_geometry_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); geometry = base / "geometry"; geometry.mkdir()
            (geometry / "expected.json").write_text(json.dumps(dict(id_descriptor=ID_DESCRIPTOR,sensitive_tiles=144,raw_sensitive_volumes=2)))
            compact = '<lccdd><readouts/><detectors><detector id="13" name="HCALBarrel" readout="HCALBarrelHits"/><detector id="14" name="HCALEndcaps" readout="HCALEndcapHits"/></detectors></lccdd>'
            (geometry / "detector.xml").write_text(compact)
            (geometry / "materials.xml").write_text('<materials/>')
            (geometry / "placements.csv").write_text('system,side,sector,layer,carrier\n13,0,0,0,0\n14,1,0,0,0\n')
            args = argparse.Namespace(geometry=geometry,output=base / "sample",events=12,input_seed=20261120)
            prepare(args)
            truth = [json.loads(line) for line in (args.output / "truth-input.jsonl").read_text().splitlines()]
            self.assertEqual([row["event"] for row in truth],list(range(12)))
            for row in truth:
                self.assertAlmostEqual(math.sqrt(sum(x*x for x in row["momentum_GeV"])+MASS_GEV**2),50.,places=12)
                self.assertTrue(-3<=row["eta"]<=3 and -math.pi<=row["phi"]<=math.pi)
            (geometry / "detector.xml").write_text(compact.replace('<readouts/>','<readouts/><fields/>'))
            args.output = base / "invalid"
            with self.assertRaises(ValueError): prepare(args)
            self.assertFalse(args.output.exists())


if __name__ == '__main__': unittest.main()
