import math
import unittest
import numpy as np
from tools.muon_layout import geometry as g
from tools.muon_layout.layout import inputs,candidates,_children,tiles
from tools.muon_layout.coverage import sphere_grid,panel_hits


class PackingControls(unittest.TestCase):
    def setUp(self):self.config,self.magnetic=inputs()

    def test_tiles_gap_size_and_identifier_uniqueness(self):
        ch=self.config['chambers'];bodies=list(candidates(self.config))
        self.assertEqual(len(bodies),len({b['id'] for b in bodies}))
        for lo,hi in tiles(-10.7,10.7,2,.02):self.assertLessEqual(hi-lo,2)
        self.assertEqual(sum(b['kind']=='barrel' for b in bodies),696)
        for b in bodies:
            self.assertEqual(len(b['vertices_m']),4)
            self.assertAlmostEqual(np.linalg.det(b['basis']),1)
            self.assertIn(b['station'],[1,2,3])

    def test_flat_barrel_volume_neighbour_clearance(self):
        bodies=list(candidates(self.config))
        for station in [1,2,3]:
            aa=next(b for b in bodies if b['id']==f'B{station}/F00/Z00')
            bb=next(b for b in bodies if b['id']==f'B{station}/F01/Z00')
            self.assertFalse(g.intersects(aa,bb))
            R=self.config['chambers']['barrel_apothems_m'][station-1]
            W=2*(R-.25)*math.tan(math.radians(7.5))-.02
            v=np.asarray(aa['vertices_m'])
            self.assertAlmostEqual(v[:,0].max()-v[:,0].min(),W)

    def test_trapezoid_all_corners_in_cylindrical_compartment(self):
        for body in candidates(self.config):
            if body['kind']!='endcap':continue
            lo,hi=body['compartment']['radial_m'];v=g.vertices3(body);r=np.linalg.norm(v[:,:2],axis=1)
            self.assertGreaterEqual(r.min(),lo-1e-12);self.assertLessEqual(r.max(),hi+1e-12)
            p=np.asarray(body['vertices_m']);self.assertAlmostEqual(p[0,0],p[3,0]);self.assertAlmostEqual(p[1,0],p[2,0])
            children=_children(body,self.config['chambers'],0)
            for child in children:
                self.assertGreaterEqual(g.polygon_area(child['vertices_m']),.25)
            if children:self.assertFalse(g.intersects(*children))

    def test_count_unique_stations_not_panels(self):
        b=g.prism('one','barrel',[3,0,0],np.column_stack(([0,1,0],[0,0,1],[1,0,0])),
                  [[-1,-1],[1,-1],[1,1],[-1,1]],.5,station=1)
        d=np.array([[1.,0,0],[-1.,0,0]])
        ss=panel_hits([b,dict(b,id='duplicate')],d,.03)
        self.assertEqual(np.isfinite(ss['active'][:,0]).sum(),1)
        self.assertEqual(np.isfinite(ss['active'][:,1]).sum(),0)

    def test_full_sphere_grid_includes_both_hemispheres(self):
        mu,phi,d=sphere_grid(20,48)
        self.assertTrue(np.allclose(np.linalg.norm(d,axis=1),1))
        self.assertEqual((d[:,2]>0).sum(),480);self.assertEqual((d[:,2]<0).sum(),480)
        self.assertAlmostEqual(20*48*(2/20)*(2*np.pi/48),4*np.pi)
        self.assertGreater(phi.min(),0);self.assertLess(phi.max(),360)


if __name__=='__main__':unittest.main()
