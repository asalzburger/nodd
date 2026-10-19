"""Independent primitive and path controls for DES040; no detector runtime."""
import math
import unittest
import numpy as np
from tools.toroid_prototype.system import load_design
from tools.toroid_prototype.geometry import coil_mask
from .geometry import (prism,beam,contains,intersects,ray_intervals,midplane_hits,
                       certify_coil_clear,coil_ray_intervals,volume)


class GeometryTests(unittest.TestCase):
    def box(self,origin=(0,0,3),depth=1):
        return prism('fixture','test',origin,np.eye(3),[[-1,-1],[1,-1],[1,1],[-1,1]],depth)

    def test_prism_interval_volume_and_boundary(self):
        b=self.box();self.assertEqual(volume(b),4)
        d=np.array([[0,0,1],[0,0,-1],[1,0,0.]])
        lo,hi=ray_intervals(b,d)
        np.testing.assert_allclose([lo[0],hi[0]],[2.5,3.5]);self.assertTrue(np.isinf(lo[1:]).all())
        self.assertTrue(contains(b,[[1,1,3.5]])[0])
        self.assertFalse(contains(b,[[1.001,0,3]])[0])

    def test_full_depth_rejects_side_entry_midplane_hit(self):
        b=self.box();d=np.array([[.32,0,1.]]);d/=np.linalg.norm(d,axis=1)[:,None]
        self.assertTrue(np.isfinite(midplane_hits(b,d)[0]))
        self.assertFalse(np.isfinite(midplane_hits(b,d,full_depth=True)[0]))

    def test_sat_actual_volume_not_projection(self):
        a=self.box();b=self.box(origin=(0,0,4.1))
        self.assertFalse(intersects(a,b));self.assertTrue(intersects(a,b,clearance=.11))
        self.assertTrue(intersects(a,self.box(origin=(0,0,4))))
        c=beam('cross',[-2,0,3],[2,0,3],.1,.1)
        self.assertTrue(intersects(a,c))

    def test_corner_only_coil_check_is_insufficient(self):
        c=load_design();b=prism('fixture','test',[4.6,0,0],np.eye(3),
                               [[-.25,-.5],[.25,-.5],[.25,.5],[-.25,.5]],1.)
        from .geometry import vertices3
        self.assertFalse(coil_mask(vertices3(b),c).any())
        result=certify_coil_clear(b,c,clearance=0)
        self.assertFalse(result['clear']);self.assertEqual(result['reason'],'occupied volume witness')

    def test_adaptive_clearance_certificate_and_near_case_rejection(self):
        c=load_design()
        b=prism('clear','test',[5.3,0,0],np.eye(3),[[-.1,-.2],[.1,-.2],[.1,.2],[-.1,.2]],.5)
        self.assertTrue(certify_coil_clear(b,c)['clear'])
        b['origin_m']=[4.9,0,0]
        self.assertFalse(certify_coil_clear(b,c)['clear'])

    def test_exact_coil_ray_intervals_match_existing_distance_mask(self):
        rng=np.random.default_rng(4040);d=rng.normal(size=(700,3));d/=np.linalg.norm(d,axis=1)[:,None]
        s=rng.uniform(.1,18,len(d));c=load_design()
        for padding in (0.,.05):
            got=np.zeros(len(d),bool)
            for _,_,lo,hi in coil_ray_intervals(d,c,clearance=padding):got|=(s>=lo)&(s<=hi)
            np.testing.assert_array_equal(got,coil_mask(s[:,None]*d,c,clearance=padding))
        # Add dense witnesses through the inner/outer legs and both endcap returns.
        p=np.array([[r,0,z] for r in [4.2,4.35,4.6,4.85,5.,8.5,8.8,9.05,9.2] for z in [0,6.5,6.8,8.,11.7,12.1]])
        s=np.linalg.norm(p,axis=1);d=p/s[:,None];got=np.zeros(len(d),bool)
        for _,_,lo,hi in coil_ray_intervals(d,c):got|=(s>=lo-1e-10)&(s<=hi+1e-10)
        # Boundary literals can round either way; compare comfortably inside/outside.
        margin=np.array([min(abs(r-x) for x in [4.35,4.85,8.55,9.05]) for r,_,z in p])
        take=margin>.001
        np.testing.assert_array_equal(got[take],coil_mask(p,c)[take])


if __name__=='__main__':unittest.main()
