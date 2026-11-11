"""Adversarial controls for the native sensor comparison (test fixtures only)."""
from copy import deepcopy
import unittest
from compare_geant4 import compare


class Geant4ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.fixture=[dict(id=123,center_mm=[1.,2.,3.],u=[1.,0.,0.],v=[0.,1.,0.],
            normal=[0.,0.,1.],size_mm=[4.,5.,6.],material='test_material',
            density_g_cm3=1.,region='test_region')]

    def test_identical_complete_inventory(self):
        self.assertEqual(compare(self.fixture,deepcopy(self.fixture),expected=1)['status'],'PASS')

    def test_rejects_missing_duplicate_or_wrong_ids(self):
        for other in ([],self.fixture*2,[dict(self.fixture[0],id=456)]):
            with self.subTest(other=other),self.assertRaises(ValueError):
                compare(self.fixture,other,expected=1)

    def test_rejects_physical_changes(self):
        for key,value in [('center_mm',[1.,2.,3.1]),('normal',[0.,0.,-1.]),
                          ('size_mm',[4.,5.,7.]),('material','other'),
                          ('center_mm',[float('nan'),2.,3.]),
                          ('density_g_cm3',1.1),('region','other')]:
            other=deepcopy(self.fixture);other[0][key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):
                compare(self.fixture,other,expected=1)


if __name__=='__main__':
    unittest.main()
