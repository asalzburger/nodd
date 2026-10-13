"""Signed sparse-hit and combined-ECAL guards, with standard library only."""
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from endcap_geometry import build,encode,ID_FIELDS
from endcap_export import compact
from endcap_transport import fixtures,observed_run,transformed,valid_cell,validate_rows
from combined_native import merge_materials,validate_ray
from barrel_geometry import sha


class TransportCombinationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.expected,cls.materials=build()

    def test_all_wheels_signed_real_hits_and_ghost_fields(self):
        r=self.expected
        for side in (1,2):
            fixture=dict(side=side)
            for w in r['wheels']:
                for ref in w['reference_points']:
                    f=dict(system=11,side=side,wheel=w['wheel'],plane=0,gap=0,rho=ref['rho'],z=ref['z'])
                    self.assertEqual(valid_cell(encode(f),r,fixture),f)
                for key,value in [('side',3),('wheel',3),('plane',1),('gap',1),('rho',w['radial_bins']),('z',10),('system',10)]:
                    invalid=dict(f);invalid[key]=value
                    with self.assertRaises(ValueError):valid_cell(encode(invalid),r,fixture)
                with self.assertRaises(ValueError):valid_cell(encode(f)|(1<<sum(n for _,n in ID_FIELDS)),r,fixture)
                with self.assertRaises(ValueError):valid_cell(-1,r,fixture)

    def test_saved_energy_and_observed_run_controls(self):
        f=dict(system=11,side=1,wheel=1,plane=0,gap=0,rho=7,z=4);cid=encode(f)
        self.assertEqual(len(validate_rows([dict(cell_id=cid,energy_GeV=.001)],self.expected,dict(side=1))),1)
        for energy in (0,-1,float('inf'),float('nan')):
            with self.assertRaises(ValueError):validate_rows([dict(cell_id=cid,energy_GeV=energy)],self.expected,dict(side=1))
        with self.assertRaises(ValueError):validate_rows([],self.expected,dict(side=1))
        request=dict(seed=42,events=1,physics_list='FTFP_BERT')
        good='PhysicsList FTFP_BERT\nRandom generator with seed 42\nFinished run 0 after 1 events'
        self.assertEqual(observed_run(good,request)['seed'],42)
        for bad in (good.replace('seed 42','seed 43'),good.replace('FTFP_BERT','QGSP_BERT'),good.replace('after 1 events','after 0 events')):
            with self.assertRaises(ValueError):observed_run(bad,request)

    def test_signed_fixture_selection_and_gun_transform(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);report=deepcopy(self.expected);compact(report,directory)
            ET.ElementTree(self.materials.root).write(directory/'materials.xml',encoding='utf-8',xml_declaration=True)
            report['artifact_sha256']={'endcaps.xml':sha(directory/'endcaps.xml'),'materials.xml':sha(directory/'materials.xml')}
            (directory/'expected.json').write_text(json.dumps(report))
            metadata=fixtures(directory/'endcaps.xml',directory/'expected.json',directory/'sparse')
            self.assertEqual(len(metadata),2)
            for m in metadata:
                self.assertEqual(len(m['retained_replicas']),3)
                self.assertEqual({r['wheel'] for r in m['retained_replicas']},{0,1,2})
                tree=ET.parse(directory/'sparse'/f"side{m['side']}"/'fixture.xml')
                self.assertEqual(len(tree.getroot().findall('detectors/detector/piece')),0)
                self.assertEqual(len(tree.getroot().findall('detectors/detector/wheel')),3)
                self.assertEqual(len(tree.getroot().findall('detectors/detector/replica')),3)
            self.assertAlmostEqual(metadata[0]['position_mm'][0],metadata[1]['position_mm'][0])
            self.assertAlmostEqual(metadata[0]['position_mm'][1],-metadata[1]['position_mm'][1])
            self.assertAlmostEqual(metadata[0]['position_mm'][2],-metadata[1]['position_mm'][2])
            for i in (1,2):self.assertAlmostEqual(metadata[0]['direction'][i],-metadata[1]['direction'][i])
            self.assertAlmostEqual(sum(v*v for v in metadata[0]['direction']),1)

    def test_material_union_identity_and_conflicts(self):
        with tempfile.TemporaryDirectory() as temp:
            paths=[Path(temp)/name for name in ('a.xml','b.xml')]
            for path in paths:path.write_text('<materials><material name="LAr"><D value="1.396" unit="g/cm3"/></material></materials>')
            self.assertEqual(len(merge_materials(paths)),1)
            paths[1].write_text('<materials><material name="LAr"><D value="1.4" unit="g/cm3"/></material></materials>')
            with self.assertRaises(ValueError):merge_materials(paths)

    def test_combined_ray_finiteness_and_eta4_absence(self):
        good=dict(eta=1.,phi_rad=.1,distance_mm=9000,x_over_x0=25,l_over_lambda=.8,LAr_path_mm=120,active_barrel_path_mm=100,active_endcap_path_mm=5)
        validate_ray(good)
        for key,value in [('active_endcap_path_mm',30),('distance_mm',float('inf')),('x_over_x0',-1),('LAr_path_mm',float('nan'))]:
            bad=dict(good);bad[key]=value
            with self.assertRaises(ValueError):validate_ray(bad)
        for sign in (-1,1):
            absent=dict(good,eta=sign*4,active_barrel_path_mm=0,active_endcap_path_mm=0);validate_ray(absent)
            absent['active_endcap_path_mm']=1
            with self.assertRaises(ValueError):validate_ray(absent)


if __name__=='__main__':unittest.main()
