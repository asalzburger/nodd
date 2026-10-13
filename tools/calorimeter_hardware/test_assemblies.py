"""Independent physical packing, symmetry and ownership controls."""
import copy,math,unittest,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from assembly_export import export
from sector_fixture import fixture
from assembly import inventory,frame_rotation
from model import I

def corners(p,u):
    for x in (-u['width_mm']/2,u['width_mm']/2):
        for y in (-u['height_mm']/2,u['height_mm']/2):
            for z in (0,u['body_depth_mm']):
                yield [p['center_mm'][j]+sum(v*p['frame'][i][j] for i,v in enumerate((x,y,z))) for j in range(3)]

def check_containment(report):
    c=report['config'];tan=math.tan(math.pi/c['sectors'])
    for r in report['regions']:
        u=next(u for u in report['units'] if u['name']==r['unit']);ids=set()
        for p in r['placements']:
            identity=(p['layer'],p['cassette'])
            if identity in ids:raise ValueError('duplicate cassette ID')
            ids.add(identity)
            for x,y,z in corners(p,u):
                if abs(y)>x*tan-c['seam_half_gap_mm']-c['edge_rail_mm']+1e-7:raise ValueError('sector edge containment')
                if r['kind']=='barrel':
                    if abs(z)>c['barrel_half_z_mm']-c['end_allocation_mm']+1e-7:raise ValueError('barrel end containment')
                    front=r['front_mm']+p['layer']*r['pitch_mm']+u['absorber_mm']
                    if x<front-1e-7 or x>front+u['body_depth_mm']+1e-7:raise ValueError('barrel layer depth')
                else:
                    if x<c['endcap_inner_apothem_mm']+c['endcap_rim_mm'] or x>r['outer_apothem_mm']-c['endcap_rim_mm']:raise ValueError('endcap radial containment')
                    front=r['front_mm']+p['layer']*r['pitch_mm']+u['absorber_mm']
                    if z<front-1e-7 or z>front+u['body_depth_mm']+1e-7:raise ValueError('endcap layer depth')

class AssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report,_=inventory()
    def test_all_logical_cassette_corners(self):check_containment(self.report)
    def test_negative_placement_and_identity_controls(self):
        x=copy.deepcopy(self.report);x['regions'][0]['placements'][0]['center_mm'][1]=1e6
        with self.assertRaisesRegex(ValueError,'edge'):check_containment(x)
        x=copy.deepcopy(self.report);x['regions'][0]['placements'].append(x['regions'][0]['placements'][0])
        with self.assertRaisesRegex(ValueError,'duplicate'):check_containment(x)
    def test_proper_transform_and_endcap_symmetry(self):
        for p in self.report['replicas']:
            f=p['frame']
            for i in range(3):
                for j in range(3):self.assertAlmostEqual(sum(f[i][k]*f[j][k] for k in range(3)),1 if i==j else 0)
            det=sum(f[0][i]*(f[1][(i+1)%3]*f[2][(i+2)%3]-f[1][(i+2)%3]*f[2][(i+1)%3]) for i in range(3))
            self.assertAlmostEqual(det,1)
        for phi in (0,.3,2.1):
            plus=frame_rotation(phi);minus=frame_rotation(phi,True);point=[350,20,4100]
            a=[sum(point[i]*plus[i][j] for i in range(3)) for j in range(3)];b=[sum([point[0],-point[1],point[2]][i]*minus[i][j] for i in range(3)) for j in range(3)]
            self.assertAlmostEqual(a[0],b[0]);self.assertAlmostEqual(a[1],b[1]);self.assertAlmostEqual(a[2],-b[2])
    def test_absorber_count_and_aggregate_conservation(self):
        r=self.report
        self.assertAlmostEqual(sum(s['mass_g'] for s in r['summary']),r['mass_g'],places=5)
        for region in r['regions']:
            layers=r['config'][region['unit']+'_layers'];plates=[p for p in region['parts'] if p['role']=='absorber'];self.assertEqual(len(plates),layers)
            self.assertTrue(all(x['mass_g']>0 for x in region['parts']))
        for unit in r['units']:
            self.assertEqual(sum(p['owner']=='sector' for p in unit['parts']),1)
    def test_area_loss_and_service_loads_are_exposed(self):
        for r in self.report['regions']:
            self.assertTrue(all(0<x['active_fraction']<x['occupied_fraction']<1 for x in r['coverage']))
        for s in self.report['summary']:
            self.assertAlmostEqual(s['water_g_s']/1000*4180*5,s['continuous_heat_W'])
        self.assertGreater(sum(s['continuous_heat_W'] for s in self.report['summary']),400000)
    def test_assembly_export_and_sparse_fixture_are_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'a',Path(t)/'b';export(a);export(b)
            for name in ('materials.xml','calorimeter.xml','expected.json'):self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            original=(a/'calorimeter.xml').read_bytes();fixture(a/'calorimeter.xml',a/'expected.json',a/'fixture.xml')
            doc=ET.parse(a/'fixture.xml');full=ET.parse(a/'calorimeter.xml')
            self.assertEqual(original,(a/'calorimeter.xml').read_bytes())
            for reduced,complete in zip(doc.getroot().find('detectors'),full.getroot().find('detectors')):
                self.assertEqual(len(reduced.findall('replica')),3)
                for r,f in zip(reduced.findall('region'),complete.findall('region')):
                    self.assertEqual(len(r.findall('passive')),len(f.findall('passive')))
                    p=r.findall('placement');self.assertEqual(len(p),len({x.get('layer') for x in p}))

    def test_identifier_and_clearance_negative_controls(self):
        for key,value in (('sectors',33),('ecal_layers',65),('barrel_half_z_mm',3950),('interface_gap_mm',-1)):
            c=copy.deepcopy(self.report['config']);c[key]=value
            with self.assertRaises(ValueError,msg=key):inventory(c)

if __name__=='__main__':unittest.main()
