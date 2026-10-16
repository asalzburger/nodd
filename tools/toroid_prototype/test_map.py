import tempfile
from pathlib import Path
import unittest
import numpy as np
from .map import FieldMap

class MapTests(unittest.TestCase):
    def make(self,path,masked=False):
        b=np.zeros((3,3,3,3));b[:]=[1,2,3]
        valid=np.ones((3,3,3),bool)
        if masked:valid[1,1,1]=False
        np.savez(path,r_m=np.array([0,1,2.]),z_m=np.array([-1,0,1.]),phi_deg=np.array([0,15,30.]),B_total_cyl_T=b,valid_field=valid)
        return FieldMap(path)

    def test_periodic_sector_rotates_vectors(self):
        with tempfile.TemporaryDirectory() as d:
            f=self.make(Path(d)/'map.npz')
            p=np.array([[np.cos(a),np.sin(a),0.] for a in np.radians([7.5,37.5,367.5,-352.5])])
            out=f.field(p)
            for point,b in zip(p,out):
                c,s=point[:2]
                np.testing.assert_allclose(b,[c-2*s,s+2*c,3],atol=1e-12)

    def test_reject_mask_and_extrapolation(self):
        with tempfile.TemporaryDirectory() as d:
            f=self.make(Path(d)/'map.npz',masked=True)
            for p in [[[.8,.1,0]],[[3,0,0]],[[1,0,2]],[[float('nan'),0,0]]]:
                with self.assertRaises(ValueError):f.field(p)

if __name__=='__main__':unittest.main()
