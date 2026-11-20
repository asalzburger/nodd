"""Contracts that catch wrong HCAL persisted addresses and primary inputs."""
import argparse
import json
import math
from pathlib import Path
import tempfile
import unittest

from transport import decode_cell, ID_DESCRIPTOR, MASS_GEV, prepare, sensitive_count, compile_unit_centers, checked_direction, PARENT_MASK


def encode(**overrides):
    values = dict(unit=0,system=13, side=0, sector=15, layer=59, carrier=4095, module=1, sensor=35)
    values.update(overrides)
    return sum(values[key] << offset for key, offset in
        (("system",0),("side",8),("sector",10),("layer",14),("carrier",20),("module",32),("sensor",34),("unit",42)))


class Contracts(unittest.TestCase):
    def test_cell_boundaries_and_reserved_fields(self):
        fields = decode_cell(encode())
        self.assertEqual([fields[k] for k in ("system","sector","layer","carrier","module","sensor")], [13,15,59,4095,1,35])
        self.assertEqual(decode_cell(encode(system=14, side=2))["side"], 2)
        for cell in (encode(layer=60), encode(module=2), encode(sensor=36), encode(side=1),
                     encode(system=14,side=0), encode() | 1 << 40, encode() | 1 << 50):
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                decode_cell(cell)

    def test_unit_bits_preserve_common_ids_and_sparse_channels(self):
        legacy=13|15<<10|59<<14|4095<<20|1<<32|35<<34
        self.assertEqual(encode(),legacy)
        edge=encode(unit=100,module=0,sensor=6)
        self.assertEqual(decode_cell(edge)["unit"],100)
        self.assertEqual(edge&PARENT_MASK,(legacy&((1<<32)-1))|100<<42)
        common=dict(channel_map=[dict(module=0,sensor=0,tile_center_mm=[0,0,2],tile_size_mm=[29.7,29.7,3])])
        narrow=dict(channel_map=[dict(module=0,sensor=6,tile_center_mm=[-4,30,2],tile_size_mm=[15.5,29.7,3])])
        mapping=compile_unit_centers(dict(units={"0":common,"100":narrow}))
        self.assertIn((100,0,6),mapping);self.assertNotIn((100,0,7),mapping)
        narrow["channel_map"].append(narrow["channel_map"][0])
        with self.assertRaises(ValueError):compile_unit_centers(dict(units={"0":common,"100":narrow}))

    def test_fixed_direction_pair_and_phase_space(self):
        self.assertEqual(checked_direction(.2,.1),(.2,.1))
        for eta,phi in ((None,0),(0,None),(math.nan,0),(0,math.inf),(0,math.pi),(3.1,0)):
            with self.subTest(eta=eta,phi=phi),self.assertRaises(ValueError):checked_direction(eta,phi)

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

    def test_fixed_preparation_retains_independent_role_and_exact_vector(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);geometry=base/'geometry';geometry.mkdir()
            (geometry/'expected.json').write_text(json.dumps(dict(id_descriptor=ID_DESCRIPTOR,sensitive_tiles=144,raw_sensitive_volumes=2)))
            (geometry/'detector.xml').write_text('<lccdd><readouts/><detectors><detector id="13" name="HCALBarrel" readout="HCALBarrelHits"/><detector id="14" name="HCALEndcaps" readout="HCALEndcapHits"/></detectors></lccdd>')
            (geometry/'materials.xml').write_text('<materials/>');(geometry/'placements.csv').write_text('system,side,sector,layer,carrier,unit\n13,0,0,0,0,0\n14,1,0,0,0,0\n')
            direction=base/'direction.json';direction.write_text(json.dumps(dict(winner=dict(eta=.12,phi_rad=.03125))))
            args=argparse.Namespace(geometry=geometry,output=base/'calibration',events=2000,input_seed=20261120,fixed_eta=.12,fixed_phi=.03125,sample_role='calibration',sample_id='TEST-calibration',direction_receipt=direction,primary_sample=None)
            prepare(args);manifest=json.loads((args.output/'sample.json').read_text());rows=[json.loads(l) for l in (args.output/'truth-input.jsonl').read_text().splitlines()]
            self.assertEqual(manifest['expected_transport_seed'],202650102);self.assertIsNone(manifest['input_seed'])
            self.assertEqual({(r['eta'],r['phi']) for r in rows},{(.12,.03125)})
            self.assertTrue(all(r['momentum_GeV']==rows[0]['momentum_GeV'] for r in rows))
            args.output=base/'bad-direction';args.fixed_phi=.04
            with self.assertRaises(ValueError):prepare(args)
            self.assertFalse(args.output.exists())


if __name__ == '__main__': unittest.main()
