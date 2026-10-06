import math
import unittest
import numpy as np
from model import load,build,cooling,rings
from check_layout import batch_hits

class ModelControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=load();cls.l=build(cls.c)
    def test_module_contract_counts_ids(self):
        self.assertEqual([r['modules'] for r in rings(self.c)],[48,60,72,84,96])
        self.assertEqual(len(self.l['modules']),4320)
        ids={(m['layer'],m['petal'],m['ring'],m['module']) for m in self.l['modules']}
        self.assertEqual(len(ids),4320)
        self.assertTrue(all(len(r['modules'])==30 and r['harnesses']==3 for r in self.l['routes']))
    def test_signed_frames(self):
        for m in self.l['modules']:
            self.assertTrue(np.allclose(np.cross(m['u'],m['v']),m['n'],atol=1e-12))
            self.assertAlmostEqual(np.dot(m['u'],m['v']),0,places=12)
    def test_collector_and_radial_limits(self):
        self.assertEqual(self.c['disc_z_mm'][0]-13.5-1310,11.5)
        self.assertLess(math.hypot(705,26),710)
        self.assertLess(math.hypot(699,17),700)
        self.assertLess(max(math.hypot(m['radius_mm']+51.5,24.5) for m in self.l['modules']),685)
        with self.assertRaises(ValueError):
            from model import load as checked
            import json,tempfile,pathlib
            c=dict(self.c,disc_z_mm=[1295.5,*self.c['disc_z_mm'][1:]])
            with tempfile.TemporaryDirectory() as d:
                p=pathlib.Path(d)/'bad.json';p.write_text(json.dumps(c));checked(p)
    def test_nearest_azimuth_bound(self):
        # At the most inward sensor point the full tangential reach is less
        # than1.5 centre spacings: nearest +/-1 cannot omit a rectangular hit.
        for r in rings(self.c):
            reach=math.atan2(24,r['radius_mm']-48)
            self.assertLess(reach,1.5*2*math.pi/r['modules'])
    def test_cooling_cut_containment_and_separation(self):
        segs=cooling(self.c);samples=[]
        for p in segs:
            d=p['dims'];center=np.array(p['center'][:2])
            if p['kind']=='torus':
                a=np.linspace(d['start'],d['start']+d['angle'],401)
                pts=center+d['major']*np.stack([np.cos(a),np.sin(a)],axis=1)
            else:
                dr=np.array([math.cos(p['rz']),math.sin(p['rz'])])*d['length']/2
                pts=np.linspace(center-dr,center+dr,401)
            r=np.linalg.norm(pts,axis=1);phi=np.arctan2(pts[:,1],pts[:,0])
            self.assertGreater(r.min()-1.25,236);self.assertLess(r.max()+1.25,685)
            self.assertGreater((r*np.sin(phi-self.c['petal_gap_mm']/236/2)).min(),1.25)
            self.assertGreater((r*np.sin(math.pi/6-self.c['petal_gap_mm']/236/2-phi)).min(),1.25)
            samples.append(pts)
        # Non-adjacent cooling envelopes must not overlap. Exclude pairs
        # sharing endpoints, whose finite torus/tube solids meet tangentially.
        for i,a in enumerate(samples):
            for j,b in enumerate(samples[i+1:],i+1):
                if min(np.linalg.norm(x-y) for x in (a[0],a[-1]) for y in (b[0],b[-1]))<1e-6:continue
                distance=np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(axis=2)).min()
                self.assertGreater(distance,2.5,(segs[i]['label'],segs[j]['label']))
    def test_pickups_clear_complete_module_envelopes(self):
        # Independent separating-axis test in xy plus exact occupied z ranges.
        ms=[m for m in self.l['modules'] if m['layer']==0]
        centers=np.array([m['center_mm'] for m in ms]);u=np.array([m['u'] for m in ms]);v=np.array([m['v'] for m in ms])
        half=np.array([24.5,51.5]);bodylo=centers[:,2]-.9;bodyhi=centers[:,2]+.1
        for i,m in enumerate(ms):
            for sign in (-1,1):
                p=centers[i].copy();p+=sign*self.c['pickup_u_mm']*u[i];p[2]=self.c['disc_z_mm'][0]-1.3
                delta=centers-p;zover=(bodyhi>p[2]+1e-9)&(bodylo<centers[i,2]-.9-1e-9)
                separated=np.zeros(len(ms),bool)
                for axis in (np.tile(u[i],(len(ms),1)),np.tile(v[i],(len(ms),1)),u,v):
                    d=np.abs(np.sum(delta*axis,axis=1))
                    reach=half[0]*np.abs(np.sum(u*axis,axis=1))+half[1]*np.abs(np.sum(v*axis,axis=1))
                    reach+=self.c['pickup_mm'][0]/2*np.abs(axis@u[i])+self.c['pickup_mm'][1]/2*np.abs(axis@v[i])
                    separated|=d>=reach-1e-9
                self.assertFalse(np.any(zover&~separated),m['name'])

    def test_first_disc_shift_can_lose_only_endcap_hit(self):
        track=dict(origin_mm=[0,0,0],eta=1.4,phi=.17,pt_GeV=1,field_T=4,charge=1)
        new,_=batch_hits(self.c,[track]);old,_=batch_hits(self.c,[track],True)
        self.assertTrue(old.any())
        self.assertFalse(new.any())

    def test_true_sensor_centre_hit(self):
        for m in (self.l['modules'][0],self.l['modules'][-1]):
            p=m['center_mm'];r=math.hypot(*p[:2]);eta=math.asinh(p[2]/r);phi=math.atan2(p[1],p[0])
            h,_=batch_hits(self.c,[dict(origin_mm=[0,0,0],eta=eta,phi=phi,pt_GeV=10,field_T=0,charge=1)])
            self.assertTrue(h[0,m['layer']])

if __name__=='__main__':unittest.main()
