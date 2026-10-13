"""Physical negative controls, ownership, readout and material conservation."""
import copy,json,math,tempfile,unittest
from pathlib import Path
from model import ROOT,build,capacity,cut_box,cut_tube,validate_cut
from export import export

class HardwareTests(unittest.TestCase):
    def setUp(self):self.c=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())
    def test_disjoint_guard_and_recess_capacity(self):
        out,_=build(self.c)
        e,h=out['units']
        self.assertEqual((e['channels'],h['channels']),(1024,144))
        self.assertEqual((e['sensitive_count'],h['sensitive_count']),(4,144))
        si=sum(p['volume_mm3'] for p in e['parts'] if p['material']=='Silicon')
        self.assertAlmostEqual(si,4*90*90*.5)
        tile=next(p for p in h['parts'] if p['role']=='sensitive')
        self.assertAlmostEqual(tile['volume_mm3'],29.7**2*3-math.pi*2.5**2*.8)
    def test_reject_overlapping_or_uncontained_cuts(self):
        d=dict(sx=10,sy=10,sz=10)
        with self.assertRaisesRegex(ValueError,'not contained'):validate_cut('box',d,[cut_box([11,8,8])])
        with self.assertRaisesRegex(ValueError,'overlap'):validate_cut('box',d,[cut_box([8,8,8]),cut_tube(1,1,0)])
        for bad in (dict(sx=1,sy=0,sz=1),dict(sx=1,sy=1,sz=float('nan'))):
            with self.assertRaises(ValueError):capacity('box',bad)
    def test_absorber_has_one_owner(self):
        out,_=build(self.c)
        for u in out['units']:
            p=[p for p in u['parts'] if p['owner']=='sector'];self.assertEqual(len(p),1)
            self.assertEqual(p[0]['role'],'absorber')
            self.assertAlmostEqual(u['mass_g'],u['cassette_mass_g']+p[0]['mass_g'])
            self.assertAlmostEqual(sum(t['mass_g'] for t in u['material_totals'].values()),u['mass_g'])
    def test_package_constituent_mass(self):
        _,m=build(self.c)
        for name in self.c['package_recipes']:
            q=m.recipes[name]
            density=sum(f*m.recipes[k]['density_g_cm3'] for k,f in q['volume_fractions'].items())
            self.assertAlmostEqual(density,q['density_g_cm3'])
            self.assertAlmostEqual(sum(q['composition'].values()),1)
        self.c['package_recipes']['HCalPackage']['volume_fractions']['Copper']=.9
        with self.assertRaisesRegex(ValueError,'normalization'):build(self.c)
    def test_reject_readout_and_service_misfits(self):
        for kind,key,val in [('ecal','sensor_active_mm',89),('ecal','asic_rows',3),('hcal','tile_pitch_mm',29.9),('hcal','recess_radius_mm',1),('hcal','pcb_mm',.05),('ecal','body_depth_mm',7)]:
            c=copy.deepcopy(self.c);c[kind][key]=val
            with self.assertRaises(ValueError,msg=key):build(c)
        self.c['converter_efficiency']=1.1
        with self.assertRaises(ValueError):build(self.c)
    def test_continuous_power_and_heat_flow(self):
        out,_=build(self.c)
        for u in out['units']:
            p=u['power'];self.assertEqual(p['duty'],1)
            self.assertAlmostEqual(p['total_heat_W'],p['LV_input_W']+p['bias_W'])
            self.assertAlmostEqual(p['water_g_s']/1000*4180*5,p['total_heat_W'])
        c=copy.deepcopy(self.c);c['hcal']['asic_continuous_W_channel']*=2
        more,_=build(c);self.assertGreater(more['units'][1]['power']['total_heat_W'],out['units'][1]['power']['total_heat_W'])
    def test_deterministic_export(self):
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'a',Path(t)/'b';export(a);export(b)
            for name in ('materials.xml','calorimeter.xml','expected.json'):self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())

if __name__=='__main__':unittest.main()
