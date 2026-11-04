"""DES033 physical turbine, virtual readout and signed-end controls."""
from copy import deepcopy
import math
import unittest
from endcap_geometry import build, cell_indices, decode, encode, frame, gap_point, inside, logical_id, polygon_at, volume
from endcap_export import totals


class EndcapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model,cls.materials=build()

    def test_complete_wheels_periods_and_source_radii(self):
        j=self.model;self.assertEqual([w['periods'] for w in j['wheels']],[384,720,1360]);self.assertEqual(len(j['replicas']),4928)
        self.assertEqual(j['physical_sensitive_elements'],9856);self.assertEqual(j['logical_cells_per_side'],601600);self.assertEqual(j['logical_channels'],1203200)
        self.assertAlmostEqual(j['wheels'][0]['inner_radius_mm'],410)
        self.assertAlmostEqual(j['wheels'][-1]['outer_radius_mm'],2790)
        for i,w in enumerate(j['wheels']):
            self.assertEqual(len(w['pieces']),8)
            self.assertEqual(sum(p['role']=='sensitive' for p in w['pieces']),2)
            self.assertGreater(w['min_sampled_gap_mm'],0)
            self.assertLess(abs(w['fill_relative_residual']),1e-10)
            if i:self.assertAlmostEqual(w['inner_radius_mm']-j['wheels'][i-1]['outer_radius_mm'],10)

    def test_native_arb8_clockwise_convention_and_convergence(self):
        for w in self.model['wheels']:
            for p in w['pieces']:
                for z in (-p['half_z_mm'],p['half_z_mm']):
                    polygon=polygon_at(p['vertices_mm'],p['half_z_mm'],z)
                    signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
                    self.assertLess(signed,0)
                a=p['clip_annulus_mm'];n=p['capacity_convergence']['fine_steps']
                finer=volume(p['vertices_mm'],p['half_z_mm'],a['rmin'],a['rmax'],n*2)
                self.assertAlmostEqual(finer/p['volume_mm3'],1,delta=2e-9)
                self.assertLess(p['capacity_convergence']['relative_change'],2e-9)

    def test_all_raw_ids_unique_and_roundtrip(self):
        j=self.model;seen=set()
        for replica in j['replicas']:
            for gap in (0,1):
                ids=dict(system=j['readout']['system_id'],**{k:replica[k] for k in ('side','wheel','plane')},gap=gap,rho=0,z=0)
                raw=encode(ids);self.assertNotIn(raw,seen);seen.add(raw);self.assertEqual(decode(raw),ids)
        self.assertEqual(len(seen),9856)
        with self.assertRaises(ValueError):encode(dict(system=11,side=1,wheel=0,plane=2048))

    def test_all_references_physical_and_both_gaps_merge(self):
        j=self.model;count=0
        for w in j['wheels']:
            p0=next(p for p in w['pieces'] if p.get('gap')==0);p1=next(p for p in w['pieces'] if p.get('gap')==1)
            for ref in w['reference_points']:
                point=ref['position_mm'];self.assertTrue(inside(p0,point))
                self.assertEqual(cell_indices(point,w,j['readout']),(ref['rho'],ref['z']))
                alternate=gap_point(p1,math.hypot(*point[:2]),point[2]);self.assertTrue(inside(p1,alternate))
                for side in (1,2):
                    for plane in (0,w['periods']-1):
                        a=logical_id(dict(system=11,side=side,wheel=w['wheel'],plane=plane,gap=0),point,w,j['readout'])
                        b=logical_id(dict(system=11,side=side,wheel=w['wheel'],plane=plane,gap=1),alternate,w,j['readout'])
                        self.assertEqual(a,b);self.assertEqual(decode(a)['gap'],0)
                count+=2*w['periods']
        self.assertEqual(count,1203200)

    def test_radial_axial_boundaries_and_outside_hits(self):
        j=self.model
        for w in j['wheels']:
            p=next(p for p in w['pieces'] if p.get('gap')==0)
            for ir in range(1,w['radial_bins']):
                r=w['inner_radius_mm']+ir*(w['outer_radius_mm']-w['inner_radius_mm'])/w['radial_bins']
                for sign in (-1,1):self.assertEqual(cell_indices(gap_point(p,r+sign*1e-6,0),w,j['readout'])[0],ir-(sign<0))
            for iz in range(1,10):
                z=-225+iz*45
                for sign in (-1,1):self.assertEqual(cell_indices(gap_point(p,(w['inner_radius_mm']+w['outer_radius_mm'])/2,z+sign*1e-6),w,j['readout'])[1],iz-(sign<0))
            self.assertEqual(cell_indices(gap_point(p,w['outer_radius_mm'],225),w,j['readout']),(w['radial_bins']-1,9))
            for point in ([w['inner_radius_mm']-1,0,0],[w['outer_radius_mm']+1,0,0],[w['inner_radius_mm'],0,226]):
                with self.assertRaises(ValueError):cell_indices(point,w,j['readout'])

    def test_proper_signed_end_transforms(self):
        for r in self.model['replicas']:
            a=r['frame'];det=sum(a[0][i]*(a[1][(i+1)%3]*a[2][(i+2)%3]-a[1][(i+2)%3]*a[2][(i+1)%3]) for i in range(3))
            self.assertAlmostEqual(det,1)
            self.assertEqual(a[2][2],1 if r['side']==1 else -1)
            self.assertEqual(math.copysign(1,r['center_mm'][2]),1 if r['side']==1 else -1)

    def test_whole_enclosure_closure_support_ownership(self):
        j=self.model;e=j['envelopes'];whole=2*math.pi*(e['warm_outer_radius_mm']**2-e['warm_inner_radius_mm']**2)*(e['warm_back_z_mm']-e['warm_front_z_mm'])
        actual=sum(2*w['periods']*sum(p['volume_mm3'] for p in w['pieces']) for w in j['wheels'])+sum(p['volume_mm3'] for p in j['passive'])
        self.assertAlmostEqual(actual/whole,1,delta=1e-10)
        self.assertEqual(sum(p['role']=='wheel_support' for p in j['passive']),6)
        for side in (1,2):
            rear=next(p for p in j['passive'] if p['name']==f'rear_bath_{side}')
            self.assertAlmostEqual(rear['dimensions_mm']['length'],250)
            self.assertAlmostEqual(abs(rear['center_mm'][2]),5585)
        # Tube ownership checks use absolute-z intervals for each signed end.
        for side in (1,2):
            parts=[p for p in j['passive'] if p['name'].endswith('_'+str(side))]
            for i,a in enumerate(parts):
                da=a['dimensions_mm'];alo,ahi=abs(a['center_mm'][2])-da['length']/2,abs(a['center_mm'][2])+da['length']/2
                for b in parts[i+1:]:
                    db=b['dimensions_mm'];blo,bhi=abs(b['center_mm'][2])-db['length']/2,abs(b['center_mm'][2])+db['length']/2
                    self.assertFalse(min(da['rmax'],db['rmax'])-max(da['rmin'],db['rmin'])>1e-8 and min(ahi,bhi)-max(alo,blo)>1e-8,(a['name'],b['name']))

    def test_negative_geometry_and_missing_wheel(self):
        for key,value in [('inclination_deg',10),('lead_inner_mm',15),('warm_front_z_mm',4800),('inner_vacuum_mm',50),('radial_bins',[10,14,33])]:
            c=deepcopy(self.model['config']);c[key]=value
            with self.assertRaises(ValueError):build(c)
        j=deepcopy(self.model);j['replicas']=[r for r in j['replicas'] if r['wheel']!=2]
        with self.assertRaises(ValueError):totals(j)

    def test_parent_exclusive_displacement_conservation(self):
        j=deepcopy(self.model);mother=next(p for p in j['passive'] if p['name']=='rear_bath_1')
        child=deepcopy(mother);child.update(name='test_service',parent_name='rear_bath_1',volume_mm3=100,mass_g=.1396,role='test_fixture')
        mother['exclusive_volume_mm3']=mother['volume_mm3']-100;mother['displaced_volume_mm3']=100;j['passive'].append(child);totals(j)
        self.assertAlmostEqual(j['mass_g'],self.model['mass_g'],delta=1e-4)
        mother['exclusive_volume_mm3']+=10000
        with self.assertRaises(ValueError):totals(j)
        child['parent_name']='nonexistent'
        with self.assertRaises(ValueError):totals(j)


if __name__=='__main__':unittest.main()
