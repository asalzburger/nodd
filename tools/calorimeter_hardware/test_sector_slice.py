"""Analytic thin-film checks of native navigation and pixel-area integration."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sector_slice_native import CPP
try:
    import ROOT as R
except ImportError:
    R=None

@unittest.skipIf(R is None,'Native ROOT runtime required; run with software/env/run.sh')
class NativeSliceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        R.gROOT.SetBatch(True)
        if not R.gInterpreter.Declare(CPP):raise RuntimeError('Native slice helper compile')

    def test_subpixel_film_and_exact_boundary_ray(self):
        mm=.1;g=R.TGeoManager('slice_fixture','Analytic test geometry only');R.SetOwnership(g,False)
        air=R.TGeoMaterial('fixture_air',1.,1.,.001);si=R.TGeoMaterial('fixture_Si',28.,14.,2.33)
        ma=R.TGeoMedium('fixture_air',1,air);ms=R.TGeoMedium('fixture_Si',2,si)
        world=g.MakeBox('fixture_world',ma,20*mm,20*mm,20*mm);g.SetTopVolume(world)
        film=g.MakeBox('fixture_film',ms,.25*mm,5*mm,5*mm)
        shift=R.TGeoTranslation(3.25*mm,0,0);R.SetOwnership(shift,False)
        world.AddNode(film,1,shift)
        # The TGeoManager owns these registered objects; Python must not delete them.
        for item in (air,si,ma,ms,world,film):R.SetOwnership(item,False)
        g.CloseGeometry()
        size=max(v.GetNumber() for v in g.GetListOfVolumes())+1
        pal=R.std.vector('double')([255.]*(3*size));flags=R.std.vector('int')([0]*size)
        for k,v in enumerate((204.,204.,0.)):pal[film.GetNumber()*3+k]=v
        flags[film.GetNumber()]=1
        pixels=R.NativeXY.render(g,mm,pal,0.,10.,0.,1.,0.,10,1,1,False)
        raw=bytes(ord(v) if isinstance(v,str) else v for v in pixels)
        # Half of the 1mm pixel at x=[3,4] is actual 0.5mm Si; it must not vanish.
        self.assertEqual(raw[9:12],bytes((230,230,128)))
        self.assertEqual(raw[:9],bytes([255]*9));self.assertEqual(raw[12:],bytes([255]*18))
        ray=list(R.NativeXY.ray(g,mm,flags,0.,0.,10.));self.assertEqual(len(ray),3)
        self.assertAlmostEqual(ray[0],3.,places=7);self.assertAlmostEqual(ray[1],.5,places=7)

if __name__=='__main__':unittest.main()
