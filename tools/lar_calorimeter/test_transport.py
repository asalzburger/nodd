import unittest
from barrel_geometry import build,encode
from check_transport import valid_cell
class TransportTests(unittest.TestCase):
    def test_real_and_ghost_hit_cells(self):
        r,_=build();valid=r['readout']['layers'][5]['indices'][0]
        fields=dict(system=10,plane=0,layer=5,gap=0,theta=valid)
        self.assertEqual(valid_cell(encode(fields),r)['theta'],valid)
        for key,value in [('theta',2047),('plane',1),('gap',1),('system',11)]:
            f=dict(fields);f[key]=value
            with self.assertRaises(ValueError):valid_cell(encode(f),r)
if __name__=='__main__':unittest.main()
